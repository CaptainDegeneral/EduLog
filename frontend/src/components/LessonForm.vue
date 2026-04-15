<script setup lang="ts">
import { computed, reactive, watch } from 'vue'

import SelectInput from '@/components/SelectInput.vue'
import TimeInput from '@/components/TimeInput.vue'
import type { Lesson, LessonPayload, LessonStatus, Student, Subject } from '@/types/models'

interface LessonFormState {
  date: string
  start_time: string
  end_time: string
  student_id: number | null
  subject_id: number | null
  rate: string
  prepayment_amount: number
  status: LessonStatus
  notes: string
}

const props = withDefaults(
    defineProps<{
      students: Student[]
      subjects: Subject[]
      initialValue?: Lesson | null
      submitLabel?: string
      submitting?: boolean
    }>(),
    {
      initialValue: null,
      submitLabel: 'Сохранить',
      submitting: false,
    },
)

const emit = defineEmits<{
  save: [payload: LessonPayload]
  cancel:[]
}>()

const form = reactive<LessonFormState>(createInitialState(props.initialValue))

// Реактивное состояние для продолжительности
const duration = reactive({
  hours: 0,
  minutes: 0,
})

const studentOptions = computed(() =>
    props.students.map((student) => ({
      label: `${student.name} · ${student.default_rate} ₽/ч`,
      value: student.id,
    })),
)

const subjectOptions = computed(() =>
    props.subjects.map((subject) => ({
      label: subject.name,
      value: subject.id,
    })),
)

const statusOptions =[
  { label: 'Запланировано', value: 'planned' },
  { label: 'Проведено', value: 'completed' },
  { label: 'Отменено', value: 'cancelled' },
] as const

const isInvalid = computed(
    () =>
        !form.date ||
        !form.start_time ||
        !form.end_time ||
        !form.student_id ||
        !form.subject_id ||
        form.prepayment_amount < 0 ||
        (duration.hours === 0 && duration.minutes === 0), // Защита от нулевой длительности
)

// --- Вспомогательные функции для расчетов времени ---

// Перевод "HH:MM" в общее количество минут
const timeToMinutes = (timeStr: string): number => {
  if (!timeStr) return 0
  const [h, m] = timeStr.split(':').map(Number)
  return (h || 0) * 60 + (m || 0)
}

// Перевод общего количества минут в "HH:MM"
const minutesToTime = (totalMins: number): string => {
  const h = Math.floor(totalMins / 60) % 24 // % 24 чтобы не выходить за рамки суток
  const m = totalMins % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

// --- Автоматизация расчетов ---

watch(
    () => props.initialValue,
    (value) => {
      Object.assign(form, createInitialState(value))

      // Инициализация продолжительности при загрузке формы
      if (form.start_time && form.end_time) {
        let startMins = timeToMinutes(form.start_time)
        let endMins = timeToMinutes(form.end_time)
        if (endMins < startMins) endMins += 24 * 60 // Учет перехода через полночь

        const diff = endMins - startMins
        duration.hours = Math.floor(diff / 60)
        duration.minutes = diff % 60
      } else {
        // Значение по умолчанию, если создаем новый урок
        duration.hours = 1
        duration.minutes = 0
      }
    },
    { immediate: true },
)

// Если изменилось время НАЧАЛА -> сдвигаем время ОКОНЧАНИЯ, сохраняя продолжительность
watch(
    () => form.start_time,
    (newTime, oldTime) => {
      if (newTime && newTime !== oldTime) {
        const startMins = timeToMinutes(newTime)
        const durationMins = (duration.hours || 0) * 60 + (duration.minutes || 0)
        form.end_time = minutesToTime(startMins + durationMins)
      }
    }
)

// Если изменилось время ОКОНЧАНИЯ (пользователь ввел вручную) -> пересчитываем ПРОДОЛЖИТЕЛЬНОСТЬ
watch(
    () => form.end_time,
    (newTime, oldTime) => {
      if (newTime && newTime !== oldTime) {
        let startMins = timeToMinutes(form.start_time)
        let endMins = timeToMinutes(newTime)
        if (endMins < startMins) endMins += 24 * 60

        const diff = endMins - startMins
        duration.hours = Math.floor(diff / 60)
        duration.minutes = diff % 60
      }
    }
)

// Если изменилась ПРОДОЛЖИТЕЛЬНОСТЬ -> пересчитываем время ОКОНЧАНИЯ
watch(
    () => [duration.hours, duration.minutes],
    ([newH, newM],[oldH, oldM]) => {
      // Проверка предотвращает бесконечный цикл (infinite loop) между вотчерами
      if (newH !== oldH || newM !== oldM) {
        const startMins = timeToMinutes(form.start_time)
        const durationMins = (Number(newH) || 0) * 60 + (Number(newM) || 0)
        form.end_time = minutesToTime(startMins + durationMins)
      }
    }
)

// ---------------------------------------------

watch(
    () => form.student_id,
    (studentId) => {
      if (!studentId || form.rate.trim()) {
        return
      }

      const student = props.students.find((item) => item.id === studentId)
      if (student) {
        form.rate = String(student.default_rate)
      }
    },
)

function submit() {
  if (isInvalid.value || !form.student_id || !form.subject_id) {
    return
  }

  emit('save', {
    date: form.date,
    start_time: form.start_time,
    end_time: form.end_time,
    student_id: form.student_id,
    subject_id: form.subject_id,
    rate: form.rate.trim() ? Number(form.rate) : null,
    prepayment_amount: Number(form.prepayment_amount),
    status: form.status,
    notes: form.notes.trim() || null,
  })
}

function createInitialState(initialValue: Lesson | null | undefined): LessonFormState {
  return {
    date: initialValue?.date ?? '',
    start_time: initialValue?.start_time.slice(0, 5) ?? '12:00', // Добавлено дефолтное время для удобства
    end_time: initialValue?.end_time.slice(0, 5) ?? '13:00',
    student_id: initialValue?.student_id ?? null,
    subject_id: initialValue?.subject_id ?? null,
    rate: initialValue ? String(initialValue.rate) : '',
    prepayment_amount: initialValue?.prepayment_amount ?? 0,
    status: initialValue?.status ?? 'planned',
    notes: initialValue?.notes ?? '',
  }
}
</script>

<template>
  <form class="grid gap-6" @submit.prevent="submit">
    <div class="grid gap-4 md:grid-cols-2">
      <label class="block">
        <span class="field-label">Дата</span>
        <input v-model="form.date" type="date" class="field" />
      </label>

      <SelectInput
          v-model="form.status"
          label="Статус"
          :options="[...statusOptions]"
          empty-label="Выберите статус"
      />
    </div>

    <!-- Изменено на 3 колонки (Начало, Длительность, Окончание) -->
    <div class="grid gap-4 md:grid-cols-3">
      <TimeInput v-model="form.start_time" label="Начало" />

      <div class="flex gap-2">
        <label class="block w-1/2">
          <span class="field-label">Часы</span>
          <input
              v-model.number="duration.hours"
              type="number"
              min="0"
              max="23"
              class="field"
              placeholder="1"
          />
        </label>
        <label class="block w-1/2">
          <span class="field-label">Минуты</span>
          <input
              v-model.number="duration.minutes"
              type="number"
              min="0"
              max="59"
              step="5"
              class="field"
              placeholder="0"
          />
        </label>
      </div>

      <TimeInput v-model="form.end_time" label="Окончание" />
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <SelectInput
          v-model="form.student_id"
          label="Ученик"
          :options="studentOptions"
          empty-label="Выберите ученика"
      />
      <SelectInput
          v-model="form.subject_id"
          label="Предмет"
          :options="subjectOptions"
          empty-label="Выберите предмет"
      />
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <label class="block">
        <span class="field-label">Ставка за час</span>
        <input
            v-model="form.rate"
            type="number"
            min="0"
            step="100"
            class="field"
        />
      </label>

      <label class="block">
        <span class="field-label">Предоплата</span>
        <input
            v-model.number="form.prepayment_amount"
            type="number"
            min="0"
            step="100"
            class="field"
        />
      </label>
    </div>

    <label class="block">
      <span class="field-label">Заметки</span>
      <textarea
          v-model="form.notes"
          rows="4"
          class="field h-auto resize-none py-3"
      />
    </label>

    <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
      <button type="button" class="btn-secondary w-full sm:w-auto" @click="emit('cancel')">Отмена</button>
      <button type="submit" class="btn-primary w-full sm:w-auto" :disabled="isInvalid || submitting">
        {{ submitLabel }}
      </button>
    </div>
  </form>
</template>