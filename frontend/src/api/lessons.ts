import http from '@/api/http'
import type { Lesson, LessonFilters, LessonPayload, MessageResponse } from '@/types/models'

export const lessonsApi = {
  async list(filters: LessonFilters = {}) {
    const { data } = await http.get<Lesson[]>('/lessons', {
      params: filters,
    })
    return data
  },
  async create(payload: LessonPayload) {
    const { data } = await http.post<Lesson>('/lessons', payload)
    return data
  },
  async update(id: number, payload: Partial<LessonPayload>) {
    const { data } = await http.put<Lesson>(`/lessons/${id}`, payload)
    return data
  },
  async remove(id: number) {
    const { data } = await http.delete<MessageResponse>(`/lessons/${id}`)
    return data
  },
}
