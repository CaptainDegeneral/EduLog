from collections import defaultdict
import logging

from app.models.enums import LessonStatus
from app.repositories.lesson import LessonRepository
from app.schemas.analytics import AnalyticsByStudentItem, AnalyticsSummary
from app.utils.datetime import calculate_debt, calculate_duration_hours, calculate_total


class AnalyticsService:
    def __init__(self, repository: LessonRepository):
        self.repository = repository
        self.logger = logging.getLogger(__name__)

    async def get_summary(self) -> AnalyticsSummary:
        self.logger.info("Building analytics summary")
        lessons = await self.repository.list()

        total_income = 0.0
        total_hours = 0.0
        total_debt = 0.0
        cancelled_count = 0

        for lesson in lessons:
            duration_hours = calculate_duration_hours(lesson.start_time, lesson.end_time)
            total = calculate_total(duration_hours, lesson.rate, lesson.status)
            debt = calculate_debt(total, lesson.prepayment_amount)
            self.logger.debug(
                "Analytics summary lesson_id=%s duration=%s total=%s debt=%s status=%s",
                lesson.id,
                duration_hours,
                total,
                debt,
                lesson.status,
            )

            if lesson.status == LessonStatus.CANCELLED:
                cancelled_count += 1
                continue

            total_income += total
            total_hours += duration_hours
            total_debt += debt

        return AnalyticsSummary(
            total_income=round(total_income, 2),
            total_hours=round(total_hours, 2),
            total_debt=round(total_debt, 2),
            cancelled_count=cancelled_count,
        )

    async def get_by_student(self) -> list[AnalyticsByStudentItem]:
        self.logger.info("Building analytics by student")
        lessons = await self.repository.list()
        buckets: dict[int, dict[str, float | int | str]] = defaultdict(
            lambda: {
                "student_name": "",
                "lessons_count": 0,
                "cancelled_count": 0,
                "total_hours": 0.0,
                "total_income": 0.0,
                "total_debt": 0.0,
            }
        )

        for lesson in lessons:
            bucket = buckets[lesson.student_id]
            bucket["student_name"] = lesson.student.name
            bucket["lessons_count"] += 1

            duration_hours = calculate_duration_hours(lesson.start_time, lesson.end_time)
            total = calculate_total(duration_hours, lesson.rate, lesson.status)
            debt = calculate_debt(total, lesson.prepayment_amount)
            self.logger.debug(
                "Analytics by student lesson_id=%s student_id=%s duration=%s total=%s debt=%s",
                lesson.id,
                lesson.student_id,
                duration_hours,
                total,
                debt,
            )

            if lesson.status == LessonStatus.CANCELLED:
                bucket["cancelled_count"] += 1
                continue

            bucket["total_hours"] += duration_hours
            bucket["total_income"] += total
            bucket["total_debt"] += debt

        items = [
            AnalyticsByStudentItem(
                student_id=student_id,
                student_name=str(data["student_name"]),
                lessons_count=int(data["lessons_count"]),
                cancelled_count=int(data["cancelled_count"]),
                total_hours=round(float(data["total_hours"]), 2),
                total_income=round(float(data["total_income"]), 2),
                total_debt=round(float(data["total_debt"]), 2),
            )
            for student_id, data in buckets.items()
        ]
        return sorted(items, key=lambda item: item.student_name.lower())
