import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api, useAuthStore } from '../store'
import { User, Lock, Save, Loader2, CheckCircle, AlertCircle } from 'lucide-react'

export default function Settings() {
  const { user, setAuth } = useAuthStore()
  const queryClient = useQueryClient()

  const [name, setName] = useState(user?.name || '')
  const [currentPw, setCurrentPw] = useState('')
  const [newPw, setNewPw] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const profileMutation = useMutation({
    mutationFn: (data: any) => api('/auth/me', { method: 'PUT', body: JSON.stringify(data) }),
    onSuccess: (updatedUser) => {
      const token = localStorage.getItem('token') || ''
      setAuth(token, updatedUser)
      setSuccess('Profile updated successfully')
      setError('')
      setCurrentPw('')
      setNewPw('')
      setConfirmPw('')
      setTimeout(() => setSuccess(''), 3000)
    },
    onError: (err: any) => {
      setError(err.message || 'Update failed')
      setSuccess('')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (newPw && newPw !== confirmPw) {
      setError('New passwords do not match')
      return
    }
    if (newPw && newPw.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    const payload: any = { name }
    if (newPw) {
      payload.current_password = currentPw
      payload.new_password = newPw
    }

    profileMutation.mutate(payload)
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Settings</h1>
      <p className="text-gray-400 mb-8">Manage your account</p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Profile section */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <User className="w-5 h-5 text-blue-400" /> Profile
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Email</label>
              <input
                value={user?.email || ''}
                disabled
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-gray-400 cursor-not-allowed"
              />
              <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Display Name</label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                placeholder="Your name"
              />
            </div>
          </div>
        </div>

        {/* Password section */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Lock className="w-5 h-5 text-purple-400" /> Change Password
          </h2>
          <p className="text-sm text-gray-400 mb-4">Leave blank to keep your current password</p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Current Password</label>
              <input
                type="password"
                value={currentPw}
                onChange={(e) => setCurrentPw(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                placeholder="Enter current password"
                autoComplete="current-password"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">New Password</label>
              <input
                type="password"
                value={newPw}
                onChange={(e) => setNewPw(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                placeholder="New password (min 8 chars)"
                autoComplete="new-password"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Confirm New Password</label>
              <input
                type="password"
                value={confirmPw}
                onChange={(e) => setConfirmPw(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                placeholder="Confirm new password"
                autoComplete="new-password"
              />
            </div>
          </div>
        </div>

        {/* Account info */}
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
          <h2 className="text-lg font-semibold mb-4">Account Info</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Plan</span>
              <span className="capitalize font-medium">{user?.plan}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Runs this month</span>
              <span>{user?.runs_this_month}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Member since</span>
              <span>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : '-'}</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-900/20 border border-red-800 rounded-lg text-red-300 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}
        {success && (
          <div className="flex items-center gap-2 p-3 bg-green-900/20 border border-green-700 rounded-lg text-green-300 text-sm">
            <CheckCircle className="w-4 h-4 shrink-0" /> {success}
          </div>
        )}

        <button
          type="submit"
          disabled={profileMutation.isPending}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium text-sm disabled:opacity-50"
        >
          {profileMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Save Changes
        </button>
      </form>
    </div>
  )
}
