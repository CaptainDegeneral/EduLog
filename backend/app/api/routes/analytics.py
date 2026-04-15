from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_analytics_service
from app.schemas.analytics import AnalyticsByStudentItem, AnalyticsSummary
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> AnalyticsSummary:
    return await service.get_summary()


@router.get("/by-student", response_model=list[AnalyticsByStudentItem])
async def get_by_student(
    service: Annotated[AnalyticsService, Depends(get_analytics_service)],
) -> list[AnalyticsByStudentItem]:
    return await service.get_by_student()
