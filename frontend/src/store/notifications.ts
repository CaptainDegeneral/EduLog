import { reactive } from 'vue'

import type { NotificationItem } from '@/types/ui'

const notifications = reactive<NotificationItem[]>([])
let nextId = 1

function push(message: string, tone: NotificationItem['tone']) {
  const item: NotificationItem = {
    id: nextId++,
    message,
    tone,
  }
  notifications.push(item)
  setTimeout(() => remove(item.id), 3500)
}

function remove(id: number) {
  const index = notifications.findIndex((item) => item.id === id)
  if (index >= 0) {
    notifications.splice(index, 1)
  }
}

export function useNotifications() {
  return {
    notifications,
    pushSuccess(message: string) {
      push(message, 'success')
    },
    pushError(message: string) {
      push(message, 'error')
    },
    remove,
  }
}
