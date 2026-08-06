import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  ArrowDown,
  ArrowUp,
  ChevronLeft,
  ChevronRight,
  Download,
  File as FileIcon,
  FolderOpen,
  Loader2,
  Pencil,
  Search,
  Trash2,
} from 'lucide-react'
import Modal from '@/components/Modal'
import { deleteFile, downloadFile, listFiles, renameFile } from '@/services/files'
import { useToast } from '@/context/ToastContext'
import { formatBytes, formatDate } from '@/utils/helpers'
import { getErrorMessage } from '@/utils/errors'

type SortBy = 'name' | 'size' | 'date'
type SortOrder = 'asc' | 'desc'

export default function FilesPage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [search, setSearch] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [sortBy, setSortBy] = useState<SortBy>('date')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [renameTarget, setRenameTarget] = useState<{ id: string; name: string } | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const [newName, setNewName] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search)
      setPage(1)
    }, 400)
    return () => clearTimeout(timer)
  }, [search])

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['files', { page, pageSize, search: debouncedSearch, sortBy, sortOrder }],
    queryFn: () =>
      listFiles({ page, pageSize, search: debouncedSearch, sortBy, sortOrder }),
    placeholderData: (prev) => prev,
  })

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ['files'] })
    void queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] })
  }

  const downloadMutation = useMutation({
    mutationFn: downloadFile,
    onSuccess: (_result, id) => {
      const name = data?.items.find((f) => f.id === id)?.original_name ?? 'file'
      toast(`Download of "${name}" started.`, 'success')
    },
    onError: (error: unknown) => toast(getErrorMessage(error), 'error'),
  })

  const renameMutation = useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) => renameFile(id, name),
    onSuccess: () => {
      setRenameTarget(null)
      toast('File renamed successfully.', 'success')
      invalidate()
    },
    onError: (error: unknown) => toast(getErrorMessage(error), 'error'),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteFile,
    onSuccess: () => {
      setDeleteTarget(null)
      toast('File deleted successfully.', 'success')
      invalidate()
    },
    onError: (error: unknown) => toast(getErrorMessage(error), 'error'),
  })

  const toggleSort = (by: SortBy) => {
    if (sortBy === by) {
      setSortOrder((o) => (o === 'desc' ? 'asc' : 'desc'))
    } else {
      setSortBy(by)
      setSortOrder(by === 'name' ? 'asc' : 'desc')
    }
    setPage(1)
  }

  const renderSortIcon = (by: SortBy) => {
    if (sortBy !== by) return null
    return sortOrder === 'desc' ? <ArrowDown className="h-3 w-3" /> : <ArrowUp className="h-3 w-3" />
  }

  const totalPages = useMemo(() => data?.total_pages ?? 0, [data])

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">My Files</h1>
          <p className="mt-1 text-sm text-slate-400">
            {data?.total ?? 0} encrypted {data?.total === 1 ? 'file' : 'files'}
          </p>
        </div>

        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by filename..."
            className="w-64 rounded-lg border border-slate-700 bg-slate-900 py-2 pl-10 pr-3 text-sm text-slate-100 placeholder-slate-500 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-600/30"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 animate-pulse rounded-xl bg-slate-900" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="overflow-hidden rounded-xl border border-slate-800">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">
                    <button
                      type="button"
                      onClick={() => toggleSort('name')}
                      className="inline-flex items-center gap-1 uppercase tracking-wide transition hover:text-slate-300"
                    >
                      Name {renderSortIcon('name')}
                    </button>
                  </th>
                  <th className="hidden px-4 py-3 font-medium sm:table-cell">
                    <button
                      type="button"
                      onClick={() => toggleSort('size')}
                      className="inline-flex items-center gap-1 uppercase tracking-wide transition hover:text-slate-300"
                    >
                      Size {renderSortIcon('size')}
                    </button>
                  </th>
                  <th className="hidden px-4 py-3 font-medium md:table-cell">
                    <button
                      type="button"
                      onClick={() => toggleSort('date')}
                      className="inline-flex items-center gap-1 uppercase tracking-wide transition hover:text-slate-300"
                    >
                      Uploaded {renderSortIcon('date')}
                    </button>
                  </th>
                  <th className="hidden px-4 py-3 font-medium lg:table-cell">Encryption</th>
                  <th className="px-4 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900/50">
                {data.items.map((file) => (
                  <tr key={file.id} className="transition hover:bg-slate-800/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600/15 text-blue-400">
                          <FileIcon className="h-4 w-4" />
                        </span>
                        <span className="truncate font-medium text-slate-200">
                          {file.original_name}
                        </span>
                      </div>
                    </td>
                    <td className="hidden px-4 py-3 text-slate-400 sm:table-cell">
                      {formatBytes(file.size)}
                    </td>
                    <td className="hidden px-4 py-3 text-slate-400 md:table-cell">
                      {formatDate(file.uploaded_at)}
                    </td>
                    <td className="hidden px-4 py-3 lg:table-cell">
                      <span className="inline-flex items-center gap-1 rounded-full bg-green-600/10 px-2 py-0.5 text-xs font-medium text-green-500">
                        {file.algorithm}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          type="button"
                          onClick={() => downloadMutation.mutate(file.id)}
                          disabled={downloadMutation.isPending}
                          title="Download"
                          aria-label={`Download ${file.original_name}`}
                          className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-blue-400"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setRenameTarget({ id: file.id, name: file.original_name })
                            setNewName(file.original_name)
                          }}
                          title="Rename"
                          aria-label={`Rename ${file.original_name}`}
                          className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-slate-200"
                        >
                          <Pencil className="h-4 w-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => setDeleteTarget(file.id)}
                          title="Delete"
                          aria-label={`Delete ${file.original_name}`}
                          className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-red-400"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <span>Rows per page</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value))
                  setPage(1)
                }}
                className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-300 outline-none"
              >
                {[10, 25, 50].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
                aria-label="Previous page"
                className="rounded-lg border border-slate-700 p-2 text-slate-400 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-sm text-slate-400">
                {isFetching ? (
                  <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
                ) : (
                  `Page ${data.page} of ${totalPages || 1}`
                )}
              </span>
              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                aria-label="Next page"
                className="rounded-lg border border-slate-700 p-2 text-slate-400 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900 py-16 text-center">
          <FolderOpen className="mb-4 h-12 w-12 text-slate-600" />
          <h2 className="text-lg font-semibold text-slate-200">
            {debouncedSearch ? 'No matching files' : 'No files uploaded yet'}
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            {debouncedSearch
              ? 'Try a different search term.'
              : 'Upload your first secure file to get started.'}
          </p>
        </div>
      )}

      <Modal
        open={renameTarget !== null}
        title="Rename File"
        onClose={() => setRenameTarget(null)}
      >
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (renameTarget && newName.trim()) {
              renameMutation.mutate({ id: renameTarget.id, name: newName.trim() })
            }
          }}
          className="space-y-4"
        >
          <div>
            <label htmlFor="new-name" className="mb-1 block text-sm font-medium text-slate-300">
              New name
            </label>
            <input
              id="new-name"
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full rounded-lg border border-slate-600 bg-slate-900 py-2.5 px-3 text-sm text-slate-100 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-600/30"
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setRenameTarget(null)}
              className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={renameMutation.isPending || !newName.trim()}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:opacity-60"
            >
              {renameMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Save
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        open={deleteTarget !== null}
        title="Delete File"
        onClose={() => setDeleteTarget(null)}
      >
        <p className="text-sm text-slate-300">
          Are you sure you want to delete{' '}
          <span className="font-semibold text-slate-100">
            {data?.items.find((f) => f.id === deleteTarget)?.original_name}
          </span>
          ? This action cannot be undone.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <button
            type="button"
            onClick={() => setDeleteTarget(null)}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget)}
            disabled={deleteMutation.isPending}
            className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-500 disabled:opacity-60"
          >
            {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Delete
          </button>
        </div>
      </Modal>
    </div>
  )
}

