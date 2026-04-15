<script setup lang="ts">
import type { SelectOption } from '@/types/ui'

const modelValue = defineModel<string | number | null>({
  default: null,
})

withDefaults(
  defineProps<{
    label?: string
    options: SelectOption[]
    emptyLabel?: string
    disabled?: boolean
  }>(),
  {
    label: '',
    emptyLabel: 'Выберите значение',
    disabled: false,
  },
)
</script>

<template>
  <label class="block">
    <span v-if="label" class="field-label">{{ label }}</span>
    <select v-model="modelValue" class="field" :disabled="disabled">
      <option :value="null">{{ emptyLabel }}</option>
      <option v-for="option in options" :key="option.value ?? 'empty'" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
