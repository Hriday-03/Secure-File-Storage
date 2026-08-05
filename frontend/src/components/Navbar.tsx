import { Menu, Search, ShieldCheck } from 'lucide-react'
import UserMenu from '@/components/UserMenu'

interface NavbarProps {
  onMenuClick: () => void
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-slate-800 bg-slate-900/95 px-4 backdrop-blur">
      <button
        type="button"
        onClick={onMenuClick}
        aria-label="Toggle sidebar"
        className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-slate-200 lg:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex items-center gap-2 lg:hidden">
        <ShieldCheck className="h-6 w-6 text-blue-500" />
        <span className="text-sm font-bold text-slate-100">Secure Files</span>
      </div>

      <div className="relative mx-auto w-full max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          type="search"
          placeholder="Search files..."
          className="w-full rounded-lg border border-slate-700 bg-slate-800 py-2 pl-10 pr-3 text-sm text-slate-100 placeholder-slate-500 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-600/30"
        />
      </div>

      <div className="ml-auto">
        <UserMenu />
      </div>
    </header>
  )
}
