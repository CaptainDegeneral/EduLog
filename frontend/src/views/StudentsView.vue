<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { studentsApi } from '@/api/students'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import DataTable from '@/components/DataTable.vue'
import { useNotifications } from '@/store/notifications'
import { useReferenceStore } from '@/store/referenceStore'
import type { Student } from '@/types/models'
import type { TableColumn } from '@/types/ui'
import { formatCurrency } from '@/utils/formatters'
import { appLogger } from '@/utils/logger'

const { pushSuccess } = useNotifications()
const references = useReferenceStore()

const students = ref<Student[]>([])
const loading = ref(false)
const creating = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const studentToDelete = ref<Student | null>(null)

const newStudent = reactive({
  name: '',
  default_rate: 0,
})

const draft = reactive({
  name: '',
  default_rate: 0,
})

const columns: TableColumn<Student>[] = [
  { key: 'name', label: 'Имя' },
  { key: 'default_rate', label: 'Ставка по умолчанию' },
  { key: 'actions', label: 'Действия', class: 'w-44' },
]

onMounted(loadStudents)

async function loadStudents() {
  loading.value = true
  appLogger.info('students', 'load students')

  try {
    students.value = await studentsApi.list()
    await references.refresh()
  } finally {
    loading.value = false
  }
}

async function createStudent() {
  creating.value = true
  appLogger.info('students', 'create student', { ...newStudent })

  try {
    await studentsApi.create({
      name: newStudent.name,
      default_rate: newStudent.default_rate,
    })
    newStudent.name = ''
    newStudent.default_rate = 0
    await loadStudents()
    pushSuccess('Ученик добавлен.')
  } finally {
    creating.value = false
  }
}

function startEdit(student: Student) {
  appLogger.info('students', 'start edit', { studentId: student.id })
  editingId.value = student.id
  draft.name = student.name
  draft.default_rate = student.default_rate
}

async function saveEdit(id: number) {
  appLogger.info('students', 'save edit', { studentId: id, draft: { ...draft } })
  await studentsApi.update(id, {
    name: draft.name,
    default_rate: draft.default_rate,
  })
  editingId.value = null
  await loadStudents()
  pushSuccess('Карточка ученика обновлена.')
}

function requestDelete(student: Student) {
  appLogger.warn('students', 'request delete', { studentId: student.id })
  studentToDelete.value = student
}

async function confirmDelete() {
  if (!studentToDelete.value) {
    return
  }

  deleting.value = true
  appLogger.info('students', 'delete student', { studentId: studentToDelete.value.id })

  try {
    await studentsApi.remove(studentToDelete.value.id)
    studentToDelete.value = null
    await loadStudents()
    pushSuccess('Ученик удалён.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <section class="space-y-5">
    <div class="surface p-5 sm:p-6">
      <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Ученики</p>
      <h2 class="mt-2 font-display text-3xl text-ink">Справочник учеников</h2>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-muted">
        Ставка по умолчанию подставляется в форму занятия автоматически.
      </p>

      <div class="mt-6 grid gap-4 md:grid-cols-[1.5fr_1fr_auto]">
        <label class="block">
          <span class="field-label">Имя</span>
          <input v-model="newStudent.name" class="field" />
        </label>

        <label class="block">
          <span class="field-label">Ставка по умолчанию</span>
          <input
            v-model.number="newStudent.default_rate"
            type="number"
            min="0"
            step="100"
            class="field"
          />
        </label>

        <div class="flex items-end">
          <button
            class="btn-primary w-full"
            :disabled="creating || !newStudent.name.trim()"
            @click="createStudent"
          >
            {{ creating ? 'Сохраняем...' : 'Добавить ученика' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading && !students.length" class="surface p-8 text-center text-sm text-muted">
      Загружаем учеников...
    </div>

    <div v-else-if="!students.length" class="surface p-8 text-center">
      <h3 class="font-display text-2xl text-ink">Пока пусто</h3>
      <p class="mt-2 text-sm text-muted">Добавьте первого ученика, чтобы создавать занятия быстрее.</p>
    </div>

    <template v-else>
      <div class="grid gap-4 md:hidden">
        <article v-for="student in students" :key="student.id" class="surface p-5">
          <div class="flex items-start justify-between gap-3">
            <div>
              <h3 class="text-lg font-semibold text-ink">{{ student.name }}</h3>
              <p class="mt-1 text-sm text-muted">{{ formatCurrency(student.default_rate) }}</p>
            </div>
          </div>

          <div class="mt-4 grid gap-3">
            <button class="btn-secondary w-full" @click="startEdit(student)">
              {{ editingId === student.id ? 'Редактируется' : 'Редактировать' }}
            </button>
            <button class="btn-danger w-full" @click="requestDelete(student)">Удалить</button>
          </div>

          <div v-if="editingId === student.id" class="mt-4 grid gap-3">
            <input v-model="draft.name" class="field" />
            <input v-model.number="draft.default_rate" type="number" min="0" step="100" class="field" />
            <div class="grid gap-3 sm:grid-cols-2">
              <button class="btn-primary w-full" @click="saveEdit(student.id)">Сохранить</button>
              <button class="btn-secondary w-full" @click="editingId = null">Отмена</button>
            </div>
          </div>
        </article>
      </div>

      <div class="hidden md:block surface p-4 sm:p-6">
        <DataTable :columns="columns" :rows="students" row-key="id">
          <template #cell-name="{ row }">
            <input v-if="editingId === row.id" v-model="draft.name" class="field min-w-48" />
            <span v-else>{{ row.name }}</span>
          </template>

          <template #cell-default_rate="{ row }">
            <input
              v-if="editingId === row.id"
              v-model.number="draft.default_rate"
              type="number"
              min="0"
              step="100"
              class="field min-w-36"
            />
            <span v-else>{{ formatCurrency(row.default_rate) }}</span>
          </template>

          <template #cell-actions="{ row }">
            <div class="flex flex-wrap gap-2">
              <template v-if="editingId === row.id">
                <button class="btn-primary" @click="saveEdit(row.id)">Сохранить</button>
                <button class="btn-secondary" @click="editingId = null">Отмена</button>
              </template>
              <template v-else>
                <button class="btn-secondary" @click="startEdit(row)">Редактировать</button>
                <button class="btn-danger" @click="requestDelete(row)">Удалить</button>
              </template>
            </div>
          </template>
        </DataTable>
      </div>
    </template>

    <ConfirmDialog
      :open="Boolean(studentToDelete)"
      :loading="deleting"
      title="Удалить ученика?"
      :description="studentToDelete ? `Карточка ${studentToDelete.name} будет удалена.` : ''"
      @close="studentToDelete = null"
      @confirm="confirmDelete"
    />
  </section>
</template>
