import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { ZoneStats } from '../types/analytics';

interface ZoneChartsProps {
  zones: Record<string, ZoneStats>;
}

export const ZoneCharts: React.FC<ZoneChartsProps> = ({ zones }) => {
  const visitorsData = Object.entries(zones)
    .map(([name, stats]) => ({
      name,
      visitors: stats.visitors,
    }))
    .sort((a, b) => b.visitors - a.visitors);

  const dwellData = Object.entries(zones)
    .map(([name, stats]) => ({
      name,
      avgDwell: stats.avg_dwell_seconds,
    }))
    .sort((a, b) => b.avgDwell - a.avgDwell);

  const CustomTooltip = ({ active, payload, label, suffix = '' }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900/95 backdrop-blur-sm text-white p-3 rounded-lg shadow-xl border border-slate-700/50 text-sm">
          <p className="font-semibold text-slate-200 mb-1">{label}</p>
          <p className="text-brand-400 font-medium">
            {payload[0].name}: <span className="text-white">{payload[0].value.toFixed(suffix === 's' ? 1 : 0)}{suffix}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
      {/* Visitors Chart */}
      <div className="bg-white p-6 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)]">
        <h3 className="text-[13px] font-bold text-slate-900 uppercase tracking-wider mb-6">Visitors by Zone</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={visitorsData} layout="vertical" margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={true} stroke="#f1f5f9" />
              <XAxis type="number" hide />
              <YAxis 
                dataKey="name" 
                type="category" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#475569', fontSize: 11, fontWeight: 600 }}
                width={120}
              />
              <Tooltip cursor={{ fill: '#f8fafc' }} content={<CustomTooltip name="Visitors" />} />
              <Bar dataKey="visitors" name="Visitors" radius={[0, 4, 4, 0]} barSize={20}>
                {visitorsData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? '#0d9488' : '#14b8a6'} fillOpacity={index === 0 ? 1 : 0.7} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Dwell Time Chart */}
      <div className="bg-white p-6 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)]">
        <h3 className="text-[13px] font-bold text-slate-900 uppercase tracking-wider mb-6">Avg Dwell Time</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dwellData} layout="vertical" margin={{ top: 0, right: 30, left: 30, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} vertical={true} stroke="#f1f5f9" />
              <XAxis type="number" hide />
              <YAxis 
                dataKey="name" 
                type="category" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#475569', fontSize: 11, fontWeight: 600 }}
                width={120}
              />
              <Tooltip cursor={{ fill: '#f8fafc' }} content={<CustomTooltip name="Avg Dwell" suffix="s" />} />
              <Bar dataKey="avgDwell" name="Avg Dwell" radius={[0, 4, 4, 0]} barSize={20}>
                {dwellData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? '#3b82f6' : '#60a5fa'} fillOpacity={index === 0 ? 1 : 0.7} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
