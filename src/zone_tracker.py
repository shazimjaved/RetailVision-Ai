from typing import Dict, List, Optional, Tuple

class ZoneTracker:
    def __init__(self, debounce_frames: int = 10, max_lost_frames: int = 30):
        """
        Manages real-time zone occupancy and temporal state for tracked objects.
        
        Args:
            debounce_frames: Number of consecutive frames a person must be in a new zone 
                             before their confirmed zone changes (prevents flickering).
            max_lost_frames: Number of frames an ID can be missing before they are considered 
                             inactive and removed from occupancy counts.
        """
        self.debounce_frames = debounce_frames
        self.max_lost_frames = max_lost_frames
        
        # State per track_id
        # {
        #   track_id: {
        #       'current_zone': str or None,
        #       'candidate_zone': str or None,
        #       'candidate_frames': int,
        #       'last_seen_frame': int
        #   }
        # }
        self.track_states: Dict[int, Dict] = {}
        
        # Global transition history
        # List of dicts: {'track_id': int, 'from_zone': str, 'to_zone': str, 'start_frame': int, 'transition_frame': int}
        self.transitions: List[Dict] = []
        
    def update(self, frame_count: int, active_detections: List[Tuple[int, Optional[str]]]):
        """
        Updates the tracker with the detections from the current frame.
        
        Args:
            frame_count: Current video frame number.
            active_detections: List of tuples containing (track_id, detected_zone_from_geometry).
                               detected_zone_from_geometry can be None (NO_ZONE).
        """
        # Process active detections
        for track_id, detected_zone in active_detections:
            # Initialize if new track
            if track_id not in self.track_states:
                self.track_states[track_id] = {
                    'current_zone': None,
                    'candidate_zone': detected_zone,
                    'candidate_frames': 1,
                    'last_seen_frame': frame_count
                }
                # Optional: If you want immediate assignment on first sight without debounce:
                # self.track_states[track_id]['current_zone'] = detected_zone
                # self._record_transition(track_id, None, detected_zone, frame_count, frame_count)
            else:
                state = self.track_states[track_id]
                state['last_seen_frame'] = frame_count
                
                # If detected zone is different from candidate zone, reset candidate
                if detected_zone != state['candidate_zone']:
                    state['candidate_zone'] = detected_zone
                    state['candidate_frames'] = 1
                else:
                    state['candidate_frames'] += 1
                
                # Check debounce threshold
                if state['candidate_frames'] >= self.debounce_frames:
                    if state['current_zone'] != state['candidate_zone']:
                        self._record_transition(
                            track_id=track_id, 
                            from_zone=state['current_zone'], 
                            to_zone=state['candidate_zone'], 
                            start_frame=frame_count - self.debounce_frames + 1,
                            transition_frame=frame_count
                        )
                        state['current_zone'] = state['candidate_zone']
                        
    def _record_transition(self, track_id: int, from_zone: Optional[str], to_zone: Optional[str], start_frame: int, transition_frame: int):
        """Records a confirmed state change."""
        if from_zone == to_zone:
            return
            
        self.transitions.append({
            'track_id': track_id,
            'from_zone': from_zone if from_zone else "NO ZONE",
            'to_zone': to_zone if to_zone else "NO ZONE",
            'start_frame': start_frame,
            'transition_frame': transition_frame
        })

    def get_occupancy_counts(self, frame_count: int, zone_names: List[str]) -> Dict[str, int]:
        """
        Returns the number of *active* people currently confirmed in each zone.
        People who have not been seen for > max_lost_frames are excluded.
        """
        counts = {z: 0 for z in zone_names}
        counts["NO ZONE"] = 0
        
        for track_id, state in self.track_states.items():
            # Check if active
            if (frame_count - state['last_seen_frame']) <= self.max_lost_frames:
                cz = state['current_zone']
                if cz is not None:
                    counts[cz] = counts.get(cz, 0) + 1
                else:
                    counts["NO ZONE"] += 1
        return counts
        
    def get_current_zone(self, track_id: int, frame_count: int) -> Optional[str]:
        """Returns the confirmed current zone for an ID, if it's considered active."""
        state = self.track_states.get(track_id)
        if state and (frame_count - state['last_seen_frame']) <= self.max_lost_frames:
            return state['current_zone']
        return None
        
    def get_recent_transitions(self, limit: int = 5) -> List[Dict]:
        """Returns the N most recent transitions."""
        return self.transitions[-limit:] if self.transitions else []
