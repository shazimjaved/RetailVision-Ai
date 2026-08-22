import cv2
import time
import math
from .detector import PersonDetector

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

import numpy as np
from .detector import PersonDetector
from .zone_tracker import ZoneTracker
from .zone_analytics import ZoneAnalytics
from .movement_heatmap import MovementHeatmap

class VideoProcessor:
    def __init__(self, source_path, output_path, model_path="yolov8s.pt", track=False, count=False, line_coords=None, zones_enabled=False, zone_debug=False, analytics_debug=False, analytics=False, heatmap_enabled=False):
        self.source_path = source_path
        self.output_path = output_path
        self.count = count
        self.zones_enabled = zones_enabled
        self.zone_debug = zone_debug
        self.analytics_debug = analytics_debug
        self.analytics = analytics
        self.heatmap_enabled = heatmap_enabled
        self.track = track if not (count or zones_enabled) else True
        self.line_coords = line_coords
        self.detector = PersonDetector(model_path=model_path)
        
        if self.zones_enabled:
            self.zone_tracker = ZoneTracker(debounce_frames=10, max_lost_frames=30)

        

        self.base_zones = {
            "CHECKOUT": np.array([
                (60, 250),
                (470, 160),
                (510, 230),
                (500, 390),
                (530, 540),
                (540, 700),
                (450, 800),
                (60, 930),
            ], np.int32),

            "CENTRAL AISLE": np.array([
                (470, 160),
                (600, 180),
                (660, 260),
                (710, 380),
                (970, 500),
                (1130, 640),
                (1280, 760),
                (1050, 1008),
                (580, 1008),
                (450, 800),
                (540, 700),
                (530, 540),
                (500, 390),
                (510, 230),
            ], np.int32),

            "PRODUCT / SHELF": np.array([
                (680, 170),   # top-left extended higher up back aisle floor
                (1080, 130),  # top-right extended higher up back shelf floor
                (1250, 240),  # right edge upper
                (1420, 370),  # right edge along shelf base
                (1580, 500),  # right edge along shelf base
                (1720, 600),  # right edge along shelf base
                (1860, 710),  # right edge near doorway fixture
                (1620, 770),  # bottom-right (above doorway mat)
                (1300, 760),  # bottom-left (bordering central aisle)
                (1180, 620),  # left edge (outside red boxes)
                (1040, 480),  # left-mid
                (900, 330),   # left-upper
                (780, 220),   # left top transition
            ], np.int32),

            "ENTRANCE": np.array([
                (1380, 830),  # top-left on dark entrance mat
                (1620, 770),  # top-mid of mat area
                (1860, 710),  # top-right near doorway threshold
                (1920, 730),  # right edge top
                (1920, 1008), # right edge bottom
                (1350, 1008), # bottom-left on mat
            ], np.int32),
        }
        self.zones = self.base_zones
        
    def process_video(self):
        cap = cv2.VideoCapture(self.source_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {self.source_path}")
            return False

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0:
            fps = 30.0 # fallback

        # Scale zones to video resolution if different from 1920x1008
        scale_x = width / 1920.0
        scale_y = height / 1008.0
        if scale_x != 1.0 or scale_y != 1.0:
            self.zones = {
                name: np.array([(int(x * scale_x), int(y * scale_y)) for x, y in poly], np.int32)
                for name, poly in self.base_zones.items()
            }
        else:
            self.zones = self.base_zones

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))

        if self.heatmap_enabled:
            self.heatmap = MovementHeatmap(width, height)
            self.tracked_samples = 0
            self.first_frame = None
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_count = 0
        total_unique_ids = set()
        max_simultaneous_ids = 0
        frames_with_ids = 0
        id_persists = False
        prev_ids = set()
        
        total_conf = 0.0
        total_detections = 0
        max_detections = 0
        
        # Counting state
        if self.line_coords:
            x1_l, y1_l, x2_l, y2_l = self.line_coords
        else:
            # Default line in 1920x1008 space, scaled to current video
            dl = (1050, 1080, 1700, 710)
            x1_l = int(dl[0] * scale_x)
            y1_l = int(dl[1] * scale_y)
            x2_l = int(dl[2] * scale_x)
            y2_l = int(dl[3] * scale_y)
            
        default_line = (x1_l, y1_l, x2_l, y2_l)
        total_entries = 0
        total_exits = 0
        total_crossings = 0
        track_state = {}
        cooldown_frames = 15
        
        # Zone Occupancy State
        # Handled by ZoneTracker class now
        if self.zones_enabled:
            self.zone_analytics = ZoneAnalytics(fps=fps, max_lost_frames=self.zone_tracker.max_lost_frames)
        
        start_time_processing = time.time()
        prev_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if self.heatmap_enabled and self.first_frame is None:
                self.first_frame = frame.copy()
                
            frame_count += 1
            
            # 1. Detection (MUST RUN ON CLEAN FRAME)
            result = self.detector.detect(frame, track=self.track)
            
            # Draw Zones Visualization
            if self.zones_enabled:
                overlay = frame.copy()
                colors = {
                    "CHECKOUT": (0, 165, 255),       # Orange
                    "CENTRAL AISLE": (255, 255, 0),  # Cyan
                    "PRODUCT / SHELF": (255, 0, 255),# Magenta
                    "ENTRANCE": (0, 255, 0)          # Green
                }
                for zone_name, polygon in self.zones.items():
                    color = colors.get(zone_name, (255, 255, 255))
                    cv2.fillPoly(overlay, [polygon], color)
                
                cv2.addWeighted(overlay, 0.12, frame, 0.88, 0, frame)
                
                for zone_name, polygon in self.zones.items():
                    color = colors.get(zone_name, (255, 255, 255))
                    cv2.polylines(frame, [polygon], isClosed=True, color=color, thickness=1)
                    
                    M = cv2.moments(polygon)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = polygon[0][0], polygon[0][1]
                        
                    (tw, th), _ = cv2.getTextSize(zone_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (cX - tw//2 - 3, cY - th//2 - 3), (cX + tw//2 + 3, cY + th//2 + 3), (0, 0, 0), -1)
                    cv2.putText(frame, zone_name, (cX - tw//2, cY + th//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # 2. Draw bounding boxes
            person_count = 0
            current_frame_ids = set()
            store_exits = []
            
            if result.boxes:
                frame_detections = len(result.boxes)
                total_detections += frame_detections
                if frame_detections > max_detections:
                    max_detections = frame_detections
                    
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    total_conf += conf
                    person_count += 1
                    
                    # Extract tracking ID if present
                    track_id = None
                    current_zone = ""
                    if self.track and box.id is not None:
                        track_id = int(box.id[0])
                        current_frame_ids.add(track_id)
                        total_unique_ids.add(track_id)
                        
                        if self.heatmap_enabled:
                            cx = int((x1 + x2) / 2)
                            cy = int((y1 + y2) / 2)
                            self.heatmap.add_point(cx, cy, weight=1.0, radius=20)
                            self.tracked_samples += 1
                        
                        # Calculate bottom-center for counting and zone analytics
                        if self.count or self.zones_enabled:
                            px = int((x1 + x2) / 2)
                            py = int(y2)
                            
                            # Counting Logic
                            if self.count:
                                cv2.circle(frame, (px, py), 4, (0, 255, 255), -1)
                                # Counting Logic (Segment Intersection)
                                if track_id not in track_state:
                                    track_state[track_id] = {'last_point': (px, py), 'last_crossing_frame': -cooldown_frames, 'last_direction': None}
                                else:
                                    last_point = track_state[track_id]['last_point']
                                    last_crossing_frame = track_state[track_id]['last_crossing_frame']
                                    last_direction = track_state[track_id]['last_direction']
                                    
                                    A = (x1_l, y1_l)
                                    B = (x2_l, y2_l)
                                    C = last_point
                                    D = (px, py)
                                    
                                    if (frame_count - last_crossing_frame) > cooldown_frames:
                                        if intersect(A, B, C, D):
                                            # Calculate direction using cross product of AB and CD
                                            cross = (B[0] - A[0]) * (D[1] - C[1]) - (B[1] - A[1]) * (D[0] - C[0])
                                            
                                            # Filter out micro-movements (jitter) that don't represent a real physical crossing
                                            if abs(cross) > 1000:
                                                direction = "ENTRY" if cross < 0 else "EXIT"
                                                
                                                # Block consecutive same-direction events for the same ID
                                                if direction != last_direction:
                                                    if direction == "ENTRY":
                                                        total_entries += 1
                                                    else:
                                                        total_exits += 1
                                                        store_exits.append(track_id)
                                                    total_crossings += 1
                                                    
                                                    track_state[track_id]['last_crossing_frame'] = frame_count
                                                    track_state[track_id]['last_direction'] = direction
                                            
                                    # Always update last point
                                    track_state[track_id]['last_point'] = (px, py)
                            
                            # Zone Detection & State Tracking
                            if self.zones_enabled:
                                zone_priority = ["ENTRANCE", "CHECKOUT", "PRODUCT / SHELF", "CENTRAL AISLE"]
                                best_zone = None
                                
                                for z_name in zone_priority:
                                    polygon = self.zones[z_name]
                                    dist = cv2.pointPolygonTest(polygon, (px, py), False)
                                    if dist >= 0:
                                        best_zone = z_name
                                        break
                                
                                self.zone_tracker.update(frame_count, [(track_id, best_zone)])
                                current_zone = self.zone_tracker.get_current_zone(track_id, frame_count)
                    
                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label
                    if track_id is not None:
                        label = f"ID: {track_id} | Person | {conf:.2f}"
                        if current_zone:
                            label += f" | {current_zone}"
                    else:
                        label = f"Person: {conf:.2f}"
                        
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), (0, 255, 0), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # Update analytics state once per frame
            if self.zones_enabled:
                self.zone_analytics.update(frame_count, self.zone_tracker, store_exits)

            # Update tracking stats
            if len(current_frame_ids) > 0:
                frames_with_ids += 1
            if len(current_frame_ids) > max_simultaneous_ids:
                max_simultaneous_ids = len(current_frame_ids)
            if not id_persists and len(current_frame_ids.intersection(prev_ids)) > 0:
                id_persists = True
            prev_ids = current_frame_ids
            # Update occupancy stats (Handled dynamically by ZoneTracker)

            # 3. Calculate FPS
            curr_time = time.time()
            current_fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            # 4. Display Info (FPS and Person Count)
            hud_w = 440
            hud_h = 135 if self.count else 95
            hud_x = 20
            hud_y = height - hud_h - 20
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (hud_x, hud_y), (hud_x + hud_w, hud_y + hud_h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
            
            cv2.putText(frame, "RetailVision AI", (hud_x + 15, hud_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            info_text = f"Active Persons: {person_count} | FPS: {current_fps:.1f}"
            cv2.putText(frame, info_text, (hud_x + 15, hud_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 220, 220), 2)
            
            # Draw Occupancy Panel
            if self.zones_enabled and self.zone_debug:
                panel_w = 260
                panel_h = 280
                panel_x = width - panel_w
                panel_y = 10
                
                # Draw semi-transparent background panel
                overlay = frame.copy()
                cv2.rectangle(overlay, (panel_x, panel_y), (width, panel_y + panel_h), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
                
                y_offset = panel_y + 25
                x_offset = panel_x + 10
                
                cv2.putText(frame, "ZONE OCCUPANCY", (x_offset, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, "---------------", (x_offset, y_offset + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 35
                
                counts = self.zone_tracker.get_occupancy_counts(frame_count, list(self.zones.keys()))
                for z_name in list(self.zones.keys()) + ["NO ZONE"]:
                    text = f"{z_name[:12]:<12}: {counts.get(z_name, 0)}"
                    cv2.putText(frame, text, (x_offset, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    y_offset += 20
                    
                y_offset += 10
                cv2.putText(frame, "RECENT TRANSITIONS", (x_offset, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, "-----------------", (x_offset, y_offset + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 35
                
                transitions = self.zone_tracker.get_recent_transitions(5)
                for t in reversed(transitions):
                    text = f"ID {t['track_id']} {t['from_zone'][:8]}->{t['to_zone'][:8]}"
                    cv2.putText(frame, text, (x_offset, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220, 220, 220), 1)
                    y_offset += 15
                    
            # Draw Analytics HUD
            if self.zones_enabled:
                panel_w = 340
                panel_h = 145
                panel_x = width - panel_w - 20
                panel_y = 20
                
                overlay = frame.copy()
                cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
                
                ay_offset = panel_y + 25
                ax_offset = panel_x + 10
                
                cv2.putText(frame, "JOURNEY ANALYTICS", (ax_offset, ay_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                ay_offset += 25
                cv2.putText(frame, "ACTIVE JOURNEYS", (ax_offset, ay_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                ay_offset += 20
                
                for track_id, segments in list(self.zone_analytics.journeys.items())[-5:]:
                    if track_id in self.zone_analytics.finalized_tracks:
                        continue
                    if segments:
                        journey_str = " -> ".join([s['zone'] for s in segments])
                        if len(journey_str) > 45:
                            journey_str = "..." + journey_str[-42:]
                        text = f"ID {track_id:<2}: {journey_str}"
                        cv2.putText(frame, text, (ax_offset, ay_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                        ay_offset += 15
            
            # Draw Counting Overlays
            if self.count:
                # Draw the localized segment
                cv2.line(frame, (x1_l, y1_l), (x2_l, y2_l), (255, 0, 0), 3)
                
                # Draw INSIDE/OUTSIDE dynamic labels based on line orientation
                dx = x2_l - x1_l
                dy = y2_l - y1_l
                length = math.hypot(dx, dy)
                if length > 0:
                    nx = dy / length * 60
                    ny = -dx / length * 60
                    mx = int((x1_l + x2_l) / 2)
                    my = int((y1_l + y2_l) / 2)
                    cv2.putText(frame, "INSIDE", (int(mx + nx) - 30, int(my + ny)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 100), 2)
                    cv2.putText(frame, "OUTSIDE", (int(mx - nx) - 40, int(my - ny)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 255), 2)

                occupancy = max(0, total_entries - total_exits)
                count_text = f"ENTRY: {total_entries} | EXIT: {total_exits} | OCCUPANCY: {occupancy}"
                cv2.putText(frame, count_text, (hud_x + 15, hud_y + 120), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 0), 2)
            
            # Write frame
            out.write(frame)
            
            if frame_count % 30 == 0:
                if total_frames > 0:
                    print(f"Processing: {frame_count} / {total_frames} frames", end='\r')
                else:
                    print(f"Processed {frame_count} frames...", end='\r')

        # Release resources
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        total_processing_time = time.time() - start_time_processing
        overall_fps = frame_count / total_processing_time if total_processing_time > 0 else 0
        avg_conf = total_conf / total_detections if total_detections > 0 else 0
        
        if self.zones_enabled:
            # Force finalize any remaining open visits at the end of the video
            for track_id in list(self.zone_analytics.open_visits.keys()):
                self.zone_analytics._close_visit(track_id, frame_count)
                self.zone_analytics.finalized_tracks.add(track_id)
                
        if self.heatmap_enabled and self.first_frame is not None:
            # Generate JSON
            import json
            import os
            
            heatmap_start = time.time()
            max_loc, max_val = self.heatmap.get_peak_density()
            heatmap_metrics = {
                "total_frames": frame_count,
                "tracked_position_samples": self.tracked_samples,
                "heatmap_resolution": {
                    "width": width,
                    "height": height
                },
                "peak_density_location": {
                    "x": int(max_loc[0]),
                    "y": int(max_loc[1])
                },
                "peak_density_value": max_val,
                "processing_fps": overall_fps
            }
            
            os.makedirs("output", exist_ok=True)
            out_json_path = "output/heatmap_analytics.json"
            out_png_path = "output/customer_heatmap.png"
            
            with open(out_json_path, "w") as f:
                json.dump(heatmap_metrics, f, indent=4)
                
            final_heatmap_img = self.heatmap.generate_heatmap(self.first_frame, blur_radius=71, alpha_factor=0.75)
            cv2.imwrite(out_png_path, final_heatmap_img)
            
        if getattr(self, 'analytics', False):
            from .analytics_report import AnalyticsDashboard
            AnalyticsDashboard.generate_report(
                output_path=self.output_path,
                total_tracking_ids=len(total_unique_ids),
                total_analytics_customers=len(self.zone_analytics.journeys) if self.zones_enabled else 0,
                entries=total_entries if self.count else 0,
                exits=total_exits if self.count else 0,
                final_occupancy=max(0, total_entries - total_exits) if self.count else 0,
                zone_stats=self.zone_analytics.get_zone_statistics() if self.zones_enabled else {},
                transition_stats=self.zone_analytics.get_transition_statistics() if self.zones_enabled else {}
            )
            
        return {
            "customers": len(self.zone_analytics.journeys) if self.zones_enabled else 0,
            "entries": total_entries if self.count else 0,
            "exits": total_exits if self.count else 0,
            "occupancy": max(0, total_entries - total_exits) if self.count else 0
        }
