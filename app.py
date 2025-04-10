from flask import Flask, render_template, request, redirect, url_for, session 
from pymongo import MongoClient
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from bson import ObjectId  # Add this import for ObjectId handling
import json
import numpy as np
import joblib

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '966d0831d5ae91dc9aff94d19daddaa5'  # Use a secret key for sessions

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['healthcare_db']  # Database name
doctors_collection = db['doctors']
patients_collection = db['patients']

# Load AI model and label encoder (Assume they are saved as .pkl files)
trained_model = joblib.load('C:\\Users\\Tanmay Shinde\\Desktop\\project_v1\\ml_models\\trained_model.pkl')  # Load your trained model
label_encoder = joblib.load('C:\\Users\\Tanmay Shinde\\Desktop\\project_v1\\ml_models\\label_encoder.pkl')  # Load your label encoder

# Treatment Mapping
treatment_mapping = {
    0: "Insulin Therapy",
    1: "Medication",
    2: "Lifestyle Changes",
    3: "Medication",
    4: "Oxygen Therapy",
    5: "Physiotherapy",
    6: "Surgery"
}

# Utility functions to interact with MongoDB
def add_doctor(doctor_info):
    doctors_collection.insert_one(doctor_info)

def add_patient(patient_info):
    patients_collection.insert_one(patient_info)

def get_patient(patient_id):
    return patients_collection.find_one({"_id": ObjectId(patient_id)})

def get_doctor_analytics(doctor_id):
    total_patients = patients_collection.count_documents({"doctor_id": doctor_id})
    cured_patients = patients_collection.count_documents({"doctor_id": doctor_id, "cure_progress": 100})
    ongoing_patients = total_patients - cured_patients
    follow_ups = patients_collection.count_documents({
        "doctor_id": doctor_id,
        "follow_up_date": {"$gte": datetime.now()}
    })
    return {
        "total_patients": total_patients,
        "cured_patients": cured_patients,
        "ongoing_patients": ongoing_patients,
        "follow_ups": follow_ups
    }

# Routes
@app.route("/")
def home():
    return redirect(url_for("login"))

    return render_template('dashboard.html', patients=patients, alerts=alerts, chart_data=chart_data)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        doctor_id = request.form.get("doctor_id")
        password = request.form.get("password")
        
        doctor = doctors_collection.find_one({"doctor_id": doctor_id, "password": password})
        
        if doctor:
            session['doctor_id'] = doctor_id
            return redirect(url_for("dashboard", doctor_id=doctor_id))
        else:
            return render_template("login.html", error="Invalid Doctor ID or Password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session['doctor_id'] = None
    return render_template("login.html")

@app.route("/dashboard/<doctor_id>")
def dashboard(doctor_id):
    if 'doctor_id' not in session or session['doctor_id'] != doctor_id:
        return redirect(url_for('login'))

    doctor = doctors_collection.find_one({"doctor_id": doctor_id})
    if not doctor:
        return "Doctor not found", 404

    analytics = get_doctor_analytics(doctor_id)
    patients_cursor = patients_collection.find({"doctor_id": doctor_id})
    patients = list(patients_cursor)

    # Create chart data for conditions
    conditions = {}
    for patient in patients:
        condition = patient.get('condition', 'Unknown')  # Use 'Unknown' if no condition exists
        conditions[condition] = conditions.get(condition, 0) + 1

    chart_data = {
    'labels': list(conditions.keys()),
    'values': list(conditions.values())
}

    doctor_info = {
        "doctor_id": doctor_id,
        "name": doctor_id,
        "total_patients": analytics['total_patients'],
        "cured_patients": analytics['cured_patients'],
        "ongoing_patients": analytics['ongoing_patients'],
        "follow_ups": analytics['follow_ups'],
        "patients": patients
    }

    return render_template("dashboard.html", doctor=doctor_info, chart_data=chart_data)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        doctor_id = request.form["doctor_id"]
        name = request.form["name"]
        
        # Collect inputs from the form
        age = int(request.form["age"])
        gender = request.form["gender"]
        hypertension = request.form["hypertension"]
        glucose_level = request.form["glucose_level"]
        chronic_disease = request.form["chronic_disease"]
        condition = request.form["condition"]
        systolic_bp = int(request.form["systolic_bp"])
        diastolic_bp = int(request.form["diastolic_bp"])
        chronic_score = request.form["chronic_score"]

        # Encode categorical variables
        gender_encoded = 1 if gender == "Male" else 0
        hypertension_encoded = 1 if hypertension == "Yes" else 0
        glucose_level_encoded = {"Low": 0, "Normal": 1, "High": 2}[glucose_level]
        chronic_disease_encoded = 1 if chronic_disease == "Yes" else 0
        condition_encoded = {"Severe": 0, "Moderate": 1, "Mild": 2}[condition]
        

        # Prepare model input
        model_input = np.array([[age, gender_encoded, hypertension_encoded, glucose_level_encoded,
                                 chronic_disease_encoded, condition_encoded, systolic_bp, diastolic_bp]])

        # Make prediction using the trained model
        prediction = trained_model.predict(model_input)
        
        # Decode the label using the treatment_mapping
        treatment_prediction_numeric = prediction[0]  # Prediction is numeric
        treatment_prediction = treatment_mapping.get(treatment_prediction_numeric, "Unknown Treatment")

        # Critical condition check
        emergency_status = "Critical" if int(systolic_bp) >= 180 or int(diastolic_bp) >= 120 else "Stable"
        emergency_status = "Critical" if int(chronic_score) >= 8 else "Stable"

        # Cure progress (mocked value)
        cure_progress = 0

        # QR Code generation
        patient_data = f"Name: {name}, Age: {age}, Treatment: {treatment_prediction}"
        qr = qrcode.make(patient_data)
        buffer = BytesIO()
        qr.save(buffer)
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        # Store patient in MongoDB with explicit conversion of numpy.int32 to int
        patient_info = {
            "doctor_id": doctor_id,
            "name": name,
            "age": int(age),  # Convert to native int
            "gender": gender,
            "hypertension": hypertension,
            "glucose_level": glucose_level,
            "chronic_disease": chronic_disease,
            "condition": condition,
            "systolic_bp": int(systolic_bp),  # Convert to native int
            "diastolic_bp": int(diastolic_bp),  # Convert to native int
            "treatment": treatment_prediction,
            "emergency_status": emergency_status,
            "cure_progress": int(cure_progress),  # Convert cure_progress to native int
            "qr_code": qr_code
        }

        # Insert the patient document into MongoDB
        add_patient(patient_info)

        return render_template("result.html", patient=patient_info)

    return render_template("register.html")


@app.route("/qr_info/<patient_id>")
def qr_info(patient_id):
    patient = get_patient(patient_id)
    if not patient:
        return "Patient not found", 404

    return render_template("qr_info.html", patient=patient)

@app.route("/add_notes/<patient_id>", methods=["GET", "POST"])
def add_notes(patient_id):
    patient = get_patient(patient_id)
    if not patient:
        return "Patient not found", 404

    if request.method == "POST":
        doctor_notes = request.form.get("doctor_notes")
        patients_collection.update_one(
            {"_id": ObjectId(patient_id)}, {"$set": {"doctor_notes": doctor_notes}}
        )
        return redirect(url_for("result", patient_id=patient_id))

    return render_template("add_notes.html", patient=patient)

@app.route("/result/<patient_id>")
def result(patient_id):
    patient = get_patient(patient_id)
    if not patient:
        return "Patient not found", 404
    return render_template("result.html", patient=patient)

# Utility function to generate QR Code
def generate_qr_code(data):
    qr = qrcode.make(json.dumps(data))
    buffer = BytesIO()
    qr.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()

if __name__ == '__main__':
    app.run(debug=True)
