from collections.abc import Sequence
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.subject import Subject
from app.repositories.lesson import LessonRepository
from app.repositories.subject import SubjectRepository
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectService:
    def __init__(
        self,
        session: AsyncSession,
        repository: SubjectRepository,
        lesson_repository: LessonRepository,
    ):
        self.session = session
        self.repository = repository
        self.lesson_repository = lesson_repository
        self.logger = logging.getLogger(__name__)

    async def list_subjects(self) -> Sequence[Subject]:
        self.logger.info("Listing subjects")
        return await self.repository.list()

    async def create_subject(self, payload: SubjectCreate) -> Subject:
        self.logger.info("Creating subject name=%s", payload.name)
        try:
            subject = await self.repository.create(payload.model_dump())
            await self.session.commit()
            return subject
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.warning("Subject create conflict name=%s", payload.name)
            raise ConflictError("Subject with this name already exists.") from exc

    async def update_subject(self, subject_id: int, payload: SubjectUpdate) -> Subject:
        self.logger.info("Updating subject id=%s", subject_id)
        subject = await self.repository.get(subject_id)
        if not subject:
            raise NotFoundError("Subject not found.")

        try:
            updated = await self.repository.update(
                subject,
                payload.model_dump(exclude_unset=True),
            )
            await self.session.commit()
            return updated
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.warning("Subject update conflict id=%s", subject_id)
            raise ConflictError("Subject with this name already exists.") from exc

    async def delete_subject(self, subject_id: int) -> None:
        self.logger.info("Deleting subject id=%s", subject_id)
        subject = await self.repository.get(subject_id)
        if not subject:
            raise NotFoundError("Subject not found.")

        lessons_count = await self.lesson_repository.count_by_subject(subject_id)
        if lessons_count:
            self.logger.warning(
                "Subject delete blocked id=%s related_lessons=%s",
                subject_id,
                lessons_count,
            )
            raise ConflictError("Cannot delete subject with existing lessons.")

        try:
            await self.repository.delete(subject)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            self.logger.warning("Subject deletion failed id=%s", subject_id)
            raise ConflictError("Subject deletion failed due to related records.") from exc
