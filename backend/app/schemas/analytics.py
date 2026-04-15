from app.schemas.common import BaseSchema


class AnalyticsSummary(BaseSchema):
    total_income: float
    total_hours: float
    total_debt: float
    cancelled_count: int


class AnalyticsByStudentItem(BaseSchema):
    student_id: int
    student_name: str
    lessons_count: int
    cancelled_count: int
    total_hours: float
    total_income: float
    total_debt: float
