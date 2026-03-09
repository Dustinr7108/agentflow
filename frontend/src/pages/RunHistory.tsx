import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../store'
import {
  ArrowLeft, CheckCircle, XCircle, Clock, Zap, DollarSign,
  ChevronDown, ChevronRight, Loader2
} from 'lucide-react'

export default function RunHistory() {
  const { id } = useParams<{ id: string }>()
  const [expandedRun, setExpandedRun] = useState<string | null>(null)

  const { data: workflow } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => api(`/workflows/${id}`),
    enabled: !!id,
  })

  const { data: runs, isLoading } = useQuery({
    queryKey: ['runs', id],
    queryFn: () => api(`/workflows/${id}/runs?limit=50`),
    enabled: !!id,
    refetchInterval: 10000,
  })

  const StatusIcon = ({ status }: { status: string }) => {
    if (status === 'completed') return <CheckCircle className="w-4 h-4 text-green-400" />
    if (status === 'failed') return <XCircle className="w-4 h-4 text-red-400" />
    return <Clock className="w-4 h-4 text-yellow-400" />
  }

  const formatDate = (s: string) => {
    try { return new Date(s).toLocaleString() } catch { return s }
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Link to={`/workflow/${id}`} className="text-gray-400 hover:text-white">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold">{workflow?.name || 'Workflow'}</h1>
          <p className="text-gray-400 text-sm">Run History</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center gap-2 text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" /> Loading runs...
        </div>
      ) : !runs?.length ? (
        <div className="text-center py-16 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No runs yet. Open the workflow editor and click Run.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {runs.map((run: any) => (
            <div key={run.id} className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
              <button
                className="w-full flex items-center justify-between p-4 hover:bg-gray-800/50 transition-colors"
                onClick={() => setExpandedRun(expandedRun === run.id ? null : run.id)}
              >
                <div className="flex items-center gap-3">
                  <StatusIcon status={run.status} />
                  <div className="text-left">
                    <div className="text-sm font-medium capitalize">{run.status}</div>
                    <div className="text-xs text-gray-400">{formatDate(run.created_at)}</div>
                  </div>
                  <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded capitalize">{run.trigger}</span>
                </div>
                <div className="flex items-center gap-6 text-sm text-gray-400">
                  <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{run.duration_ms}ms</span>
                  <span className="flex items-center gap-1"><Zap className="w-3.5 h-3.5" />{run.total_tokens.toLocaleString()}</span>
                  <span className="flex items-center gap-1"><DollarSign className="w-3.5 h-3.5" />${run.total_cost_usd?.toFixed(4)}</span>
                  {expandedRun === run.id ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </div>
              </button>

              {expandedRun === run.id && (
                <div className="border-t border-gray-800 p-4 space-y-4">
                  {run.error && (
                    <div className="p-3 bg-red-900/20 border border-red-800 rounded-lg text-red-300 text-sm">
                      {run.error}
                    </div>
                  )}

                  <div>
                    <div className="text-xs text-gray-400 mb-2 font-medium">NODE RESULTS</div>
                    <div className="space-y-2">
                      {Object.entries(run.node_results || {}).map(([nodeId, result]: [string, any]) => (
                        <div key={nodeId} className="bg-gray-800 rounded-lg p-3">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <StatusIcon status={result.status} />
                              <span className="text-sm font-mono text-gray-300">{nodeId}</span>
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span>{result.duration_ms}ms</span>
                              {result.tokens_used > 0 && <span>{result.tokens_used} tokens</span>}
                            </div>
                          </div>
                          {result.output !== undefined && (
                            <pre className="text-xs text-gray-400 bg-gray-900 rounded p-2 overflow-auto max-h-40 whitespace-pre-wrap">
                              {typeof result.output === 'string' ? result.output : JSON.stringify(result.output, null, 2)}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {run.output_data && (
                    <div>
                      <div className="text-xs text-gray-400 mb-2 font-medium">FINAL OUTPUT</div>
                      <pre className="text-xs text-gray-300 bg-gray-800 rounded-lg p-3 overflow-auto max-h-48 whitespace-pre-wrap">
                        {typeof run.output_data === 'string' ? run.output_data : JSON.stringify(run.output_data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
