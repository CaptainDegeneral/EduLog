<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { subjectsApi } from '@/api/subjects'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import DataTable from '@/components/DataTable.vue'
import { useNotifications } from '@/store/notifications'
import { useReferenceStore } from '@/store/referenceStore'
import type { Subject } from '@/types/models'
import type { TableColumn } from '@/types/ui'
import { appLogger } from '@/utils/logger'

const { pushSuccess } = useNotifications()
const references = useReferenceStore()

const subjects = ref<Subject[]>([])
const loading = ref(false)
const creating = ref(false)
const deleting = ref(false)
const editingId = ref<number | null>(null)
const subjectToDelete = ref<Subject | null>(null)

const newSubject = reactive({
  name: '',
})

const draft = reactive({
  name: '',
})

const columns: TableColumn<Subject>[] = [
  { key: 'name', label: 'Название предмета' },
  { key: 'actions', label: 'Действия', class: 'w-44' },
]

onMounted(loadSubjects)

async function loadSubjects() {
  loading.value = true
  appLogger.info('subjects', 'load subjects')

  try {
    subjects.value = await subjectsApi.list()
    await references.refresh()
  } finally {
    loading.value = false
  }
}

async function createSubject() {
  creating.value = true
  appLogger.info('subjects', 'create subject', { ...newSubject })

  try {
    await subjectsApi.create({
      name: newSubject.name,
    })
    newSubject.name = ''
    await loadSubjects()
    pushSuccess('Предмет добавлен.')
  } finally {
    creating.value = false
  }
}

function startEdit(subject: Subject) {
  appLogger.info('subjects', 'start edit', { subjectId: subject.id })
  editingId.value = subject.id
  draft.name = subject.name
}

async function saveEdit(id: number) {
  appLogger.info('subjects', 'save edit', { subjectId: id, draft: { ...draft } })
  await subjectsApi.update(id, {
    name: draft.name,
  })
  editingId.value = null
  await loadSubjects()
  pushSuccess('Предмет обновлён.')
}

function requestDelete(subject: Subject) {
  appLogger.warn('subjects', 'request delete', { subjectId: subject.id })
  subjectToDelete.value = subject
}

async function confirmDelete() {
  if (!subjectToDelete.value) {
    return
  }

  deleting.value = true
  appLogger.info('subjects', 'delete subject', { subjectId: subjectToDelete.value.id })

  try {
    await subjectsApi.remove(subjectToDelete.value.id)
    subjectToDelete.value = null
    await loadSubjects()
    pushSuccess('Предмет удалён.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <section class="space-y-5">
    <div class="surface p-5 sm:p-6">
      <p class="text-xs font-semibold uppercase tracking-[0.18em] text-muted">Предметы</p>
      <h2 class="mt-2 font-display text-3xl text-ink">Справочник предметов</h2>
      <p class="mt-2 max-w-2xl text-sm leading-6 text-muted">
        Используйте единый список предметов, чтобы записи оставались чистыми и единообразными.
      </p>

      <div class="mt-6 grid gap-4 md:grid-cols-[1fr_auto]">
        <label class="block">
          <span class="field-label">Название</span>
          <input v-model="newSubject.name" class="field" />
        </label>

        <div class="flex items-end">
          <button
            class="btn-primary w-full"
            :disabled="creating || !newSubject.name.trim()"
            @click="createSubject"
          >
            {{ creating ? 'Сохраняем...' : 'Добавить предмет' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading && !subjects.length" class="surface p-8 text-center text-sm text-muted">
      Загружаем предметы...
    </div>

    <div v-else-if="!subjects.length" class="surface p-8 text-center">
      <h3 class="font-display text-2xl text-ink">Пока пусто</h3>
      <p class="mt-2 text-sm text-muted">Добавьте предмет, чтобы привязывать его к занятиям.</p>
    </div>

    <template v-else>
      <div class="grid gap-4 md:hidden">
        <article v-for="subject in subjects" :key="subject.id" class="surface p-5">
          <h3 class="text-lg font-semibold text-ink">{{ subject.name }}</h3>

          <div class="mt-4 grid gap-3">
            <button class="btn-secondary w-full" @click="startEdit(subject)">
              {{ editingId === subject.id ? 'Редактируется' : 'Редактировать' }}
            </button>
            <button class="btn-danger w-full" @click="requestDelete(subject)">Удалить</button>
          </div>

          <div v-if="editingId === subject.id" class="mt-4 grid gap-3">
            <input v-model="draft.name" class="field" />
            <div class="grid gap-3 sm:grid-cols-2">
              <button class="btn-primary w-full" @click="saveEdit(subject.id)">Сохранить</button>
              <button class="btn-secondary w-full" @click="editingId = null">Отмена</button>
            </div>
          </div>
        </article>
      </div>

      <div class="hidden md:block surface p-4 sm:p-6">
        <DataTable :columns="columns" :rows="subjects" row-key="id">
          <template #cell-name="{ row }">
            <input v-if="editingId === row.id" v-model="draft.name" class="field min-w-52" />
            <span v-else>{{ row.name }}</span>
          </template>

          <template #cell-actions="{ row }">
            <div class="flex flex-wrap gap-2">
              <template v-if="editingId === row.id">
                <button class="btn-primary" @click="saveEdit(row.id)">Сохранить</button>
                <button class="btn-secondary" @click="editingId = null">Отмена</button>
              </template>
              <template v-else>
                <button class="btn-secondary" @click="startEdit(row)">Редактировать</button>
                <button class="btn-danger" @click="requestDelete(row)">Удалить</button>
              </template>
            </div>
          </template>
        </DataTable>
      </div>
    </template>

    <ConfirmDialog
      :open="Boolean(subjectToDelete)"
      :loading="deleting"
      title="Удалить предмет?"
      :description="subjectToDelete ? `Запись «${subjectToDelete.name}» будет удалена.` : ''"
      @close="subjectToDelete = null"
      @confirm="confirmDelete"
    />
  </section>
</template>
