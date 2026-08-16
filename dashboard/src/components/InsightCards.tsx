import React from 'react';
import type { AnalyticsData } from '../types/analytics';
import { Trophy, Clock, GitMerge } from 'lucide-react';
import { cn } from './KpiCard';

interface InsightCardsProps {
  data: AnalyticsData;
}

export const InsightCards: React.FC<InsightCardsProps> = ({ data }) => {
  // Derive Most Visited Zone
  let mostVisitedZone = 'N/A';
  let maxVisitors = -1;
  Object.entries(data.zones).forEach(([zone, stats]) => {
    if (stats.visitors > maxVisitors) {
      maxVisitors = stats.visitors;
      mostVisitedZone = zone;
    }
  });

  // Derive Highest Dwell Zone
  let highestDwellZone = 'N/A';
  let maxDwell = -1;
  Object.entries(data.zones).forEach(([zone, stats]) => {
    if (stats.avg_dwell_seconds > maxDwell) {
      maxDwell = stats.avg_dwell_seconds;
      highestDwellZone = zone;
    }
  });

  // Derive Most Active Flow
  let mostActiveFlowStr = 'N/A';
  let maxFlowCount = -1;
  data.top_transitions.forEach(transition => {
    if (transition.count > maxFlowCount) {
      maxFlowCount = transition.count;
      mostActiveFlowStr = `${transition.from} → ${transition.to}`;
    }
  });

  const cards = [
    {
      title: 'Most Visited Zone',
      value: mostVisitedZone,
      subtitle: maxVisitors >= 0 ? `${maxVisitors} visitors` : '',
      icon: Trophy,
      iconBg: 'bg-amber-50',
      iconColor: 'text-amber-500',
    },
    {
      title: 'Highest Dwell Zone',
      value: highestDwellZone,
      subtitle: maxDwell >= 0 ? `${(maxDwell / 60).toFixed(1)} min average` : '',
      icon: Clock,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-500',
    },
    {
      title: 'Most Active Flow',
      value: mostActiveFlowStr,
      subtitle: maxFlowCount >= 0 ? `${maxFlowCount} transition${maxFlowCount !== 1 ? 's' : ''}` : '',
      icon: GitMerge,
      iconBg: 'bg-purple-50',
      iconColor: 'text-purple-500',
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-6">
      {cards.map((card, i) => (
        <div key={i} className="bg-gradient-to-br from-white to-slate-50/80 p-5 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)] hover:shadow-[0_4px_15px_-3px_rgba(6,81,237,0.08)] transition-all duration-300 flex items-start space-x-4 group">
          <div className={cn("p-3 rounded-xl flex-shrink-0 transition-transform duration-300 group-hover:scale-110", card.iconBg, card.iconColor)}>
            <card.icon size={20} strokeWidth={2.5} />
          </div>
          <div>
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1.5">{card.title}</h4>
            <div className="text-[15px] font-bold text-slate-900 leading-tight mb-1">{card.value}</div>
            {card.subtitle && (
              <div className="text-[12px] font-medium text-slate-500">{card.subtitle}</div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
