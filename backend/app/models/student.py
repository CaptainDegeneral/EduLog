from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_rate: Mapped[float] = mapped_column(Float, nullable=False)

    lessons = relationship(
        "Lesson",
        back_populates="student",
        passive_deletes=True,
    )
