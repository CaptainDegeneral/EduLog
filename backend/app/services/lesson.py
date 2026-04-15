import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.models.enums import LessonStatus
from app.models.lesson import Lesson
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.repositories.subject import SubjectRepository
from app.schemas.lesson import LessonCreate, LessonFilters, LessonRead, LessonUpdate
from app.schemas.student import StudentReference
from app.schemas.subject import SubjectReference
from app.utils.datetime import calculate_debt, calculate_duration_hours, calculate_total


class LessonService:
    def __init__(
        self,
        session: AsyncSession,
        repository: LessonRepository,
        student_repository: StudentRepository,
        subject_repository: SubjectRepository,
    ):
        self.session = session
        self.repository = repository
        self.student_repository = student_repository
        self.subject_repository = subject_repository
        self.logger = logging.getLogger(__name__)

    async def list_lessons(self, filters: LessonFilters) -> list[LessonRead]:
        self.logger.info("Listing lessons filters=%s", filters.model_dump(exclude_none=True))
        lessons = await self.repository.list(filters)
        return [self.serialize_lesson(lesson) for lesson in lessons]

    async def create_lesson(self, payload: LessonCreate) -> LessonRead:
        self.logger.info(
            "Creating lesson student_id=%s subject_id=%s date=%s",
            payload.student_id,
            payload.subject_id,
            payload.date,
        )
        student = await self.student_repository.get(payload.student_id)
        if not student:
            raise NotFoundError("Student not found.")

        subject = await self.subject_repository.get(payload.subject_id)
        if not subject:
            raise NotFoundError("Subject not found.")

        rate = payload.rate if payload.rate is not None else student.default_rate
        self._validate_payload(
            start_time=payload.start_time,
            end_time=payload.end_time,
            rate=rate,
            prepayment_amount=payload.prepayment_amount,
        )

        if payload.status != LessonStatus.CANCELLED:
            await self._ensure_no_overlap(
                student_id=payload.student_id,
                lesson_date=payload.date,
                start_time=payload.start_time,
                end_time=payload.end_time,
            )

        lesson = await self.repository.create(
            {
                **payload.model_dump(exclude={"rate"}),
                "rate": rate,
            }
        )
        lesson = await self.repository.get(lesson.id)
        await self.session.commit()
        return self.serialize_lesson(lesson)

    async def update_lesson(self, lesson_id: int, payload: LessonUpdate) -> LessonRead:
        self.logger.info("Updating lesson id=%s payload_fields=%s", lesson_id, sorted(payload.model_dump(exclude_unset=True).keys()))
        lesson = await self.repository.get(lesson_id)
        if not lesson:
            raise NotFoundError("Lesson not found.")

        update_data = payload.model_dump(exclude_unset=True)
        merged_data = {
            "date": update_data.get("date", lesson.date),
            "start_time": update_data.get("start_time", lesson.start_time),
            "end_time": update_data.get("end_time", lesson.end_time),
            "student_id": update_data.get("student_id", lesson.student_id),
            "subject_id": update_data.get("subject_id", lesson.subject_id),
            "rate": update_data.get("rate", lesson.rate),
            "prepayment_amount": update_data.get(
                "prepayment_amount",
                lesson.prepayment_amount,
            ),
            "status": update_data.get("status", lesson.status),
            "notes": update_data.get("notes", lesson.notes),
        }

        student = await self.student_repository.get(merged_data["student_id"])
        if not student:
            raise NotFoundError("Student not found.")

        subject = await self.subject_repository.get(merged_data["subject_id"])
        if not subject:
            raise NotFoundError("Subject not found.")

        if merged_data["rate"] is None:
            merged_data["rate"] = student.default_rate

        self._validate_payload(
            start_time=merged_data["start_time"],
            end_time=merged_data["end_time"],
            rate=merged_data["rate"],
            prepayment_amount=merged_data["prepayment_amount"],
        )

        if merged_data["status"] != LessonStatus.CANCELLED:
            await self._ensure_no_overlap(
                student_id=merged_data["student_id"],
                lesson_date=merged_data["date"],
                start_time=merged_data["start_time"],
                end_time=merged_data["end_time"],
                exclude_lesson_id=lesson.id,
            )

        updated = await self.repository.update(lesson, merged_data)
        updated = await self.repository.get(updated.id)
        await self.session.commit()
        return self.serialize_lesson(updated)

    async def delete_lesson(self, lesson_id: int) -> None:
        self.logger.info("Deleting lesson id=%s", lesson_id)
        lesson = await self.repository.get(lesson_id)
        if not lesson:
            raise NotFoundError("Lesson not found.")

        await self.repository.delete(lesson)
        await self.session.commit()

    def serialize_lesson(self, lesson: Lesson) -> LessonRead:
        duration_hours = calculate_duration_hours(lesson.start_time, lesson.end_time)
        total = calculate_total(duration_hours, lesson.rate, lesson.status)
        debt = calculate_debt(total, lesson.prepayment_amount)
        self.logger.debug(
            "Computed lesson metrics lesson_id=%s duration=%s total=%s debt=%s",
            lesson.id,
            duration_hours,
            total,
            debt,
        )

        return LessonRead(
            id=lesson.id,
            date=lesson.date,
            start_time=lesson.start_time,
            end_time=lesson.end_time,
            student_id=lesson.student_id,
            subject_id=lesson.subject_id,
            rate=lesson.rate,
            prepayment_amount=lesson.prepayment_amount,
            status=lesson.status,
            notes=lesson.notes,
            student=StudentReference(id=lesson.student.id, name=lesson.student.name),
            subject=SubjectReference(id=lesson.subject.id, name=lesson.subject.name),
            duration_hours=duration_hours,
            total=total,
            debt=debt,
        )

    def _validate_payload(
        self,
        *,
        start_time,
        end_time,
        rate: float,
        prepayment_amount: float,
    ) -> None:
        if end_time <= start_time:
            self.logger.warning("Lesson validation failed reason=end_before_start start=%s end=%s", start_time, end_time)
            raise ValidationError("Lesson end_time must be greater than start_time.")
        if rate < 0:
            self.logger.warning("Lesson validation failed reason=negative_rate rate=%s", rate)
            raise ValidationError("Lesson rate must be greater than or equal to zero.")
        if prepayment_amount < 0:
            self.logger.warning("Lesson validation failed reason=negative_prepayment prepayment=%s", prepayment_amount)
            raise ValidationError(
                "Lesson prepayment_amount must be greater than or equal to zero."
            )

    async def _ensure_no_overlap(
        self,
        *,
        student_id: int,
        lesson_date,
        start_time,
        end_time,
        exclude_lesson_id: int | None = None,
    ) -> None:
        overlaps = await self.repository.find_overlapping_lessons(
            student_id=student_id,
            lesson_date=lesson_date,
            start_time=start_time,
            end_time=end_time,
            exclude_lesson_id=exclude_lesson_id,
        )

        if overlaps:
            self.logger.warning(
                "Lesson overlap detected student_id=%s date=%s start=%s end=%s exclude_id=%s",
                student_id,
                lesson_date,
                start_time,
                end_time,
                exclude_lesson_id,
            )
            raise ConflictError("Lesson overlaps with another lesson for this student.")
