import cv2
import time
from .detector import PersonDetector

class VideoProcessor:
    def __init__(self, source_path, output_path, model_path="yolov8n.pt"):
        self.source_path = source_path
        self.output_path = output_path
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
        
        prev_time = time.time()
        
        print(f"Processing video: {self.source_path}")
        print(f"Output will be saved to: {self.output_path}")

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # 1. Detection
            result = self.detector.detect(frame)
            
            # 2. Draw bounding boxes
            person_count = 0
            if result.boxes:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    person_count += 1
                    
                    # Draw box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw label
                    label = f"Person: {conf:.2f}"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw, y1), (0, 255, 0), -1)
                    cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            # 3. Calculate FPS
            curr_time = time.time()
            current_fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            # 4. Display Info (FPS and Person Count)
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
        print("Processing complete.")
        return True
