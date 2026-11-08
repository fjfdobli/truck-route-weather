const BASE_URL = import.meta.env.VITE_API_URL ?? '/api'

export class ApiError extends Error {
  constructor(message, fields = {}) {
    super(message)
    this.fields = fields
  }
}

export async function request(path, { body, signal } = {}) {
  let response
  try {
    response = await fetch(BASE_URL + path, {
      method: body ? 'POST' : 'GET',
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body && JSON.stringify(body),
      signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new ApiError('Could not reach the server. Check your connection and try again.')
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) throw toApiError(data, response.status)
  return data
}

function toApiError(data, status) {
  if (data?.detail) return new ApiError(data.detail)
  if (data && typeof data === 'object') {
    const fields = Object.fromEntries(Object.entries(data).map(([field, messages]) => [field, flatten(messages)]))
    return new ApiError('Please fix the highlighted fields.', fields)
  }
  return new ApiError(`Something went wrong (${status}). Please try again.`)
}

function flatten(messages) {
  if (typeof messages === 'string') return messages
  const list = Array.isArray(messages) ? messages : Object.values(messages ?? {})
  return list.map(flatten).join(' ')
}
