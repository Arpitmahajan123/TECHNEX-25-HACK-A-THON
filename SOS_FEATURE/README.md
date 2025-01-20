# Women Safety Application

A Flask-based web application designed to enhance women's safety through quick SOS alerts and location sharing.

## Features

- User Registration with Aadhaar verification
- Secure Login System
- Emergency SOS Button
- Real-time Location Tracking
- SMS Alerts to Emergency Contacts
- Encrypted Data Storage

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Twilio Account (for SMS functionality)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd women-safety-app
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

5. Initialize the database:
```bash
flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Security Features

- Password Hashing
- Data Encryption
- Secure Session Management
- Input Validation
- CSRF Protection

## Important Notes

- Make sure to keep your `.env` file secure and never commit it to version control
- The application uses SQLite by default for simplicity. For production, consider using PostgreSQL
- Ensure your Twilio account has sufficient credits for SMS functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details
