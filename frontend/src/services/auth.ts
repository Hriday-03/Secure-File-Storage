import api from './api'
import type { ApiEnvelope, AuthPayload, User } from '@/types'

export async function register(name: string, email: string, password: string): Promise<AuthPayload> {
  const { data } = await api.post<ApiEnvelope<AuthPayload>>('/auth/register', {
    name,
    email,
    password,
  })
  return data.data as AuthPayload
}

export async function login(email: string, password: string): Promise<AuthPayload> {
  const { data } = await api.post<ApiEnvelope<AuthPayload>>('/auth/login', { email, password })
  return data.data as AuthPayload
}

export async function logout(): Promise<void> {
  await api.post<ApiEnvelope<null>>('/auth/logout')
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<ApiEnvelope<User>>('/auth/me')
  return data.data as User
}
