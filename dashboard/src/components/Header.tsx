import React from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';

interface HeaderProps {
  onRefresh: () => void;
  isRefreshing: boolean;
  lastUpdated: Date | null;
  error?: string | null;
}

export const Header: React.FC<HeaderProps> = ({ onRefresh, isRefreshing, lastUpdated, error }) => {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-8 py-4 flex justify-between items-center sticky top-0 z-20">
      <div>
        <h2 className="text-xl font-semibold text-slate-900 tracking-tight">Retail Customer Intelligence</h2>
        <p className="text-[13px] text-slate-500 mt-0.5 font-medium">
          AI-powered analysis of customer movement, zone activity and dwell behavior
        </p>
      </div>
      <div className="flex flex-col items-end justify-center">
        <div className="flex items-center space-x-4">
          {error ? (
            <div className="flex items-center text-[13px] font-medium text-red-600">
              <AlertCircle size={14} className="mr-1.5" />
              Unable to load analytics
            </div>
          ) : isRefreshing ? (
            <div className="flex items-center text-[13px] font-medium text-slate-500">
              <RefreshCw size={14} className="mr-1.5 animate-spin" />
              Updating analytics...
            </div>
          ) : (
            <div className="flex items-center text-[13px] font-medium text-slate-600">
              <div className="w-2 h-2 rounded-full bg-emerald-500 mr-2 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
              Live Data
            </div>
          )}
          
          <div className="h-4 w-px bg-slate-200"></div>
          
          <button 
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center px-3.5 py-1.5 bg-white border border-slate-200 rounded-md text-[13px] font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 hover:border-slate-300 transition-all disabled:opacity-50 shadow-sm"
          >
            <RefreshCw size={14} className={`mr-2 ${isRefreshing ? 'animate-spin text-brand-500' : 'text-slate-400'}`} />
            Refresh
          </button>
        </div>
        
        {lastUpdated && !isRefreshing && (
          <div className="text-[11px] text-slate-400 font-medium mt-1.5 uppercase tracking-wider">
            Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </header>
  );
};
