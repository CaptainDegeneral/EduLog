<script setup lang="ts" generic="T extends Record<string, unknown>">
import type { TableColumn } from '@/types/ui'

defineProps<{
  columns: TableColumn<T>[]
  rows: T[]
  rowKey: keyof T | ((row: T) => string | number)
  emptyText?: string
}>()

function resolveKey<TItem extends Record<string, unknown>>(
  row: TItem,
  rowKey: keyof TItem | ((currentRow: TItem) => string | number),
) {
  return typeof rowKey === 'function' ? rowKey(row) : String(row[rowKey])
}
</script>

<template>
  <div class="overflow-hidden rounded-[28px] border border-sand/30">
    <table class="min-w-full border-separate border-spacing-0 text-sm">
      <thead>
        <tr class="bg-sand/15 text-left text-xs uppercase tracking-[0.18em] text-muted">
          <th
            v-for="column in columns"
            :key="String(column.key)"
            class="px-4 py-4 font-semibold"
            :class="column.headerClass"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>

      <tbody class="bg-white/70">
        <tr v-if="!rows.length">
          <td :colspan="columns.length" class="px-4 py-8 text-center text-muted">
            {{ emptyText ?? 'Нет данных.' }}
          </td>
        </tr>

        <tr
          v-for="row in rows"
          :key="resolveKey(row, rowKey)"
          class="transition hover:bg-sand/10"
        >
          <td
            v-for="column in columns"
            :key="String(column.key)"
            class="border-t border-sand/15 px-4 py-4 align-top text-ink"
            :class="column.class"
          >
            <slot :name="`cell-${String(column.key)}`" :row="row">
              {{ row[column.key as keyof T] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
