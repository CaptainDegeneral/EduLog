from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repositories.lesson import LessonRepository
from app.repositories.student import StudentRepository
from app.repositories.subject import SubjectRepository
from app.services.analytics import AnalyticsService
from app.services.lesson import LessonService
from app.services.student import StudentService
from app.services.subject import SubjectService

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_student_service(session: DbSession) -> StudentService:
    return StudentService(
        session=session,
        repository=StudentRepository(session),
        lesson_repository=LessonRepository(session),
    )


async def get_subject_service(session: DbSession) -> SubjectService:
    return SubjectService(
        session=session,
        repository=SubjectRepository(session),
        lesson_repository=LessonRepository(session),
    )


async def get_lesson_service(session: DbSession) -> LessonService:
    return LessonService(
        session=session,
        repository=LessonRepository(session),
        student_repository=StudentRepository(session),
        subject_repository=SubjectRepository(session),
    )


async def get_analytics_service(session: DbSession) -> AnalyticsService:
    return AnalyticsService(repository=LessonRepository(session))
