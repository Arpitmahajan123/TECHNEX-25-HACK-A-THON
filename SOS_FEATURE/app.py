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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///women_safety.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create cipher suite for encryption
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    aadhaar_number = db.Column(db.String(200), unique=True, nullable=False)  # Encrypted
    mobile_number = db.Column(db.String(200), nullable=False)  # Encrypted
    emergency_contact = db.Column(db.String(200), nullable=False)  # Encrypted
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

            if User.query.filter_by(email=email).first():
                flash('Email already registered')
                return redirect(url_for('register'))

            # Create new user instance
            user = User(
                name=name,
                email=email
            )
            
            # Set encrypted fields
            user.aadhaar_number = user.encrypt_data(aadhaar)
            user.mobile_number = user.encrypt_data(mobile)
            user.emergency_contact = user.encrypt_data(emergency)
            user.set_password(password)

            # Add and commit to database
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
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()

            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully!')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password')
        except Exception as e:
            flash(f'Login error: {str(e)}')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/send_sos', methods=['POST'])
@login_required
def send_sos():
    try:
        data = request.json
        lat = data.get('lat')
        lng = data.get('lng')
        
        if not lat or not lng:
            return jsonify({'success': False, 'error': 'Location data missing'}), 400

        # Format the Google Maps link
        maps_link = f"https://www.google.com/maps?q={lat},{lng}"
        
        # Emergency contact number (recipient)
        to_number = os.getenv('EMERGENCY_CONTACT')  # Get emergency contact from environment variable

        # Twilio phone number for sending SMS
        from_number = os.getenv('TWILIO_PHONE_NUMBER')  # Get Twilio phone number from environment variable

        # Prepare message
        message_body = f"""
EMERGENCY SOS ALERT!
{current_user.name} needs immediate help!
Their current location: {maps_link}
This is an emergency alert. Please take immediate action.
        """

        try:
            # Initialize Twilio client
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            
            # Debug logging
            print(f"\nTwilio Credentials:")
            print(f"Account SID: {account_sid}")
            print(f"Auth Token: {'*' * len(auth_token) if auth_token else 'None'}")
            
            client = Client(account_sid, auth_token)

            # Log attempt
            print(f"\nAttempting to send SMS:")
            print(f"From: {from_number} (Twilio number)")
            print(f"To: {to_number} (Emergency contact)")
            print(f"Message: {message_body}")

            # Send message using Twilio phone number
            message = client.messages.create(
                to=to_number,
                from_=from_number,
                body=message_body
            )
            
            print(f"Message sent successfully! SID: {message.sid}")
            
            return jsonify({
                'success': True,
                'message': 'Emergency alert sent successfully',
                'debug_info': {
                    'message_sid': message.sid,
                    'to': to_number,
                    'from': from_number,
                    'location': maps_link
                }
            })

        except TwilioRestException as twilio_error:
            error_msg = str(twilio_error)
            print(f"Twilio Error Details: {error_msg}")
            
            if twilio_error.code == 20003:
                error_msg = "Authentication failed. Please check Twilio credentials."
            elif twilio_error.code in [21211, 21214]:
                error_msg = "Invalid phone number format"
            elif twilio_error.code == 21606:
                error_msg = "Invalid Twilio phone number"
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'debug_info': {
                    'error_code': twilio_error.code,
                    'to': to_number,
                    'from': from_number
                }
            }), 500

        except Exception as e:
            print(f"General Error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"An unexpected error occurred: {str(e)}",
                'debug_info': {
                    'to': to_number,
                    'from': from_number
                }
            }), 500

    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
