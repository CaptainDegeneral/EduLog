import http from '@/api/http'
import type { MessageResponse, Subject } from '@/types/models'

export const subjectsApi = {
  async list() {
    const { data } = await http.get<Subject[]>('/subjects')
    return data
  },
  async create(payload: Omit<Subject, 'id'>) {
    const { data } = await http.post<Subject>('/subjects', payload)
    return data
  },
  async update(id: number, payload: Partial<Omit<Subject, 'id'>>) {
    const { data } = await http.put<Subject>(`/subjects/${id}`, payload)
    return data
  },
  async remove(id: number) {
    const { data } = await http.delete<MessageResponse>(`/subjects/${id}`)
    return data
  },
}
