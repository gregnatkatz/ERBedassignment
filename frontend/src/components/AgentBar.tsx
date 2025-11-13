import { Agent } from '../types';

interface AgentBarProps {
  agents: Agent[];
}

export function AgentBar({ agents }: AgentBarProps) {
  return (
    <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-lg p-4 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <svg className="w-5 h-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
        </svg>
        <span className="text-sm font-semibold text-slate-300">Agent Lightning Network - Real-Time AI Orchestration</span>
      </div>
      <div className="flex flex-wrap gap-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              agent.active
                ? 'bg-blue-500/40 text-blue-100 border-2 border-blue-400 shadow-2xl shadow-blue-400/60 scale-110 animate-pulse'
                : 'bg-slate-700/50 text-slate-400 border border-slate-600/50'
            }`}
          >
            <span className="mr-2">{agent.active ? '⚡' : '○'}</span>
            {agent.name}
            <span className="ml-2 text-xs opacity-75">{agent.confidence}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
