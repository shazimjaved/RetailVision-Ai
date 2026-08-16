import React from 'react';
import type { ZoneStats } from '../types/analytics';

interface ZoneComparisonProps {
  zones: Record<string, ZoneStats>;
}

export const ZoneComparison: React.FC<ZoneComparisonProps> = ({ zones }) => {
  const data = Object.entries(zones)
    .map(([name, stats]) => ({
      name,
      visitors: stats.visitors,
      visits: stats.visits,
    }))
    .sort((a, b) => b.visitors - a.visitors);

  return (
    <div className="bg-white p-6 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)] mt-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-[13px] font-bold text-slate-900 uppercase tracking-wider">Zone Activity Comparison</h3>
      </div>
      
      <div className="space-y-3">
        <div className="grid grid-cols-12 gap-4 pb-2 border-b border-slate-100 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          <div className="col-span-6">Zone</div>
          <div className="col-span-3 text-right">Unique Visitors</div>
          <div className="col-span-3 text-right">Total Visits</div>
        </div>
        
        {data.map((item) => (
          <div key={item.name} className="grid grid-cols-12 gap-4 items-center py-2 group hover:bg-slate-50/50 rounded-lg transition-colors -mx-2 px-2">
            <div className="col-span-6 flex items-center">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-300 mr-2.5 group-hover:bg-brand-400 transition-colors"></div>
              <span className="text-[13px] font-semibold text-slate-700">{item.name}</span>
            </div>
            <div className="col-span-3 text-right">
              <span className="text-[14px] font-bold text-slate-900">{item.visitors}</span>
            </div>
            <div className="col-span-3 text-right">
              <span className="text-[14px] font-bold text-slate-900">{item.visits}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
