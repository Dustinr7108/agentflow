import { Outlet, Link, useNavigate, Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store'
import { Workflow, LayoutTemplate, LogOut, Zap, CreditCard, Settings, Bot } from 'lucide-react'

const NAV_ITEMS = [
  { to: '/', icon: Workflow, label: 'Workflows' },
  { to: '/templates', icon: LayoutTemplate, label: 'Templates' },
  { to: '/agents', icon: Bot, label: 'Agent Builder' },
  { to: '/billing', icon: CreditCard, label: 'Billing' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="min-h-screen bg-gray-950 flex">
      <nav className="w-64 bg-gray-900 border-r border-gray-800 p-4 flex flex-col">
        <div className="flex items-center gap-2 mb-8 px-2">
          <Zap className="w-8 h-8 text-blue-500" />
          <span className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AgentFlow
          </span>
        </div>

        <div className="space-y-1 flex-1">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => {
            const active = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  active ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                {label}
              </Link>
            )
          })}
        </div>

        <div className="border-t border-gray-800 pt-4">
          <div className="px-3 py-2 text-sm text-gray-400">
            <div className="font-medium text-gray-300 truncate">{user.name || user.email}</div>
            <div className="text-xs capitalize">{user.plan} plan</div>
            <div className="text-xs">{user.runs_this_month} runs this month</div>
          </div>
          <button
            onClick={() => { logout(); navigate('/login') }}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-red-400 transition-colors w-full"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </nav>

      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
