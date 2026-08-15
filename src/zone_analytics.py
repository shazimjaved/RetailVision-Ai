from typing import Dict, List, Set, Optional

class ZoneAnalytics:
    def __init__(self, fps: float, max_lost_frames: int):
        self.fps = fps if fps > 0 else 30.0
        self.max_lost_frames = max_lost_frames
        
        # Completed visits
        # List of dicts: {track_id, zone, entry_frame, exit_frame, entry_time, exit_time, dwell_seconds, visit_number}
        self.visits: List[Dict] = []
        
        # Currently open visits
        # Dict: track_id -> {zone, entry_frame, visit_number}
        self.open_visits: Dict[int, Dict] = {}
        
        # Completed structured segments per track
        # Dict: track_id -> [list of segment dicts]
        self.journeys: Dict[int, List[Dict]] = {}
        
        # Track IDs that have been permanently finalized (no further tracking)
        self.finalized_tracks: Set[int] = set()
        
        # Tracker transition index
        self.last_processed_transition = 0
        
        # Track visit numbers per zone per track_id
        # {track_id: {zone_name: visit_count}}
        self.visit_counters: Dict[int, Dict[str, int]] = {}

    def _open_visit(self, track_id: int, zone: str, entry_frame: int):
        """Internal method to open a new visit for a track_id."""
        if zone == "NO ZONE" or zone is None:
            return
            
        if track_id not in self.visit_counters:
            self.visit_counters[track_id] = {}
            
        self.visit_counters[track_id][zone] = self.visit_counters[track_id].get(zone, 0) + 1
        
        self.open_visits[track_id] = {
            "zone": zone,
            "entry_frame": entry_frame,
            "visit_number": self.visit_counters[track_id][zone]
        }
        
    def _close_visit(self, track_id: int, exit_frame: int):
        """Internal method to close the current open visit for a track_id."""
        if track_id not in self.open_visits:
            return None
            
        open_visit = self.open_visits.pop(track_id)
        
        # Ensure exit frame is at least entry frame to avoid negative dwell
        exit_frame = max(exit_frame, open_visit["entry_frame"])
        dwell_seconds = (exit_frame - open_visit["entry_frame"]) / self.fps
        
        completed_visit = {
            "track_id": track_id,
            "zone": open_visit["zone"],
            "entry_frame": open_visit["entry_frame"],
            "exit_frame": exit_frame,
            "entry_time": open_visit["entry_frame"] / self.fps,
            "exit_time": exit_frame / self.fps,
            "dwell_seconds": dwell_seconds,
            "visit_number": open_visit["visit_number"]
        }
        
        self.visits.append(completed_visit)
        
        if track_id not in self.journeys:
            self.journeys[track_id] = []
            
        segment = {
            "zone": completed_visit["zone"],
            "entry_frame": completed_visit["entry_frame"],
            "exit_frame": completed_visit["exit_frame"],
            "dwell_seconds": completed_visit["dwell_seconds"]
        }
        self.journeys[track_id].append(segment)
        
        return completed_visit

    def update(self, frame_count: int, zone_tracker, phase_3_exits: List[int]):
        """
        Updates the analytics state.
        
        Args:
            frame_count: Current frame number.
            zone_tracker: Reference to the ZoneTracker instance.
            phase_3_exits: List of track_ids that generated a Phase 3 EXIT crossing in this frame.
        """
        # 1. Process Phase 3 EXIT (Semantic Completion - PRIMARY)
        for track_id in phase_3_exits:
            if track_id not in self.finalized_tracks:
                self._close_visit(track_id, frame_count)
                self.finalized_tracks.add(track_id)
                
        # 2. Process Zone Tracker Transitions
        for i in range(self.last_processed_transition, len(zone_tracker.transitions)):
            t = zone_tracker.transitions[i]
            track_id = t['track_id']
            trans_frame = t['transition_frame']
            to_zone = t['to_zone']
            
            # Skip if track already finalized (e.g., via Phase 3 EXIT)
            if track_id in self.finalized_tracks:
                continue
                
            self._close_visit(track_id, trans_frame)
            self._open_visit(track_id, to_zone, trans_frame)
            
        self.last_processed_transition = len(zone_tracker.transitions)
        
        # 3. Process Fallback Completion (Permanent Track Loss)
        for track_id, state in list(zone_tracker.track_states.items()):
            if track_id in self.finalized_tracks:
                continue
                
            if frame_count - state['last_seen_frame'] > self.max_lost_frames:
                self._close_visit(track_id, state['last_seen_frame'])
                self.finalized_tracks.add(track_id)

    def get_zone_statistics(self) -> Dict[str, Dict]:
        """Returns aggregate analytics for each zone."""
        stats = {}
        for visit in self.visits:
            z = visit["zone"]
            if z not in stats:
                stats[z] = {
                    "unique_visitors": set(),
                    "total_visits": 0,
                    "total_dwell": 0.0,
                    "max_dwell": 0.0,
                    "min_dwell": float('inf')
                }
            
            s = stats[z]
            s["unique_visitors"].add(visit["track_id"])
            s["total_visits"] += 1
            dwell = visit["dwell_seconds"]
            s["total_dwell"] += dwell
            s["max_dwell"] = max(s["max_dwell"], dwell)
            s["min_dwell"] = min(s["min_dwell"], dwell)
            
        # Clean up sets into counts and compute averages
        for z, s in stats.items():
            s["unique_visitors_count"] = len(s["unique_visitors"])
            del s["unique_visitors"]
            s["avg_dwell"] = s["total_dwell"] / s["total_visits"] if s["total_visits"] > 0 else 0
            if s["min_dwell"] == float('inf'):
                s["min_dwell"] = 0.0
                
        return stats
        
    def get_transition_statistics(self) -> Dict[str, int]:
        """Returns counts of adjacent zone transitions across all journeys."""
        trans_counts = {}
        for track_id, segments in self.journeys.items():
            for i in range(len(segments) - 1):
                from_z = segments[i]['zone']
                to_z = segments[i+1]['zone']
                if from_z != to_z:
                    t_str = f"{from_z} -> {to_z}"
                    trans_counts[t_str] = trans_counts.get(t_str, 0) + 1
        return trans_counts
