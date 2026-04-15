import http from '@/api/http'
import type { AnalyticsByStudentItem, AnalyticsSummary } from '@/types/models'

export const analyticsApi = {
  async summary() {
    const { data } = await http.get<AnalyticsSummary>('/analytics/summary')
    return data
  },
  async byStudent() {
    const { data } = await http.get<AnalyticsByStudentItem[]>('/analytics/by-student')
    return data
  },
}
