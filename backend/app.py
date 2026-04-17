import os
import io
import traceback
import hashlib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from PIL import Image
from datetime import datetime, date
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ── MongoDB Connection ────────────────────────────────────────────────────
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/food_classification')
DB_NAME   = 'food_classification'

def connect_mongodb():
    """Auto-connect to MongoDB and verify connection on startup."""
    try:
        c  = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        c.admin.command('ping')          # actual connection test
        database = c[DB_NAME]
        print("=" * 60)
        print(f"✅ MongoDB connected successfully!")
        print(f"   Database : {DB_NAME}")
        print(f"   Host     : {c.HOST}:{c.PORT}")
        print(f"   Collections: users, user_metrics, food_records")
        print("=" * 60)
        return c, database
    except Exception as e:
        print("=" * 60)
        print(f"❌ MongoDB connection FAILED: {e}")
        print(f"   URI tried: {MONGO_URI[:50]}...")
        print("   Check your MONGO_URI in .env file")
        print("=" * 60)
        raise SystemExit(1)

client, db  = connect_mongodb()
users_col   = db['users']
metrics_col = db['user_metrics']
records_col = db['food_records']

# Indexes for performance
users_col.create_index('email',    unique=True)
users_col.create_index('username', unique=True)
records_col.create_index('user_id')
print(f"✅ Indexes verified on all collections")

UPLOAD_FOLDER      = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE      = 50 * 1024 * 1024

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

print("=" * 60)
print(f"MongoDB connected")
print("Loading TFLite MobileNetV2 model...")
print("=" * 60)

from tflite_loader import analyze_food_tflite as analyze_food_local

def load_model():
    from tflite_loader import _load_interpreter
    return _load_interpreter()

# ── Helpers ───────────────────────────────────────────────────────────────
def allowed_file(f):
    return '.' in f and f.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def str_id(obj_id):
    return str(obj_id)

def calculate_age_from_dob(dob_str):
    try:
        dob   = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        age   = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return None

def calculate_bmi(h, w):
    if not h or not w or h <= 0 or w <= 0:
        return 0
    return round(w / ((h / 100) ** 2), 1)

def get_bmi_category(bmi):
    if bmi < 18.5:  return 'Underweight'
    elif bmi < 25:  return 'Normal'
    elif bmi < 30:  return 'Overweight'
    else:           return 'Obese'

def calculate_tdee(w, h, age, gender, activity):
    if gender.lower() == 'male':
        bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
    else:
        bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
    multipliers = {
        'sedentary':      1.2,
        'lightly_active': 1.375,
        'active':         1.55,
        'very_active':    1.725,
        'extra_active':   1.9,
    }
    return round(bmr * multipliers.get(activity.lower(), 1.55), 1)

def get_recommendation(cal, daily, bmi, gender):
    bmi_cat     = get_bmi_category(bmi)
    meal_target = daily / 3
    pct         = (cal / daily) * 100 if daily > 0 else 0

    if cal <= meal_target:
        status, status_text = 'success', 'Safe meal - within single-meal target'
    elif cal <= meal_target * 1.2:
        status, status_text = 'warning', 'Moderate - slightly above meal target'
    else:
        status, status_text = 'danger',  'High calorie alert - exceeds meal target'

    recs   = []
    avoids = []

    if bmi_cat == 'Underweight':
        recs = [
            'Increase calorie intake with nutrient-dense foods like nuts and avocado',
            'Add protein-rich foods (eggs, legumes, dairy) at every meal',
            'Eat 5-6 smaller meals throughout the day to boost total intake',
            'Include healthy fats like olive oil, seeds, and nut butters',
            'Consult a nutritionist for a personalized weight-gain meal plan',
        ]
        avoids = [
            'Avoid skipping meals - even small snacks count toward your daily goal',
            'Avoid excessive cardio without compensating with extra calories',
            'Avoid low-fat or diet versions of foods; you need the calories',
            'Avoid prolonged gaps (>4 hrs) between meals',
            'Avoid caffeine on an empty stomach - it suppresses appetite',
        ]
    elif bmi_cat == 'Normal':
        recs = [
            'Maintain your balanced diet - you are in the healthy weight range',
            'Aim for 25-30g of fiber daily through vegetables, fruits, and whole grains',
            'Stay hydrated with 2-3 liters of water to support metabolism',
            'Include lean proteins to support muscle maintenance and satiety',
            'Continue regular physical activity (150 min/week moderate intensity)',
        ]
        avoids = [
            'Avoid ultra-processed snacks that add empty calories',
            'Avoid skipping breakfast - it leads to overeating later',
            'Avoid sugary beverages; they add calories without nutrition',
            'Avoid large portions late at night - digestion slows down',
            'Avoid crash diets; they disrupt your current healthy balance',
        ]
    elif bmi_cat == 'Overweight':
        recs = [
            'Reduce daily intake by 300-500 kcal below your TDEE for steady loss',
            'Prioritize high-volume, low-calorie foods like leafy greens and soups',
            'Aim for at least 150-200 min/week of moderate cardio',
            'Eat protein first at each meal to improve satiety and reduce cravings',
            'Track your meals for 2 weeks to identify hidden calorie sources',
        ]
        avoids = [
            'Avoid refined carbohydrates (white bread, pastries, sugary cereals)',
            'Avoid fried foods and fast food - calorie density is very high',
            'Avoid eating while distracted (TV, phone) - leads to overconsumption',
            'Avoid alcohol - it adds empty calories and lowers inhibition around food',
            'Avoid skipping meals - paradoxically causes overeating later',
        ]
    else:
        recs = [
            'Consult a doctor or registered dietitian for a medically supervised plan',
            'Start with small sustainable changes - even 5-10% weight loss improves health',
            'Focus on low-glycemic foods to stabilize blood sugar and reduce hunger',
            'Begin with low-impact exercise (walking, swimming) to build consistency',
            'Track every meal to build awareness of total daily intake patterns',
        ]
        avoids = [
            'Avoid all sugary beverages including fruit juice, soda, and energy drinks',
            'Avoid high-sodium processed foods that cause water retention and bloating',
            'Avoid fad diets or extreme restriction - they cause rebound weight gain',
            'Avoid sedentary stretches >1 hour; set reminders to move every 45 min',
            'Avoid using food as emotional comfort - seek support if stress-eating',
        ]

    if gender.lower() == 'female':
        recs.append('Iron-rich foods (spinach, lentils) are especially important for women')
    else:
        recs.append('Adequate zinc from lean meat and seeds supports testosterone levels')

    return {
        'status':          status,
        'status_text':     status_text,
        'meal_pct':        round(pct, 1),
        'recommendations': recs[:5],
        'avoids':          avoids[:5],
        'bmi_category':    bmi_cat,
    }

# ── Routes ────────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'mode': 'MongoDB + MobileNetV2'}), 200

@app.route('/api/init-db', methods=['POST'])
def init_db():
    return jsonify({'message': 'MongoDB auto-initializes on first insert'}), 200

@app.route('/api/test-model', methods=['GET'])
def test_model():
    try:
        load_model()
        return jsonify({'status': 'success', 'model': 'MobileNetV2 TFLite'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ── Auth ──────────────────────────────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data      = request.json
    full_name = data.get('full_name', '').strip()
    username  = data.get('username', '').strip()
    email     = data.get('email', '').strip().lower()
    password  = data.get('password', '')
    dob       = data.get('dob', '')
    gender    = data.get('gender', 'male')

    if not all([full_name, username, email, password, dob]):
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    age = calculate_age_from_dob(dob)
    if age is None or age < 5 or age > 120:
        return jsonify({'error': 'Invalid date of birth'}), 400

    if users_col.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400
    if users_col.find_one({'username': username}):
        return jsonify({'error': 'Username already taken'}), 400

    try:
        result = users_col.insert_one({
            'full_name':     full_name,
            'username':      username,
            'email':         email,
            'password_hash': hash_password(password),
            'dob':           dob,
            'age':           age,
            'gender':        gender,
            'created_at':    datetime.utcnow(),
        })
        return jsonify({
            'user_id':   str_id(result.inserted_id),
            'full_name': full_name,
            'age':       age,
            'message':   'Registered successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data     = request.json
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = users_col.find_one({'email': email, 'password_hash': hash_password(password)})
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({
        'user_id':   str_id(user['_id']),
        'full_name': user['full_name'],
        'username':  user['username'],
        'email':     user['email'],
        'gender':    user['gender'],
        'age':       user['age'],
        'message':   'Login successful'
    }), 200

# ── Metrics ───────────────────────────────────────────────────────────────
@app.route('/api/users/<user_id>/metrics', methods=['POST'])
def save_user_metrics(user_id):
    d   = request.json
    h   = float(d['height_cm'])
    w   = float(d['weight_kg'])
    age = int(d.get('age', 25))
    gen = d.get('gender', 'male')
    act = d.get('activity_level', 'active')
    bmi = calculate_bmi(h, w)
    dc  = calculate_tdee(w, h, age, gen, act)

    try:
        metrics_col.insert_one({
            'user_id':        user_id,
            'height_cm':      h,
            'weight_kg':      w,
            'age':            age,
            'gender':         gen,
            'bmi':            bmi,
            'daily_calories': dc,
            'activity_level': act,
            'recorded_at':    datetime.utcnow(),
        })
        return jsonify({
            'bmi':            bmi,
            'bmi_category':   get_bmi_category(bmi),
            'daily_calories': dc,
            'message':        'Saved'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ── Classify Food ─────────────────────────────────────────────────────────
@app.route('/api/classify-food', methods=['POST'])
def classify_food_endpoint():
    user_id       = request.form.get('user_id')
    h             = request.form.get('height_cm', type=float)
    w             = request.form.get('weight_kg', type=float)
    age           = request.form.get('age', 25, type=int)
    gender        = request.form.get('gender', 'male')
    activity      = request.form.get('activity_level', 'active')
    # ✅ If user selected a food name override from frontend, use it
    food_override = request.form.get('food_name_override', '').strip()

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    file = request.files['image']
    if not file.filename or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    if not h or not w:
        return jsonify({'error': 'height_cm and weight_kg are required'}), 400

    try:
        image_bytes = file.read()
        ai, err     = analyze_food_local(image_bytes)

        if ai:
            food_name         = ai.get('food_name', 'Unknown Food')
            calories          = float(ai.get('calories', 200))
            description       = ai.get('description', '')
            confidence        = ai.get('confidence', 'medium')
            estimated_portion = ai.get('estimated_portion', 'medium')
        else:
            food_name, calories, description, confidence, estimated_portion = (
                'Unknown Food', 200.0, '', 'low', 'medium'
            )

        # ✅ Override food name if user selected one — saves correctly in history
        if food_override:
            food_name = food_override

        bmi     = calculate_bmi(h, w)
        dc      = calculate_tdee(w, h, age, gender, activity)
        bmi_cat = get_bmi_category(bmi)
        rec     = get_recommendation(calories, dc, bmi, gender)

        img   = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
        fname = secure_filename(f"{user_id}_{datetime.now().timestamp()}.jpg")
        img.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))

        records_col.insert_one({
            'user_id':           user_id,
            'food_name':         food_name,
            'calories':          calories,
            'estimated_portion': estimated_portion,
            'image_path':        fname,
            'bmi':               bmi,
            'daily_calories':    dc,
            'recommendation':    rec['status_text'],
            'created_at':        datetime.utcnow(),
        })

        return jsonify({
            'food_name':         food_name,
            'calories':          calories,
            'estimated_portion': estimated_portion,
            'description':       description,
            'confidence':        confidence,
            'bmi':               bmi,
            'bmi_category':      bmi_cat,
            'daily_calories':    dc,
            'meal_target':       round(dc / 3, 1),
            'meal_pct':          rec['meal_pct'],
            'recommendation':    rec['status_text'],
            'recommendations':   rec['recommendations'],
            'avoids':            rec['avoids'],
            'status':            rec['status'],
            'image':             fname,
        }), 200

    except Exception as e:
        print(f"[classify-food] ERROR:\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ── User Profile ──────────────────────────────────────────────────────────
@app.route('/api/users/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    try:
        user = users_col.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        metrics = metrics_col.find_one(
            {'user_id': user_id},
            sort=[('recorded_at', DESCENDING)]
        )

        result = {
            'user_id':   str_id(user['_id']),
            'full_name': user['full_name'],
            'username':  user['username'],
            'email':     user['email'],
            'gender':    user['gender'],
            'age':       user['age'],
        }
        if metrics:
            result.update({
                'height':         metrics['height_cm'],
                'weight':         metrics['weight_kg'],
                'bmi':            metrics['bmi'],
                'daily_calories': metrics['daily_calories'],
                'activity':       metrics['activity_level'],
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── History ───────────────────────────────────────────────────────────────
@app.route('/api/users/<user_id>/history', methods=['GET'])
def get_user_history(user_id):
    try:
        records = list(records_col.find(
            {'user_id': user_id},
            sort=[('created_at', DESCENDING)],
            limit=50
        ))
        return jsonify([{
            'food_name':         r['food_name'],
            'calories':          r['calories'],
            'estimated_portion': r.get('estimated_portion', 'medium'),
            'bmi':               r.get('bmi', 0),
            'bmi_category':      get_bmi_category(r.get('bmi', 22)),
            'daily_calories':    r.get('daily_calories', 0),
            'recommendation':    r.get('recommendation', ''),
            'created_at':        str(r.get('created_at', '')),
            'image_path':        r.get('image_path', ''),
        } for r in records]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Startup ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port  = int(os.getenv('PORT', 5000))
    host  = os.getenv('API_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"\n🚀 Starting Flask on {host}:{port} | debug={debug}\n")
    app.run(debug=debug, host=host, port=port)