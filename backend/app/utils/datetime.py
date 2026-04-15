from datetime import datetime, time

from app.models.enums import LessonStatus


def calculate_duration_hours(start_time: time, end_time: time) -> float:
    start_dt = datetime.combine(datetime.min.date(), start_time)
    end_dt = datetime.combine(datetime.min.date(), end_time)
    seconds = (end_dt - start_dt).total_seconds()
    return round(seconds / 3600, 2)


def calculate_total(duration_hours: float, rate: float, status: LessonStatus) -> float:
    if status == LessonStatus.CANCELLED:
        return 0.0
    return round(duration_hours * rate, 2)


def calculate_debt(total: float, prepayment_amount: float) -> float:
    return round(total - prepayment_amount, 2)
