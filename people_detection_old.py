import cv2
import numpy as np
from tracking.centroidtracker import CentroidTracker
from tracking.trackableobject import TrackableObject
import dlib
import imutils
from imutils.video import FPS
from imutils.video import VideoStream
import time

# Classes the model is trained to predict
CLASSES = ['background', 'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable',
           'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep',
           'sofa', 'train', 'tvmonitor']
# Random colour for each class
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# Load model
net = cv2.dnn.readNetFromCaffe('model/MobileNetSSD_deploy.prototxt', 'model/MobileNetSSD_deploy.caffemodel')

vs = VideoStream(src=0).start()
time.sleep(2.0)

ct = CentroidTracker(maxDisappeared=100, maxDistance=50)
trackers = []
trackableObjects = {}

totalFrames = 0

fps = FPS().start()

while True:
    frame = vs.read()
    (H, W) = frame.shape[:2]

    frame = imutils.resize(frame, width=500)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    rects = []

    if totalFrames % 30 == 0:
        trackers = []

        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
        net.setInput(blob)
        detections = net.forward()

        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.7:
                idx = int(detections[0, 0, i, 1])

                if CLASSES[idx] != 'person':
                    continue

                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype('int')

                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(startX, startY, endX, endY)
                tracker.start_track(rgb, rect)

                cv2.rectangle(frame, (startX, startY), (endX, endY),
                              (0, 255, 0), 2)

                label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
                print("[INFO] {}".format(label))

                trackers.append(tracker)
    else:
        for tracker in trackers:
            tracker.update(rgb)
            pos = tracker.get_position()

            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          (0, 255, 0), 2)

            rects.append((startX, startY, endX, endY))

    objects = ct.update(rects)

    for (objectID, centroid) in objects.items():
        to = trackableObjects.get(objectID, None)

        if to is None:
            to = TrackableObject(objectID, centroid)
        else:
            to.centroids.append(centroid)

        trackableObjects[objectID] = to

        text = f'ID {objectID}'
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    cv2.imshow('People Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    totalFrames += 1
    fps.update()

fps.stop()
vs.stop()
cv2.destroyAllWindows()
