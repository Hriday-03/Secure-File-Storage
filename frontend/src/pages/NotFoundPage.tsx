import { Link } from 'react-router'
import { FileQuestion } from 'lucide-react'

export default function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <FileQuestion className="h-16 w-16 text-slate-600" />
      <h1 className="mt-6 text-4xl font-bold text-slate-100">404</h1>
      <p className="mt-2 text-sm text-slate-400">The page you are looking for does not exist.</p>
      <Link
        to="/"
        className="mt-6 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
      >
        Back to Dashboard
      </Link>
    </div>
  )
}