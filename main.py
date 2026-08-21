import argparse
import os
import sys
from src.video_processor import VideoProcessor

def print_header(source):
    print("RetailVision AI By Shazim Javed")
    print("────────────────────────────────────")
    print(f"Input: {source}\n")
    print("[1/5] Detecting & tracking...")
    print("[2/5] Counting customers...")
    print("[3/5] Analyzing zones...")
    print("[4/5] Generating heatmap...")
    print("[5/5] Exporting analytics...\n")

def print_footer(metrics):
    print("Processing complete.\n")
    print(f"Customers: {metrics.get('customers', 0)}")
    print(f"Entries: {metrics.get('entries', 0)}")
    print(f"Exits: {metrics.get('exits', 0)}")
    print(f"Occupancy: {metrics.get('occupancy', 0)}")
    print("Zones analyzed: 4\n")
    print("Outputs:")
    print("  analytics.json")
    print("  heatmap_analytics.json")
    print("  customer_heatmap.png")
    print("  processed video")

def main():
    parser = argparse.ArgumentParser(description="RetailVision AI Unified Production Runner")
    parser.add_argument("--source", type=str, required=True, help="Path to input video")
    parser.add_argument("--output", type=str, default="output/processed.mp4", help="Path to output video")
    parser.add_argument("--model", type=str, default="models/yolov8s.pt", help="Path to YOLO model (e.g. models/yolov8s.pt)")
    
    # Optional debug flags (not required for normal execution)
    parser.add_argument("--zone-debug", action="store_true", help="Enable zone occupancy debug overlay")
    parser.add_argument("--analytics-debug", action="store_true", help="Enable analytics debug overlay")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"ERROR: Input video not found:\n{args.source}")
        sys.exit(1)

    print_header(args.source)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    model_path = args.model

    try:
        processor = VideoProcessor(
            source_path=args.source,
            output_path=args.output,
            model_path=model_path,
            track=True,
            count=True,
            zones_enabled=True,
            zone_debug=args.zone_debug,
            analytics_debug=args.analytics_debug,
            analytics=True,
            heatmap_enabled=True
        )
        
        metrics = processor.process_video()
        
        if not metrics:
            print("ERROR: Unable to open input video or processing failed.")
            sys.exit(1)
            
        print_footer(metrics)

    except Exception as e:
        print(f"\nERROR: Processing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
