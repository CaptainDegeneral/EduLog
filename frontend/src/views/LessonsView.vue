<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { lessonsApi } from '@/api/lessons'
import Badge from '@/components/Badge.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import DataTable from '@/components/DataTable.vue'
import LessonForm from '@/components/LessonForm.vue'
import Modal from '@/components/Modal.vue'
import SelectInput from '@/components/SelectInput.vue'
import TimeInput from '@/components/TimeInput.vue'
import { useNotifications } from '@/store/notifications'
import { useReferenceStore } from '@/store/referenceStore'
import type { Lesson, LessonPayload, LessonStatus } from '@/types/models'
import type { TableColumn } from '@/types/ui'
import { formatCurrency, formatDate, formatTime } from '@/utils/formatters'
import { appLogger } from '@/utils/logger'

interface LessonRowDraft {
  date: string
  start_time: string
  end_time: string
  student_id: number
  subject_id: number
  rate: number
  prepayment_amount: number
  status: LessonStatus
  notes: string
}

const { pushSuccess } = useNotifications()
const references = useReferenceStore()

const lessons = ref<Lesson[]>([])
const loading = ref(false)
const formSubmitting = ref(false)
const savingRow = ref(false)
const deleting = ref(false)
const formModalOpen = ref(false)
const activeLesson = ref<Lesson | null>(null)
const lessonToDelete = ref<Lesson | null>(null)
const editingId = ref<number | null>(null)
const filtersReady = ref(false)

const filters = reactive<{
  date: string
  student_id: number | null
  status: LessonStatus | null
}>({
  date: '',
  student_id: null,
  status: null,
})

const draft = reactive<LessonRowDraft>({
  date: '',
  start_time: '',
  end_time: '',
  student_id: 0,
  subject_id: 0,
  rate: 0,
  prepayment_amount: 0,
  status: 'planned',
  notes: '',
})

const columns: TableColumn<Lesson>[] = [
  { key: 'date', label: 'Дата' },
  { key: 'student', label: 'Ученик' },
  { key: 'subject', label: 'Предмет' },
  { key: 'time', label: 'Время' },
  { key: 'rate', label: 'Ставка' },
  { key: 'total', label: 'Сумма' },
  { key: 'debt', label: 'Долг' },
  { key: 'status', label: 'Статус' },
  { key: 'actions', label: 'Действия', class: 'w-52' },
]

const studentOptions = computed(() =>
  references.state.students.map((student) => ({
    label: student.name,
    value: student.id,
  })),
)

const subjectOptions = computed(() =>
  references.state.subjects.map((subject) => ({
    label: subject.name,
    value: subject.id,
  })),
)

const statusOptions = [
  { label: 'Все статусы', value: null },
  { label: 'Запланировано', value: 'planned' },
  { label: 'Проведено', value: 'completed' },
  { label: 'Отменено', value: 'cancelled' },
] as const

const rowStatusOptions = [
  { label: 'Запланировано', value: 'planned' },
  { label: 'Проведено', value: 'completed' },
  { label: 'Отменено', value: 'cancelled' },
] as const

const formTitle = computed(() =>
  activeLesson.value ? 'Редактирование занятия' : 'Новое занятие',
)

let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(
  () => [filters.date, filters.student_id, filters.status],
  () => {
    if (!filtersReady.value) {
      return
    }

    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    debounceTimer = setTimeout(() => {
      void loadLessons()
    }, 350)
  },
)

onMounted(async () => {
  await Promise.all([references.refresh(), loadLessons()])
  filtersReady.value = true
})

onBeforeUnmount(() => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
})

async function loadLessons() {
  loading.value = true
  appLogger.info('lessons', 'loading lessons', { ...filters })

  try {
    lessons.value = await lessonsApi.list({
      date: filters.date || undefined,
      student_id: filters.student_id ?? undefined,
      status: filters.status ?? undefined,
    })
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  appLogger.info('lessons', 'open create form')
  activeLesson.value = null
  formModalOpen.value = true
}

function openEditModal(lesson: Lesson) {
  appLogger.info('lessons', 'open edit form', { lessonId: lesson.id })
  activeLesson.value = lesson
  formModalOpen.value = true
}

async function submitLessonForm(payload: LessonPayload) {
  formSubmitting.value = true
  const mode = activeLesson.value ? 'update' : 'create'
  appLogger.info('lessons', `${mode} lesson`, payload)

  try {
    if (activeLesson.value) {
      await lessonsApi.update(activeLesson.value.id, payload)
      pushSuccess('Изменения сохранены.')
    } else {
      await lessonsApi.create(payload)
      pushSuccess('Занятие создано.')
    }

    formModalOpen.value = false
    activeLesson.value = null
    await loadLessons()
  } finally {
    formSubmitting.value = false
  }
}

function startInlineEdit(lesson: Lesson) {
  appLogger.info('lessons', 'start inline edit', { lessonId: lesson.id })
  editingId.value = lesson.id
  Object.assign(draft, {
    date: lesson.date,
    start_time: lesson.start_time.slice(0, 5),
    end_time: lesson.end_time.slice(0, 5),
    student_id: lesson.student_id,
    subject_id: lesson.subject_id,
    rate: lesson.rate,
    prepayment_amount: lesson.prepayment_amount,
    status: lesson.status,
    notes: lesson.notes ?? '',
  })
}

function cancelInlineEdit() {
  editingId.value = null
}

async function saveInlineEdit(lessonId: number) {
  savingRow.value = true
  appLogger.info('lessons', 'save inline edit', { lessonId, draft: { ...draft } })

  try {
    await lessonsApi.update(lessonId, {
      date: draft.date,
      start_time: draft.start_time,
      end_time: draft.end_time,
      student_id: draft.student_id,
      subject_id: draft.subject_id,
      rate: draft.rate,
      prepayment_amount: draft.prepayment_amount,
      status: draft.status,
      notes: draft.notes.trim() || null,
    })

    editingId.value = null
    await loadLessons()
    pushSuccess('Изменения сохранены.')
  } finally {
    savingRow.value = false
  }
}

function requestDelete(lesson: Lesson) {
  appLogger.warn('lessons', 'request delete', { lessonId: lesson.id })
  lessonToDelete.value = lesson
}

async function confirmDelete() {
  if (!lessonToDelete.value) {
    return
  }

  deleting.value = true
  appLogger.info('lessons', 'delete lesson', { lessonId: lessonToDelete.value.id })

  try {
    await lessonsApi.remove(lessonToDelete.value.id)
    lessonToDelete.value = null
    await loadLessons()
    pushSuccess('Занятие удалено.')
  } finally {
    deleting.value = false
  }
}

function isEditing(lessonId: number) {
  return editingId.value === lessonId
}
</script>

<template>
  <section class="space-y-5">
    <div class="surface p-5 sm:p-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Занятия</p>
          <h2 class="mt-2 font-display text-3xl text-ink">Журнал занятий</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-muted">
            Управляйте расписанием, оплатами и долгами в одном журнале.
          </p>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row">
          <button class="btn-secondary w-full sm:w-auto" :disabled="loading" @click="loadLessons">
            {{ loading ? 'Обновление...' : 'Обновить' }}
          </button>
          <button class="btn-primary w-full sm:w-auto" @click="openCreateModal">
            Новое занятие
          </button>
        </div>
      </div>

      <div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <label class="block">
          <span class="field-label">Дата</span>
          <input v-model="filters.date" type="date" class="field" />
        </label>

        <SelectInput
          v-model="filters.student_id"
          label="Ученик"
          :options="studentOptions"
          empty-label="Все ученики"
        />

        <SelectInput
          v-model="filters.status"
          label="Статус"
          :options="[...statusOptions]"
          empty-label="Все статусы"
        />

        <div class="flex items-end">
          <button class="btn-secondary w-full" :disabled="loading" @click="loadLessons">
            Применить сейчас
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading && !lessons.length" class="surface p-8 text-center text-sm text-muted">
      Загружаем занятия...
    </div>

    <div v-else-if="!lessons.length" class="surface p-8 text-center">
      <h3 class="font-display text-2xl text-ink">Нет занятий</h3>
      <p class="mt-2 text-sm text-muted">Добавьте первое занятие или измените фильтры.</p>
    </div>

    <div v-else class="space-y-4">
      <div class="grid gap-4 lg:hidden">
        <article
          v-for="lesson in lessons"
          :key="lesson.id"
          class="surface border p-5"
          :class="lesson.debt > 0 ? 'border-amber-200 bg-amber-50/70' : 'border-sand/35 bg-panel/95'"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <h3 class="text-lg font-semibold text-ink">{{ lesson.student.name }}</h3>
              <p class="mt-1 text-sm text-muted">{{ lesson.subject.name }}</p>
            </div>
            <Badge :status="lesson.status" />
          </div>

          <div class="mt-4 grid gap-3 text-sm text-ink">
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Дата</span>
              <span>{{ formatDate(lesson.date) }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Время</span>
              <span>{{ formatTime(lesson.start_time) }} - {{ formatTime(lesson.end_time) }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Длительность</span>
              <span>{{ lesson.duration_hours }} ч</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Сумма</span>
              <span class="font-semibold">{{ formatCurrency(lesson.total) }}</span>
            </div>
          </div>

          <div class="mt-4 flex flex-wrap items-center justify-between gap-3">
            <Badge :debt="lesson.debt" />
            <span class="text-sm font-semibold text-amber-700" v-if="lesson.debt > 0">
              {{ formatCurrency(lesson.debt) }}
            </span>
            <span class="text-sm text-muted" v-else>Долга нет</span>
          </div>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <button class="btn-secondary w-full" @click="openEditModal(lesson)">Редактировать</button>
            <button class="btn-danger w-full" @click="requestDelete(lesson)">Удалить</button>
          </div>
        </article>
      </div>

      <div class="hidden lg:block">
        <DataTable :columns="columns" :rows="lessons" row-key="id">
          <template #cell-date="{ row }">
            <div v-if="isEditing(row.id)">
              <input v-model="draft.date" type="date" class="field min-w-36" />
            </div>
            <span v-else>{{ formatDate(row.date) }}</span>
          </template>

          <template #cell-student="{ row }">
            <div v-if="isEditing(row.id)">
              <SelectInput v-model="draft.student_id" :options="studentOptions" />
            </div>
            <span v-else>{{ row.student.name }}</span>
          </template>

          <template #cell-subject="{ row }">
            <div v-if="isEditing(row.id)">
              <SelectInput v-model="draft.subject_id" :options="subjectOptions" />
            </div>
            <span v-else>{{ row.subject.name }}</span>
          </template>

          <template #cell-time="{ row }">
            <div v-if="isEditing(row.id)" class="grid gap-2">
              <TimeInput v-model="draft.start_time" />
              <TimeInput v-model="draft.end_time" />
            </div>
            <div v-else class="space-y-1">
              <p>{{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}</p>
              <p class="text-xs text-muted">{{ row.duration_hours }} ч</p>
            </div>
          </template>

          <template #cell-rate="{ row }">
            <div v-if="isEditing(row.id)" class="space-y-2">
              <input v-model.number="draft.rate" type="number" min="0" step="100" class="field min-w-28" />
              <textarea
                v-model="draft.notes"
                class="field min-h-24 resize-none py-3"
              />
            </div>
            <div v-else class="space-y-1">
              <p>{{ formatCurrency(row.rate) }}</p>
              <p class="text-xs text-muted">{{ row.notes || 'Без заметок' }}</p>
            </div>
          </template>

          <template #cell-total="{ row }">
            <div class="space-y-1">
              <p>{{ formatCurrency(row.total) }}</p>
              <p class="text-xs text-muted">Предоплата: {{ formatCurrency(row.prepayment_amount) }}</p>
            </div>
          </template>

          <template #cell-debt="{ row }">
            <div v-if="isEditing(row.id)" class="space-y-2">
              <input
                v-model.number="draft.prepayment_amount"
                type="number"
                min="0"
                step="100"
                class="field min-w-28"
              />
              <Badge :debt="row.debt" />
            </div>
            <div v-else class="space-y-2">
              <p>{{ formatCurrency(row.debt) }}</p>
              <Badge :debt="row.debt" />
            </div>
          </template>

          <template #cell-status="{ row }">
            <div v-if="isEditing(row.id)" class="space-y-2">
              <SelectInput v-model="draft.status" :options="[...rowStatusOptions]" />
            </div>
            <Badge v-else :status="row.status" />
          </template>

          <template #cell-actions="{ row }">
            <div class="flex flex-wrap gap-2">
              <template v-if="isEditing(row.id)">
                <button class="btn-primary" :disabled="savingRow" @click="saveInlineEdit(row.id)">
                  Сохранить
                </button>
                <button class="btn-secondary" :disabled="savingRow" @click="cancelInlineEdit">
                  Отмена
                </button>
              </template>
              <template v-else>
                <button class="btn-secondary" @click="startInlineEdit(row)">Редактировать</button>
                <button class="btn-danger" @click="requestDelete(row)">Удалить</button>
              </template>
            </div>
          </template>
        </DataTable>
      </div>
    </div>

    <Modal :open="formModalOpen" :title="formTitle" subtitle="Форма занятия" @close="formModalOpen = false">
      <LessonForm
        :students="references.state.students"
        :subjects="references.state.subjects"
        :initial-value="activeLesson"
        :submitting="formSubmitting"
        :submit-label="activeLesson ? 'Сохранить изменения' : 'Создать занятие'"
        @cancel="formModalOpen = false"
        @save="submitLessonForm"
      />
    </Modal>

    <ConfirmDialog
      :open="Boolean(lessonToDelete)"
      :loading="deleting"
      title="Удалить занятие?"
      :description="lessonToDelete ? `Запись для ${lessonToDelete.student.name} будет удалена без возможности восстановления.` : ''"
      @close="lessonToDelete = null"
      @confirm="confirmDelete"
    />
  </section>
</template>
