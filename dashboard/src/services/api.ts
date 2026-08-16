import type { AnalyticsData } from '../types/analytics';

export async function fetchAnalyticsData(): Promise<AnalyticsData> {
  const response = await fetch('/api/analytics.json');
  if (!response.ok) {
    throw new Error(`Failed to fetch analytics data: ${response.statusText}`);
  }
  return response.json();
}
