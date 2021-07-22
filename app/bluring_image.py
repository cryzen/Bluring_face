from bluring.face_blurring import anonymize_face_pixelate
from bluring.face_blurring import anonymize_face_simple

import os

import numpy as np
import cv2


class BlurImage:
    def __init__(self, images, face, destination, 
                                method="simple", 
                                blocks=0, 
                                confidence=0.5):
        self.path = images
        self.face = face
        self.destination = destination
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

    def relative_path_definition(self):
        
        filenames = []
        
        try:
            filenames.extend((os.listdir(self.path)))
        except Exception:
            filenames.append(os.path.basename(self.path))

        return filenames

    def treatment(self):
        
        filenames = self.relative_path_definition()

        for filename in filenames:
            
            if filename in self.path:
                filename_path = self.path
            else:
                filename_path = os.path.join(self.path, filename)

            print(filename_path)

            image = cv2.imread(filename_path)
            orig = image.copy()
            (h, w) = image.shape[:2]

            blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300),
                (104.0, 177.0, 123.0))

            print("[INFO] computing face detections...")
            self.net.setInput(blob)
            detections = self.net.forward()

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence > self.confidence:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    face = image[startY:endY, startX:endX]

                    if self.method == "simple":
                        face = anonymize_face_simple(face, factor=3.0)
                    else:
                        face = anonymize_face_pixelate(face, blocks=self.blocks)

                    image[startY:endY, startX:endX] = face

            print("[INFO] saving image...")
            output = np.hstack([image])
            ext = os.path.splitext(filename)
            new_filename = ext[0] + "_blured" + ext[1]
            cv2.imwrite(os.path.join(self.destination, new_filename), output)
            cv2.waitKey(0)