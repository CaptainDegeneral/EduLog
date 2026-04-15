import axios from 'axios'

import { useNotifications } from '@/store/notifications'
import { appLogger } from '@/utils/logger'

const { pushError } = useNotifications()

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

http.interceptors.request.use(
  (config) => {
    appLogger.info('api', 'request', {
      method: config.method,
      url: config.url,
      params: config.params,
      data: config.data,
    })
    return config
  },
  (error) => {
    appLogger.error('api', 'request_error', error)
    return Promise.reject(error)
  },
)

http.interceptors.response.use(
  (response) => {
    appLogger.info('api', 'response', {
      method: response.config.method,
      url: response.config.url,
      status: response.status,
      data: response.data,
    })
    return response
  },
  (error) => {
    const message =
      error.response?.data?.detail ?? error.message ?? 'Не удалось выполнить запрос.'

    appLogger.error('api', 'response_error', {
      method: error.config?.method,
      url: error.config?.url,
      status: error.response?.status,
      message,
      data: error.response?.data,
    })

    pushError(message)
    return Promise.reject(error)
  },
)

export default http
