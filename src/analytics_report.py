import json
import os
from typing import Dict, List, Any

class AnalyticsDashboard:
    """
    Phase 4.4: Retail Analytics Dashboard & Summary.
    Responsible for presenting existing Phase 3 and Phase 4.3 analytics data.
    Does NOT recalculate metrics or duplicate business logic.
    """


    @staticmethod
    def generate_report(
        output_path: str,
        total_tracking_ids: int,
        total_analytics_customers: int,
        entries: int,
        exits: int,
        final_occupancy: int,
        zone_stats: Dict[str, Dict],
        transition_stats: Dict[str, int]
    ):
        """Generates the JSON export and prints the ASCII dashboard."""
        
        # 1. Prepare JSON Export Payload
        
        # Sort transitions by count descending
        top_transitions_list = sorted(transition_stats.items(), key=lambda x: x[1], reverse=True)
        top_transitions_formatted = [
            {"from": k.split(" -> ")[0], "to": k.split(" -> ")[1], "count": v}
            for k, v in top_transitions_list
        ]
        
        # Format zone stats for JSON
        zones_json = {}
        for zone, stats in zone_stats.items():
            zones_json[zone] = {
                "visitors": stats.get("unique_visitors_count", 0),
                "visits": stats.get("total_visits", 0),
                "avg_dwell_seconds": round(stats.get("avg_dwell", 0.0), 1),
                "max_dwell_seconds": round(stats.get("max_dwell", 0.0), 1)
            }
            
        payload = {
            "customers": {
                "total_tracking_ids": total_tracking_ids,
                "total_analytics_customers": total_analytics_customers,
                "entries": entries,
                "exits": exits,
                "final_occupancy": final_occupancy
            },
            "zones": zones_json,
            "top_transitions": top_transitions_formatted
        }
        
        # Write JSON file
        json_path = os.path.join(os.path.dirname(output_path), "analytics.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(payload, f, indent=4)
            
        # 2. Print Console Message
        
        print("\n" + "="*60)
        print("RETAILVISION AI")
        print("Web Dashboard is active. Use 'npm run dev' in the dashboard directory.")
        print(f"JSON Report exported to: {json_path}")
        print("="*60 + "\n")
