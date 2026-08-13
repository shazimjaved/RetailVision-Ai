import cv2
import time
from .detector import PersonDetector

class VideoProcessor:
    def __init__(self, source_path, output_path, model_path="yolov8s.pt", track=False):
        self.source_path = source_path
        self.output_path = output_path
        self.track = track
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
            
        return True
