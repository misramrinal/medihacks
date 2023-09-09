from flask import Flask,render_template,Response
import cv2
import situp

app=Flask(__name__)
cap = cv2.VideoCapture(1)
cap.set(3, 1280)
cap.set(4, 720)
sit = situp.situps()

def generate_frames():
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        if not success:
            break
        else:
            # frame = img
            frame = sit.situpcounter(img)
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/situp')
def index():
    return render_template('video.html')

@app.route('/video')
def video():
    return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(host='localhost', port=80, debug=False)