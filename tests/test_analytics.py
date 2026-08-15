import unittest
from src.zone_analytics import ZoneAnalytics

class MockZoneTracker:
    def __init__(self, max_lost_frames=30):
        self.transitions = []
        self.track_states = {}
        self.max_lost_frames = max_lost_frames

class TestZoneAnalytics(unittest.TestCase):
    def test_single_zone_visit(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=10.0, max_lost_frames=30)
        
        tracker.track_states[1] = {'last_seen_frame': 100}
        tracker.transitions.append({
            'track_id': 1, 'from_zone': 'NO ZONE', 'to_zone': 'ENTRANCE', 
            'start_frame': 90, 'transition_frame': 100
        })
        
        analytics.update(100, tracker, [])
        self.assertIn(1, analytics.open_visits)
        self.assertEqual(analytics.open_visits[1]['zone'], 'ENTRANCE')
        
        tracker.track_states[1]['last_seen_frame'] = 150
        analytics.update(200, tracker, []) 
        
        self.assertNotIn(1, analytics.open_visits)
        self.assertIn(1, analytics.finalized_tracks)
        self.assertEqual(len(analytics.visits), 1)
        
        visit = analytics.visits[0]
        self.assertEqual(visit['zone'], 'ENTRANCE')
        self.assertEqual(visit['entry_frame'], 100)
        self.assertEqual(visit['exit_frame'], 150)
        self.assertEqual(visit['dwell_seconds'], 5.0)

    def test_multiple_zone_transitions(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=30.0, max_lost_frames=30)
        
        tracker.track_states[2] = {'last_seen_frame': 100}
        tracker.transitions.append({
            'track_id': 2, 'from_zone': 'NO ZONE', 'to_zone': 'ENTRANCE', 
            'start_frame': 90, 'transition_frame': 100
        })
        analytics.update(100, tracker, [])
        
        tracker.track_states[2]['last_seen_frame'] = 200
        tracker.transitions.append({
            'track_id': 2, 'from_zone': 'ENTRANCE', 'to_zone': 'CENTRAL AISLE', 
            'start_frame': 190, 'transition_frame': 200
        })
        analytics.update(200, tracker, [])
        
        self.assertEqual(len(analytics.visits), 1)
        self.assertEqual(analytics.visits[0]['zone'], 'ENTRANCE')
        self.assertEqual(analytics.open_visits[2]['zone'], 'CENTRAL AISLE')
        
        tracker.track_states[2]['last_seen_frame'] = 300
        analytics.update(400, tracker, [])
        
        self.assertEqual(len(analytics.visits), 2)
        self.assertEqual(analytics.journeys[2][0]['zone'], 'ENTRANCE')
        self.assertEqual(analytics.journeys[2][1]['zone'], 'CENTRAL AISLE')
        
    def test_repeated_zone_visits(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=30.0, max_lost_frames=30)
        
        tracker.track_states[3] = {'last_seen_frame': 50}
        tracker.transitions.append({'track_id': 3, 'from_zone': 'NO ZONE', 'to_zone': 'PRODUCT / SHELF', 'transition_frame': 50})
        tracker.transitions.append({'track_id': 3, 'from_zone': 'PRODUCT / SHELF', 'to_zone': 'CENTRAL AISLE', 'transition_frame': 100})
        tracker.transitions.append({'track_id': 3, 'from_zone': 'CENTRAL AISLE', 'to_zone': 'PRODUCT / SHELF', 'transition_frame': 150})
        analytics.update(150, tracker, [])
        
        tracker.track_states[3]['last_seen_frame'] = 200
        analytics.update(250, tracker, [])
        
        self.assertEqual(len(analytics.visits), 3)
        self.assertEqual(analytics.visits[0]['zone'], 'PRODUCT / SHELF')
        self.assertEqual(analytics.visits[0]['visit_number'], 1)
        self.assertEqual(analytics.visits[1]['zone'], 'CENTRAL AISLE')
        self.assertEqual(analytics.visits[2]['zone'], 'PRODUCT / SHELF')
        self.assertEqual(analytics.visits[2]['visit_number'], 2)

    def test_phase_3_exit_finalization(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=30.0, max_lost_frames=30)
        
        tracker.track_states[4] = {'last_seen_frame': 100}
        tracker.transitions.append({'track_id': 4, 'from_zone': 'NO ZONE', 'to_zone': 'CHECKOUT', 'transition_frame': 10})
        analytics.update(100, tracker, [])
        
        tracker.track_states[4]['last_seen_frame'] = 150
        analytics.update(150, tracker, phase_3_exits=[4])
        
        self.assertIn(4, analytics.finalized_tracks)
        self.assertEqual(len(analytics.visits), 1)
        self.assertEqual(analytics.visits[0]['exit_frame'], 150)
        
        tracker.transitions.append({'track_id': 4, 'from_zone': 'CHECKOUT', 'to_zone': 'ENTRANCE', 'transition_frame': 160})
        analytics.update(160, tracker, [])
        self.assertEqual(len(analytics.visits), 1)

    def test_temporary_track_loss(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=30.0, max_lost_frames=30)
        
        tracker.track_states[5] = {'last_seen_frame': 100}
        tracker.transitions.append({'track_id': 5, 'from_zone': 'NO ZONE', 'to_zone': 'ENTRANCE', 'transition_frame': 100})
        analytics.update(100, tracker, [])
        
        tracker.track_states[5]['last_seen_frame'] = 100
        analytics.update(120, tracker, [])
        
        self.assertNotIn(5, analytics.finalized_tracks)
        self.assertIn(5, analytics.open_visits)
        
    def test_no_zone_handling(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=30.0, max_lost_frames=30)
        
        tracker.track_states[6] = {'last_seen_frame': 100}
        tracker.transitions.append({'track_id': 6, 'from_zone': 'NO ZONE', 'to_zone': 'ENTRANCE', 'transition_frame': 100})
        analytics.update(100, tracker, [])
        
        tracker.track_states[6]['last_seen_frame'] = 150
        tracker.transitions.append({'track_id': 6, 'from_zone': 'ENTRANCE', 'to_zone': 'NO ZONE', 'transition_frame': 150})
        analytics.update(150, tracker, [])
        
        self.assertNotIn(6, analytics.open_visits)
        self.assertEqual(len(analytics.visits), 1)
        self.assertEqual(analytics.visits[0]['zone'], 'ENTRANCE')
        
        tracker.track_states[6]['last_seen_frame'] = 200
        tracker.transitions.append({'track_id': 6, 'from_zone': 'NO ZONE', 'to_zone': 'CENTRAL AISLE', 'transition_frame': 200})
        analytics.update(200, tracker, [])
        
        self.assertIn(6, analytics.open_visits)
        self.assertEqual(analytics.open_visits[6]['zone'], 'CENTRAL AISLE')

    def test_transition_statistics(self):
        tracker = MockZoneTracker()
        analytics = ZoneAnalytics(fps=30.0, max_lost_frames=30)
        
        tracker.track_states[7] = {'last_seen_frame': 10}
        tracker.transitions.append({'track_id': 7, 'from_zone': 'NO ZONE', 'to_zone': 'ENTRANCE', 'transition_frame': 10})
        analytics.update(10, tracker, [])
        
        tracker.track_states[7]['last_seen_frame'] = 20
        tracker.transitions.append({'track_id': 7, 'from_zone': 'ENTRANCE', 'to_zone': 'CENTRAL AISLE', 'transition_frame': 20})
        analytics.update(20, tracker, [])
        
        tracker.track_states[7]['last_seen_frame'] = 30
        tracker.transitions.append({'track_id': 7, 'from_zone': 'CENTRAL AISLE', 'to_zone': 'PRODUCT / SHELF', 'transition_frame': 30})
        analytics.update(30, tracker, [])
        
        analytics.update(30, tracker, phase_3_exits=[7])
        
        stats = analytics.get_transition_statistics()
        self.assertEqual(stats['ENTRANCE -> CENTRAL AISLE'], 1)
        self.assertEqual(stats['CENTRAL AISLE -> PRODUCT / SHELF'], 1)

if __name__ == '__main__':
    unittest.main()
