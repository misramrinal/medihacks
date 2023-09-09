import cv2
import numpy as np
import time
import os
import posedetection as pd
import math

class pushup():
    def __init__(self):
        self.detector = pd.poseDetector(detectionCon=0.6, checkpoints = [0, 14, 15], pushup=True)
        self.preva = 0
        self.prevb = 0
        self.count=0
        self.maxlength = 0
        self.volBar = 400
    
    def pushupcounter(self, img):
        img = cv2.flip(img, 1)
        img = self.detector.findPose(img)
        lmList = self.detector.findPosition(img)
        print(len(lmList))
        if len(lmList) != 0:
            x1, y1 = lmList[0][1:]
            x2, y2 = lmList[14][1:]
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            fingers = self.detector.fingersUp()
            currenta = fingers[0]
            if currenta == 1 :
                if self.preva == 0 :
                    self.count+=1

            self.preva = currenta
            if fingers[0] :
                length = y2 - y1
                self.maxlength = max(self.maxlength,y2 - y1)
                print(length)
                vol = np.interp(length, [0, self.maxlength], [0, 100])
                self.volBar = np.interp(length, [0, self.maxlength], [150, 400])
                volPer = np.interp(length, [0, self.maxlength], [100, 0])
                cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)

                print(self.volBar)
            cv2.putText(img, f'PushUps : {int(self.count)}', (40, 550), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)
            
        return img
            
       
def main():
    cap = cv2.VideoCapture(1)
    cap.set(3, 1280)
    cap.set(4, 720)
    pup = pushup()
    while True:
        success, img = cap.read()
        newimg = pup.pushupcounter(img)
        cv2.imshow("Image", newimg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
        

if __name__ == "__main__":
    main()