# DocAI: Healthcare Portal for Doctors
## DEMO VIDEO:
https://tinyurl.com/arshia-doc

DocAI is a web-based healthcare portal designed for doctors to manage patient records, integrate IoT data, and leverage AI for treatment predictions.

## Features

- Doctor authentication and dashboard
- Patient management system
- IoT data integration for real-time patient monitoring
- AI-powered treatment recommendations
- QR code generation for patient identification

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Machine Learning**: scikit-learn
- **Frontend**: HTML, CSS, JavaScript

## Setup Instructions

### Prerequisites

- Python 3.10+
- MongoDB
- Required Python packages (see lib.txt)

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r lib.txt
   ```
3. Set up MongoDB:
   - Create a database named `healthcare_db`
   - Create collections: `doctors` and `patients`
   - Use the script in `initialdata/MongoDBScript_init.txt` to initialize data

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at `http://localhost:5000`

## Default Login

- **Doctor ID**: arshia
- **Password**: arshia123
