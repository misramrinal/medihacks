import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))
# city_mapping = pickle.load(open('city_mapping.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/', methods=["GET", "POST"])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    Gender = request.form['Gender']
    Age = int(request.form['Age'])
    Sleep = float(request.form['Sleep Duration'])
    SleepQuality = float(request.form['SleepQuality'])
    PhysicalActivity = float(request.form['PhysicalActivity'])
    Systolic = float(request.form['Systolic'])
    Diastolic = float(request.form['Diastolic'])
    Stress = int(request.form['Stress'])
    HeartRate = float(request.form['HeartRate'])
    Temperature = float(request.form['Temperature'])
    DailySteps = float(request.form['DailySteps'])
    bs = float(request.form['bs'])
    
    with open('gender_mapping.pkl', 'rb') as f:
        vocab = pickle.load(f)
    Gender = vocab[Gender]
    # with open('sleep_mapping.pkl', 'rb') as f:
    #     vocab = pickle.load(f)
    # Sleep = vocab[Sleep]
    # cteam2 = vocab[team2]
    # cwin  = vocab[tosswin]
    with open('stress_mapping.pkl', 'rb') as f:
        vocab = pickle.load(f)
    Stress=vocab[Stress]
    # city1 = tuple(city1)
    # cteam1 = tuple(cteam1)
    # cteam2 = tuple(cteam2)
    # cwin = tuple(cwin)
    # cdecide = tuple(cdecide)


    # lst = np.array([city1, cteam1, cteam2, cwin, cdecide], dtype='int32').reshape(1,-1)
    data = [[Gender, Age, Sleep, SleepQuality, PhysicalActivity, Systolic, Diastolic, Stress, bs, HeartRate, Temperature, DailySteps]]
    # columns = ['City', 'Team1', 'Team2', 'TossWinner', 'TossDecision']
    # df = pd.Series(data, index=columns).to_frame().T

    input_df = pd.DataFrame(data, columns=['Gender', 'Age', 'Sleep Duration', 'Quality of Sleep', 'Physical Activity Level', 'Systolic', 'Diastolic', 'Stress Level', 'bs', 'Heart Rate', 'Temperature', 'Daily Steps'])
    # input_df = pd.DataFrame({'City':city1,'Team1':cteam1,'Team2':cteam2,'TossWinner':cwin,'TossDecision':cdecide})
    # final_features = np.array(input_df)
    # final_features=np.array(final_features)
    # print(final_features)
    prediction = model.predict(input_df)
    # if prediction==cteam1:
    #     prediction=team1
    # if prediction==cteam2:
    #     prediction=team2
    if(prediction[0]==0):
        prediction='It works!!'

    print(prediction)
    # output = round(prediction[0], 2)

    return render_template('index.html', prediction_text='{}'.format(prediction))
    # return render_template('index.html', prediction_text='Hi')

@app.route('/predict_api',methods=['POST'])
def predict_api():
    '''
    For direct API calls trought request
    '''
    data = request.get_json(force=True)
    prediction = model.predict([np.array(list(data.values()))])

    output = prediction[0]
    return jsonify(output)

if __name__ == "__main__":
    app.run(debug=True)