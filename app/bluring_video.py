from bluring.face_blurring import anonymize_face_pixelate
from bluring.face_blurring import anonymize_face_simple

import os

import numpy as np
import cv2


class BlurVideo:
    def __init__(self, video, face, destination,
                 method="simple",
                 blocks=0,
                 confidence=0.5):

        self.video = video
        self.face = face
        self.destination = destination
        self.method = method
        self.blocks = blocks
        self.confidence = confidence

        self.load_face_detector()
        self.load_video()
        self.treatment()

    def load_face_detector(self):

        print("[INFO] loading face detector model...")
        prototxtPath = os.path.sep.join([self.face, "deploy.prototxt"])
        weightsPath = os.path.sep.join([self.face,
                                        "res10_300x300_ssd_iter_140000.caffemodel"])
        self.net = cv2.dnn.readNet(prototxtPath, weightsPath)

    def load_video(self):

        print("[INFO] load video...")
        self.cap = cv2.VideoCapture(self.video)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
        size = (width, height)

        fourcc = cv2.VideoWriter_fourcc(*"MPEG")
        self.out = cv2.VideoWriter(self.destination, fourcc, 20.0, size)

    def treatment(self):

        try:

            while self.cap.isOpened():
                ret, frame = self.cap.read()

                (h, w) = frame.shape[:2]

                blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300),
                                             (104.0, 177.0, 123.0))

                self.net.setInput(blob)
                detections = self.net.forward()

                for i in range(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]

                    if confidence > self.confidence:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        face = frame[startY:endY, startX:endX]

                        if self.method == "simple":
                            face = anonymize_face_simple(face, factor=3.0)

                        else:
                            face = anonymize_face_pixelate(face,
                                                           blocks=self.blocks)

                        frame[startY:endY, startX:endX] = face

                self.out.write(frame)

            self.cap.release()

        except AttributeError:

            cv2.destroyAllWindows()
