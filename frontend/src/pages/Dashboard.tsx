import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'
import {
  Clock,
  Database,
  FileStack,
  FolderOpen,
  ShieldCheck,
  UploadCloud,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import api from '@/services/api'
import type { ApiEnvelope } from '@/types'
import { formatBytes } from '@/utils/helpers'

interface DashboardStats {
  total_files: number
  total_size: number
  last_upload_at: string | null
  algorithm: string
}

function StatCard({
  icon: Icon,
  label,
  value,
  sub,
}: {
  icon: typeof Database
  label: string
  value: string
  sub?: string
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/15 text-blue-400">
        <Icon className="h-5 w-5" />
      </div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-slate-100">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data } = await api.get<ApiEnvelope<DashboardStats>>('/dashboard/stats')
      return data.data as DashboardStats
    },
  })

  const firstName = user?.name.split(' ')[0] ?? 'there'

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Welcome back, {firstName}</h1>
        <p className="mt-1 text-sm text-slate-400">
          Your files are encrypted with AES-256-GCM and only you can access them.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          icon={FileStack}
          label="Total Files"
          value={isLoading ? '...' : String(data?.total_files ?? 0)}
        />
        <StatCard
          icon={Database}
          label="Storage Used"
          value={isLoading ? '...' : formatBytes(data?.total_size ?? 0)}
          sub="Encrypted at rest"
        />
        <StatCard
          icon={Clock}
          label="Last Upload"
          value={
            isLoading
              ? '...'
              : data?.last_upload_at
                ? new Date(data.last_upload_at).toLocaleDateString()
                : 'Never'
          }
        />
        <StatCard
          icon={ShieldCheck}
          label="Encryption"
          value={isLoading ? '...' : (data?.algorithm ?? 'AES-256-GCM')}
          sub="Authenticated encryption"
        />
      </div>

      {!isLoading && data?.total_files === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900 py-16 text-center">
          <FolderOpen className="mb-4 h-12 w-12 text-slate-600" />
          <h2 className="text-lg font-semibold text-slate-200">No files uploaded yet</h2>
          <p className="mt-1 text-sm text-slate-500">
            Upload your first secure file to get started.
          </p>
          <Link
            to="/upload"
            className="mt-6 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            <UploadCloud className="h-4 w-4" />
            Upload File
          </Link>
        </div>
      )}
    </div>
  )
}
