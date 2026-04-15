from pydantic import Field

from app.schemas.common import BaseSchema


class StudentBase(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    default_rate: float = Field(ge=0)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    default_rate: float | None = Field(default=None, ge=0)


class StudentReference(BaseSchema):
    id: int
    name: str


class StudentRead(StudentBase):
    id: int
