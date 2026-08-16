import React from 'react';
import type { ZoneStats } from '../types/analytics';

interface ZoneSummaryTableProps {
  zones: Record<string, ZoneStats>;
}

export const ZoneSummaryTable: React.FC<ZoneSummaryTableProps> = ({ zones }) => {
  const entries = Object.entries(zones).sort((a, b) => b[1].visitors - a[1].visitors);
  
  if (entries.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)] mt-6 overflow-hidden">
      <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/30">
        <h3 className="text-[13px] font-bold text-slate-900 uppercase tracking-wider">Zone Summary</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/50 text-slate-400 text-[11px] font-bold uppercase tracking-wider">
              <th className="px-6 py-4 border-b border-slate-200/80">Zone</th>
              <th className="px-6 py-4 border-b border-slate-200/80 text-right">Visitors</th>
              <th className="px-6 py-4 border-b border-slate-200/80 text-right">Visits</th>
              <th className="px-6 py-4 border-b border-slate-200/80 text-right">Avg Dwell</th>
              <th className="px-6 py-4 border-b border-slate-200/80 text-right">Max Dwell</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100/80 text-[14px]">
            {entries.map(([name, stats]) => (
              <tr key={name} className="hover:bg-brand-50/30 transition-colors group">
                <td className="px-6 py-4 font-semibold text-slate-700 flex items-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-slate-300 mr-3 group-hover:bg-brand-400 transition-colors"></div>
                  {name}
                </td>
                <td className="px-6 py-4 font-medium text-slate-900 text-right">{stats.visitors === 0 ? <span className="text-slate-400 font-normal">No data</span> : stats.visitors}</td>
                <td className="px-6 py-4 font-medium text-slate-900 text-right">{stats.visits === 0 ? <span className="text-slate-400 font-normal">No data</span> : stats.visits}</td>
                <td className="px-6 py-4 font-medium text-slate-600 text-right">
                  {stats.avg_dwell_seconds === 0 ? <span className="text-slate-400 font-normal">No data</span> : `${stats.avg_dwell_seconds.toFixed(1)}s`}
                </td>
                <td className="px-6 py-4 font-medium text-slate-600 text-right">
                  {stats.max_dwell_seconds === 0 ? <span className="text-slate-400 font-normal">No data</span> : `${stats.max_dwell_seconds.toFixed(1)}s`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
