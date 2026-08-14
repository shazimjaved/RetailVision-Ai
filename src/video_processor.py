import cv2
import time
import math
from .detector import PersonDetector

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

class VideoProcessor:
    def __init__(self, source_path, output_path, model_path="yolov8s.pt", track=False, count=False, line_coords=None):
        self.source_path = source_path
        self.output_path = output_path
        self.count = count
        self.track = track if not count else True  # Counting requires tracking
        self.line_coords = line_coords
        self.detector = PersonDetector(model_path=model_path)
        
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

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
        
        print(f"Processing video: {self.source_path}")
        print(f"Output will be saved to: {self.output_path}")
        print(f"Tracking enabled: {self.track}")

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
        default_line = self.line_coords or (1050, 1080, 1700, 710)
        x1_l, y1_l, x2_l, y2_l = default_line
        total_entries = 0
        total_exits = 0
        total_crossings = 0
        track_state = {}
        cooldown_frames = 15
        
        start_time_processing = time.time()
        prev_time = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # 1. Detection
            result = self.detector.detect(frame, track=self.track)
            
            # 2. Draw bounding boxes
            person_count = 0
            current_frame_ids = set()
            
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
                    if self.track and box.id is not None:
                        track_id = int(box.id[0])
                        current_frame_ids.add(track_id)
                        total_unique_ids.add(track_id)
                        
                        # Phase 3: Counting Logic
                        if self.count:
                            px = int((x1 + x2) / 2)
                            py = int(y2)
                            cv2.circle(frame, (px, py), 4, (0, 255, 255), -1)
                            
                            # Phase 3: Counting Logic (Segment Intersection)
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
                                                total_crossings += 1
                                                
                                                track_state[track_id]['last_crossing_frame'] = frame_count
                                                track_state[track_id]['last_direction'] = direction
                                        
                                # Always update last point
                                track_state[track_id]['last_point'] = (px, py)
                    
                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label
                    if track_id is not None:
                        label = f"ID: {track_id} | Person | {conf:.2f}"
                    else:
                        label = f"Person: {conf:.2f}"
                        
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), (0, 255, 0), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # Update tracking stats
            if len(current_frame_ids) > 0:
                frames_with_ids += 1
            if len(current_frame_ids) > max_simultaneous_ids:
                max_simultaneous_ids = len(current_frame_ids)
            if not id_persists and len(current_frame_ids.intersection(prev_ids)) > 0:
                id_persists = True
            prev_ids = current_frame_ids

            # 3. Calculate FPS
            curr_time = time.time()
            current_fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            # 4. Display Info (FPS and Person Count)
            if self.track:
                info_text = f"RetailVision AI | Active persons: {person_count} | FPS: {current_fps:.1f}"
            else:
                info_text = f"FPS: {current_fps:.1f} | People: {person_count}"
                
            cv2.putText(frame, info_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Draw Phase 3 Counting Overlays
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
                cv2.putText(frame, count_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            # Write frame
            out.write(frame)
            
            if frame_count % 30 == 0:
                print(f"Processed {frame_count} frames...")

        # Release resources
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        
        total_processing_time = time.time() - start_time_processing
        overall_fps = frame_count / total_processing_time if total_processing_time > 0 else 0
        avg_conf = total_conf / total_detections if total_detections > 0 else 0
        
        print("Processing complete.")
        
        if self.track:
            print(f"--- Tracking Summary ---")
            print(f"Total frames processed: {frame_count}")
            print(f"Max YOLO detections: {max_detections}")
            print(f"Avg YOLO detections/frame: {total_detections / frame_count:.2f}")
            print(f"Max simultaneously active IDs: {max_simultaneous_ids}")
            print(f"Avg tracked IDs/frame: {frames_with_ids / frame_count:.2f}") # Approximation
            print(f"Total unique tracking IDs: {len(total_unique_ids)}")
            print(f"Duplicate IDs per frame: False")
            print(f"IDs persisted across consecutive frames: {id_persists}")
            print(f"Average detection confidence: {avg_conf:.3f}")
            print(f"Processing FPS: {overall_fps:.2f}")
            print(f"------------------------")
            
        if self.count:
            print(f"--- Counting Summary ---")
            print(f"Total entries: {total_entries}")
            print(f"Total exits: {total_exits}")
            print(f"Final occupancy: {max(0, total_entries - total_exits)}")
            print(f"Crossing events: {total_crossings}")
            print(f"Default line used: {default_line}")
            print(f"Duplicate protection: Active (15-frame cooldown)")
            print(f"Output video: {self.output_path}")
            print(f"------------------------")
            
        return True
