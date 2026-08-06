import type { DragEvent, ChangeEvent } from 'react'
import { useCallback, useRef, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertCircle, CheckCircle2, FileUp, Loader2, UploadCloud, X } from 'lucide-react'
import { uploadFile } from '@/services/files'
import { getErrorMessage } from '@/utils/errors'
import { useToast } from '@/context/ToastContext'
import { formatBytes } from '@/utils/helpers'

interface UploadItem {
  file: File
  percent: number
  status: 'uploading' | 'success' | 'error'
  error?: string
}

export default function UploadPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [items, setItems] = useState<UploadItem[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const addFiles = useCallback((files: File[]) => {
    setItems((prev) => [
      ...prev,
      ...files.map((file) => ({ file, percent: 0, status: 'uploading' as const })),
    ])
  }, [])

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      uploadFile(file, (percent) => {
        setItems((prev) =>
          prev.map((item) =>
            item.file === file ? { ...item, percent } : item,
          ),
        )
      }),
    onSuccess: (record, file) => {
      setItems((prev) =>
        prev.map((item) =>
          item.file === file ? { ...item, percent: 100, status: 'success' } : item,
        ),
      )
      toast(`"${record.original_name}" uploaded and encrypted.`, 'success')
      void queryClient.invalidateQueries({ queryKey: ['files'] })
      void queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
    },
    onError: (error: unknown, file) => {
      setItems((prev) =>
        prev.map((item) =>
          item.file === file ? { ...item, status: 'error', error: getErrorMessage(error) } : item,
        ),
      )
      toast(`Upload failed for "${file.name}".`, 'error')
    },
  })

  const handleFiles = (files: FileList | File[]) => {
    const list = Array.from(files)
    addFiles(list)
    list.forEach((file) => uploadMutation.mutate(file))
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) handleFiles(e.target.files)
    e.target.value = ''
  }

  const removeItem = (index: number) => {
    setItems((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Upload Files</h1>
        <p className="mt-1 text-sm text-slate-400">
          Files are encrypted with AES-256-GCM before they touch the server.
        </p>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click()
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-16 text-center transition ${
          isDragging
            ? 'border-blue-500 bg-blue-600/10'
            : 'border-slate-700 bg-slate-900 hover:border-slate-500'
        }`}
      >
        <UploadCloud className="mb-4 h-12 w-12 text-slate-500" />
        <p className="text-lg font-semibold text-slate-200">Drag files here</p>
        <p className="mt-1 text-sm text-slate-500">or</p>
        <span className="mt-3 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500">
          <FileUp className="h-4 w-4" />
          Browse Files
        </span>
        <input
          ref={inputRef}
          type="file"
          multiple
          className="hidden"
          onChange={onInputChange}
          aria-label="Choose files to upload"
        />
      </div>

      {items.length > 0 && (
        <div className="space-y-3">
          {items.map((item, index) => (
            <div
              key={`${item.file.name}-${index}`}
              className="rounded-xl border border-slate-800 bg-slate-900 p-4"
            >
              <div className="flex items-center gap-3">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-200">{item.file.name}</p>
                  <p className="text-xs text-slate-500">{formatBytes(item.file.size)}</p>
                </div>

                {item.status === 'uploading' && (
                  <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                )}
                {item.status === 'success' && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                {item.status === 'error' && <AlertCircle className="h-5 w-5 text-red-500" />}

                {item.status !== 'uploading' && (
                  <button
                    type="button"
                    onClick={() => removeItem(index)}
                    aria-label="Remove from list"
                    className="text-slate-500 transition hover:text-slate-300"
                  >
                    <X className="h-4 w-4" />
                  </button>
                )}
              </div>

              {item.status === 'uploading' && (
                <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
                  <div
                    className="h-full rounded-full bg-blue-600 transition-all duration-200"
                    style={{ width: `${item.percent}%` }}
                  />
                </div>
              )}
              {item.status === 'error' && (
                <p className="mt-2 text-xs text-red-400">{item.error}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
