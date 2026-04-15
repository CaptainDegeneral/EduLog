from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.lessons import router as lessons_router
from app.api.routes.students import router as students_router
from app.api.routes.subjects import router as subjects_router

api_router = APIRouter()
api_router.include_router(students_router)
api_router.include_router(subjects_router)
api_router.include_router(lessons_router)
api_router.include_router(analytics_router)
