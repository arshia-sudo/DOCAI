from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
patients_collection = db['patients']

def get_patients():
    """Retrieve all patients from the database."""
    patients = list(patients_collection.find({}))  # Retrieve all fields
    for patient in patients:
        patient['id'] = str(patient['_id'])  # Map MongoDB '_id' to 'id' as a string
        del patient['_id']  # Remove MongoDB's native '_id' field to avoid conflicts
    return patients

def add_patient(name, age, condition):
    """Add a new patient to the database."""
    patient = {
        'name': name,
        'age': age,
        'condition': condition,
        'iot_data': [],
        'alerts': [],
        'iot_integrated': False  # Adding an IoT integration status flag
    }
    result = patients_collection.insert_one(patient)  # Insert the patient into the collection
    patient['id'] = str(result.inserted_id)  # Use the '_id' assigned by MongoDB as the 'id'
    return patient

def generate_alerts(patients):
    """Generate critical alerts based on patient conditions."""
    alerts = []
    for patient in patients:
        if "high bp" in patient['condition'].lower():
            alerts.append(f"Critical Alert: {patient['name']} has high blood pressure!")
        if "high heart rate" in patient['condition'].lower():
            alerts.append(f"Critical Alert: {patient['name']} has a high heart rate!")
    return alerts

def update_patient_with_iot(patient_id, iot_data):
    """Update a patient's record with IoT data and integrate IoT."""
    patients_collection.update_one(
        {'_id': patient_id},
        {'$set': {'iot_integrated': True, 'iot_data': iot_data}}
    )
