from pydantic import Field

from app.schemas.common import BaseSchema


class SubjectBase(BaseSchema):
    name: str = Field(min_length=1, max_length=255)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class SubjectReference(BaseSchema):
    id: int
    name: str


class SubjectRead(SubjectBase):
    id: int
