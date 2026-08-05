import { useState } from 'react'
import { useAuth } from '@/context/AuthContext'

export default function UserMenu() {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)

  if (!user) return null
  const initials = user.name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex items-center gap-2 rounded-full p-1 transition hover:bg-slate-700/60"
      >
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
          {initials}
        </span>
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} aria-hidden="true" />
          <div
            role="menu"
            className="absolute right-0 z-20 mt-2 w-56 rounded-xl border border-slate-700 bg-slate-800 py-2 shadow-xl"
          >
            <div className="border-b border-slate-700 px-4 py-3">
              <p className="truncate text-sm font-semibold text-slate-100">{user.name}</p>
              <p className="truncate text-xs text-slate-400">{user.email}</p>
            </div>
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setOpen(false)
                void logout()
              }}
              className="w-full px-4 py-2 text-left text-sm text-red-400 transition hover:bg-slate-700/60"
            >
              Logout
            </button>
          </div>
        </>
      )}
    </div>
  )
}
