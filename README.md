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

### Phase 3: Customer Counting
Implements an accurate segment-based counting line at the store entrance to track customer entries, exits, and current occupancy. Features include bounding-box bottom-center contact points, jitter filtering, and a 15-frame debounce for highly reliable physical counting.

### Phase 4: Zone & Journey Analytics
Stateful zone occupancy tracking and customer journey analytics, producing aggregate metrics like zone visits, dwell times, and flow transitions.

### Phase 5: Web Dashboard
A professional React/Vite/Tailwind CSS frontend application that consumes the analytics data output by the Python pipeline to present a polished, real-time UI containing KPIs, zone performance charts, and customer flow visualizations.

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

### Customer Counting (Phase 3)
```bash
python main.py --source input/sample.mp4 --track --count
```
Output: `output/counting_result.mp4`

### Zone & Journey Analytics (Phase 4)
```bash
python main.py --source input/sample.mp4 --track --count --zones --zone-debug --analytics-debug
```
Output: `output/zones_result.mp4`

### Analytics Export (Phase 4.4)
```bash
python main.py --source input/sample.mp4 --track --count --zones --analytics
```
Output: Generates `output/analytics.json` containing the final processed retail metrics.

### Web Dashboard (Phase 5)
1. Generate the analytics data first (using the command above).
2. Start the React dashboard:
   ```bash
   cd dashboard
   npm run dev
   ```
3. Open `http://localhost:5173` in your browser.

### Options
| Flag | Default | Description |
|------|---------|-------------|
| `--source` | — | Path to input video (required) |
| `--track` | off | Enable BoT-SORT multi-object tracking |
| `--count` | off | Enable entry/exit counting (Phase 3) |
| `--zones` | off | Enable zone visualization (Phase 4.1) |
| `--zone-debug` | off | Enable zone transitions/occupancy debug overlay (Phase 4.2) |
| `--analytics-debug` | off | Enable zone analytics debug overlay (Phase 4.3) |
| `--model` | `yolov8s.pt` | YOLO model variant |
| `--output` | auto | Custom output path |
