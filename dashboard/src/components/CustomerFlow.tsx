import React from 'react';
import type { TransitionStats } from '../types/analytics';
import { ArrowRight, MoveRight } from 'lucide-react';

interface CustomerFlowProps {
  transitions: TransitionStats[];
}

export const CustomerFlow: React.FC<CustomerFlowProps> = ({ transitions }) => {
  // Sort by count descending
  const sorted = [...transitions].sort((a, b) => b.count - a.count);
  
  if (sorted.length === 0) {
    return (
      <div className="bg-white p-6 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)] mt-6">
        <h3 className="text-[13px] font-bold text-slate-900 uppercase tracking-wider mb-6">Customer Flow</h3>
        <div className="h-32 flex flex-col items-center justify-center text-slate-400 bg-slate-50/50 rounded-xl border border-slate-100 border-dashed">
          <MoveRight className="h-8 w-8 text-slate-300 mb-2" />
          <span className="text-sm font-medium">No transition data available</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)] mt-6">
      <h3 className="text-[13px] font-bold text-slate-900 uppercase tracking-wider mb-5">Top Zone Transitions</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sorted.map((t) => (
          <div key={`${t.from}-${t.to}`} className="flex items-center p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-white hover:border-slate-200 hover:shadow-sm transition-all group">
            <div className="flex-1 flex flex-col items-end text-right">
              <span className="text-[13px] font-semibold text-slate-700 uppercase tracking-wide group-hover:text-slate-900 transition-colors">{t.from}</span>
            </div>
            
            <div className="mx-4 flex flex-col items-center justify-center min-w-[80px]">
              <div className="text-[11px] font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full mb-1 border border-brand-100">
                {t.count} transition{t.count !== 1 ? 's' : ''}
              </div>
              <ArrowRight size={16} className="text-slate-400 group-hover:text-brand-500 transition-colors" />
            </div>
            
            <div className="flex-1 flex flex-col items-start">
              <span className="text-[13px] font-semibold text-slate-700 uppercase tracking-wide group-hover:text-slate-900 transition-colors">{t.to}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
