<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'

import { useNotifications } from '@/store/notifications'

const route = useRoute()
const { notifications, remove } = useNotifications()

const navItems = [
  { label: 'Занятия', shortLabel: 'Занятия', to: '/lessons' },
  { label: 'Ученики', shortLabel: 'Ученики', to: '/students' },
  { label: 'Предметы', shortLabel: 'Предметы', to: '/subjects' },
  { label: 'Аналитика', shortLabel: 'Отчёты', to: '/analytics' },
]
</script>

<template>
  <div class="mx-auto min-h-screen max-w-7xl lg:grid lg:grid-cols-[240px_minmax(0,1fr)] lg:gap-6 lg:px-6 lg:py-6">
    <aside class="hidden lg:block">
      <div class="surface sticky top-6 flex min-h-[calc(100vh-3rem)] flex-col p-6">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-accent">EduLog</p>
          <h1 class="mt-3 font-display text-4xl text-ink">Учёт занятий</h1>
          <p class="mt-3 text-sm leading-6 text-muted">
            Быстрый доступ к расписанию, справочникам и отчётам без лишних экранов.
          </p>
        </div>

        <nav class="mt-8 flex flex-1 flex-col gap-2">
          <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              class="rounded-2xl px-4 py-3 text-sm font-semibold transition"
              :class="
              route.path === item.to
                ? 'bg-ink text-white'
                : 'text-ink hover:bg-white/70 hover:text-accent'
            "
          >
            {{ item.label }}
          </RouterLink>
        </nav>
      </div>
    </aside>

    <div class="min-w-0 px-4 pb-24 pt-4 sm:px-6 sm:pb-28 lg:px-0 lg:pb-6 lg:pt-0">
      <header class="mb-5 lg:hidden">
        <div class="surface px-5 py-4">
          <p class="text-xs font-semibold uppercase tracking-[0.24em] text-accent">EduLog</p>
          <h1 class="mt-2 font-display text-3xl text-ink">Учёт занятий</h1>
        </div>
      </header>

      <main>
        <RouterView />
      </main>
    </div>

    <nav class="fixed bottom-3 left-1/2 z-40 flex w-[calc(100%-1.5rem)] max-w-md -translate-x-1/2 gap-1 rounded-[28px] border border-sand/35 bg-panel/95 p-2 shadow-soft backdrop-blur lg:hidden">
      <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex-1 rounded-2xl px-3 py-3 text-center text-xs font-semibold transition"
          :class="
          route.path === item.to
            ? 'bg-ink text-white'
            : 'text-ink hover:bg-white/70 hover:text-accent'
        "
      >
        {{ item.shortLabel }}
      </RouterLink>
    </nav>

    <div class="fixed right-4 top-4 z-50 flex w-[calc(100%-2rem)] max-w-sm flex-col gap-3">
      <div
          v-for="item in notifications"
          :key="item.id"
          class="rounded-2xl border px-4 py-3 text-sm shadow-soft"
          :class="
          item.tone === 'error'
            ? 'border-danger/25 bg-white text-danger'
            : 'border-moss/25 bg-white text-moss'
        "
      >
        <div class="flex items-start justify-between gap-3">
          <span>{{ item.message }}</span>
          <button class="text-xs font-semibold uppercase tracking-[0.18em]" @click="remove(item.id)">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>