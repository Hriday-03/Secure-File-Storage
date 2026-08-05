import { NavLink } from 'react-router'
import { Clock, FolderOpen, LayoutDashboard, ShieldCheck, UploadCloud, UserCircle } from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/upload', label: 'Upload', icon: UploadCloud, end: false },
  { to: '/files', label: 'My Files', icon: FolderOpen, end: false },
  { to: '/recent', label: 'Recent Files', icon: Clock, end: false },
  { to: '/profile', label: 'Profile', icon: UserCircle, end: false },
]

export default function Sidebar() {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-slate-800 bg-slate-900">
      <div className="flex h-16 items-center gap-2 border-b border-slate-800 px-6">
        <ShieldCheck className="h-6 w-6 text-blue-500" />
        <span className="text-sm font-bold text-slate-100">Secure Files</span>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-600/15 text-blue-400'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
              }`
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
