from datetime import date as DateType
from datetime import time as TimeType

from pydantic import Field

from app.models.enums import LessonStatus
from app.schemas.common import BaseSchema
from app.schemas.student import StudentReference
from app.schemas.subject import SubjectReference


class LessonBase(BaseSchema):
    date: DateType
    start_time: TimeType
    end_time: TimeType
    student_id: int = Field(gt=0)
    subject_id: int = Field(gt=0)
    prepayment_amount: float = Field(default=0, ge=0)
    status: LessonStatus = LessonStatus.PLANNED
    notes: str | None = None


class LessonCreate(LessonBase):
    rate: float | None = Field(default=None, ge=0)


class LessonUpdate(BaseSchema):
    date: DateType | None = None
    start_time: TimeType | None = None
    end_time: TimeType | None = None
    student_id: int | None = Field(default=None, gt=0)
    subject_id: int | None = Field(default=None, gt=0)
    rate: float | None = Field(default=None, ge=0)
    prepayment_amount: float | None = Field(default=None, ge=0)
    status: LessonStatus | None = None
    notes: str | None = None


class LessonRead(BaseSchema):
    id: int
    date: DateType
    start_time: TimeType
    end_time: TimeType
    student_id: int
    subject_id: int
    rate: float
    prepayment_amount: float
    status: LessonStatus
    notes: str | None
    student: StudentReference
    subject: SubjectReference
    duration_hours: float
    total: float
    debt: float


class LessonFilters(BaseSchema):
    date: DateType | None = None
    student_id: int | None = None
    status: LessonStatus | None = None
