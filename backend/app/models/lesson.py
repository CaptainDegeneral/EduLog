from datetime import date as DateType
from datetime import time as TimeType

from sqlalchemy import Date, Enum, Float, ForeignKey, Index, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import LessonStatus


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        Index("ix_lessons_date", "date"),
        Index("ix_lessons_student_id", "student_id"),
        Index("ix_lessons_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    start_time: Mapped[TimeType] = mapped_column(Time, nullable=False)
    end_time: Mapped[TimeType] = mapped_column(Time, nullable=False)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    prepayment_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    status: Mapped[LessonStatus] = mapped_column(
        Enum(LessonStatus, name="lesson_status"),
        nullable=False,
        default=LessonStatus.PLANNED,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    student = relationship("Student", back_populates="lessons")
    subject = relationship("Subject", back_populates="lessons")
