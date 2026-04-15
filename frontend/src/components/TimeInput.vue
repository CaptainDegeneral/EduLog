<script setup lang="ts">
const modelValue = defineModel<string>({
  default: '',
})

withDefaults(
  defineProps<{
    label?: string
    step?: number
  }>(),
  {
    label: '',
    step: 300,
  },
)
</script>

<template>
  <label class="block">
    <span v-if="label" class="field-label">{{ label }}</span>
    <input v-model="modelValue" type="time" class="field" :step="step" />
  </label>
</template>
