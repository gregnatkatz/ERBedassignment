import { Bed } from '../types';

interface BedCardProps {
  bed: Bed;
}

const ESI_COLORS = {
  1: 'from-red-900 to-red-800 border-red-500',
  2: 'from-orange-900 to-orange-800 border-orange-500',
  3: 'from-yellow-900 to-yellow-800 border-yellow-500',
  4: 'from-green-900 to-green-800 border-green-500',
  5: 'from-blue-900 to-blue-800 border-blue-500',
};

const ESI_LABELS = {
  1: 'ESI-1 CRITICAL',
  2: 'ESI-2 EMERGENT',
  3: 'ESI-3 URGENT',
  4: 'ESI-4',
  5: 'ESI-5',
};

export function BedCard({ bed }: BedCardProps) {
  if (!bed.occupied) {
    return (
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-4 border-2 border-slate-700 h-40 flex flex-col items-center justify-center">
        <div className="text-slate-600 text-sm mb-2">{bed.bed_number}</div>
        <div className="text-slate-500 text-2xl font-bold">AVAILABLE</div>
        <div className="text-slate-600 text-xs mt-2">OPEN</div>
      </div>
    );
  }

  const esiColor = ESI_COLORS[bed.esi_score as keyof typeof ESI_COLORS] || ESI_COLORS[3];
  const esiLabel = ESI_LABELS[bed.esi_score as keyof typeof ESI_LABELS] || 'ESI-3';

  return (
    <div className={`bg-gradient-to-br ${esiColor} rounded-lg p-4 border-2 h-40 flex flex-col justify-between relative overflow-hidden`}>
      <div className="absolute top-2 right-2 bg-black/30 px-2 py-1 rounded text-xs font-bold text-white">
        {bed.wait_time_minutes}m
      </div>
      
      <div>
        <div className="text-xs text-white/70 mb-1">{bed.bed_number}</div>
        <div className="text-xl font-bold text-white mb-1">{bed.patient_name}</div>
        <div className="text-sm font-semibold text-white/90">{esiLabel}</div>
      </div>
      
      <div className="text-xs text-white/80">{bed.chief_complaint}</div>
    </div>
  );
}
