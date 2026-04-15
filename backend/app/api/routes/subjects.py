from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_subject_service
from app.schemas.common import MessageResponse
from app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate
from app.services.subject import SubjectService

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectRead])
async def list_subjects(
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> list[SubjectRead]:
    subjects = await service.list_subjects()
    return [SubjectRead.model_validate(subject) for subject in subjects]


@router.post("", response_model=SubjectRead, status_code=status.HTTP_201_CREATED)
async def create_subject(
    payload: SubjectCreate,
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> SubjectRead:
    subject = await service.create_subject(payload)
    return SubjectRead.model_validate(subject)


@router.put("/{subject_id}", response_model=SubjectRead)
async def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> SubjectRead:
    subject = await service.update_subject(subject_id, payload)
    return SubjectRead.model_validate(subject)


@router.delete("/{subject_id}", response_model=MessageResponse)
async def delete_subject(
    subject_id: int,
    service: Annotated[SubjectService, Depends(get_subject_service)],
) -> MessageResponse:
    await service.delete_subject(subject_id)
    return MessageResponse(detail="Subject deleted successfully.")
