import React from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface KpiCardProps {
  title: string;
  value: string | number;
  icon: any;
  subtitle?: string;
  className?: string;
  valueClassName?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({ title, value, icon: Icon, subtitle, className, valueClassName }) => {
  return (
    <div className={cn("bg-white p-5 rounded-[16px] border border-slate-200/75 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.05)] hover:shadow-[0_4px_15px_-3px_rgba(6,81,237,0.08)] transition-all duration-300 flex flex-col group", className)}>
      <div className="flex items-center space-x-3 mb-3">
        <div className="p-2 bg-slate-50 text-slate-500 rounded-lg border border-slate-100 group-hover:bg-brand-50 group-hover:text-brand-600 group-hover:border-brand-100 transition-colors duration-300">
          <Icon size={18} strokeWidth={2.5} />
        </div>
        <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">{title}</h3>
      </div>
      <div className="mt-1">
        <div className={cn("text-3xl font-bold text-slate-900 tracking-tight", valueClassName)}>{value}</div>
        {subtitle && (
          <div className="text-[12px] font-medium text-slate-400 mt-1">{subtitle}</div>
        )}
      </div>
    </div>
  );
};
