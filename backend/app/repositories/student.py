from collections.abc import Sequence

from sqlalchemy import select

from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    model = Student

    async def list(self, statement=None) -> Sequence[Student]:
        query = statement if statement is not None else select(Student).order_by(Student.name.asc())
        return await super().list(query)
