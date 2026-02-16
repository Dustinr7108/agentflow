import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../store'
import {
  Megaphone, PenTool, BarChart, Database, Bell,
  ArrowRight, Copy
} from 'lucide-react'

const CATEGORY_ICONS: Record<string, any> = {
  marketing: Megaphone,
  content: PenTool,
  business: BarChart,
  data: Database,
  automation: Bell,
}

const CATEGORY_COLORS: Record<string, string> = {
  marketing: 'text-green-400 bg-green-900/30',
  content: 'text-blue-400 bg-blue-900/30',
  business: 'text-purple-400 bg-purple-900/30',
  data: 'text-orange-400 bg-orange-900/30',
  automation: 'text-pink-400 bg-pink-900/30',
}

export default function Templates() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: templates = [], isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => api('/templates/'),
  })

  const createFromTemplate = useMutation({
    mutationFn: (template: any) =>
      api('/workflows/', {
        method: 'POST',
        body: JSON.stringify({
          name: template.name,
          description: template.description,
          graph: template.graph,
        }),
      }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      navigate(`/workflow/${data.id}`)
    },
  })

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Templates</h1>
        <p className="text-gray-400 mt-1">Start with a pre-built workflow and customize it</p>
      </div>

      {isLoading ? (
        <div className="text-gray-400">Loading templates...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((tmpl: any) => {
            const Icon = CATEGORY_ICONS[tmpl.category] || BarChart
            const colorClass = CATEGORY_COLORS[tmpl.category] || 'text-gray-400 bg-gray-900/30'

            return (
              <div
                key={tmpl.id}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-all group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-2 rounded-lg ${colorClass}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-xs text-gray-500 capitalize px-2 py-1 bg-gray-800 rounded-full">
                    {tmpl.category}
                  </span>
                </div>

                <h3 className="text-lg font-medium mb-2">{tmpl.name}</h3>
                <p className="text-sm text-gray-400 mb-4 line-clamp-2">{tmpl.description}</p>

                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">{tmpl.agent_count} agents</span>
                  <button
                    onClick={() => createFromTemplate.mutate(tmpl)}
                    disabled={createFromTemplate.isPending}
                    className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                    Use Template
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
