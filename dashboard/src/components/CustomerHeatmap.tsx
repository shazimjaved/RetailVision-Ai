import React from 'react';
import { Map, Info } from 'lucide-react';
import type { HeatmapAnalytics } from '../types/analytics';

interface CustomerHeatmapProps {
  data: HeatmapAnalytics | null;
  error: string | null;
  lastUpdated: Date | null;
}

export const CustomerHeatmap: React.FC<CustomerHeatmapProps> = ({ data, error, lastUpdated }) => {
  // If there's an error (e.g. file doesn't exist), show a graceful empty state
  if (error || !data) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden p-8 flex flex-col items-center justify-center min-h-[400px] text-center">
        <div className="bg-slate-50 text-slate-400 w-16 h-16 rounded-full flex items-center justify-center mb-4 border border-slate-100">
          <Map size={32} />
        </div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">Customer Heatmap Unavailable</h3>
        <p className="text-slate-500 max-w-md">
          {error || "The heatmap data is not available yet. Run the processing pipeline to generate the heatmap."}
        </p>
      </div>
    );
  }

  // Cache buster for the image so it refreshes when the dashboard refreshes
  const timestamp = lastUpdated ? lastUpdated.getTime() : Date.now();
  const imageUrl = `/api/customer_heatmap.png?t=${timestamp}`;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-base font-bold text-slate-900">Customer Movement Density</h3>
            <p className="text-xs text-slate-500 mt-1">Visual representation of customer spatial presence across the retail floor.</p>
          </div>
        </div>
        
        <div className="p-6">
          <div className="relative rounded-xl overflow-hidden border border-slate-200 shadow-sm bg-slate-50 flex items-center justify-center min-h-[300px]">
            <img 
              src={imageUrl} 
              alt="Customer Movement Heatmap" 
              className="w-full h-auto object-contain max-h-[700px]"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.onerror = null; 
                // Hide broken image icon and show fallback text via sibling or parent if needed
                // For simplicity, we just leave standard broken image or can replace with a placeholder
              }}
            />
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-100 border-t border-slate-100 bg-slate-50/30">
          <div className="p-5 flex flex-col items-center text-center">
            <span className="text-3xl font-bold text-slate-800 tracking-tight">{data.tracked_position_samples.toLocaleString()}</span>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">Position Samples</span>
          </div>
          <div className="p-5 flex flex-col items-center text-center">
            <span className="text-3xl font-bold text-slate-800 tracking-tight">{data.heatmap_resolution.width} × {data.heatmap_resolution.height}</span>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">Resolution</span>
          </div>
          <div className="p-5 flex flex-col items-center text-center">
            <span className="text-3xl font-bold text-slate-800 tracking-tight">({data.peak_density_location.x}, {data.peak_density_location.y})</span>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mt-1">Peak Location</span>
          </div>
        </div>
      </div>

      <div className="bg-blue-50/50 border border-blue-100 rounded-xl p-5 flex gap-4">
        <div className="flex-shrink-0 mt-0.5">
          <Info className="h-5 w-5 text-blue-500" />
        </div>
        <div>
          <h4 className="text-sm font-bold text-blue-900 mb-1">How to read the heatmap</h4>
          <p className="text-sm text-blue-800/80 leading-relaxed">
            Hotter areas (yellow/white) indicate higher accumulated customer presence, while cooler areas (red/black) indicate lower presence. 
            The density reflects repeated tracked positions over time. This visualizes <strong>tracked customer spatial presence</strong> 
            and complements the zone-level analytics. It does not directly measure product interest, purchasing intent, or conversion.
          </p>
        </div>
      </div>
    </div>
  );
};
