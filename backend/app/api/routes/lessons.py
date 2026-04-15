from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.dependencies import get_lesson_service
from app.models.enums import LessonStatus
from app.schemas.common import MessageResponse
from app.schemas.lesson import LessonCreate, LessonFilters, LessonRead, LessonUpdate
from app.services.lesson import LessonService

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("", response_model=list[LessonRead])
async def list_lessons(
    service: Annotated[LessonService, Depends(get_lesson_service)],
    lesson_date: date | None = Query(default=None, alias="date"),
    student_id: int | None = Query(default=None),
    status_filter: LessonStatus | None = Query(default=None, alias="status"),
) -> list[LessonRead]:
    filters = LessonFilters(
        date=lesson_date,
        student_id=student_id,
        status=status_filter,
    )
    return await service.list_lessons(filters)


@router.post("", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    payload: LessonCreate,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> LessonRead:
    return await service.create_lesson(payload)


@router.put("/{lesson_id}", response_model=LessonRead)
async def update_lesson(
    lesson_id: int,
    payload: LessonUpdate,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> LessonRead:
    return await service.update_lesson(lesson_id, payload)


@router.delete("/{lesson_id}", response_model=MessageResponse)
async def delete_lesson(
    lesson_id: int,
    service: Annotated[LessonService, Depends(get_lesson_service)],
) -> MessageResponse:
    await service.delete_lesson(lesson_id)
    return MessageResponse(detail="Lesson deleted successfully.")
