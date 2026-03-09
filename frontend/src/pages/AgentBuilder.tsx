import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../store'
import {
  Brain, Search, Code, Globe, Shuffle, GitBranch,
  Plus, Pencil, Trash2, X, Save, Loader2
} from 'lucide-react'

const AGENT_TYPES = [
  { type: 'llm', name: 'LLM Agent', icon: Brain },
  { type: 'web_search', name: 'Web Search', icon: Search },
  { type: 'code_exec', name: 'Code Runner', icon: Code },
  { type: 'api_call', name: 'API Call', icon: Globe },
  { type: 'data_transform', name: 'Transform', icon: Shuffle },
  { type: 'conditional', name: 'Conditional', icon: GitBranch },
]

const ICON_MAP: Record<string, any> = {
  llm: Brain, web_search: Search, code_exec: Code,
  api_call: Globe, data_transform: Shuffle, conditional: GitBranch,
}

const DEFAULT_CONFIGS: Record<string, object> = {
  llm: { model: 'gpt-4o-mini', temperature: 0.7, max_tokens: 1000 },
  web_search: { max_results: 5 },
  code_exec: { timeout: 30 },
  api_call: { url: '', method: 'GET', headers: {} },
  data_transform: { operation: 'passthrough' },
  conditional: { field: '', operator: 'eq', value: '' },
}

export default function AgentBuilder() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState({
    name: '', description: '', agent_type: 'llm',
    config: JSON.stringify(DEFAULT_CONFIGS.llm, null, 2),
  })
  const [configError, setConfigError] = useState('')

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api('/agents/'),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => api('/agents/', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['agents'] }); resetForm() },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: any) => api(`/agents/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['agents'] }); resetForm() },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api(`/agents/${id}`, { method: 'DELETE' }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['agents'] }),
  })

  const resetForm = () => {
    setShowForm(false); setEditingId(null)
    setForm({ name: '', description: '', agent_type: 'llm', config: JSON.stringify(DEFAULT_CONFIGS.llm, null, 2) })
    setConfigError('')
  }

  const startEdit = (agent: any) => {
    setEditingId(agent.id)
    setForm({ name: agent.name, description: agent.description, agent_type: agent.agent_type, config: JSON.stringify(agent.config, null, 2) })
    setShowForm(true)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault(); setConfigError('')
    let config: object
    try { config = JSON.parse(form.config) } catch { setConfigError('Invalid JSON'); return }
    const payload = { name: form.name, description: form.description, agent_type: form.agent_type, config }
    if (editingId) updateMutation.mutate({ id: editingId, data: payload })
    else createMutation.mutate(payload)
  }

  const userAgents = (agents || []).filter((a: any) =>!a.is_builtin)
  const builtinAgents = (agents || []).filter((a: any) => a.is_builtin)
  const isPending = createMutation.isPending || updateMutation.isPending
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">Agent Builder</h1>
          <p className="text-gray-400">Create reusable custom agents for your workflows</p>
        </div>
        <button onClick={() => { resetForm(); setShowForm(true) }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium">
          <Plus className="w-4 h-4" /> New Agent
        </button>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl border border-gray-800 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-800">
              <h2 className="text-lg font-semibold">{editingId ? 'Edit Agent' : 'New Agent'}</h2>
              <button onClick={resetForm} className="text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Agent Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {AGENT_TYPES.map((at) => (
                    <button key={at.type} type="button"
                      onClick={() => setForm(f => ({ ...f, agent_type: at.type, config: JSON.stringify(DEFAULT_CONFIGS[at.type] || {}, null, 2) }))}
                      className={`flex items-center gap-2 p-3 rounded-lg border text-sm ${form.agent_type === at.type ? 'border-blue-500 bg-blue-950/30' : 'border-gray-700 hover:border-gray-600'}`}>
                      <at.icon className="w-4 h-4" />{at.name}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Name</label>
                <input value={form.name} onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))} required
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500" placeholder="My Agent" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <input value={form.description} onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500" placeholder="What does this agent do?" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Config (JSON)</label>
                <textarea value={form.config} onChange={(e) => setForm(f => ({ ...f, config: e.target.value }))} rows={7}
                  className={`w-full px-3 py-2 bg-gray-800 border rounded-lg text-sm font-mono focus:outline-none resize-none ${configError ? 'border-red-500' : 'border-gray-700 focus:border-blue-500'}`} />
                {configError && <p className="text-red-400 text-xs mt-1">{configError}</p>}
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={resetForm} className="px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 rounded-lg">Cancel</button>
                <button type="submit" disabled={isPending}
                  className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 rounded-lg font-medium disabled:opacity-50">
                  {isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  {editingId ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      <h2 className="text-base font-semibold text-gray-300 mb-3">Your Custom Agents ({userAgents.length})</h2>
      {isLoading ? (
        <div className="flex items-center gap-2 text-gray-400 mb-6"><Loader2 className="w-4 h-4 animate-spin" /> Loading...</div>
      ) : userAgents.length === 0 ? (
        <div className="text-center py-10 bg-gray-900 rounded-xl border border-dashed border-gray-700 mb-6">
          <p className="text-gray-500 mb-3">No custom agents yet</p>
          <button onClick={() => { resetForm(); setShowForm(true) }} className="text-sm text-blue-400 hover:text-blue-300">Create your first agent</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
          {userAgents.map((agent: any) => {
            const Icon = ICON_MAP[agent.agent_type] || Brain
            return (
              <div key={agent.id} className="bg-gray-900 rounded-xl border border-gray-800 p-4 flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-gray-800 rounded-lg"><Icon className="w-4 h-4 text-gray-300" /></div>
                  <div>
                    <div className="font-medium text-sm">{agent.name}</div>
                    <div className="text-xs text-gray-400 capitalize">{agent.agent_type.replace('_', ' ')}</div>
                    {agent.description && <div className="text-xs text-gray-500 mt-1">{agent.description}</div>}
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => startEdit(agent)} className="p-1.5 text-gray-400 hover:text-blue-400 rounded"><Pencil className="w-3.5 h-3.5" /></button>
                  <button onClick={() => { if (confirm('Delete this agent?')) deleteMutation.mutate(agent.id) }} className="p-1.5 text-gray-400 hover:text-red-400 rounded"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
            )
          })}
        </div>
      )}
      <h2 className="text-base font-semibold text-gray-300 mb-3">Built-in Agents ({builtinAgents.length})</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {builtinAgents.map((agent: any) => {
          const Icon = ICON_MAP[agent.agent_type] || Brain
          return (
            <div key={agent.id} className="bg-gray-900 rounded-xl border border-gray-800/50 p-4 flex items-start gap-3 opacity-80">
              <div className="p-2 bg-gray-800 rounded-lg"><Icon className="w-4 h-4 text-gray-400" /></div>
              <div>
                <div className="font-medium text-sm">{agent.name}</div>
                <div className="text-xs text-gray-400 capitalize">{agent.agent_type.replace('_', ' ')}</div>
                {agent.description && <div className="text-xs text-gray-500 mt-1">{agent.description}</div>}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
