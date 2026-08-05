import api from './api'
import type { ApiEnvelope, FileListResponse, FileRecord } from '@/types'

export interface ListFilesParams {
  page?: number
  pageSize?: number
  search?: string
  sortBy?: 'name' | 'size' | 'date'
  sortOrder?: 'asc' | 'desc'
}

export async function uploadFile(
  file: File,
  onProgress: (percent: number) => void,
): Promise<FileRecord> {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<ApiEnvelope<FileRecord>>('/files/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress(Math.round((e.loaded / e.total) * 100))
    },
  })
  return data.data as FileRecord
}

export async function listFiles(params: ListFilesParams = {}): Promise<FileListResponse> {
  const { data } = await api.get<ApiEnvelope<FileListResponse>>('/files', {
    params: {
      page: params.page ?? 1,
      page_size: params.pageSize ?? 10,
      search: params.search || undefined,
      sort_by: params.sortBy ?? 'date',
      sort_order: params.sortOrder ?? 'desc',
    },
  })
  return data.data as FileListResponse
}

export async function getFile(id: string): Promise<FileRecord> {
  const { data } = await api.get<ApiEnvelope<FileRecord>>(`/files/${id}`)
  return data.data as FileRecord
}

export async function deleteFile(id: string): Promise<string> {
  const { data } = await api.delete<ApiEnvelope<{ message: string }>>(`/files/${id}`)
  return data.data?.message ?? 'File deleted.'
}

export async function renameFile(id: string, newName: string): Promise<FileRecord> {
  const { data } = await api.put<ApiEnvelope<FileRecord>>(`/files/${id}/rename`, { new_name: newName })
  return data.data as FileRecord
}

export async function downloadFile(id: string): Promise<void> {
  const res = await api.get(`/files/${id}/download`, { responseType: 'blob' })
  const disposition = res.headers['content-disposition'] ?? ''
  const match = disposition.match(/filename\*=UTF-8''([^;]+)/)
  let name = 'download'
  if (match) {
    try {
      name = decodeURIComponent(match[1])
    } catch {
      name = match[1]
    }
  }
  const url = URL.createObjectURL(res.data as Blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = name
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}