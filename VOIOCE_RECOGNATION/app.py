from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here123456789')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///women_safety.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'ACcd19bfe941a7973d3444da3e404234a7')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'b30d3ab8d1594fba740e1cba86831f57')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+16203372593')
EMERGENCY_CONTACT = os.getenv('EMERGENCY_CONTACT', '+917276779611')

# Verify Twilio credentials are loaded
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, EMERGENCY_CONTACT]):
    print("Warning: Some Twilio credentials are missing!")

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create cipher suite for encryption
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    aadhaar_number = db.Column(db.String(200), unique=True, nullable=False)
    mobile_number = db.Column(db.String(200), nullable=False)
    emergency_contact = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def encrypt_data(self, data):
        return cipher_suite.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        return cipher_suite.decrypt(encrypted_data.encode()).decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            aadhaar = request.form.get('aadhaar')
            mobile = request.form.get('mobile')
            emergency = request.form.get('emergency')
            email = request.form.get('email')
            password = request.form.get('password')

            if not all([name, aadhaar, mobile, emergency, email, password]):
                flash('All fields are required')
                return redirect(url_for('register'))

            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))

            user = User(
                name=name,
                email=email
            )
            
            user.aadhaar_number = user.encrypt_data(aadhaar)
            user.mobile_number = user.encrypt_data(mobile)
            user.emergency_contact = user.encrypt_data(emergency)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/send_sos', methods=['POST'])
@login_required
def send_sos():
    try:
        # Get location data if provided
        data = request.json or {}
        lat = data.get('lat')
        lng = data.get('lng')
        
        # Format the Google Maps link if location is available
        location_text = ""
        if lat and lng:
            maps_link = f"https://www.google.com/maps?q={lat},{lng}"
            location_text = f"\nTheir current location: {maps_link}"

        # Debug print statements
        print("\nDEBUG: Current Environment Variables:")
        print(f"TWILIO_ACCOUNT_SID: {TWILIO_ACCOUNT_SID}")
        print(f"TWILIO_AUTH_TOKEN: {TWILIO_AUTH_TOKEN[:5]}...")  # Only print first 5 chars for security
        print(f"TWILIO_PHONE_NUMBER: {TWILIO_PHONE_NUMBER}")
        print(f"EMERGENCY_CONTACT: {EMERGENCY_CONTACT}")

        # Prepare message
        message_body = f"""EMERGENCY SOS ALERT!
{current_user.name} needs immediate help!{location_text}
This is an emergency alert. Please take immediate action."""

        # Verify Twilio credentials
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, EMERGENCY_CONTACT]):
            missing_creds = []
            if not TWILIO_ACCOUNT_SID: missing_creds.append("TWILIO_ACCOUNT_SID")
            if not TWILIO_AUTH_TOKEN: missing_creds.append("TWILIO_AUTH_TOKEN")
            if not TWILIO_PHONE_NUMBER: missing_creds.append("TWILIO_PHONE_NUMBER")
            if not EMERGENCY_CONTACT: missing_creds.append("EMERGENCY_CONTACT")
            raise ValueError(f"Missing Twilio credentials: {', '.join(missing_creds)}")

        # Initialize Twilio client
        print("\nDEBUG: Initializing Twilio client...")
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Log attempt
        print(f"\nAttempting to send SMS:")
        print(f"From: {TWILIO_PHONE_NUMBER}")
        print(f"To: {EMERGENCY_CONTACT}")
        print(f"Message: {message_body}")

        # Send message
        message = client.messages.create(
            to=EMERGENCY_CONTACT,
            from_=TWILIO_PHONE_NUMBER,
            body=message_body
        )
        
        print(f"Message sent successfully! SID: {message.sid}")
        
        return jsonify({
            'success': True,
            'message': 'Emergency alert sent successfully',
            'debug_info': {
                'message_sid': message.sid,
                'to': EMERGENCY_CONTACT,
                'from': TWILIO_PHONE_NUMBER
            }
        })

    except TwilioRestException as twilio_error:
        error_msg = f"Twilio Error: {str(twilio_error)}"
        print(f"DEBUG: {error_msg}")
        print(f"DEBUG: Error Code: {twilio_error.code}")
        print(f"DEBUG: Error Message: {twilio_error.msg}")
        
        if twilio_error.code == 20003:
            error_msg = "Authentication failed. Please check Twilio credentials."
        elif twilio_error.code in [21211, 21214]:
            error_msg = "Invalid phone number format. Please ensure phone numbers include country code (e.g., +1)"
        elif twilio_error.code == 21606:
            error_msg = "The Twilio phone number is invalid or not active"
        elif twilio_error.code == 20404:
            error_msg = "The Twilio phone number does not exist or is not in your account"
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'debug_info': {
                'code': twilio_error.code,
                'message': str(twilio_error)
            }
        }), 500

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500

@app.route('/check_voice', methods=['POST'])
@login_required
def check_voice():
    try:
        text = request.json.get('text', '').lower()
        if 'help help' in text:
            return jsonify({'status': 'success', 'trigger_alert': True})
        return jsonify({'status': 'success', 'trigger_alert': False})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
