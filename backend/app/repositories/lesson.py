from collections.abc import Sequence
from datetime import date, time
import logging

from sqlalchemy import Select, func, select
from sqlalchemy.orm import selectinload

from app.models.enums import LessonStatus
from app.models.lesson import Lesson
from app.repositories.base import BaseRepository
from app.schemas.lesson import LessonFilters


class LessonRepository(BaseRepository[Lesson]):
    model = Lesson
    logger = logging.getLogger(__name__)

    def _base_statement(self) -> Select[tuple[Lesson]]:
        return (
            select(Lesson)
            .options(
                selectinload(Lesson.student),
                selectinload(Lesson.subject),
            )
            .order_by(Lesson.date.desc(), Lesson.start_time.desc(), Lesson.id.desc())
        )

    async def get(self, entity_id: int) -> Lesson | None:
        statement = self._base_statement().where(Lesson.id == entity_id)
        result = await self.session.scalars(statement)
        lesson = result.first()
        self.logger.debug("Repository get model=Lesson id=%s found=%s", entity_id, lesson is not None)
        return lesson

    async def list(self, filters: LessonFilters | None = None) -> Sequence[Lesson]:
        statement = self._base_statement()

        if filters:
            if filters.date:
                statement = statement.where(Lesson.date == filters.date)
            if filters.student_id:
                statement = statement.where(Lesson.student_id == filters.student_id)
            if filters.status:
                statement = statement.where(Lesson.status == filters.status)

        lessons = await super().list(statement)
        self.logger.info(
            "Repository list model=Lesson count=%s filters=%s",
            len(lessons),
            filters.model_dump() if filters else {},
        )
        return lessons

    async def find_overlapping_lessons(
        self,
        *,
        student_id: int,
        lesson_date: date,
        start_time: time,
        end_time: time,
        exclude_lesson_id: int | None = None,
    ) -> Sequence[Lesson]:
        statement = self._base_statement().where(
            Lesson.student_id == student_id,
            Lesson.date == lesson_date,
            Lesson.status != LessonStatus.CANCELLED,
            Lesson.start_time < end_time,
            Lesson.end_time > start_time,
        )

        if exclude_lesson_id is not None:
            statement = statement.where(Lesson.id != exclude_lesson_id)

        result = await self.session.scalars(statement)
        overlaps = result.all()
        self.logger.info(
            "Repository overlap_check student_id=%s date=%s count=%s",
            student_id,
            lesson_date,
            len(overlaps),
        )
        return overlaps

    async def count_by_student(self, student_id: int) -> int:
        statement = select(func.count(Lesson.id)).where(Lesson.student_id == student_id)
        count = int((await self.session.scalar(statement)) or 0)
        self.logger.debug("Repository count_by_student student_id=%s count=%s", student_id, count)
        return count

    async def count_by_subject(self, subject_id: int) -> int:
        statement = select(func.count(Lesson.id)).where(Lesson.subject_id == subject_id)
        count = int((await self.session.scalar(statement)) or 0)
        self.logger.debug("Repository count_by_subject subject_id=%s count=%s", subject_id, count)
        return count
