import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import {
  Brain, Search, Code, Globe, Shuffle, GitBranch,
  Mail, PenTool, BarChart, Share2
} from 'lucide-react'

const AGENT_ICONS: Record<string, any> = {
  llm: Brain,
  web_search: Search,
  code_exec: Code,
  api_call: Globe,
  data_transform: Shuffle,
  conditional: GitBranch,
}

const AGENT_COLORS: Record<string, string> = {
  llm: 'from-blue-600 to-blue-800',
  web_search: 'from-green-600 to-green-800',
  code_exec: 'from-yellow-600 to-yellow-800',
  api_call: 'from-purple-600 to-purple-800',
  data_transform: 'from-orange-600 to-orange-800',
  conditional: 'from-pink-600 to-pink-800',
}

function AgentNode({ data, selected }: NodeProps) {
  const Icon = AGENT_ICONS[data.agent_type] || Brain
  const gradient = AGENT_COLORS[data.agent_type] || 'from-gray-600 to-gray-800'

  return (
    <>
      <Handle type="target" position={Position.Left} />

      <div className={`${selected ? 'ring-2 ring-blue-500' : ''} rounded-xl overflow-hidden`}>
        {/* Header */}
        <div className={`bg-gradient-to-r ${gradient} px-4 py-2.5 flex items-center gap-2`}>
          <Icon className="w-4 h-4 text-white/80" />
          <span className="text-sm font-medium text-white truncate">{data.label || data.agent_type}</span>
        </div>

        {/* Body */}
        <div className="bg-gray-900 px-4 py-3">
          <p className="text-xs text-gray-400 line-clamp-2">
            {data.objective || data.description || 'Configure this agent...'}
          </p>
          {data.status && (
            <div className={`mt-2 text-xs font-medium ${
              data.status === 'completed' ? 'text-green-400' :
              data.status === 'failed' ? 'text-red-400' :
              data.status === 'running' ? 'text-blue-400' :
              data.status === 'skipped' ? 'text-gray-500' :
              'text-gray-400'
            }`}>
              {data.status === 'running' ? '...' : data.status}
              {data.duration_ms ? ` (${data.duration_ms}ms)` : ''}
            </div>
          )}
        </div>
      </div>

      {/* Conditional nodes get two output handles */}
      {data.agent_type === 'conditional' ? (
        <>
          <Handle type="source" position={Position.Right} id="true" style={{ top: '35%' }} />
          <Handle type="source" position={Position.Right} id="false" style={{ top: '65%' }} />
        </>
      ) : (
        <Handle type="source" position={Position.Right} />
      )}
    </>
  )
}

export default memo(AgentNode)
