import { Alert } from '../types';
import { AlertTriangle } from 'lucide-react';
import { useEffect, useRef } from 'react';

interface AlertFeedProps {
  alerts: Alert[];
  onRequestBed: () => void;
}

const SEVERITY_COLORS = {
  critical: 'border-l-4 border-red-500 bg-red-950/30',
  high: 'border-l-4 border-orange-500 bg-orange-950/30',
  medium: 'border-l-4 border-yellow-500 bg-yellow-950/30',
  low: 'border-l-4 border-blue-500 bg-blue-950/30',
};

export function AlertFeed({ alerts, onRequestBed }: AlertFeedProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [alerts]);

  function formatTimeAgo(timestamp: string): string {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins === 1) return '1m ago';
    if (diffMins < 60) return `${diffMins}m ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return '1h ago';
    return `${diffHours}h ago`;
  }

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">AI Alerts & Recommendations</h2>
        </div>
        <button
          onClick={onRequestBed}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          <span>+</span>
          Request Bed
        </button>
      </div>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-900">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`${SEVERITY_COLORS[alert.severity]} rounded-lg p-4 transition-all hover:bg-opacity-50`}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl">{alert.icon}</span>
              <div className="flex-1">
                <div className="font-semibold text-white text-sm mb-1">{alert.alert_type}</div>
                <div className="text-slate-300 text-xs mb-2">{alert.message}</div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{alert.agent_id}</span>
                  <span>{formatTimeAgo(alert.created_at)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
