from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
import bcrypt
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# MongoDB configuration
app.config['MONGO_URI'] = 'mongodb://localhost:27017/userDB'
mongo = PyMongo(app)

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    return len(phone) == 10 and phone.isdigit()

def validate_aadhar(aadhar):
    return len(aadhar) == 4 and aadhar.isdigit()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        leo_password = request.form.get('leo_password')
        
        user = mongo.db.users.find_one({'email': email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']) and \
           bcrypt.checkpw(leo_password.encode('utf-8'), user['leo_password']):
            session['user_id'] = str(user['_id'])
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
        
        # Check if email already exists
        if mongo.db.users.find_one({'email': email}):
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Hash passwords
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_leo_password = bcrypt.hashpw(leo_password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user document
        user = {
            'name': name,
            'aadhar_last_four': aadhar,
            'gender': gender,
            'email': email,
            'password': hashed_password,
            'leo_password': hashed_leo_password,
            'phone': phone,
            'parent_phone': parent_phone,
            'created_at': datetime.utcnow()
        }
        
        mongo.db.users.insert_one(user)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "Welcome to Dashboard!"  # You can create a dashboard template later

if __name__ == '__main__':
    app.run(debug=True)
