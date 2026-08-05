import axios from 'axios'

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { message?: string; error?: string } | undefined
    if (data?.message) return data.message
    if (data?.error) return data.error.replace(/_/g, ' ').toLowerCase()
    if (error.response) return `Request failed with status ${error.response.status}`
    return 'Network error. Please check your connection.'
  }
  if (error instanceof Error && error.message) return error.message
  return 'An unexpected error occurred.'
}
