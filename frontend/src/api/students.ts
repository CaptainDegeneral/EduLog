import http from '@/api/http'
import type { MessageResponse, Student } from '@/types/models'

export const studentsApi = {
  async list() {
    const { data } = await http.get<Student[]>('/students')
    return data
  },
  async create(payload: Omit<Student, 'id'>) {
    const { data } = await http.post<Student>('/students', payload)
    return data
  },
  async update(id: number, payload: Partial<Omit<Student, 'id'>>) {
    const { data } = await http.put<Student>(`/students/${id}`, payload)
    return data
  },
  async remove(id: number) {
    const { data } = await http.delete<MessageResponse>(`/students/${id}`)
    return data
  },
}
