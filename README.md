# RetailVision AI

A computer vision portfolio project for retail store analytics built with Python, OpenCV, and Ultralytics YOLO.

## Architecture

```
Input Video → YOLOv8s (Person Detection) → BoT-SORT (Multi-Object Tracking) → Annotated Output Video
```

- **Detector:** YOLOv8s — selected over YOLOv8n after benchmarking showed 22% higher person detection coverage (13.4 vs 11.0 avg detections/frame) with stronger confidence scores.
- **Tracker:** BoT-SORT (default Ultralytics configuration, ReID disabled) — selected after controlled experiments against ByteTrack and BoT-SORT+ReID. BoT-SORT reduced tracking fragmentation by ~24% compared to ByteTrack while preserving full detection coverage. Its camera motion compensation (sparseOptFlow) handles the minor camera movement in retail CCTV footage.

> **Note:** Some identity fragmentation remains during extended occlusions and person crossings. This is expected behavior for an IoU-based tracker without dedicated re-identification.

## Phases

### Phase 1: Video Ingestion & Person Detection
Reads a local video file, runs YOLOv8s for person detection, and outputs the processed video with bounding boxes, confidence scores, and person count per frame.

### Phase 2: Multi-Object Tracking
Integrates BoT-SORT to assign persistent tracking IDs to detected persons across video frames.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```
2. Place a test video in the `input/` directory.

## Usage

### Detection Only (Phase 1)
```bash
python main.py --source input/sample.mp4
```
Output: `output/processed.mp4`

### Detection + Tracking (Phase 2)
```bash
python main.py --source input/sample.mp4 --track
```
Output: `output/tracking_result.mp4`

### Options
| Flag | Default | Description |
|------|---------|-------------|
| `--source` | — | Path to input video (required) |
| `--track` | off | Enable BoT-SORT multi-object tracking |
| `--model` | `yolov8s.pt` | YOLO model variant |
| `--output` | auto | Custom output path |
