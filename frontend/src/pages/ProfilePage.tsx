import { useCallback, useState } from 'react'
import { KeyRound, Save, UserRound } from 'lucide-react'

import { useAuth } from '@/context/AuthContext'
import { useToast } from '@/context/ToastContext'
import * as usersService from '@/services/users'
import { getErrorMessage } from '@/utils/errors'

const inputClass =
  'w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30'

export default function ProfilePage() {
  const { user, updateUser } = useAuth()
  const { toast } = useToast()
  const [name, setName] = useState(user?.name ?? '')
  const [savingName, setSavingName] = useState(false)

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [changingPassword, setChangingPassword] = useState(false)

  const handleSaveName = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      const trimmed = name.trim()
      if (trimmed.length < 2) {
        toast('Name must be at least 2 characters.', 'error')
        return
      }
      setSavingName(true)
      try {
        const updated = await usersService.updateProfile(trimmed)
        updateUser(updated)
        toast('Profile updated.', 'success')
      } catch (err) {
        toast(getErrorMessage(err), 'error')
      } finally {
        setSavingName(false)
      }
    },
    [name, toast, updateUser],
  )

  const handleChangePassword = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      if (newPassword.length < 8) {
        toast('New password must be at least 8 characters.', 'error')
        return
      }
      if (newPassword !== confirmPassword) {
        toast('New passwords do not match.', 'error')
        return
      }
      setChangingPassword(true)
      try {
        await usersService.changePassword(currentPassword, newPassword)
        toast('Password changed.', 'success')
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
      } catch (err) {
        toast(getErrorMessage(err), 'error')
      } finally {
        setChangingPassword(false)
      }
    },
    [currentPassword, newPassword, confirmPassword, toast],
  )

  return (
    <div className="mx-auto max-w-6xl">
      <h1 className="text-2xl font-bold text-slate-100">Profile</h1>
      <p className="mt-1 text-sm text-slate-400">Manage your account details and password.</p>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="flex items-center gap-2">
            <UserRound className="h-5 w-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-slate-100">Account details</h2>
          </div>

          <form onSubmit={handleSaveName} className="mt-5 space-y-4">
            <div>
              <label htmlFor="profile-name" className="mb-1 block text-sm font-medium text-slate-300">
                Name
              </label>
              <input
                id="profile-name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                maxLength={255}
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="profile-email" className="mb-1 block text-sm font-medium text-slate-300">
                Email
              </label>
              <input id="profile-email" type="email" value={user?.email ?? ''} disabled className={`${inputClass} opacity-60`} />
              <p className="mt-1 text-xs text-slate-500">Email cannot be changed.</p>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-300">Member since</label>
              <p className="text-sm text-slate-400">
                {user
                  ? new Date(user.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
                  : '—'}
              </p>
            </div>
            <button
              type="submit"
              disabled={savingName}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              {savingName ? 'Saving…' : 'Save changes'}
            </button>
          </form>
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6">
          <div className="flex items-center gap-2">
            <KeyRound className="h-5 w-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-slate-100">Change password</h2>
          </div>

          <form onSubmit={handleChangePassword} className="mt-5 space-y-4">
            <div>
              <label htmlFor="current-password" className="mb-1 block text-sm font-medium text-slate-300">
                Current password
              </label>
              <input
                id="current-password"
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                autoComplete="current-password"
                className={inputClass}
              />
            </div>
            <div>
              <label htmlFor="new-password" className="mb-1 block text-sm font-medium text-slate-300">
                New password
              </label>
              <input
                id="new-password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                maxLength={72}
                className={inputClass}
              />
              <p className="mt-1 text-xs text-slate-500">At least 8 characters, max 72.</p>
            </div>
            <div>
              <label htmlFor="confirm-password" className="mb-1 block text-sm font-medium text-slate-300">
                Confirm new password
              </label>
              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                autoComplete="new-password"
                className={inputClass}
              />
            </div>
            <button
              type="submit"
              disabled={changingPassword}
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <KeyRound className="h-4 w-4" />
              {changingPassword ? 'Changing…' : 'Change password'}
            </button>
          </form>
        </section>
      </div>
    </div>
  )
}
