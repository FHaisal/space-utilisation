from tracking.centroidtracker import CentroidTracker
from tracking.trackableobject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import dlib
import cv2
from utility import update_json, update_csv


class PeopleCounter:
    def __init__(self, video_url=None, raspi=False, record_url=None, max_disappeared=40, max_distance=50):
        self.CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                        "sofa", "train", "tvmonitor"]

        self.net = cv2.dnn.readNetFromCaffe('model/MobileNetSSD_deploy.prototxt',
                                            'model/MobileNetSSD_deploy.caffemodel')

        if video_url:
            if raspi:
                self.stream = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
            else:
                self.stream = cv2.VideoCapture(video_url)
        else:
            self.stream = VideoStream(src=0).start()
            time.sleep(2.0)

        self.width, self.height = None, None

        self.raspi = raspi
        self.video_url = video_url
        self.centroid_tracker = CentroidTracker(maxDisappeared=max_disappeared, maxDistance=max_distance)
        self.trackers = []
        self.trackable_objects = {}

        self.total_frames = 0
        self.total_exited = 0
        self.total_entered = 0

        self.fps = FPS().start()

        self.record_url = record_url
        self.writer = None

    def start(self, frames=10, accuracy=0.5):
        while True:
            frame = self.stream.read()
            frame = frame[1] if self.video_url else frame

            if self.video_url and frame is None:
                break

            frame = imutils.resize(frame, width=500)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if self.width is None or self.height is None:
                (self.height, self.width) = frame.shape[:2]

            if self.record_url and self.writer is None:
                fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                self.writer = cv2.VideoWriter(self.record_url, fourcc, 30,
                                              (self.width, self.height), True)

            rects = []

            if self.total_frames % frames == 0:
                self.trackers = []

                blob = cv2.dnn.blobFromImage(frame, 0.007843, (self.width, self.height), 127.5)
                self.net.setInput(blob)
                detections = self.net.forward()

                for i in np.arange(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]

                    if confidence > accuracy:
                        index = int(detections[0, 0, i, 1])

                        if self.CLASSES[index] != 'person':
                            continue

                        box = detections[0, 0, i, 3:7] * np.array([self.width, self.height, self.width, self.height])
                        (start_x, start_y, end_x, end_y) = box.astype('int')

                        tracker = dlib.correlation_tracker()
                        rect = dlib.rectangle(start_x, start_y, end_x, end_y)
                        tracker.start_track(rgb, rect)

                        self.trackers.append(tracker)
            else:
                for tracker in self.trackers:
                    tracker.update(rgb)
                    pos = tracker.get_position()

                    start_x = int(pos.left())
                    start_y = int(pos.top())
                    end_x = int(pos.right())
                    end_y = int(pos.bottom())

                    rects.append((start_x, start_y, end_x, end_y))

            cv2.line(frame, (0, self.height // 2), (self.width, self.height // 2), (0, 255, 0), 2)

            objects = self.centroid_tracker.update(rects)

            for (object_id, centroid) in objects.items():
                trackable_object = self.trackable_objects.get(object_id, None)

                if trackable_object is None:
                    trackable_object = TrackableObject(object_id, centroid)
                else:
                    y = [c[1] for c in trackable_object.centroids]
                    direction = centroid[1] - np.mean(y)
                    trackable_object.centroids.append(centroid)

                    location = None
                    if self.video_url and not self.raspi:
                        location = self.video_url

                    if not trackable_object.counted:
                        if direction < 0 and centroid[1] < self.height // 2:
                            self.total_entered += 1
                            trackable_object.counted = True

                            update_json('entered', location)
                            update_csv('entered', location)

                        elif direction > 0 and centroid[1] > self.height // 2:
                            self.total_exited += 1
                            trackable_object.counted = True

                            update_json('exited', location)
                            update_csv('exited', location)

                self.trackable_objects[object_id] = trackable_object

                text = f'ID {object_id}'
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            info = [
                ("Entered", self.total_entered),
                ("Exited", self.total_exited),
            ]

            for (i, (title, value)) in enumerate(info):
                text = f'{title}: {value}'
                cv2.putText(frame, text, (10, self.height - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if self.writer is not None:
                self.writer.write(frame)

            cv2.imshow('People Counter', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break

            self.total_frames += 1
            self.fps.update()

    def stop(self):
        self.fps.stop()

        if self.writer:
            self.writer.release()

        if self.video_url:
            self.stream.release()
        else:
            self.stream.stop()

        cv2.destroyAllWindows()
