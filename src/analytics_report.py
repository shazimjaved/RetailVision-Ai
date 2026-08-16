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
    def _draw_bar(value: float, max_value: float, width: int = 20) -> str:
        """Helper to draw an ASCII bar chart."""
        if max_value == 0 or value == 0:
            return " " * width
        filled = int((value / max_value) * width)
        return "█" * filled + " " * (width - filled)

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
            
        # 2. Print Console Dashboard
        
        print("\n" + "="*60)
        print("RETAILVISION AI")
        print("Retail Customer Analytics Dashboard")
        print("="*60)
        
        print(f"\n[ Total Customers: {total_analytics_customers} ]  [ Entries: {entries} ]  [ Exits: {exits} ]  [ Occupancy: {final_occupancy} ]")
        print(f"(Total Tracking IDs Generated: {total_tracking_ids})")
        
        print("\n" + "-"*60)
        print("ZONE PERFORMANCE")
        print("-"*60)
        
        # Zone Visitors Chart
        print("\n[ Zone Visitors Chart ]")
        max_visitors = max([s.get("unique_visitors_count", 0) for s in zone_stats.values()]) if zone_stats else 0
        for zone, stats in zone_stats.items():
            visitors = stats.get("unique_visitors_count", 0)
            bar = AnalyticsDashboard._draw_bar(visitors, max_visitors)
            print(f"{zone[:15]:<15} |{bar}| {visitors}")

        # Average Dwell Time Chart
        print("\n[ Average Dwell Time Chart (seconds) ]")
        max_dwell = max([s.get("avg_dwell", 0) for s in zone_stats.values()]) if zone_stats else 0
        for zone, stats in zone_stats.items():
            avg_dwell = stats.get("avg_dwell", 0)
            bar = AnalyticsDashboard._draw_bar(avg_dwell, max_dwell)
            print(f"{zone[:15]:<15} |{bar}| {avg_dwell:.1f}s")
            
        print("\n" + "-"*60)
        print("CUSTOMER FLOW")
        print("-"*60)
        
        print("\n[ Top Valid Zone Transitions ]")
        if top_transitions_list:
            for i, (t_name, count) in enumerate(top_transitions_list[:5], 1):
                print(f"  {i}. {t_name:<30} : {count}")
        else:
            print("  No transitions recorded.")
            
        print("\n" + "-"*60)
        print("ZONE SUMMARY TABLE")
        print("-"*60)
        
        print(f"{'Zone':<17} {'Visitors':<10} {'Visits':<8} {'Avg Dwell':<12} {'Max Dwell':<10}")
        print("-" * 60)
        for zone, stats in zone_stats.items():
            visitors = stats.get("unique_visitors_count", 0)
            visits = stats.get("total_visits", 0)
            avg_dwell = f"{stats.get('avg_dwell', 0.0):.1f}s"
            max_dwell = f"{stats.get('max_dwell', 0.0):.1f}s"
            print(f"{zone:<17} {visitors:<10} {visits:<8} {avg_dwell:<12} {max_dwell:<10}")
            
        print("="*60)
        print(f"JSON Report exported to: {json_path}")
        print("="*60 + "\n")
