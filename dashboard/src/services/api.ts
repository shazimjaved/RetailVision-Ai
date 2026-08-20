import type { AnalyticsData, HeatmapAnalytics } from '../types/analytics';

export async function fetchAnalyticsData(): Promise<AnalyticsData> {
  const response = await fetch('/api/analytics.json');
  if (!response.ok) {
    throw new Error(`Failed to fetch analytics data: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchHeatmapData(): Promise<HeatmapAnalytics> {
  const response = await fetch('/api/heatmap_analytics.json');
  if (!response.ok) {
    throw new Error(`Failed to fetch heatmap data: ${response.statusText}`);
  }
  return response.json();
}
