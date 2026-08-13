from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_path="yolov8s.pt"):
        """
        Initializes the YOLO model for person detection.
        Uses yolov8s.pt by default (downloads automatically if not present).
        """
        self.model = YOLO(model_path)
        # In COCO dataset, class 0 is 'person'
        self.person_class_id = 0

    def detect(self, frame, track=False):
        """
        Runs inference on a single frame and returns person detections.
        """
        if track:
            # Run inference with tracking enabled, persist=True keeps tracking history across frames
            results = self.model.track(frame, classes=[self.person_class_id], persist=True, tracker="botsort.yaml", verbose=False)
        else:
            # Run inference without tracking
            results = self.model(frame, classes=[self.person_class_id], verbose=False)
        return results[0]
