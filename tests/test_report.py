import unittest
import os
import json
import io
import sys
from src.analytics_report import AnalyticsDashboard

class TestAnalyticsReport(unittest.TestCase):
    def setUp(self):
        self.output_path = "output/test_video.mp4"
        self.json_path = "output/analytics.json"
        
        # Clean up existing test json if any
        if os.path.exists(self.json_path):
            os.remove(self.json_path)
            
    def tearDown(self):
        # Clean up
        if os.path.exists(self.json_path):
            os.remove(self.json_path)

    def test_json_export_and_console(self):
        zone_stats = {
            "CHECKOUT": {"unique_visitors_count": 5, "total_visits": 6, "avg_dwell": 12.5, "max_dwell": 25.0},
            "ENTRANCE": {"unique_visitors_count": 10, "total_visits": 10, "avg_dwell": 2.0, "max_dwell": 5.0}
        }
        transition_stats = {
            "ENTRANCE -> CHECKOUT": 3,
            "CHECKOUT -> ENTRANCE": 2
        }
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            AnalyticsDashboard.generate_report(
                output_path=self.output_path,
                total_tracking_ids=15,
                total_analytics_customers=10,
                entries=10,
                exits=8,
                final_occupancy=2,
                zone_stats=zone_stats,
                transition_stats=transition_stats
            )
        finally:
            sys.stdout = sys.__stdout__
            
        output_str = captured_output.getvalue()
        
        # Verify Console Output contains expected elements
        self.assertIn("RETAILVISION AI", output_str)
        self.assertIn("Total Customers: 10", output_str)
        self.assertIn("Entries: 10", output_str)
        self.assertIn("Occupancy: 2", output_str)
        
        # Verify JSON file creation
        self.assertTrue(os.path.exists(self.json_path))
        with open(self.json_path, "r") as f:
            data = json.load(f)
            
        self.assertEqual(data["customers"]["total_tracking_ids"], 15)
        self.assertEqual(data["customers"]["final_occupancy"], 2)
        
        self.assertEqual(data["zones"]["CHECKOUT"]["visitors"], 5)
        self.assertEqual(data["zones"]["CHECKOUT"]["avg_dwell_seconds"], 12.5)
        
        self.assertEqual(len(data["top_transitions"]), 2)
        self.assertEqual(data["top_transitions"][0]["from"], "ENTRANCE")
        self.assertEqual(data["top_transitions"][0]["to"], "CHECKOUT")
        self.assertEqual(data["top_transitions"][0]["count"], 3)

    def test_empty_stats(self):
        # Should handle completely empty data gracefully
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            AnalyticsDashboard.generate_report(
                output_path=self.output_path,
                total_tracking_ids=0,
                total_analytics_customers=0,
                entries=0,
                exits=0,
                final_occupancy=0,
                zone_stats={},
                transition_stats={}
            )
        finally:
            sys.stdout = sys.__stdout__
            
        self.assertTrue(os.path.exists(self.json_path))
        with open(self.json_path, "r") as f:
            data = json.load(f)
            
        self.assertEqual(data["customers"]["total_tracking_ids"], 0)
        self.assertEqual(data["zones"], {})
        self.assertEqual(data["top_transitions"], [])

if __name__ == "__main__":
    unittest.main()
