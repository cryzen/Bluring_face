from bluring.face_blurring import anonymize_face_pixelate
from bluring.face_blurring import anonymize_face_simple

import os

import numpy as np
import cv2


class BlurVideoStream:

    def __init__(self, frame, face, method="simple", blocks=0, confidence=0.5):

        self.frame = frame
        self.face = face
        self.method = method
        self.blocks = blocks
        self.confidence = confidence

        self.load_face_detector()
        self.treatment()

    def load_face_detector(self):

        print("[INFO] loading face detector model...")
        prototxtPath = os.path.sep.join([self.face, "deploy.prototxt"])
        weightsPath = os.path.sep.join([self.face,
                                        "res10_300x300_ssd_iter_140000.caffemodel"])

        self.net = cv2.dnn.readNet(prototxtPath, weightsPath)

    def treatment(self):

        while True:

            (h, w) = self.frame.shape[:2]
            blob = cv2.dnn.blobFromImage(self.frame, 1.0, (300, 300),
                                         (104.0, 177.0, 123.0))
            self.net.setInput(blob)
            detections = self.net.forward()

            for i in range(0, detections.shape[2]):

                confidence = detections[0, 0, i, 2]

                if confidence > self.confidence:

                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    face = self.frame[startY:endY, startX:endX]

                    if self.method == "simple":
                        face = anonymize_face_simple(face, factor=3.0)

                    else:
                        face = anonymize_face_pixelate(face,
                                                       blocks=self.blocks)

                    self.frame[startY:endY, startX:endX] = face

            return self.frame
