import { useEffect, useState } from 'react';
import { Users, LogIn, LogOut, UsersRound, Activity } from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { KpiCard } from './components/KpiCard';
import { InsightCards } from './components/InsightCards';
import { ZoneCharts } from './components/ZoneCharts';
import { ZoneComparison } from './components/ZoneComparison';
import { CustomerFlow } from './components/CustomerFlow';
import { ZoneSummaryTable } from './components/ZoneSummaryTable';
import { fetchAnalyticsData } from './services/api';
import type { AnalyticsData } from './types/analytics';

function App() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const loadData = async () => {
    try {
      setIsRefreshing(true);
      setError(null);
      const analytics = await fetchAnalyticsData();
      setData(analytics);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Analytics data unavailable. Run the RetailVision AI processing pipeline to generate analytics.json.');
    } finally {
      setIsRefreshing(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="flex h-screen bg-surface-light overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col h-screen overflow-y-auto relative scroll-smooth">
        <Header onRefresh={loadData} isRefreshing={isRefreshing} lastUpdated={lastUpdated} error={error} />
        
        <main className="flex-1 p-6 lg:p-8">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="relative flex items-center justify-center">
                <div className="absolute animate-ping h-12 w-12 rounded-full bg-brand-400 opacity-20"></div>
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500"></div>
              </div>
            </div>
          ) : error || !data ? (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-lg mx-auto">
              <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                <div className="bg-red-50 text-red-500 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Activity size={32} />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Analytics Data Unavailable</h3>
                <p className="text-slate-500 mb-6 text-sm">{error}</p>
                <button onClick={loadData} className="px-6 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors shadow-sm">
                  Retry Connection
                </button>
              </div>
            </div>
          ) : (
            <div className="max-w-7xl mx-auto animate-in fade-in duration-500">
              
              {/* Overview Section */}
              <section id="overview" className="scroll-mt-24">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="text-lg font-bold text-slate-900 tracking-tight">Customer Overview</h2>
                  <div className="flex items-center text-[11px] font-bold uppercase tracking-wider text-slate-500 bg-white px-3 py-1.5 rounded-full border border-slate-200 shadow-sm">
                    Total Tracking IDs <span className="text-brand-600 ml-2 bg-brand-50 px-2 py-0.5 rounded-full">{data.customers.total_tracking_ids}</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                  <KpiCard 
                    title="Total Customers" 
                    value={data.customers.total_analytics_customers} 
                    icon={Users} 
                    subtitle="Analytics Customers"
                  />
                  <KpiCard 
                    title="Entries" 
                    value={data.customers.entries} 
                    icon={LogIn} 
                    subtitle="Customers entered"
                  />
                  <KpiCard 
                    title="Exits" 
                    value={data.customers.exits} 
                    icon={LogOut} 
                    subtitle="Customers exited"
                  />
                  <KpiCard 
                    title="Current Occupancy" 
                    value={data.customers.final_occupancy} 
                    icon={UsersRound} 
                    subtitle="Currently inside"
                    className="border-brand-200 bg-gradient-to-b from-brand-50/50 to-white"
                    valueClassName="text-brand-700"
                  />
                </div>

                <InsightCards data={data} />
              </section>

              {/* Zone Performance Section */}
              <section id="zones" className="mt-10 scroll-mt-24">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-bold text-slate-900 tracking-tight">Zone Performance</h2>
                </div>
                <ZoneCharts zones={data.zones} />
                <ZoneComparison zones={data.zones} />
                <ZoneSummaryTable zones={data.zones} />
              </section>

              {/* Customer Flow Section */}
              <section id="flow" className="mt-10 pb-12 scroll-mt-24">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-bold text-slate-900 tracking-tight">Customer Flow</h2>
                </div>
                <CustomerFlow transitions={data.top_transitions} />
              </section>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
