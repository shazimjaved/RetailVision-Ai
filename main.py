import argparse
import os
from src.video_processor import VideoProcessor

def main():
    parser = argparse.ArgumentParser(description="RetailVision AI")
    parser.add_argument("--source", type=str, default=None, help="Path to input video")
    parser.add_argument("--output", type=str, default=None, help="Path to output video")
    parser.add_argument("--track", action="store_true", help="Enable multi-object tracking (Phase 2)")
    parser.add_argument("--count", action="store_true", help="Enable entry/exit counting (Phase 3)")
    parser.add_argument("--zones", action="store_true", help="Enable zone visualization (Phase 4.1)")
    parser.add_argument("--zone-debug", action="store_true", help="Enable zone transitions/occupancy debug overlay (Phase 4.2)")
    parser.add_argument("--analytics-debug", action="store_true", help="Enable zone analytics debug overlay (Phase 4.3)")
    parser.add_argument("--analytics", action="store_true", help="Generate final retail analytics dashboard and JSON report (Phase 4.4)")
    parser.add_argument("--line", type=int, nargs=4, help="Counting line coordinates: x1 y1 x2 y2", default=None)
    parser.add_argument("--model", type=str, default="yolov8s.pt", help="Path to YOLO model (e.g. yolov8n.pt, yolov8s.pt)")
    parser.add_argument("--test", action="store_true", help="Run a quick initialization test without a video")
    args = parser.parse_args()

    # Determine default output path based on tracking mode
    output_path = args.output
    if output_path is None:
        if args.zones:
            output_path = "output/zones_result.mp4"
        elif args.count:
            output_path = "output/counting_result.mp4"
        elif args.track:
            output_path = "output/tracking_result.mp4"
        else:
            output_path = "output/processed.mp4"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Ensure models directory exists for downloading weights
    os.makedirs("models", exist_ok=True)
    # Strictly enforce that the model goes into the models/ folder
    model_filename = os.path.basename(args.model)
    model_path = os.path.join("models", model_filename)
    
    if args.test:
        print("Running initialization test...")
        from src.detector import PersonDetector
        try:
            detector = PersonDetector(model_path=args.model)
            print("Model initialized successfully!")
            print("Initialization test passed.")
            return
        except Exception as e:
            print(f"Initialization test failed: {e}")
            return

    if args.source is None:
        print("Error: Please provide an input video using --source")
        return
        
    if not os.path.exists(args.source):
        print(f"Error: Input video not found at {args.source}")
        return

    processor = VideoProcessor(
        source_path=args.source,
        output_path=output_path,
        model_path=model_path,
        track=args.track,
        count=args.count,
        line_coords=args.line,
        zones_enabled=args.zones,
        zone_debug=args.zone_debug,
        analytics_debug=args.analytics_debug,
        analytics=args.analytics
    )
    processor.process_video()

if __name__ == "__main__":
    main()
