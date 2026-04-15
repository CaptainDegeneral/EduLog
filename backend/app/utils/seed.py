from datetime import date, time, timedelta

from sqlalchemy import select

from app.core.database import AsyncSessionFactory
from app.models.enums import LessonStatus
from app.models.lesson import Lesson
from app.models.student import Student
from app.models.subject import Subject


async def seed_database() -> None:
    async with AsyncSessionFactory() as session:
        student_exists = await session.scalar(select(Student.id).limit(1))
        if student_exists:
            return

        students = [
            Student(name="Анна Смирнова", default_rate=1800),
            Student(name="Илья Кузнецов", default_rate=2200),
            Student(name="Мария Орлова", default_rate=2000),
        ]
        subjects = [
            Subject(name="Математика"),
            Subject(name="Физика"),
            Subject(name="Английский"),
        ]

        session.add_all(students)
        session.add_all(subjects)
        await session.flush()

        today = date.today()
        lessons = [
            Lesson(
                date=today - timedelta(days=2),
                start_time=time(16, 0),
                end_time=time(17, 30),
                student_id=students[0].id,
                subject_id=subjects[0].id,
                rate=students[0].default_rate,
                prepayment_amount=1000,
                status=LessonStatus.COMPLETED,
                notes="Подготовка к контрольной.",
            ),
            Lesson(
                date=today - timedelta(days=1),
                start_time=time(18, 0),
                end_time=time(19, 0),
                student_id=students[1].id,
                subject_id=subjects[1].id,
                rate=students[1].default_rate,
                prepayment_amount=0,
                status=LessonStatus.PLANNED,
                notes="Разбор задач по механике.",
            ),
            Lesson(
                date=today,
                start_time=time(15, 0),
                end_time=time(16, 0),
                student_id=students[2].id,
                subject_id=subjects[2].id,
                rate=students[2].default_rate,
                prepayment_amount=500,
                status=LessonStatus.CANCELLED,
                notes="Отмена по болезни.",
            ),
        ]

        session.add_all(lessons)
        await session.commit()
