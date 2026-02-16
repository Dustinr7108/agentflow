import { useState, useCallback, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactFlow, {
  Controls, Background, MiniMap,
  addEdge, applyNodeChanges, applyEdgeChanges,
  Node, Edge, Connection, NodeChange, EdgeChange,
  BackgroundVariant,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { api } from '../store'
import AgentNode from '../components/AgentNode'
import {
  Play, Save, ArrowLeft, Plus, Settings, X,
  Brain, Search, Code, Globe, Shuffle, GitBranch,
  Loader2, CheckCircle, XCircle
} from 'lucide-react'

const nodeTypes = { agent: AgentNode }

const AGENT_TYPES = [
  { type: 'llm', name: 'LLM Agent', icon: Brain, color: 'blue' },
  { type: 'web_search', name: 'Web Search', icon: Search, color: 'green' },
  { type: 'code_exec', name: 'Code Runner', icon: Code, color: 'yellow' },
  { type: 'api_call', name: 'API Call', icon: Globe, color: 'purple' },
  { type: 'data_transform', name: 'Transform', icon: Shuffle, color: 'orange' },
  { type: 'conditional', name: 'Condition', icon: GitBranch, color: 'pink' },
]

export default function WorkflowEditor() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [nodes, setNodes] = useState<Node[]>([])
  const [edges, setEdges] = useState<Edge[]>([])
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [showAgentPanel, setShowAgentPanel] = useState(false)
  const [runResult, setRunResult] = useState<any>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [inputData, setInputData] = useState('{}')
  const nodeIdCounter = useRef(0)

  // Load workflow
  const { data: workflow } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => api(`/workflows/${id}`),
    enabled: !!id,
  })

  // Initialize nodes/edges from workflow data
  useEffect(() => {
    if (workflow?.graph) {
      const g = workflow.graph
      const flowNodes = (g.nodes || []).map((n: any) => ({
        id: n.id,
        type: 'agent',
        position: n.position || { x: 0, y: 0 },
        data: {
          label: n.objective?.slice(0, 40) || n.agent_type,
          agent_type: n.agent_type || 'llm',
          objective: n.objective || '',
          config_overrides: n.config_overrides || {},
          agent_def_id: n.agent_def_id || '',
        },
      }))
      const flowEdges = (g.edges || []).map((e: any, i: number) => ({
        id: `e-${i}`,
        source: e.source_id,
        target: e.target_id,
        sourceHandle: e.condition || undefined,
        label: e.condition || undefined,
        animated: true,
      }))
      setNodes(flowNodes)
      setEdges(flowEdges)
      nodeIdCounter.current = flowNodes.length
    }
  }, [workflow])

  const onNodesChange = useCallback((changes: NodeChange[]) => setNodes((n) => applyNodeChanges(changes, n)), [])
  const onEdgesChange = useCallback((changes: EdgeChange[]) => setEdges((e) => applyEdgeChanges(changes, e)), [])
  const onConnect = useCallback((conn: Connection) => setEdges((e) => addEdge({ ...conn, animated: true }, e)), [])

  const addNode = (agentType: string) => {
    const newId = `node-${++nodeIdCounter.current}`
    const newNode: Node = {
      id: newId,
      type: 'agent',
      position: { x: 200 + nodeIdCounter.current * 60, y: 200 },
      data: {
        label: agentType,
        agent_type: agentType,
        objective: '',
        config_overrides: {},
      },
    }
    setNodes((prev) => [...prev, newNode])
    setShowAgentPanel(false)
    setSelectedNode(newNode)
  }

  // Save workflow
  const saveMutation = useMutation({
    mutationFn: () => {
      const graph = {
        nodes: nodes.map((n) => ({
          id: n.id,
          agent_type: n.data.agent_type,
          agent_def_id: n.data.agent_def_id || '',
          objective: n.data.objective || '',
          position: n.position,
          config_overrides: n.data.config_overrides || {},
          stop_on_failure: true,
        })),
        edges: edges.map((e) => ({
          source_id: e.source,
          target_id: e.target,
          condition: e.sourceHandle || '',
        })),
      }
      return api(`/workflows/${id}`, {
        method: 'PUT',
        body: JSON.stringify({ graph }),
      })
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['workflow', id] }),
  })

  // Run workflow
  const runWorkflow = async () => {
    await saveMutation.mutateAsync()
    setIsRunning(true)
    setRunResult(null)
    try {
      let parsed = {}
      try { parsed = JSON.parse(inputData) } catch {}
      const result = await api(`/workflows/${id}/run`, {
        method: 'POST',
        body: JSON.stringify({ input_data: parsed }),
      })
      setRunResult(result)

      // Update node statuses
      if (result.node_results) {
        setNodes((prev) =>
          prev.map((n) => {
            const nr = result.node_results[n.id]
            if (nr) {
              return {
                ...n,
                data: { ...n.data, status: nr.status, duration_ms: nr.duration_ms },
              }
            }
            return n
          })
        )
      }
    } catch (err: any) {
      setRunResult({ status: 'error', error: err.message })
    } finally {
      setIsRunning(false)
    }
  }

  const updateNodeData = (key: string, value: any) => {
    if (!selectedNode) return
    setNodes((prev) =>
      prev.map((n) =>
        n.id === selectedNode.id
          ? { ...n, data: { ...n.data, [key]: value, label: key === 'objective' ? value.slice(0, 40) || n.data.agent_type : n.data.label } }
          : n
      )
    )
    setSelectedNode((prev) => prev ? { ...prev, data: { ...prev.data, [key]: value } } : null)
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="bg-gray-900 border-b border-gray-800 px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/')} className="text-gray-400 hover:text-white">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-lg font-semibold">{workflow?.name || 'Loading...'}</h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAgentPanel(true)}
            className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
          >
            <Plus className="w-4 h-4" /> Add Agent
          </button>
          <button
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
          >
            <Save className="w-4 h-4" /> Save
          </button>
          <button
            onClick={runWorkflow}
            disabled={isRunning || nodes.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium disabled:opacity-50"
          >
            {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            {isRunning ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Canvas */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, node) => setSelectedNode(node)}
            onPaneClick={() => setSelectedNode(null)}
            nodeTypes={nodeTypes}
            fitView
            deleteKeyCode={['Backspace', 'Delete']}
          >
            <Background variant={BackgroundVariant.Dots} color="#334155" gap={20} size={1} />
            <Controls />
            <MiniMap
              nodeColor={(n) => {
                const colors: Record<string, string> = {
                  llm: '#3b82f6', web_search: '#22c55e', code_exec: '#eab308',
                  api_call: '#a855f7', data_transform: '#f97316', conditional: '#ec4899',
                }
                return colors[n.data?.agent_type] || '#6b7280'
              }}
            />
          </ReactFlow>
        </div>

        {/* Agent palette */}
        {showAgentPanel && (
          <div className="w-72 bg-gray-900 border-l border-gray-800 p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Add Agent</h3>
              <button onClick={() => setShowAgentPanel(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-2">
              {AGENT_TYPES.map((at) => (
                <button
                  key={at.type}
                  onClick={() => addNode(at.type)}
                  className="w-full flex items-center gap-3 px-3 py-3 bg-gray-800 hover:bg-gray-700 rounded-lg text-left transition-colors"
                >
                  <at.icon className="w-5 h-5 text-gray-300" />
                  <span className="text-sm">{at.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Node config panel */}
        {selectedNode && !showAgentPanel && (
          <div className="w-80 bg-gray-900 border-l border-gray-800 p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2">
                <Settings className="w-4 h-4" /> Configure
              </h3>
              <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Type</label>
                <div className="text-sm text-gray-300 capitalize">{selectedNode.data.agent_type}</div>
              </div>

              <div>
                <label className="block text-xs text-gray-400 mb-1">Objective / Prompt</label>
                <textarea
                  value={selectedNode.data.objective || ''}
                  onChange={(e) => updateNodeData('objective', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500 resize-none"
                  placeholder="What should this agent do?"
                />
              </div>

              {selectedNode.data.agent_type === 'llm' && (
                <div>
                  <label className="block text-xs text-gray-400 mb-1">System Prompt</label>
                  <textarea
                    value={selectedNode.data.config_overrides?.system_prompt || ''}
                    onChange={(e) => updateNodeData('config_overrides', {
                      ...selectedNode.data.config_overrides,
                      system_prompt: e.target.value,
                    })}
                    rows={3}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500 resize-none"
                    placeholder="System instructions..."
                  />
                </div>
              )}

              {selectedNode.data.agent_type === 'api_call' && (
                <>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">URL</label>
                    <input
                      value={selectedNode.data.config_overrides?.url || ''}
                      onChange={(e) => updateNodeData('config_overrides', {
                        ...selectedNode.data.config_overrides,
                        url: e.target.value,
                      })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                      placeholder="https://api.example.com/data"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Method</label>
                    <select
                      value={selectedNode.data.config_overrides?.method || 'GET'}
                      onChange={(e) => updateNodeData('config_overrides', {
                        ...selectedNode.data.config_overrides,
                        method: e.target.value,
                      })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                    >
                      <option>GET</option>
                      <option>POST</option>
                      <option>PUT</option>
                      <option>DELETE</option>
                    </select>
                  </div>
                </>
              )}

              {selectedNode.data.agent_type === 'conditional' && (
                <>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Field to Check</label>
                    <input
                      value={selectedNode.data.config_overrides?.field || ''}
                      onChange={(e) => updateNodeData('config_overrides', {
                        ...selectedNode.data.config_overrides,
                        field: e.target.value,
                      })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                      placeholder="e.g. output.count"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Operator</label>
                    <select
                      value={selectedNode.data.config_overrides?.operator || 'eq'}
                      onChange={(e) => updateNodeData('config_overrides', {
                        ...selectedNode.data.config_overrides,
                        operator: e.target.value,
                      })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm"
                    >
                      <option value="eq">Equals</option>
                      <option value="ne">Not Equals</option>
                      <option value="gt">Greater Than</option>
                      <option value="gte">Greater or Equal</option>
                      <option value="lt">Less Than</option>
                      <option value="lte">Less or Equal</option>
                      <option value="contains">Contains</option>
                      <option value="is_empty">Is Empty</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Value</label>
                    <input
                      value={selectedNode.data.config_overrides?.value || ''}
                      onChange={(e) => updateNodeData('config_overrides', {
                        ...selectedNode.data.config_overrides,
                        value: e.target.value,
                      })}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                      placeholder="Expected value"
                    />
                  </div>
                </>
              )}

              {/* Results */}
              {selectedNode.data.status && (
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Result</label>
                  <div className={`text-sm ${
                    selectedNode.data.status === 'completed' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {selectedNode.data.status}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Run results panel */}
        {runResult && !selectedNode && !showAgentPanel && (
          <div className="w-80 bg-gray-900 border-l border-gray-800 p-4 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold flex items-center gap-2">
                {runResult.status === 'completed' ? (
                  <CheckCircle className="w-4 h-4 text-green-400" />
                ) : (
                  <XCircle className="w-4 h-4 text-red-400" />
                )}
                Run Result
              </h3>
              <button onClick={() => setRunResult(null)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Status</span>
                <span className={runResult.status === 'completed' ? 'text-green-400' : 'text-red-400'}>
                  {runResult.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Duration</span>
                <span>{runResult.duration_ms}ms</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Tokens</span>
                <span>{runResult.total_tokens}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cost</span>
                <span>${runResult.total_cost_usd}</span>
              </div>

              {runResult.output_data && (
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Output</label>
                  <pre className="bg-gray-800 rounded-lg p-3 text-xs overflow-auto max-h-64 whitespace-pre-wrap">
                    {typeof runResult.output_data === 'string'
                      ? runResult.output_data
                      : JSON.stringify(runResult.output_data, null, 2)}
                  </pre>
                </div>
              )}

              {runResult.error && (
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-3 text-xs text-red-300">
                  {runResult.error}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Input data bar */}
      <div className="bg-gray-900 border-t border-gray-800 px-4 py-2 flex items-center gap-4 shrink-0">
        <span className="text-xs text-gray-400">Input Data (JSON):</span>
        <input
          value={inputData}
          onChange={(e) => setInputData(e.target.value)}
          className="flex-1 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm font-mono focus:outline-none focus:border-blue-500"
          placeholder='{"topic": "AI trends", "industry": "healthcare"}'
        />
      </div>
    </div>
  )
}
