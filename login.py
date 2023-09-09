import os
from flask import Flask, redirect, url_for, request, jsonify, render_template, session, flash, abort, Response
import uuid as uuid
from firebase import firebase
import requests
import pyrebase
from collections import OrderedDict
import pickle
import pandas as pd
import pathlib
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import cv2
import situp
import pushup

app = Flask(__name__)
app.secret_key = "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"
firebase = firebase.FirebaseApplication('https://titanesp32-default-rtdb.asia-southeast1.firebasedatabase.app/', None)
app.app_context().push()
model = pickle.load(open('model.pkl', 'rb'))

config={
    "apiKey": "AIzaSyA3UkN9CswTBMmPdPrR7UzEHILtqgCZ548",
  "authDomain": "titanesp32.firebaseapp.com",
  "databaseURL": "https://titanesp32-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "titanesp32",
  "storageBucket": "titanesp32.appspot.com",
  "messagingSenderId": "698992859910",
  "appId": "1:698992859910:web:c898ebdf0c072158e49c87",
  "measurementId": "G-NETX6BS1Y6"
}

firebas=pyrebase.initialize_app(config)

# firebas= pyrebase.initialize_app(config)
authe = firebas.auth()
database = firebas.database()

age=0
weighht=0
height=0
gender=""
sleep_duration=0


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev
GOOGLE_CLIENT_ID = "203782484797-ffqasuq4ud6k5kil4qnl2jab068vs966.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://localhost/callback"
)

# This is the landing page
@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/home')
def homei():
    return render_template('dashboard.html')

@app.route("/login_page")
def login_page():
    return render_template("login.html")

# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    global age,gender,sleep_duration, height, weight
    result = firebase.get('/user', None)
    username = request.form["Username"]
    user_list = list(result.values())

    for user_data in user_list:
        if "username" in user_data and user_data["username"] == username:
            age = int(user_data["age"])
            gender = user_data["gender"]
            height = int(user_data["height"])
            weight = int(user_data["weight"])
            sleep_duration = int(user_data["sleep_duration"])
            return redirect(url_for('dashboard'))

    flash("That User Doesn't Exist! Try Again...")
    return render_template('login.html')

# This will be triggered when the user signin is successfull
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard2.html')

# This fuction is used to predict the stress level and fitness score based on the input parameters
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    global age, gender, sleep_duration, height, weight
    
    # Getting input parameters from the database
    data_sys= database.child('systolic').get().val()
    data_dia= database.child('diastolic').get().val()
    data_temp= database.child('Temperature').get().val()
    data_HR= database.child('heartrate').get().val()
    data_SD= database.child('sleep_disorder').get().val()
    data_step= database.child('steps').get().val()
    
    data_sys = OrderedDict(data_sys)
    data_dia = OrderedDict(data_dia)
    data_temp = OrderedDict(data_temp)
    data_HR = OrderedDict(data_HR)
    data_SD = OrderedDict(data_SD)
    data_step = OrderedDict(data_step)
    
    value_sys = float(data_sys['data'])
    value_dia = float(data_dia['data'])
    value_temp = float(data_temp['data']) + 21
    value_HR = float(data_HR['data'])
    value_SD = str(data_SD['data'])
    value_step = float(data_step['data'])
    
    # Converting 'Male' and 'Female' keyword into numerical value
    with open('gender_mapping.pkl', 'rb') as f:
        vocab = pickle.load(f)
    gendr = vocab[gender]
    
    # Converting sleep disorder values into numerical values
    with open('sleep_mapping.pkl', 'rb') as f:
        vocab = pickle.load(f)
    SD=vocab[value_SD]
    
    
    # Getting BMI of the user
    height_meters=height/100
    Bmi=weight/(height_meters*height_meters)
    Bmi=round(Bmi,2)
    
    # Sending the input parameters into the trained model
    data = [[gendr, age, sleep_duration, value_sys, value_dia, value_HR, value_temp, value_step, SD]]
    input_df = pd.DataFrame(data, columns=['Gender', 'Age', 'Sleep Duration', 'Systolic', 'Diastolic', 'Heart Rate', 'Temperature', 'Daily Steps', 'Sleep Disorder'])
    prediction = model.predict(input_df)
    score = model.predict_proba(input_df)
    prediction=int(prediction)
    
    # Predicting the fitness score
    fitness_negative = (abs(value_HR - 70))*0.67 + (abs(Bmi - 22))*1 + (abs(value_sys - 120))*0.1 + (abs(value_dia - 80))*0.09 + (prediction)*1 + SD*(0.18) + (abs(value_step - 10000))*0.02 + (abs(value_temp - 98.6))*0.08
    fitness_positive = (sleep_duration-8)*0.81
    fitness_score = 100 - fitness_negative + fitness_positive
    
    HR_text=""
    sys_text=""
    dia_text=""
    temp_text=""
    Bmi_text=""
    
    
    # Some more optimizations
    if(value_HR < 60 or value_HR > 100):
        HR_text = f"We detected abnormal heart rate from your readings. Your heart rate reading is {value_HR}"
        flash(HR_text)
        
    if(value_dia < 65 or value_dia > 95):
        dia_text = f"We detected abnormal systolic pressure from your readings. Your systolic pressure reading is {value_dia}"
        flash(dia_text)
        
    if(value_sys < 105 or value_sys > 140):
        sys_text = f"We detected abnormal diastolic pressure from your readings. Your diastolic pressure reading is {value_sys}"
        flash(sys_text)
        
    if(Bmi < 18.5 or Bmi > 35):
        Bmi_text = f"We detected abnormal BMI from your readings. Your BMI reading is {Bmi}"
        flash(Bmi)
        
    if(value_temp < 95 or value_temp > 101):
        temp_text = f"We detected abnormal temperature from your readings. Your temperature reading is {value_temp}"
        flash(temp_text )
        
    return render_template('index.html', prediction_text=prediction, input_text=Bmi, fitness_text=fitness_score, HR_text=HR_text, sys_text=sys_text, dia_text=dia_text, Bmi_text=Bmi_text, temp_text=temp_text)

# Create Logout Page

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You Have Been Logged Out!  Thanks For Stopping By...")
    return redirect(url_for('home'))


# Create Sign UP page
@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == 'POST' and len(dict(request.form)) > 0:
        userdata = dict(request.form)
        username = userdata["username"]
        email = userdata["email"]
        name = userdata["name"]
        age = userdata["age"]
        gender = userdata["gender"]
        height = userdata["height"]
        weight = userdata["weight"]
        sleep_duration = userdata["sleep_duration"]
        
        result = firebase.get('/user', None)
        user_list = list(result.values())

        # Check if the provided username exists in any dictionary
        for user_data in user_list:
            if "username" in user_data and user_data["username"] == username:
                flash("That Username Already Exits!")
                return render_template('login.html')

        
        new_data = {"username": username,"email": email,"name": name, "age": age,"gender": gender,"height": height,"weight": weight,"sleep_duration": sleep_duration}
        firebase.post("/user", new_data)
        return render_template('login.html',prediction_text=username)
    
    else:
        if "user" in session:
            flash("Already Logged In!")
            return render_template('login.html')
        

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper
        

@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/protected_area")
@login_is_required
def protected_area():
    return redirect(url_for('dashboard'))


@app.route("/login_google")
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
sit = situp.situps()
push=pushup.pushup()

def generate_frames_situp():
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
def situp():
    return render_template('situp.html')

@app.route('/video_situp')
def video():
    return Response(generate_frames_situp(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pushup')
def pushup():
    return render_template('pushup.html')

def generate_frames_pushup():
    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        if not success:
            break
        else:
            # frame = img
            frame = push.pushupcounter(img)
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
        yield(b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
   

if __name__ == "__main__":
    # db.create_all()
    app.run(host='localhost', port=80, debug=True)