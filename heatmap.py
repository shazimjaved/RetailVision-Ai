import argparse
import cv2
import os
import json
import time
import numpy as np

from src.detector import PersonDetector
from src.movement_heatmap import MovementHeatmap

def get_base_zones():
    # Helper to grab the zone polygons exactly as defined in Phase 4.1
    # We could import VideoProcessor but to stay isolated, we just define them identically
    return {
        "CHECKOUT": np.array([(60, 250), (470, 160), (510, 230), (500, 390), (530, 540), (540, 700), (450, 800), (60, 930)], np.int32),
        "CENTRAL AISLE": np.array([(470, 160), (600, 180), (660, 260), (710, 380), (970, 500), (1130, 640), (1280, 760), (1050, 1008), (580, 1008), (450, 800), (540, 700), (530, 540), (500, 390), (510, 230)], np.int32),
        "PRODUCT / SHELF": np.array([(680, 170), (1080, 130), (1250, 240), (1420, 370), (1580, 500), (1720, 600), (1860, 710), (1620, 770), (1300, 760), (1180, 620), (1040, 480), (900, 330), (780, 220)], np.int32),
        "ENTRANCE": np.array([(1380, 830), (1620, 770), (1860, 710), (1920, 730), (1920, 1008), (1350, 1008)], np.int32)
    }

def draw_zones(image, width, height):
    zones = get_base_zones()
    scale_x = width / 1920.0
    scale_y = height / 1008.0
    
    colors = {
        "CHECKOUT": (0, 165, 255),       
        "CENTRAL AISLE": (255, 255, 0),  
        "PRODUCT / SHELF": (255, 0, 255),
        "ENTRANCE": (0, 255, 0)          
    }
    
    for name, poly in zones.items():
        scaled_poly = np.array([(int(x * scale_x), int(y * scale_y)) for x, y in poly], np.int32)
        color = colors.get(name, (255,255,255))
        # Draw outline
        cv2.polylines(image, [scaled_poly], isClosed=True, color=color, thickness=2)

def main():
    parser = argparse.ArgumentParser(description="Phase 7: Customer Movement Heatmap")
    parser.add_argument("--source", type=str, required=True, help="Path to input video")
    parser.add_argument("--zones", action="store_true", help="Overlay zone boundaries on the heatmap")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: {args.source} not found.")
        return

    os.makedirs("output", exist_ok=True)
    
    cap = cv2.VideoCapture(args.source)
    if not cap.isOpened():
        print("Error opening video stream.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    out_mp4_path = "output/heatmap_result.mp4"
    out_png_path = "output/customer_heatmap.png"
    out_json_path = "output/heatmap_analytics.json"

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_mp4_path, fourcc, fps, (width, height))

    # We use baseline tracking to ensure consistency with frozen Phase 1-6
    detector = PersonDetector(model_path="models/yolov8s.pt")
    tracker_config = "cfg/botsort_baseline.yaml"
    
    heatmap = MovementHeatmap(width, height)
    
    frame_count = 0
    tracked_samples = 0
    start_time = time.time()
    
    first_frame = None

    print(f"Generating Phase 7 Movement Heatmap from {args.source}...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if first_frame is None:
            first_frame = frame.copy()

        frame_count += 1
        
        # Draw zones onto the background if requested, before blending
        bg_frame = frame.copy()
        if args.zones:
            draw_zones(bg_frame, width, height)

        # Detect and Track
        result = detector.detect(frame, track=True)
        
        if result.boxes:
            for box in result.boxes:
                # Only process tracked persons
                if box.id is not None:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Center of bounding box
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    
                    heatmap.add_point(cx, cy, weight=1.0, radius=20)
                    tracked_samples += 1

        # Generate ongoing heatmap overlay for the MP4 output
        # blur_radius of 71 gives a nice wide smooth spread for people
        blended_frame = heatmap.generate_heatmap(bg_frame, blur_radius=71, alpha_factor=0.65)
        out.write(blended_frame)

        if frame_count % 30 == 0:
            print(f"Processed {frame_count} frames, accumulated {tracked_samples} samples...")

    cap.release()
    out.release()
    
    # Generate final static PNG using the first frame as a clean background
    if first_frame is not None:
        if args.zones:
            draw_zones(first_frame, width, height)
            
        final_heatmap_img = heatmap.generate_heatmap(first_frame, blur_radius=71, alpha_factor=0.75)
        cv2.imwrite(out_png_path, final_heatmap_img)
        
    processing_time = time.time() - start_time
    
    # Generate JSON
    max_loc, max_val = heatmap.get_peak_density()
    metrics = {
        "total_frames": frame_count,
        "tracked_position_samples": tracked_samples,
        "heatmap_resolution": {
            "width": width,
            "height": height
        },
        "peak_density_location": {
            "x": int(max_loc[0]),
            "y": int(max_loc[1])
        },
        "peak_density_value": max_val,
        "processing_fps": frame_count / processing_time if processing_time > 0 else 0
    }
    
    with open(out_json_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print("\nPhase 7 Implementation Complete!")
    print(f"Outputs:")
    print(f" - MP4 Overlay: {out_mp4_path}")
    print(f" - Static PNG:  {out_png_path}")
    print(f" - Metrics:     {out_json_path}")
    
if __name__ == "__main__":
    main()
