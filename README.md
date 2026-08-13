# RetailVision AI

RetailVision AI is a computer vision portfolio project designed for retail analytics.

## Phase 1: Video Ingestion & Person Detection
This phase implements a minimal Python application that reads a local video file, runs a YOLOv8 model for person detection, and outputs the processed video with bounding boxes, confidence scores, FPS, and the total person count per frame.

## Setup
1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place a test video in the `input/` directory.

## Usage
Run the main script:
```bash
python main.py --source input/sample.mp4
```
