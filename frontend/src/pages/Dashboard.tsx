import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../store'
import { Plus, Play, Clock, CheckCircle, XCircle, Trash2 } from 'lucide-react'

export default function Dashboard() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')

  const { data: workflows = [], isLoading } = useQuery({
    queryKey: ['workflows'],
    queryFn: () => api('/workflows/'),
  })

  const createMutation = useMutation({
    mutationFn: (name: string) =>
      api('/workflows/', { method: 'POST', body: JSON.stringify({ name, description: '' }) }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] })
      navigate(`/workflow/${data.id}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api(`/workflows/${id}`, { method: 'DELETE' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workflows'] }),
  })

  const handleCreate = () => {
    if (!newName.trim()) return
    createMutation.mutate(newName.trim())
    setNewName('')
    setShowCreate(false)
  }

  const statusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />
      case 'running': return <Play className="w-4 h-4 text-blue-400 animate-pulse" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Workflows</h1>
          <p className="text-gray-400 mt-1">Design and run AI agent workflows</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors"
        >
          <Plus className="w-5 h-5" /> New Workflow
        </button>
      </div>

      {/* Create modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Create New Workflow</h2>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
              placeholder="Workflow name..."
              className="w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 text-white mb-4"
              autoFocus
            />
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowCreate(false)} className="px-4 py-2 text-gray-400 hover:text-white">
                Cancel
              </button>
              <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg">
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Workflow grid */}
      {isLoading ? (
        <div className="text-gray-400">Loading workflows...</div>
      ) : workflows.length === 0 ? (
        <div className="text-center py-20">
          <div className="text-gray-500 text-6xl mb-4">&#x1F680;</div>
          <h2 className="text-xl text-gray-300 mb-2">No workflows yet</h2>
          <p className="text-gray-500 mb-6">Create your first AI workflow or start from a template</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => setShowCreate(true)}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium"
            >
              Create Workflow
            </button>
            <button
              onClick={() => navigate('/templates')}
              className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg font-medium border border-gray-700"
            >
              Browse Templates
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.map((wf: any) => (
            <div
              key={wf.id}
              className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors cursor-pointer group"
              onClick={() => navigate(`/workflow/${wf.id}`)}
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="text-lg font-medium group-hover:text-blue-400 transition-colors">
                  {wf.name}
                </h3>
                <button
                  onClick={(e) => { e.stopPropagation(); deleteMutation.mutate(wf.id) }}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                {wf.description || 'No description'}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{wf.graph?.nodes?.length || 0} agents</span>
                <span>{new Date(wf.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
