export interface CustomersStats {
  total_tracking_ids: number;
  total_analytics_customers: number;
  entries: number;
  exits: number;
  final_occupancy: number;
}

export interface HeatmapAnalytics {
  total_frames: number;
  tracked_position_samples: number;
  heatmap_resolution: {
    width: number;
    height: number;
  };
  peak_density_location: {
    x: number;
    y: number;
  };
  peak_density_value: number;
  processing_fps?: number;
}


export interface ZoneStats {
  visitors: number;
  visits: number;
  avg_dwell_seconds: number;
  max_dwell_seconds: number;
}

export interface TransitionStats {
  from: string;
  to: string;
  count: number;
}

export interface AnalyticsData {
  customers: CustomersStats;
  zones: Record<string, ZoneStats>;
  top_transitions: TransitionStats[];
}
