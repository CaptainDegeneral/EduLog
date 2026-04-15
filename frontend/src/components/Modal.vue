<script setup lang="ts">
withDefaults(
  defineProps<{
    open: boolean
    title: string
    subtitle?: string
    maxWidthClass?: string
  }>(),
  {
    subtitle: '',
    maxWidthClass: 'max-w-3xl',
  },
)

const emit = defineEmits<{
  close: []
}>()
</script>

<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-40 flex items-center justify-center bg-ink/35 px-4 py-8"
        @click.self="emit('close')"
      >
        <div class="surface max-h-[90vh] w-full overflow-y-auto p-6 sm:p-8" :class="maxWidthClass">
          <div class="mb-5 flex items-start justify-between gap-4">
            <div>
              <p v-if="subtitle" class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">
                {{ subtitle }}
              </p>
              <h2 class="mt-2 font-display text-3xl text-ink">{{ title }}</h2>
            </div>
            <button class="btn-secondary" @click="emit('close')">Закрыть</button>
          </div>
          <slot />
        </div>
      </div>
    </transition>
  </Teleport>
</template>
