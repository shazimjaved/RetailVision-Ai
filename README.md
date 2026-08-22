# 🛒 RetailVision AI
> Built by **Shazim Javed**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8s-yellow.svg)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8.svg?logo=opencv)](https://opencv.org/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg?logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF.svg?logo=vite)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC.svg?logo=tailwind-css)](https://tailwindcss.com/)

RetailVision AI is a mature, production-ready computer-vision retail analytics system. It converts standard CCTV footage into actionable, real-time retail intelligence, offering comprehensive spatial and journey analytics without requiring specialized hardware.

---

## 📸 System Previews

<div align="center">
  <img src="assets/screenshot.jpg" alt="Video Processing HUD" width="48%" style="border-radius: 8px; margin: 1%;"/>
  <img src="assets/image.png" alt="Analytics View 1" width="48%" style="border-radius: 8px; margin: 1%;"/>
  <img src="assets/image2.png" alt="Analytics View 2" width="48%" style="border-radius: 8px; margin: 1%;"/>
  <img src="assets/image3.png" alt="Analytics View 3" width="48%" style="border-radius: 8px; margin: 1%;"/>
</div>

---

## ✨ Core Capabilities

RetailVision AI processes video footage to extract the following intelligence:

- 🎯 **Person Detection & Tracking**: Powered by Ultralytics YOLOv8s and BoT-SORT multi-object tracking.
- 🚪 **Entry & Exit Counting**: Accurately counts customers entering and leaving the field of view.
- 📊 **Store Occupancy**: Maintains a real-time tally of current store occupancy.
- 🏪 **Zone Analytics**: Tracks customer presence across 4 predefined retail zones.
- 🗺️ **Customer Journeys & Dwell Time**: Analyzes how long customers spend in each zone and maps their path through the store.
- 🌡️ **Movement Heatmaps**: Generates a spatial density heatmap showing the most highly trafficked areas.
- 💻 **Web Dashboard**: An interactive React/Vite/Tailwind dashboard to visualize the generated JSON analytics.

---

## 🚀 Quick Start

Execute the complete RetailVision AI pipeline with a single command:

```bash
# Activate your virtual environment first
.venv\Scripts\activate  # On Windows
source .venv/bin/activate # On Unix/MacOS

# Run the complete analysis pipeline
python main.py --source input/sample.mp4
```

### Outputs

The system will automatically process the video and generate the following artifacts in the `output/` directory:
- 📄 `analytics.json`: Complete customer journey and dwell-time analytics.
- 📄 `heatmap_analytics.json`: Spatial peak density coordinates and heatmap metadata.
- 🖼️ `customer_heatmap.png`: A high-resolution spatial heatmap visualization.
- 🎞️ `processed.mp4`: The final annotated video containing all visual layers (bounding boxes, trajectories, zones, active journey HUD).

---

## 📈 Dashboard Visualization

RetailVision AI includes a gorgeous, web-based presentation layer to consume and visualize the generated analytics.

To start the dashboard:
```bash
cd dashboard
npm install
npm run dev
```
Then, open the provided `localhost` URL in your browser. The dashboard will automatically read from the `output/` folder in the repository root.

---

## 🏗️ Architecture

The pipeline is designed to perform a single-pass extraction of all required computer vision metrics to maximize performance.

```mermaid
graph TD;
    A[Input Video] --> B[YOLOv8s Person Detection];
    B --> C[BoT-SORT Tracking];
    C --> D[Entry / Exit Counting];
    D --> E[4-Zone Customer Tracking];
    E --> F[Customer Journey & Dwell Analytics];
    F --> G[Movement Heatmap Rendering];
    G --> H[Analytics JSON Export];
    H --> I[React Web Dashboard];
```

---

## 🧪 Engineering Notes & Experimental Research

RetailVision AI's production pipeline uses the frozen BoT-SORT baseline tracker without Re-ID. During development, a BoT-SORT + Re-ID experimental benchmark was conducted, which demonstrated that enabling Re-ID actually degraded tracking stability (higher ID switches) on our target retail CCTV angles. As such, Re-ID remains disabled in the production orchestration.

Unit testing infrastructure for the core analytics engines (counting, zones, heatmaps) can be found in the `tests/` directory. Run them via:
```bash
python -m unittest discover tests
```
