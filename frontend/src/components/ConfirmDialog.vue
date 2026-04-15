<script setup lang="ts">
import Modal from '@/components/Modal.vue'

withDefaults(
  defineProps<{
    open: boolean
    title?: string
    description: string
    confirmLabel?: string
    loading?: boolean
  }>(),
  {
    title: 'Подтвердите действие',
    confirmLabel: 'Удалить',
    loading: false,
  },
)

const emit = defineEmits<{
  close: []
  confirm: []
}>()
</script>

<template>
  <Modal
    :open="open"
    :title="title"
    subtitle="Подтверждение"
    max-width-class="max-w-lg"
    @close="emit('close')"
  >
    <div class="space-y-6">
      <p class="text-sm leading-6 text-muted">{{ description }}</p>

      <div class="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
        <button class="btn-secondary w-full sm:w-auto" :disabled="loading" @click="emit('close')">
          Отмена
        </button>
        <button class="btn-danger w-full sm:w-auto" :disabled="loading" @click="emit('confirm')">
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </Modal>
</template>
