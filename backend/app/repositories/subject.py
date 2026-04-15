from collections.abc import Sequence

from sqlalchemy import select

from app.models.subject import Subject
from app.repositories.base import BaseRepository


class SubjectRepository(BaseRepository[Subject]):
    model = Subject

    async def list(self, statement=None) -> Sequence[Subject]:
        query = statement if statement is not None else select(Subject).order_by(Subject.name.asc())
        return await super().list(query)
