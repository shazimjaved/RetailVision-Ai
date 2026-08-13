import argparse
import os
from src.video_processor import VideoProcessor

def main():
    parser = argparse.ArgumentParser(description="RetailVision AI - Phase 1")
    parser.add_argument("--source", type=str, default=None, help="Path to input video")
    parser.add_argument("--output", type=str, default="output/processed.mp4", help="Path to output video")
    parser.add_argument("--test", action="store_true", help="Run a quick initialization test without a video")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Ensure models directory exists for downloading weights
    os.makedirs("models", exist_ok=True)
    model_path = "models/yolov8n.pt"

    if args.test:
        print("Running initialization test...")
        from src.detector import PersonDetector
        try:
            detector = PersonDetector(model_path=model_path)
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

    processor = VideoProcessor(source_path=args.source, output_path=args.output, model_path=model_path)
    processor.process_video()

if __name__ == "__main__":
    main()
