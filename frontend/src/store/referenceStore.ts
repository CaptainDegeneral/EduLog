import { reactive, readonly } from 'vue'

import { studentsApi } from '@/api/students'
import { subjectsApi } from '@/api/subjects'
import type { Student, Subject } from '@/types/models'

const state = reactive({
  students: [] as Student[],
  subjects: [] as Subject[],
  loading: false,
})

export function useReferenceStore() {
  async function refresh() {
    state.loading = true
    try {
      const [students, subjects] = await Promise.all([
        studentsApi.list(),
        subjectsApi.list(),
      ])
      state.students = students
      state.subjects = subjects
    } finally {
      state.loading = false
    }
  }

  return {
    state: readonly(state),
    refresh,
  }
}
