from collections.abc import Sequence
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.student import Student
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    def __init__(
        self,
        session: AsyncSession,
        repository: StudentRepository,
        lesson_repository: LessonRepository,
    ):
        self.session = session
        self.repository = repository
        self.lesson_repository = lesson_repository
        self.logger = logging.getLogger(__name__)

    async def list_students(self) -> Sequence[Student]:
        self.logger.info("Listing students")
        return await self.repository.list()

    async def create_student(self, payload: StudentCreate) -> Student:
        self.logger.info("Creating student name=%s default_rate=%s", payload.name, payload.default_rate)
        student = await self.repository.create(payload.model_dump())
        await self.session.commit()
        return student

    async def update_student(self, student_id: int, payload: StudentUpdate) -> Student:
        self.logger.info("Updating student id=%s", student_id)
        student = await self.repository.get(student_id)
        if not student:
            raise NotFoundError("Student not found.")

        updated = await self.repository.update(
            student,
            payload.model_dump(exclude_unset=True),
        )
        await self.session.commit()
        return updated

    async def delete_student(self, student_id: int) -> None:
        self.logger.info("Deleting student id=%s", student_id)
        student = await self.repository.get(student_id)
        if not student:
            raise NotFoundError("Student not found.")

        lessons_count = await self.lesson_repository.count_by_student(student_id)
        if lessons_count:
            self.logger.warning(
                "Student delete blocked id=%s related_lessons=%s",
                student_id,
                lessons_count,
            )
            raise ConflictError("Cannot delete student with existing lessons.")

        try:
            await self.repository.delete(student)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.warning("Student deletion failed id=%s", student_id)
            raise ConflictError("Student deletion failed due to related records.") from exc
