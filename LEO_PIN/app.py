from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    aadhar_last_four = db.Column(db.String(4), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    leo_password = db.Column(db.LargeBinary, nullable=False)
    phone = db.Column(db.String(10), nullable=False)
    parent_phone = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    return len(phone) == 10 and phone.isdigit()

def validate_aadhar(aadhar):
    return len(aadhar) == 4 and aadhar.isdigit()

def validate_leo_password(password):
    return len(password) == 4 and password.isdigit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        leo_password = request.form.get('leo_password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password) and \
           bcrypt.checkpw(leo_password.encode('utf-8'), user.leo_password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        aadhar = request.form.get('aadhar')
        gender = request.form.get('gender')
        email = request.form.get('email')
        password = request.form.get('password')
        leo_password = request.form.get('leo_password')
        phone = request.form.get('phone')
        parent_phone = request.form.get('parent_phone')
        
        # Validation
        if not all([name, aadhar, gender, email, password, leo_password, phone, parent_phone]):
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        if not validate_email(email):
            flash('Invalid email format', 'error')
            return redirect(url_for('register'))
        
        if not validate_phone(phone) or not validate_phone(parent_phone):
            flash('Invalid phone number format', 'error')
            return redirect(url_for('register'))
        
        if not validate_aadhar(aadhar):
            flash('Invalid Aadhar number format (need last 4 digits)', 'error')
            return redirect(url_for('register'))
            
        if not validate_leo_password(leo_password):
            flash('LEO password must be exactly 4 digits', 'error')
            return redirect(url_for('register'))
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Hash passwords
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_leo_password = bcrypt.hashpw(leo_password.encode('utf-8'), bcrypt.gensalt())
        
        # Create new user
        new_user = User(
            name=name,
            aadhar_last_four=aadhar,
            gender=gender,
            email=email,
            password=hashed_password,
            leo_password=hashed_leo_password,
            phone=phone,
            parent_phone=parent_phone
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/verify-pin', methods=['POST'])
def verify_pin():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    pin = data.get('pin')
    
    if not pin or not pin.isdigit() or len(pin) != 4:
        return jsonify({'success': False, 'message': 'Invalid PIN format'})
    
    user = User.query.get(session['user_id'])
    if user and bcrypt.checkpw(pin.encode('utf-8'), user.leo_password):
        return jsonify({'success': True, 'message': 'PIN verified successfully'})
    return jsonify({'success': False, 'message': 'Incorrect PIN'})

@app.route('/delete-app')
def delete_app():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash('Your account has been deleted successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
