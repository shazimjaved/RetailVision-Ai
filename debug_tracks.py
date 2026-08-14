import cv2
from src.video_processor import VideoProcessor
import numpy as np

cap = cv2.VideoCapture("input/sample.mp4")
processor = VideoProcessor("input/sample.mp4", "output/debug.mp4", track=True)

track_histories = {39: [], 324: []}

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    frame_count += 1
    
    result = processor.detector.detect(frame, track=True)
    if result and result.boxes and result.boxes.id is not None:
        boxes = result.boxes
        for i in range(len(boxes.id)):
            track_id = int(boxes.id[i])
            if track_id in track_histories:
                x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                px = int((x1 + x2) / 2)
                py = int(y2)
                track_histories[track_id].append((frame_count, px, py))
    
    if frame_count > 600: break

print("Track 39:")
for f, x, y in track_histories[39]:
    print(f"Frame {f}: ({x}, {y})")

print("\nTrack 324:")
for f, x, y in track_histories[324]:
    print(f"Frame {f}: ({x}, {y})")
