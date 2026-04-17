import os
import hashlib
from datetime import datetime
from functools import wraps
from flask import jsonify

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename(filename):
    """Generate secure filename"""
    timestamp = datetime.now().timestamp()
    name = hashlib.md5(filename.encode()).hexdigest()
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
    return f"{name}_{timestamp}.{ext}"

def calculate_bmi(height_cm, weight_kg):
    """Calculate Body Mass Index"""
    if height_cm <= 0 or weight_kg <= 0:
        return None
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 25:
        return 'Normal'
    elif bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'

def calculate_bmr(weight_kg, height_cm, age, gender):
    """Calculate Basal Metabolic Rate using Harris-Benedict equation"""
    if gender.lower() == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age)
    return round(bmr, 2)

def calculate_tdee(weight_kg, height_cm, age, gender, activity_level):
    """Calculate Total Daily Energy Expenditure"""
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'active': 1.55,
        'very_active': 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier
    return round(tdee, 2)

def get_calorie_recommendation(food_calories, daily_calories):
    """Get personalized calorie recommendation"""
    meal_target = daily_calories / 3
    
    if food_calories <= meal_target:
        return {
            'message': 'Safe meal - within single-meal target',
            'status': 'success',
            'color': 'success'
        }
    elif food_calories <= meal_target * 1.2:
        return {
            'message': 'Moderate - consider smaller portion',
            'status': 'warning',
            'color': 'warning'
        }
    elif food_calories <= daily_calories:
        return {
            'message': 'High calorie - may exceed daily limit',
            'status': 'danger',
            'color': 'danger'
        }
    else:
        return {
            'message': 'Very high calorie alert',
            'status': 'danger',
            'color': 'danger'
        }

def require_api_key(f):
    """Decorator to require API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = os.getenv('API_KEY')
        if not api_key:
            return f(*args, **kwargs)
        
        from flask import request
        key = request.headers.get('X-API-Key')
        
        if not key or key != api_key:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def handle_db_error(f):
    """Decorator to handle database errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return decorated_function
