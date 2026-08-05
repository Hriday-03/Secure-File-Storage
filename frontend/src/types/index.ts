export interface User {
  id: string
  name: string
  email: string
  created_at: string
}

export interface AuthPayload {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface ApiEnvelope<T> {
  success: boolean
  message: string
  data: T | null
  error: string | null
}

export interface FileRecord {
  id: string
  original_name: string
  size: number
  mime_type: string | null
  algorithm: string
  uploaded_at: string
}

export interface FileListResponse {
  items: FileRecord[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
