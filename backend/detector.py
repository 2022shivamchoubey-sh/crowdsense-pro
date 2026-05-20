try:
    from ultralytics import YOLO
    HAS_YOLO = True
except Exception as e:
    print(f"Warning: YOLO/Torch not available. Running in MOCK mode. Error: {e}")
    HAS_YOLO = False

import cv2, numpy as np
import random
from collections import OrderedDict
import math

TRACKED_CLASSES = {0: 'person', 2: 'car', 3: 'motorcycle', 7: 'truck', 1: 'bicycle'}

# ROI Zones (Hardcoded for a typical 640x480 frame for demonstration)
ZONE_A = np.array([[10, 150], [310, 150], [310, 470], [10, 470]])
ZONE_B = np.array([[330, 150], [630, 150], [630, 470], [330, 470]])
TRIPWIRE_Y = 300

class CentroidTracker:
    def __init__(self, max_disappeared=10):
        self.next_id = 0
        self.objects = OrderedDict() # id: (cx, cy)
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.crossed_in = 0
        self.crossed_out = 0

    def register(self, centroid):
        self.objects[self.next_id] = centroid
        self.disappeared[self.next_id] = 0
        self.next_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")
        for (i, (x1, y1, x2, y2)) in enumerate(rects):
            cx = int((x1 + x2) / 2.0)
            cy = int((y1 + y2) / 2.0)
            input_centroids[i] = (cx, cy)

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            D = np.zeros((len(object_ids), len(input_centroids)))
            for i, oc in enumerate(object_centroids):
                for j, ic in enumerate(input_centroids):
                    D[i, j] = math.hypot(oc[0] - ic[0], oc[1] - ic[1])

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if D[row, col] > 80:
                    continue

                object_id = object_ids[row]
                old_y = self.objects[object_id][1]
                new_y = input_centroids[col][1]

                # Tripwire logic
                if old_y < TRIPWIRE_Y and new_y >= TRIPWIRE_Y:
                    self.crossed_in += 1
                elif old_y > TRIPWIRE_Y and new_y <= TRIPWIRE_Y:
                    self.crossed_out += 1

                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

            for col in unused_cols:
                self.register(input_centroids[col])

        return self.objects

class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt', confidence=0.45):
        if HAS_YOLO:
            self.model = YOLO(model_path)
        self.confidence = confidence
        self.tracker = CentroidTracker()

    def detect(self, frame: np.ndarray) -> dict:
        zone_counts = {'zone_a': 0, 'zone_b': 0}

        if not HAS_YOLO:
            counts = {'person': random.randint(2, 12), 'car': random.randint(1, 8), 'motorcycle': 0, 'truck': 1, 'bicycle': 2}
            annotated = frame.copy() if frame is not None else np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.polylines(annotated, [ZONE_A], True, (0, 255, 0), 2)
            cv2.polylines(annotated, [ZONE_B], True, (255, 0, 0), 2)
            cv2.line(annotated, (0, TRIPWIRE_Y), (annotated.shape[1], TRIPWIRE_Y), (0, 0, 255), 2)
            return {'counts': counts, 'detections': [], 'frame': annotated, 'zone_a': random.randint(0, 5), 'zone_b': random.randint(0, 5), 'in': random.randint(10, 50), 'out': random.randint(10, 50)}

        results = self.model(frame, conf=self.confidence, verbose=False)[0]
        counts = {v: 0 for v in TRACKED_CLASSES.values()}
        detections = []
        rects = []
        
        annotated = results.plot()

        for box in results.boxes:
            cls_id = int(box.cls[0])
            if cls_id not in TRACKED_CLASSES:
                continue
            label = TRACKED_CLASSES[cls_id]
            counts[label] += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            rects.append((x1, y1, x2, y2))
            detections.append({'label': label, 'bbox': [x1, y1, x2, y2], 'conf': float(box.conf[0])})
            
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)
            
            if cv2.pointPolygonTest(ZONE_A, (cx, cy), False) >= 0:
                zone_counts['zone_a'] += 1
            if cv2.pointPolygonTest(ZONE_B, (cx, cy), False) >= 0:
                zone_counts['zone_b'] += 1

        objects = self.tracker.update(rects)

        # Draw overlays
        cv2.polylines(annotated, [ZONE_A], True, (0, 255, 0), 2)
        cv2.putText(annotated, "Zone A", (ZONE_A[0][0], ZONE_A[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.polylines(annotated, [ZONE_B], True, (255, 0, 0), 2)
        cv2.putText(annotated, "Zone B", (ZONE_B[0][0], ZONE_B[0][1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        cv2.line(annotated, (0, TRIPWIRE_Y), (annotated.shape[1], TRIPWIRE_Y), (0, 0, 255), 2)
        cv2.putText(annotated, "Tripwire", (10, TRIPWIRE_Y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        for (objectID, centroid) in objects.items():
            text = f"ID {objectID}"
            cv2.putText(annotated, text, (centroid[0] - 10, centroid[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.circle(annotated, (centroid[0], centroid[1]), 4, (0, 255, 255), -1)

        return {
            'counts': counts,
            'detections': detections,
            'frame': annotated,
            'zone_a': zone_counts['zone_a'],
            'zone_b': zone_counts['zone_b'],
            'in': self.tracker.crossed_in,
            'out': self.tracker.crossed_out
        }
