import { Bed } from '../types';
import { BedCard } from './BedCard';
import { Activity } from 'lucide-react';

interface BedGridProps {
  beds: Bed[];
}

export function BedGrid({ beds }: BedGridProps) {
  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">Emergency Department - Live Status (16 Beds)</h2>
        </div>
      </div>
      
      <div className="grid grid-cols-4 gap-4">
        {beds.map((bed) => (
          <BedCard key={bed.id} bed={bed} />
        ))}
      </div>
    </div>
  );
}
