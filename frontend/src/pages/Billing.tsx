import { useQuery, useMutation } from '@tanstack/react-query'
import { api, useAuthStore } from '../store'
import { CreditCard, Zap, TrendingUp, CheckCircle, Loader2, BarChart3, DollarSign } from 'lucide-react'

const PLANS = [
  {
    id: 'free', name: 'Free', price: '$0', period: '/month', runs: 10,
    features: ['10 workflow runs/month', '6 agent types', 'Visual editor', 'Community support'],
  },
  {
    id: 'starter', name: 'Starter', price: '$29', period: '/month', runs: 100,
    features: ['100 runs/month', 'All agent types', 'Template gallery', 'Email support', 'Scheduled workflows'],
  },
  {
    id: 'pro', name: 'Pro', price: '$99', period: '/month', runs: 1000, popular: true,
    features: ['1,000 runs/month', 'Priority execution', 'Webhook triggers', 'Advanced analytics', 'Priority support'],
  },
  {
    id: 'enterprise', name: 'Enterprise', price: '$299', period: '/month', runs: 10000,
    features: ['10,000 runs/month', 'Custom integrations', 'Dedicated support', 'SLA guarantee', 'SSO/SAML'],
  },
]

export default function Billing() {
  const { user } = useAuthStore()

  const { data: usage, isLoading } = useQuery({
    queryKey: ['usage'],
    queryFn: () => api('/billing/usage'),
  })

  const checkoutMutation = useMutation({
    mutationFn: (plan: string) => api(`/billing/checkout?plan=${plan}`, { method: 'POST' }),
    onSuccess: (data) => {
      if (data?.checkout_url) window.location.href = data.checkout_url
    },
  })

  const pct = usage ? Math.min(100, (usage.runs_this_month / usage.runs_limit) * 100) : 0

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">Billing & Usage</h1>
      <p className="text-gray-400 mb-8">Manage your plan and track usage</p>

      {isLoading ? (
        <div className="flex items-center gap-2 text-gray-400 mb-8">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading usage...
        </div>
      ) : usage && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2"><Zap className="w-4 h-4" /> Runs This Month</div>
            <div className="text-2xl font-bold">{usage.runs_this_month}</div>
            <div className="text-xs text-gray-500 mt-1">of {usage.runs_limit} limit</div>
            <div className="mt-3 h-1.5 bg-gray-800 rounded-full">
              <div className={`h-full rounded-full ${pct > 80 ? 'bg-red-500' : pct > 60 ? 'bg-yellow-500' : 'bg-blue-500'}`} style={{ width: `${pct}%` }} />
            </div>
          </div>
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2"><BarChart3 className="w-4 h-4" /> Total Tokens</div>
            <div className="text-2xl font-bold">{usage.total_tokens.toLocaleString()}</div>
            <div className="text-xs text-gray-500 mt-1">all time</div>
          </div>
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2"><DollarSign className="w-4 h-4" /> Total Spend</div>
            <div className="text-2xl font-bold">${usage.total_cost_usd?.toFixed(2)}</div>
            <div className="text-xs text-gray-500 mt-1">all time</div>
          </div>
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <div className="flex items-center gap-2 text-gray-400 text-sm mb-2"><TrendingUp className="w-4 h-4" /> Current Plan</div>
            <div className="text-2xl font-bold capitalize">{usage.plan}</div>
            <div className="text-xs text-gray-500 mt-1">{usage.runs_limit} runs/month</div>
          </div>
        </div>
      )}

      <h2 className="text-lg font-semibold mb-4">Plans</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {PLANS.map((plan: any) => {
          const isCurrent = user?.plan === plan.id
          return (
            <div key={plan.id} className={`relative bg-gray-900 rounded-xl p-6 border ${plan.popular ? 'border-purple-500' : isCurrent ? 'border-blue-500' : 'border-gray-800'}`}>
              {plan.popular && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-purple-600 text-white text-xs px-3 py-1 rounded-full font-medium">Most Popular</div>}
              {isCurrent && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-medium">Current</div>}
              <h3 className="font-bold text-lg mb-1">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className="text-gray-400 text-sm">{plan.period}</span>
              </div>
              <ul className="space-y-2 mb-6">
                {plan.features.map((f: string) => (
                  <li key={f} className="flex items-start gap-2 text-sm text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-400 shrink-0 mt-0.5" />{f}
                  </li>
                ))}
              </ul>
              {isCurrent ? (
                <button disabled className="w-full py-2 rounded-lg bg-gray-700 text-gray-400 text-sm cursor-not-allowed">Current Plan</button>
              ) : plan.id === 'free' ? (
                <button disabled className="w-full py-2 rounded-lg bg-gray-800 text-gray-500 text-sm cursor-not-allowed">Free</button>
              ) : (
                <button
                  onClick={() => checkoutMutation.mutate(plan.id)}
                  disabled={checkoutMutation.isPending}
                  className="w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {checkoutMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <CreditCard className="w-4 h-4" />}
                  Upgrade
                </button>
              )}
            </div>
          )
        })}
      </div>

      {new URLSearchParams(window.location.search).get('success') === 'true' && (
        <div className="mt-6 p-4 bg-green-900/20 border border-green-700 rounded-xl text-green-300 flex items-center gap-2">
          <CheckCircle className="w-5 h-5" /> Payment successful! Your plan has been upgraded.
        </div>
      )}
      {new URLSearchParams(window.location.search).get('canceled') === 'true' && (
        <div className="mt-6 p-4 bg-yellow-900/20 border border-yellow-700 rounded-xl text-yellow-300">
          Payment canceled. Your plan was not changed.
        </div>
      )}
    </div>
  )
}
