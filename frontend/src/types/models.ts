export type LessonStatus = 'planned' | 'completed' | 'cancelled'

export interface Student {
  id: number
  name: string
  default_rate: number
}

export interface Subject {
  id: number
  name: string
}

export interface StudentReference {
  id: number
  name: string
}

export interface SubjectReference {
  id: number
  name: string
}

export interface Lesson {
  id: number
  date: string
  start_time: string
  end_time: string
  student_id: number
  subject_id: number
  rate: number
  prepayment_amount: number
  status: LessonStatus
  notes: string | null
  student: StudentReference
  subject: SubjectReference
  duration_hours: number
  total: number
  debt: number
}

export interface LessonPayload {
  date: string
  start_time: string
  end_time: string
  student_id: number
  subject_id: number
  rate: number | null
  prepayment_amount: number
  status: LessonStatus
  notes: string | null
}

export interface LessonFilters {
  date?: string
  student_id?: number
  status?: LessonStatus
}

export interface AnalyticsSummary {
  total_income: number
  total_hours: number
  total_debt: number
  cancelled_count: number
}

export interface AnalyticsByStudentItem {
  student_id: number
  student_name: string
  lessons_count: number
  cancelled_count: number
  total_hours: number
  total_income: number
  total_debt: number
}

export interface MessageResponse {
  detail: string
}
