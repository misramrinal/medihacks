from flask import Flask,render_template,Response
import cv2

camera=cv2.VideoCapture(0)
while True:
     _, frame=camera.read()
     cv2.imshow("yo", frame)
     if cv2.waitKey(1) & 0xFF == ord('q'):
         break
camera.release()
cv2.destroyAllWindows()
        
