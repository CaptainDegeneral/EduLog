const prefix = '[EduLog]'

function write(
  method: 'debug' | 'info' | 'warn' | 'error',
  scope: string,
  message: string,
  data?: unknown,
) {
  const line = `${prefix} ${scope}: ${message}`

  if (data !== undefined) {
    console[method](line, data)
    return
  }

  console[method](line)
}

export const appLogger = {
  debug(scope: string, message: string, data?: unknown) {
    write('debug', scope, message, data)
  },
  info(scope: string, message: string, data?: unknown) {
    write('info', scope, message, data)
  },
  warn(scope: string, message: string, data?: unknown) {
    write('warn', scope, message, data)
  },
  error(scope: string, message: string, data?: unknown) {
    write('error', scope, message, data)
  },
}
