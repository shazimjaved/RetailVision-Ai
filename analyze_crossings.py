"""
Phase 3 Visual Event Validation Script
Re-runs the YOLOv8s + BoT-SORT pipeline and logs every crossing event
with frame number, track ID, direction, and coordinates.
Also saves a snapshot frame for each crossing event for visual inspection.
"""
import cv2
import os
import math
from ultralytics import YOLO

# --- Segment intersection helpers ---
def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def main():
    source = "input/sample.mp4"
    snapshot_dir = "output/crossing_snapshots"
    os.makedirs(snapshot_dir, exist_ok=True)

    model = YOLO("yolov8s.pt")
    cap = cv2.VideoCapture(source)
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {width}x{height} @ {fps:.1f} FPS, {total_frames} frames")

    # Counting line
    x1_l, y1_l, x2_l, y2_l = 1050, 1080, 1700, 710
    print(f"Counting line: ({x1_l},{y1_l}) -> ({x2_l},{y2_l})")

    # State
    track_state = {}
    cooldown_frames = 15
    events = []
    frame_count = 0

    print("  Processing frames...")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"  Processed {frame_count}/{total_frames} frames...")

        results = model.track(frame, persist=True, tracker="botsort.yaml",
                              classes=[0], verbose=False)
        result = results[0]

        if result.boxes:
            for box in result.boxes:
                if box.id is None:
                    continue
                track_id = int(box.id[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                px = int((x1 + x2) / 2)
                py = int(y2)

                if track_id not in track_state:
                    track_state[track_id] = {
                        'last_point': (px, py),
                        'last_crossing_frame': -cooldown_frames,
                        'last_direction': None
                    }
                else:
                    last_point = track_state[track_id]['last_point']
                    last_cf = track_state[track_id]['last_crossing_frame']
                    last_dir = track_state[track_id]['last_direction']

                    A = (x1_l, y1_l)
                    B = (x2_l, y2_l)
                    C = last_point
                    D = (px, py)

                    if (frame_count - last_cf) > cooldown_frames:
                        if intersect(A, B, C, D):
                            cross = (B[0]-A[0])*(D[1]-C[1]) - (B[1]-A[1])*(D[0]-C[0])
                            
                            # Filter jitter
                            if abs(cross) > 1000:
                                direction = "ENTRY" if cross < 0 else "EXIT"
                                
                                # Block consecutive same-direction events
                                if direction != last_dir:
                                    event = {
                                        'frame': frame_count,
                                        'time_sec': frame_count / fps,
                                        'track_id': track_id,
                                        'direction': direction,
                                        'cross_value': cross,
                                        'prev_point': last_point,
                                        'curr_point': (px, py),
                                        'bbox': (x1, y1, x2, y2),
                                        'conf': conf
                                    }
                                    events.append(event)

                                    # Save annotated snapshot
                                    snap = frame.copy()
                                    cv2.line(snap, (x1_l, y1_l), (x2_l, y2_l), (255, 0, 0), 3)
                                    cv2.circle(snap, last_point, 6, (0, 0, 255), -1)  # prev = red
                                    cv2.circle(snap, (px, py), 6, (0, 255, 0), -1)    # curr = green
                                    cv2.arrowedLine(snap, last_point, (px, py), (255, 255, 0), 2)
                                    cv2.rectangle(snap, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                    label = f"ID:{track_id} {direction} f:{frame_count}"
                                    cv2.putText(snap, label, (x1, y1-10),
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
                                    
                                    # INSIDE/OUTSIDE labels
                                    dx = x2_l - x1_l
                                    dy = y2_l - y1_l
                                    length = math.hypot(dx, dy)
                                    if length > 0:
                                        nx = dy / length * 60
                                        ny = -dx / length * 60
                                        mx = int((x1_l + x2_l) / 2)
                                        my = int((y1_l + y2_l) / 2)
                                        cv2.putText(snap, "INSIDE", (int(mx+nx)-30, int(my+ny)),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,100,100), 2)
                                        cv2.putText(snap, "OUTSIDE", (int(mx-nx)-40, int(my-ny)),
                                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100,100,255), 2)

                                    snap_path = os.path.join(snapshot_dir,
                                        f"event_{len(events):02d}_f{frame_count}_{direction}_ID{track_id}.jpg")
                                    cv2.imwrite(snap_path, snap)

                                    track_state[track_id]['last_crossing_frame'] = frame_count
                                    track_state[track_id]['last_direction'] = direction

                    track_state[track_id]['last_point'] = (px, py)

        if frame_count % 100 == 0:
            print(f"  Processed {frame_count}/{total_frames} frames...")

    cap.release()

    # --- Final Report ---
    print("\n" + "="*60)
    print("CROSSING EVENT LOG")
    print("="*60)
    
    entries = 0
    exits = 0
    for i, ev in enumerate(events):
        if ev['direction'] == 'ENTRY':
            entries += 1
        else:
            exits += 1
        print(f"\nEvent #{i+1}:")
        print(f"  Frame:       {ev['frame']} ({ev['time_sec']:.2f}s)")
        print(f"  Track ID:    {ev['track_id']}")
        print(f"  Direction:   {ev['direction']}")
        print(f"  Cross value: {ev['cross_value']:.0f}")
        print(f"  Prev point:  {ev['prev_point']}")
        print(f"  Curr point:  {ev['curr_point']}")
        print(f"  BBox:        {ev['bbox']}")
        print(f"  Confidence:  {ev['conf']:.3f}")
        print(f"  Snapshot:    {snapshot_dir}/event_{i+1:02d}_f{ev['frame']}_{ev['direction']}_ID{ev['track_id']}.jpg")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total frames:     {frame_count}")
    print(f"Total events:     {len(events)}")
    print(f"Total entries:    {entries}")
    print(f"Total exits:      {exits}")
    print(f"Final occupancy:  {max(0, entries - exits)}")
    print(f"Snapshots saved:  {snapshot_dir}/")
    print("="*60)

if __name__ == "__main__":
    main()
