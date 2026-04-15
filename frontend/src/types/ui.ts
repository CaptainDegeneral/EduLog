export interface SelectOption {
  label: string
  value: string | number | null
}

export interface TableColumn<T> {
  key: keyof T | string
  label: string
  class?: string
  headerClass?: string
}

export interface NotificationItem {
  id: number
  message: string
  tone: 'error' | 'success'
}
