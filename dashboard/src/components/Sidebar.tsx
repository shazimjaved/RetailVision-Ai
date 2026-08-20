import React from 'react';
import { LayoutDashboard, Map, GitMerge, MapPinned } from 'lucide-react';
import { cn } from './KpiCard';
import retailerLogo from '../assets/shopping-cart.png';

const navItems = [
  { name: 'Overview', icon: LayoutDashboard, href: '#overview' },
  { name: 'Zone Analytics', icon: Map, href: '#zones' },
  { name: 'Customer Flow', icon: GitMerge, href: '#flow' },
  { name: 'Customer Heatmap', icon: MapPinned, href: '#heatmap' },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#0B1120] text-slate-300 flex flex-col h-screen sticky top-0 border-r border-slate-800/50">
      <div className="p-6">
        <h1 className="text-lg font-bold text-white tracking-tight flex items-center">
          <img src={retailerLogo} alt="RetailVision AI Logo" className="w-8 h-8 mr-2.5 rounded object-contain" />
          RetailVision<span className="text-brand-400">AI</span>
        </h1>
        <p className="text-[10px] text-slate-500 mt-1.5 uppercase tracking-[0.2em] font-medium ml-8.5">Intelligence</p>
      </div>
      
      <div className="px-4 py-2">
        <div className="h-px bg-slate-800/60 w-full mb-4"></div>
      </div>

      <nav className="flex-1 px-4 space-y-1.5">
        {navItems.map((item) => (
          <a
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center px-3.5 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 group relative",
              item.name === 'Overview' 
                ? "bg-brand-500/10 text-brand-400" 
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
            )}
          >
            {item.name === 'Overview' && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-brand-500 rounded-r-full"></div>
            )}
            <item.icon className={cn(
              "mr-3 flex-shrink-0 h-5 w-5 transition-colors duration-200", 
              item.name === 'Overview' ? "text-brand-400" : "text-slate-500 group-hover:text-slate-400"
            )} />
            {item.name}
          </a>
        ))}
      </nav>

      <div className="p-4 mt-auto">
        <div className="text-center text-xs text-slate-500 font-medium">
          System Developed By <span className="text-brand-400">Shazim Javed</span>
        </div>
      </div>
    </aside>
  );
};
