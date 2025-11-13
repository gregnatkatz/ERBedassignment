import { Metrics } from '../types';
import { Clock, Users, Bed, Star } from 'lucide-react';

interface MetricsPanelProps {
  metrics: Metrics;
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const metricCards = [
    {
      title: 'Door-to-Provider',
      value: `${metrics.door_to_provider}min`,
      change: '-38% improvement',
      baseline: 'Baseline: 45min',
      icon: Clock,
      color: 'text-blue-400',
    },
    {
      title: 'LWBS Rate',
      value: `${metrics.lwbs_rate}%`,
      change: '-62% reduction',
      baseline: 'Baseline: 8.1%',
      icon: Users,
      color: 'text-green-400',
    },
    {
      title: 'Bed Utilization',
      value: `${metrics.bed_utilization}%`,
      change: '+12% efficiency',
      baseline: 'Baseline: 67%',
      icon: Bed,
      color: 'text-cyan-400',
    },
    {
      title: 'Patient Satisfaction',
      value: `${metrics.patient_satisfaction}/5`,
      change: '+28% increase',
      baseline: 'Baseline: 3.2/5',
      icon: Star,
      color: 'text-purple-400',
    },
  ];

  return (
    <div className="grid grid-cols-4 gap-4 mt-6">
      {metricCards.map((metric) => {
        const Icon = metric.icon;
        return (
          <div
            key={metric.title}
            className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-6 border border-slate-700"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-slate-400">{metric.title}</h3>
              <Icon className={`w-5 h-5 ${metric.color}`} />
            </div>
            <div className="text-4xl font-bold text-blue-400 mb-2">{metric.value}</div>
            <div className="text-sm text-green-400 mb-1">{metric.change}</div>
            <div className="text-xs text-slate-500">{metric.baseline}</div>
          </div>
        );
      })}
    </div>
  );
}
