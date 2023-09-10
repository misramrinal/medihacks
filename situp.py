import cv2
import numpy as np
import time
import os
import posedetection as pd
import math

class situps():
    def __init__(self):
        self.detector = pd.poseDetector(detectionCon=0.6, checkpoints = [25, 26, 32, 31])
        self.preva = 0
        self.prevb = 0
        self.count=0
        self.maxlength = 0
        self.volBar = 400

    def situpcounter(self,img):
        img = self.detector.findPose(img)
        lmList = self.detector.findPosition(img)
        if len(lmList) != 0:
            x1, y1 = lmList[25][1:]
            x2, y2 = lmList[23][1:]
            y3 = lmList[32][2]
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            fingers = self.detector.fingersUp()
            currenta = fingers[0]
            currentb = fingers[1]
            if currenta == 1 and currentb == 1:
                if self.preva == 0 and self.prevb == 0:
                    self.count+=1
            self.preva = currenta
            self.prevb = currentb
            if fingers[2] and fingers[3] and y3 < 700:
                length = math.hypot(x2 - x1, y2 - y1)
                self.maxlength = max(self.maxlength,math.hypot(x2 - x1, y2 - y1))
                print(length)
                vol = np.interp(length, [0, self.maxlength], [0, 100])
                self.volBar = np.interp(length, [0, self.maxlength], [150, 400])
                volPer = np.interp(length, [0, self.maxlength], [100, 0])
                cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)
                print(self.volBar)
            cv2.putText(img, f'Situps : {int(self.count)}', (40, 550), cv2.FONT_HERSHEY_COMPLEX,
                    1, (100, 20, 160), 3)
        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(self.volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        return img

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    sit = situps()
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        sit.situpcounter(img)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()