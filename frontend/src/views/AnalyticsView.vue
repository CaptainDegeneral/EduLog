<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { analyticsApi } from '@/api/analytics'
import DataTable from '@/components/DataTable.vue'
import type { AnalyticsByStudentItem, AnalyticsSummary } from '@/types/models'
import type { TableColumn } from '@/types/ui'
import { formatCurrency } from '@/utils/formatters'
import { appLogger } from '@/utils/logger'

const summary = ref<AnalyticsSummary | null>(null)
const byStudent = ref<AnalyticsByStudentItem[]>([])
const loading = ref(false)

const columns: TableColumn<AnalyticsByStudentItem>[] = [
  { key: 'student_name', label: 'Ученик' },
  { key: 'lessons_count', label: 'Всего занятий' },
  { key: 'cancelled_count', label: 'Отмены' },
  { key: 'total_hours', label: 'Часы' },
  { key: 'total_income', label: 'Доход' },
  { key: 'total_debt', label: 'Долг' },
]

onMounted(loadAnalytics)

async function loadAnalytics() {
  loading.value = true
  appLogger.info('analytics', 'load analytics')

  try {
    const [summaryData, byStudentData] = await Promise.all([
      analyticsApi.summary(),
      analyticsApi.byStudent(),
    ])
    summary.value = summaryData
    byStudent.value = byStudentData
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="space-y-5">
    <div class="surface p-5 sm:p-6">
      <div class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Аналитика</p>
          <h2 class="mt-2 font-display text-3xl text-ink">Сводные показатели</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-muted">
            Доход, часы, отмены и задолженность считаются по фактическим данным занятий.
          </p>
        </div>

        <button class="btn-secondary w-full md:w-auto" :disabled="loading" @click="loadAnalytics">
          {{ loading ? 'Обновление...' : 'Обновить' }}
        </button>
      </div>

      <div class="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article class="rounded-[28px] border border-sand/35 bg-white/70 p-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Доход</p>
          <p class="mt-3 font-display text-3xl text-ink">
            {{ formatCurrency(summary?.total_income ?? 0) }}
          </p>
        </article>

        <article class="rounded-[28px] border border-sand/35 bg-white/70 p-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Часы</p>
          <p class="mt-3 font-display text-3xl text-ink">{{ summary?.total_hours ?? 0 }}</p>
        </article>

        <article class="rounded-[28px] border border-sand/35 bg-white/70 p-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Долг</p>
          <p class="mt-3 font-display text-3xl text-amber-700">
            {{ formatCurrency(summary?.total_debt ?? 0) }}
          </p>
        </article>

        <article class="rounded-[28px] border border-sand/35 bg-white/70 p-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Отменено</p>
          <p class="mt-3 font-display text-3xl text-rose-700">
            {{ summary?.cancelled_count ?? 0 }}
          </p>
        </article>
      </div>
    </div>

    <div v-if="loading && !byStudent.length" class="surface p-8 text-center text-sm text-muted">
      Загружаем аналитику...
    </div>

    <div v-else-if="!byStudent.length" class="surface p-8 text-center">
      <h3 class="font-display text-2xl text-ink">Нет данных</h3>
      <p class="mt-2 text-sm text-muted">После первых занятий здесь появятся сводные показатели.</p>
    </div>

    <template v-else>
      <div class="grid gap-4 md:hidden">
        <article v-for="item in byStudent" :key="item.student_id" class="surface p-5">
          <div class="flex items-start justify-between gap-3">
            <h3 class="text-lg font-semibold text-ink">{{ item.student_name }}</h3>
            <span class="rounded-full bg-sand/20 px-3 py-1 text-xs font-semibold text-ink">
              {{ item.lessons_count }} занятий
            </span>
          </div>

          <div class="mt-4 grid gap-2 text-sm">
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Часы</span>
              <span>{{ item.total_hours }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Доход</span>
              <span>{{ formatCurrency(item.total_income) }}</span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Долг</span>
              <span :class="item.total_debt > 0 ? 'font-semibold text-amber-700' : 'text-moss'">
                {{ formatCurrency(item.total_debt) }}
              </span>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="text-muted">Отмены</span>
              <span>{{ item.cancelled_count }}</span>
            </div>
          </div>
        </article>
      </div>

      <div class="hidden md:block surface p-4 sm:p-6">
        <DataTable :columns="columns" :rows="byStudent" row-key="student_id">
          <template #cell-total_income="{ row }">
            {{ formatCurrency(row.total_income) }}
          </template>

          <template #cell-total_debt="{ row }">
            <span :class="row.total_debt > 0 ? 'text-amber-700' : 'text-moss'">
              {{ formatCurrency(row.total_debt) }}
            </span>
          </template>
        </DataTable>
      </div>
    </template>
  </section>
</template>
