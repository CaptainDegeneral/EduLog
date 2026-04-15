from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_student_service
from app.schemas.common import MessageResponse
from app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from app.services.student import StudentService

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentRead])
async def list_students(
    service: Annotated[StudentService, Depends(get_student_service)],
) -> list[StudentRead]:
    students = await service.list_students()
    return [StudentRead.model_validate(student) for student in students]


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreate,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> StudentRead:
    student = await service.create_student(payload)
    return StudentRead.model_validate(student)


@router.put("/{student_id}", response_model=StudentRead)
async def update_student(
    student_id: int,
    payload: StudentUpdate,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> StudentRead:
    student = await service.update_student(student_id, payload)
    return StudentRead.model_validate(student)


@router.delete("/{student_id}", response_model=MessageResponse)
async def delete_student(
    student_id: int,
    service: Annotated[StudentService, Depends(get_student_service)],
) -> MessageResponse:
    await service.delete_student(student_id)
    return MessageResponse(detail="Student deleted successfully.")
