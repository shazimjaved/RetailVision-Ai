from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_path="yolov8n.pt"):
        """
        Initializes the YOLO model for person detection.
        Uses yolov8n.pt by default (downloads automatically if not present).
        """
        self.model = YOLO(model_path)
        # In COCO dataset, class 0 is 'person'
        self.person_class_id = 0

    def detect(self, frame):
        """
        Runs inference on a single frame and returns person detections.
        """
        # Run inference, stream=True is often faster for video
        results = self.model(frame, classes=[self.person_class_id], verbose=False)
        return results[0]
