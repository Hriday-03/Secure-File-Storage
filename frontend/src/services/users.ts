import api from './api'
import type { ApiEnvelope, User } from '@/types'

export async function updateProfile(name: string): Promise<User> {
  const { data } = await api.put<ApiEnvelope<User>>('/users/profile', { name })
  return data.data as User
}

export async function changePassword(current_password: string, new_password: string): Promise<void> {
  await api.post<ApiEnvelope<null>>('/users/change-password', { current_password, new_password })
}
