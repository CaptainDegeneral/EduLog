<script setup lang="ts">
import { computed } from 'vue'

import type { LessonStatus } from '@/types/models'

const props = defineProps<{
  status?: LessonStatus
  debt?: number
}>()

const classes = computed(() => {
  if (props.debt !== undefined && props.debt > 0) {
    return 'bg-amber-100 text-amber-800'
  }

  switch (props.status) {
    case 'completed':
      return 'bg-emerald-100 text-emerald-800'
    case 'cancelled':
      return 'bg-rose-100 text-rose-800'
    default:
      return 'bg-slate-200 text-slate-700'
  }
})

const label = computed(() => {
  if (props.debt !== undefined) {
    return props.debt > 0 ? 'Есть долг' : 'Без долга'
  }

  switch (props.status) {
    case 'completed':
      return 'Проведено'
    case 'cancelled':
      return 'Отменено'
    default:
      return 'Запланировано'
  }
})
</script>

<template>
  <span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold" :class="classes">
    {{ label }}
  </span>
</template>
