
# import os
# import io
# import traceback
# import hashlib
# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from werkzeug.utils import secure_filename
# from PIL import Image
# from datetime import datetime, date
# from pymongo import MongoClient, DESCENDING
# from bson import ObjectId
# from dotenv import load_dotenv

# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# print("\n" + "="*60)
# print("🍕 FOOD CLASSIFICATION API - FULL VERSION")
# print("="*60)

# # ── MongoDB Connection ─────────────────────────────────────────
# MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
# db = None
# users_col = None
# metrics_col = None
# records_col = None

# try:
#     client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
#     client.admin.command('ping')
#     db = client['food_classification']
#     print("✅ MongoDB connected successfully!")
    
#     # Collections
#     users_col = db['users']
#     metrics_col = db['user_metrics']
#     records_col = db['food_records']
    
#     # Create indexes
#     users_col.create_index('email', unique=True)
#     users_col.create_index('username', unique=True)
#     records_col.create_index('user_id')
#     print("✅ Indexes created")
    
# except Exception as e:
#     print(f"⚠️ MongoDB connection failed: {e}")
#     print("   Continuing without database...")

# # ── CONFIG ──────────────────────────────────────────
# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# # ── HELPERS ─────────────────────────────────────────
# def hash_password(pw):
#     return hashlib.sha256(pw.encode()).hexdigest()

# def str_id(obj_id):
#     return str(obj_id)

# def calculate_age_from_dob(dob_str):
#     try:
#         dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
#         today = date.today()
#         age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#         return age
#     except:
#         return 25

# def calculate_bmi(h, w):
#     if not h or not w or h <= 0 or w <= 0:
#         return 0
#     return round(w / ((h / 100) ** 2), 1)

# def get_bmi_category(bmi):
#     if bmi < 18.5: return 'Underweight'
#     elif bmi < 25: return 'Normal'
#     elif bmi < 30: return 'Overweight'
#     else: return 'Obese'

# def calculate_tdee(w, h, age, gender, activity):
#     if gender.lower() == 'male':
#         bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
#     else:
#         bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
    
#     multipliers = {
#         'sedentary': 1.2,
#         'lightly_active': 1.375,
#         'active': 1.55,
#         'very_active': 1.725,
#         'extra_active': 1.9
#     }
#     return round(bmr * multipliers.get(activity.lower(), 1.55), 1)

# def get_calories_for_food(food_name):
#     """Return realistic calories for common foods"""
#     food_lower = food_name.lower()
    
#     # High calorie - Junk foods
#     if 'pizza' in food_lower: return 700
#     if 'burger' in food_lower: return 650
#     if 'cheeseburger' in food_lower: return 750
#     if 'fries' in food_lower: return 500
#     if 'cake' in food_lower: return 450
#     if 'ice cream' in food_lower: return 300
#     if 'chocolate' in food_lower: return 250
#     if 'biryani' in food_lower: return 650
#     if 'pasta' in food_lower: return 500
#     if 'noodles' in food_lower: return 450
#     if 'samosa' in food_lower: return 280
#     if 'donut' in food_lower: return 300
#     if 'pastry' in food_lower: return 400
#     if 'cookie' in food_lower: return 250
#     if 'brownie' in food_lower: return 350
#     if 'fried chicken' in food_lower: return 600
#     if 'taco' in food_lower: return 300
#     if 'burrito' in food_lower: return 550
    
#     # Medium calorie
#     if 'naan' in food_lower: return 300
#     if 'roti' in food_lower or 'chapati' in food_lower: return 120
#     if 'rice' in food_lower and 'fried' not in food_lower: return 200
#     if 'fried rice' in food_lower: return 350
#     if 'dosa' in food_lower: return 250
#     if 'idli' in food_lower: return 150
#     if 'vada' in food_lower: return 200
#     if 'poha' in food_lower: return 250
#     if 'upma' in food_lower: return 220
    
#     # Low calorie - Healthy foods
#     if 'salad' in food_lower: return 150
#     if 'apple' in food_lower: return 95
#     if 'banana' in food_lower: return 105
#     if 'orange' in food_lower: return 60
#     if 'mango' in food_lower: return 150
#     if 'watermelon' in food_lower: return 80
#     if 'grapes' in food_lower: return 70
#     if 'dal' in food_lower: return 180
#     if 'sambar' in food_lower: return 100
#     if 'soup' in food_lower: return 120
    
#     return 220  # Default

# def get_recommendations_for_bmi(bmi_cat):
#     if bmi_cat == 'Underweight':
#         return [
#             '🥜 Increase calorie intake with nutrient-dense foods like nuts and avocado',
#             '🥚 Add protein-rich foods (eggs, legumes, dairy) at every meal',
#             '🍽️ Eat 5-6 smaller meals throughout the day to boost total intake',
#             '🫒 Include healthy fats like olive oil, seeds, and nut butters',
#             '👨‍⚕️ Consult a nutritionist for a personalized weight-gain meal plan'
#         ]
#     elif bmi_cat == 'Normal':
#         return [
#             '🥗 Maintain your balanced diet - you are in the healthy weight range',
#             '🌾 Aim for 25-30g of fiber daily through vegetables, fruits, and whole grains',
#             '💧 Stay hydrated with 2-3 liters of water to support metabolism',
#             '🍗 Include lean proteins to support muscle maintenance and satiety',
#             '🏃 Continue regular physical activity (150 min/week moderate intensity)'
#         ]
#     else:  # Overweight/Obese
#         return [
#             '📉 Reduce daily intake by 300-500 kcal below your TDEE for steady loss',
#             '🥬 Prioritize high-volume, low-calorie foods like leafy greens and soups',
#             '🏋️ Aim for at least 150-200 min/week of moderate cardio',
#             '🍽️ Eat protein first at each meal to improve satiety',
#             '📝 Track your meals for 2 weeks to identify hidden calorie sources'
#         ]

# def get_avoids_for_bmi(bmi_cat):
#     if bmi_cat == 'Underweight':
#         return [
#             '❌ Avoid skipping meals - even small snacks count',
#             '❌ Avoid excessive cardio without compensating with extra calories',
#             '❌ Avoid low-fat or diet versions of foods',
#             '❌ Avoid prolonged gaps (>4 hrs) between meals'
#         ]
#     elif bmi_cat == 'Normal':
#         return [
#             '❌ Avoid ultra-processed snacks that add empty calories',
#             '❌ Avoid sugary beverages; they add calories without nutrition',
#             '❌ Avoid large portions late at night - digestion slows down',
#             '❌ Avoid crash diets; they disrupt your current healthy balance'
#         ]
#     else:  # Overweight/Obese
#         return [
#             '❌ Avoid refined carbohydrates (white bread, pastries, sugary cereals)',
#             '❌ Avoid fried foods and fast food - calorie density is very high',
#             '❌ Avoid eating while distracted (TV, phone) - leads to overconsumption',
#             '❌ Avoid alcohol - it adds empty calories',
#             '❌ Avoid skipping meals - paradoxically causes overeating later'
#         ]

# # ── ✅ MAIN RECOMMENDATION FUNCTION ──
# def get_recommendation(calories, daily_calories, bmi, gender, food_name):
#     bmi_cat = get_bmi_category(bmi)
#     meal_target = daily_calories / 3
#     pct = (calories / daily_calories) * 100 if daily_calories > 0 else 0
    
#     # Junk food list
#     junk_foods = ['pizza', 'burger', 'cheeseburger', 'cake', 'ice cream', 'chocolate', 
#                   'fries', 'pasta', 'noodles', 'biryani', 'samosa', 'pastry', 'donut', 
#                   'cookie', 'brownie', 'muffin', 'fried', 'cheese', 'butter', 'taco', 
#                   'burrito', 'fried chicken', 'hot dog', 'bacon', 'sausage']
#     is_junk = any(junk in food_name.lower() for junk in junk_foods)
    
#     # Debug print
#     print(f"\n🍔 ANALYZING: {food_name}")
#     print(f"   Calories: {calories}, BMI: {bmi} ({bmi_cat})")
#     print(f"   Daily: {daily_calories}, Meal Target: {int(meal_target)}")
#     print(f"   Is Junk Food: {is_junk}")
    
#     # ── HEALTH STATUS LOGIC ──
#     food_health_status = 'healthy'
#     food_health_message = ''
    
#     if bmi_cat == 'Underweight':
#         if is_junk:
#             food_health_status = 'neutral'
#             food_health_message = '⚠️ Junk food gives calories, but choose nutrient-dense options instead'
#         elif calories > meal_target:
#             food_health_status = 'healthy'
#             food_health_message = '✅ Good! High-calorie foods help you gain healthy weight'
#         else:
#             food_health_status = 'neutral'
#             food_health_message = '⚠️ Consider adding more calories to reach your weight goals'
            
#     elif bmi_cat == 'Normal':
#         if is_junk:
#             food_health_status = 'unhealthy'
#             food_health_message = '🔴 Junk food - eat occasionally only!'
#         elif calories > meal_target * 1.2:
#             food_health_status = 'unhealthy'
#             food_health_message = f'🔴 Too many calories ({calories} kcal) for one meal'
#         elif calories > meal_target:
#             food_health_status = 'neutral'
#             food_health_message = '⚠️ Moderate - watch your portions'
#         else:
#             food_health_status = 'healthy'
#             food_health_message = '✅ Healthy choice! Good balance'
            
#     else:  # Overweight or Obese
#         if is_junk:
#             food_health_status = 'unhealthy'
#             food_health_message = '🔴 Junk food - avoid for weight loss!'
#         elif calories > meal_target:
#             food_health_status = 'unhealthy'
#             food_health_message = f'🔴 Too many calories ({calories} kcal) for your weight goal'
#         elif calories > meal_target * 0.8:
#             food_health_status = 'neutral'
#             food_health_message = '⚠️ Moderate - okay occasionally'
#         else:
#             food_health_status = 'healthy'
#             food_health_message = '✅ Great low-calorie choice! Supports weight loss'
    
#     # Status for UI progress bar
#     if calories <= meal_target:
#         status = 'success'
#         status_text = 'Safe meal - within target'
#     elif calories <= meal_target * 1.2:
#         status = 'warning'
#         status_text = 'Moderate - slightly above target'
#     else:
#         status = 'danger'
#         status_text = 'High calorie alert'
    
#     print(f"   ✅ Health Status: {food_health_status}")
#     print(f"   Message: {food_health_message}\n")
    
#     return {
#         'status': status,
#         'status_text': status_text,
#         'meal_pct': round(pct, 1),
#         'food_health_status': food_health_status,
#         'food_health_message': food_health_message,
#         'recommendations': get_recommendations_for_bmi(bmi_cat),
#         'avoids': get_avoids_for_bmi(bmi_cat),
#         'bmi_category': bmi_cat
#     }

# # Try to load AI model
# try:
#     from tflite_loader import analyze_food_tflite as analyze_food_local
#     print("✅ MobileNetV2 model loaded successfully")
# except ImportError:
#     print("⚠️ tflite_loader not found, using mock AI")
#     def analyze_food_local(image_bytes):
#         return {
#             'food_name': 'Food',
#             'calories': 200,
#             'description': 'Food detected from image',
#             'confidence': 'medium',
#             'estimated_portion': 'medium'
#         }, None
# except Exception as e:
#     print(f"⚠️ Error loading AI model: {e}")
#     def analyze_food_local(image_bytes):
#         return {
#             'food_name': 'Food',
#             'calories': 200,
#             'description': 'Food detected from image',
#             'confidence': 'low',
#             'estimated_portion': 'medium'
#         }, None

# # ── API ROUTES ─────────────────────────────────────────

# @app.route('/api/health', methods=['GET'])
# def health():
#     return jsonify({'status': 'running', 'mode': 'Food Classification API'}), 200

# @app.route('/api/test-model', methods=['GET'])
# def test_model():
#     try:
#         return jsonify({'status': 'success', 'model': 'MobileNetV2 TFLite'})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/uploads/<path:filename>', methods=['GET'])
# def serve_upload(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# # ── AUTH ROUTES ─────────────────────────────────────────

# @app.route('/api/register', methods=['POST'])
# def register():
#     data = request.json
#     full_name = data.get('full_name', '').strip()
#     username = data.get('username', '').strip()
#     email = data.get('email', '').strip().lower()
#     password = data.get('password', '')
#     dob = data.get('dob', '')
#     gender = data.get('gender', 'male')
    
#     print(f"\n📝 Registering user: {email}")
    
#     if not all([full_name, username, email, password, dob]):
#         return jsonify({'error': 'All fields are required'}), 400
#     if len(password) < 6:
#         return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
#     age = calculate_age_from_dob(dob)
    
#     if users_col is None:
#         # Mock registration
#         return jsonify({
#             'user_id': 'mock_' + str(int(datetime.now().timestamp())),
#             'full_name': full_name,
#             'age': age,
#             'message': 'Registered successfully (Demo Mode)'
#         }), 201
    
#     # Check existing users
#     if users_col.find_one({'email': email}):
#         return jsonify({'error': 'Email already registered'}), 400
#     if users_col.find_one({'username': username}):
#         return jsonify({'error': 'Username already taken'}), 400
    
#     try:
#         result = users_col.insert_one({
#             'full_name': full_name,
#             'username': username,
#             'email': email,
#             'password_hash': hash_password(password),
#             'dob': dob,
#             'age': age,
#             'gender': gender,
#             'created_at': datetime.utcnow(),
#         })
#         print(f"   ✅ User created with ID: {result.inserted_id}")
#         return jsonify({
#             'user_id': str_id(result.inserted_id),
#             'full_name': full_name,
#             'age': age,
#             'message': 'Registered successfully'
#         }), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400

# @app.route('/api/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email', '').strip().lower()
#     password = data.get('password', '')
    
#     print(f"\n🔐 Login attempt: {email}")
    
#     if not email or not password:
#         return jsonify({'error': 'Email and password are required'}), 400
    
#     if users_col is None:
#         # Mock login
#         return jsonify({
#             'user_id': 'mock_user',
#             'full_name': 'Demo User',
#             'username': 'demouser',
#             'email': email,
#             'gender': 'male',
#             'age': 25,
#             'message': 'Login successful (Demo Mode)'
#         }), 200
    
#     user = users_col.find_one({'email': email, 'password_hash': hash_password(password)})
    
#     if user:
#         print(f"   ✅ User found: {user.get('full_name')}")
#         return jsonify({
#             'user_id': str_id(user['_id']),
#             'full_name': user.get('full_name', 'User'),
#             'username': user.get('username', 'user'),
#             'email': user.get('email', ''),
#             'gender': user.get('gender', 'male'),
#             'age': user.get('age', 25),
#             'message': 'Login successful'
#         }), 200
#     else:
#         print(f"   ❌ Invalid credentials")
#         return jsonify({'error': 'Invalid email or password'}), 401

# # ── USER METRICS ─────────────────────────────────────────

# @app.route('/api/users/<user_id>/metrics', methods=['POST'])
# def save_user_metrics(user_id):
#     try:
#         data = request.json
#         print(f"\n📊 Saving metrics for user: {user_id}")
        
#         h = float(data['height_cm'])
#         w = float(data['weight_kg'])
#         age = int(data.get('age', 25))
#         gen = data.get('gender', 'male')
#         act = data.get('activity_level', 'active')
        
#         bmi = calculate_bmi(h, w)
#         dc = calculate_tdee(w, h, age, gen, act)
        
#         if metrics_col is not None:
#             metrics_col.insert_one({
#                 'user_id': user_id,
#                 'height_cm': h,
#                 'weight_kg': w,
#                 'age': age,
#                 'gender': gen,
#                 'bmi': bmi,
#                 'daily_calories': dc,
#                 'activity_level': act,
#                 'recorded_at': datetime.utcnow(),
#             })
#             print(f"   ✅ Metrics saved to DB! BMI: {bmi}, Daily Calories: {dc}")
#         else:
#             print(f"   ✅ Metrics calculated (Demo): BMI: {bmi}, Daily Calories: {dc}")
        
#         return jsonify({
#             'bmi': bmi,
#             'bmi_category': get_bmi_category(bmi),
#             'daily_calories': dc,
#             'message': 'Metrics saved successfully'
#         }), 201
        
#     except Exception as e:
#         print(f"❌ Error saving metrics: {e}")
#         return jsonify({'error': str(e)}), 400

# # ── USER PROFILE ─────────────────────────────────────────

# @app.route('/api/users/<user_id>/profile', methods=['GET'])
# def get_user_profile(user_id):
#     try:
#         print(f"\n👤 Fetching profile for user: {user_id}")
        
#         result = {
#             'user_id': user_id,
#             'full_name': 'User',
#             'username': 'user',
#             'email': 'user@example.com',
#             'gender': 'male',
#             'age': 25,
#         }
        
#         if users_col is not None:
#             try:
#                 user = users_col.find_one({'_id': ObjectId(user_id)})
#                 if user:
#                     result.update({
#                         'full_name': user.get('full_name', 'User'),
#                         'username': user.get('username', 'user'),
#                         'email': user.get('email', ''),
#                         'gender': user.get('gender', 'male'),
#                         'age': user.get('age', 25),
#                     })
#             except:
#                 pass
            
#             # Get latest metrics
#             if metrics_col is not None:
#                 metrics = metrics_col.find_one(
#                     {'user_id': user_id},
#                     sort=[('recorded_at', DESCENDING)]
#                 )
#                 if metrics:
#                     result.update({
#                         'height': metrics['height_cm'],
#                         'weight': metrics['weight_kg'],
#                         'bmi': metrics['bmi'],
#                         'daily_calories': metrics['daily_calories'],
#                         'activity': metrics['activity_level'],
#                     })
        
#         print(f"   ✅ Profile fetched: {result.get('full_name')}")
#         return jsonify(result), 200
        
#     except Exception as e:
#         print(f"❌ Error fetching profile: {e}")
#         return jsonify({'error': str(e)}), 500

# # ── USER HISTORY ─────────────────────────────────────────

# @app.route('/api/users/<user_id>/history', methods=['GET'])
# def get_user_history(user_id):
#     try:
#         print(f"\n📜 Fetching history for user: {user_id}")
        
#         records = []
#         if records_col is not None:
#             records = list(records_col.find(
#                 {'user_id': user_id},
#                 sort=[('created_at', DESCENDING)],
#                 limit=50
#             ))
        
#         result = [{
#             'food_name': r.get('food_name', ''),
#             'calories': r.get('calories', 0),
#             'estimated_portion': r.get('estimated_portion', 'medium'),
#             'bmi': r.get('bmi', 0),
#             'bmi_category': get_bmi_category(r.get('bmi', 22)),
#             'daily_calories': r.get('daily_calories', 0),
#             'recommendation': r.get('recommendation', ''),
#             'created_at': str(r.get('created_at', '')),
#             'image_path': r.get('image_path', ''),
#         } for r in records]
        
#         print(f"   ✅ Found {len(result)} records")
#         return jsonify(result), 200
        
#     except Exception as e:
#         print(f"❌ Error fetching history: {e}")
#         return jsonify({'error': str(e)}), 500

# # ── CLASSIFY FOOD (MAIN ENDPOINT) ─────────────────────────

# @app.route('/api/classify-food', methods=['POST'])
# def classify_food():
#     print("\n" + "="*50)
#     print("📸 NEW FOOD ANALYSIS REQUEST")
#     print("="*50)
    
#     try:
#         # Get form data
#         user_id = request.form.get('user_id', 'test')
#         h = float(request.form.get('height_cm', 170))
#         w = float(request.form.get('weight_kg', 70))
#         age = int(request.form.get('age', 25))
#         gender = request.form.get('gender', 'male')
#         activity = request.form.get('activity_level', 'active')
#         food_override = request.form.get('food_name_override', '')
        
#         print(f"📊 User: {user_id}")
#         print(f"   Height={h}cm, Weight={w}kg, Age={age}, Gender={gender}")
#         print(f"🍔 Selected Food: {food_override if food_override else 'None'}")
        
#         # Process image
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image provided'}), 400
        
#         file = request.files['image']
#         if not file.filename:
#             return jsonify({'error': 'No file selected'}), 400
        
#         image_bytes = file.read()
        
#         # Get AI analysis
#         ai_result, _ = analyze_food_local(image_bytes)
        
#         if ai_result and not food_override:
#             food_name = ai_result.get('food_name', 'Food')
#             calories = float(ai_result.get('calories', 200))
#             description = ai_result.get('description', '')
#             confidence = ai_result.get('confidence', 'medium')
#             estimated_portion = ai_result.get('estimated_portion', 'medium')
#         else:
#             food_name = 'Food'
#             calories = 200
#             description = ''
#             confidence = 'low'
#             estimated_portion = 'medium'
        
#         # Override with user selection
#         if food_override:
#             food_name = food_override
#             calories = get_calories_for_food(food_name)
        
#         # Calculate metrics
#         bmi = calculate_bmi(h, w)
#         bmi_cat = get_bmi_category(bmi)
#         daily_calories = calculate_tdee(w, h, age, gender, activity)
        
#         # Get recommendation
#         rec = get_recommendation(calories, daily_calories, bmi, gender, food_name)
        
#         # Save to database (if real user and DB available)
#         if records_col is not None and user_id and user_id != 'test' and user_id != 'mock_user':
#             try:
#                 # Save image
#                 img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
#                 fname = secure_filename(f"{user_id}_{datetime.now().timestamp()}.jpg")
#                 img.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                
#                 # Save record
#                 records_col.insert_one({
#                     'user_id': user_id,
#                     'food_name': food_name,
#                     'calories': calories,
#                     'estimated_portion': estimated_portion,
#                     'image_path': fname,
#                     'bmi': bmi,
#                     'daily_calories': daily_calories,
#                     'recommendation': rec['status_text'],
#                     'created_at': datetime.utcnow(),
#                 })
#                 print(f"   💾 Saved to database")
#             except Exception as db_error:
#                 print(f"   ⚠️ Could not save to DB: {db_error}")
        
#         # Build response
#         response = {
#             "food_name": food_name,
#             "calories": calories,
#             "estimated_portion": estimated_portion,
#             "description": description,
#             "confidence": confidence,
#             "bmi": bmi,
#             "bmi_category": bmi_cat,
#             "daily_calories": daily_calories,
#             "meal_target": round(daily_calories / 3, 1),
#             "meal_pct": rec['meal_pct'],
#             "recommendation": rec['status_text'],
#             "recommendations": rec['recommendations'],
#             "avoids": rec['avoids'],
#             "status": rec['status'],
#             "food_health_status": rec['food_health_status'],
#             "food_health_message": rec['food_health_message']
#         }
        
#         print(f"\n✅ SENDING RESPONSE:")
#         print(f"   Food: {response['food_name']}")
#         print(f"   Health Status: {response['food_health_status']}")
#         print(f"   Message: {response['food_health_message']}")
#         print("="*50 + "\n")
        
#         return jsonify(response), 200
        
#     except Exception as e:
#         print(f"❌ ERROR: {traceback.format_exc()}")
#         return jsonify({"error": str(e)}), 500

# # ── INIT DB ENDPOINT ─────────────────────────────────────────

# @app.route('/api/init-db', methods=['POST'])
# def init_db():
#     return jsonify({'message': 'MongoDB auto-initializes on first insert'}), 200

# # ── RUN SERVER ─────────────────────────────────────────

# if __name__ == '__main__':
#     port = int(os.getenv('PORT', 5000))
#     host = os.getenv('API_HOST', '0.0.0.0')
#     debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
#     print(f"\n🚀 Server running on http://{host}:{port}")
#     print(f"📍 API Base URL: http://localhost:{port}/api")
#     print(f"📍 Test with: http://localhost:{port}/api/health")
#     print("\n📋 Testing Guide:")
#     print("   - Underweight (BMI < 18.5): Height 170, Weight 50 → Pizza = NEUTRAL")
#     print("   - Normal (BMI 18.5-24.9): Height 170, Weight 70 → Pizza = UNHEALTHY")
#     print("   - Overweight (BMI 25-29.9): Height 170, Weight 85 → Pizza = UNHEALTHY")
#     print("\n✅ Ready for requests...\n")
    
#     app.run(debug=debug, host=host, port=port)



















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

print("\n" + "="*60)
print("🍕 FOOD CLASSIFICATION API - WITH FUNGI DETECTION")
print("="*60)

# ── MongoDB Connection ─────────────────────────────────────────
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
db = None
users_col = None
metrics_col = None
records_col = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    db = client['food_classification']
    print("✅ MongoDB connected successfully!")
    
    # Collections
    users_col = db['users']
    metrics_col = db['user_metrics']
    records_col = db['food_records']
    
    # Create indexes
    users_col.create_index('email', unique=True)
    users_col.create_index('username', unique=True)
    records_col.create_index('user_id')
    print("✅ Indexes created")
    
except Exception as e:
    print(f"⚠️ MongoDB connection failed: {e}")
    print("   Continuing without database...")

# ── CONFIG ──────────────────────────────────────────
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# ── HELPERS ─────────────────────────────────────────
def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def str_id(obj_id):
    return str(obj_id)

def calculate_age_from_dob(dob_str):
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    except:
        return 25

def calculate_bmi(h, w):
    if not h or not w or h <= 0 or w <= 0:
        return 0
    return round(w / ((h / 100) ** 2), 1)

def get_bmi_category(bmi):
    if bmi < 18.5: return 'Underweight'
    elif bmi < 25: return 'Normal'
    elif bmi < 30: return 'Overweight'
    else: return 'Obese'

def calculate_tdee(w, h, age, gender, activity):
    if gender.lower() == 'male':
        bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
    else:
        bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
    
    multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'active': 1.55,
        'very_active': 1.725,
        'extra_active': 1.9
    }
    return round(bmr * multipliers.get(activity.lower(), 1.55), 1)

# ── FUNGI DETECTION (NEW) ─────────────────────────────────────────
def get_fungi_health_info(food_name):
    """Return health information about fungi-based foods"""
    food_lower = food_name.lower()
    
    # Mushrooms (edible fungi)
    mushrooms = ['mushroom', 'shiitake', 'portobello', 'portabella', 'oyster', 
                 'enoki', 'maitake', 'morel', 'chanterelle', 'cremini', 
                 'button mushroom', 'white mushroom', 'king oyster', 
                 'lions mane', 'reishi', 'cordyceps']
    
    if any(m in food_lower for m in mushrooms):
        return {
            'is_fungus': True,
            'type': 'mushroom',
            'benefits': [
                '🍄 Rich in vitamin D (supports bone health)',
                '🧬 Contains beta-glucans for immune support',
                '🛡️ Antioxidant properties (ergothioneine)',
                '💪 Low calorie, nutrient-dense protein source',
                '❤️ May help lower cholesterol levels'
            ],
            'nutritional_note': 'One of few plant-based sources of vitamin D',
            'health_score': '+10'  # Bonus for healthy food
        }
    
    # Fermented fungi products
    if 'tempeh' in food_lower:
        return {
            'is_fungus': True,
            'type': 'fermented_fungus',
            'benefits': [
                '🌱 Complete plant protein (all essential amino acids)',
                '🦠 Probiotic benefits from fermentation',
                '🥩 Excellent meat substitute',
                '💪 High in iron and calcium',
                '🧪 May improve gut health'
            ],
            'nutritional_note': 'Made from fermented soybeans with Rhizopus mold',
            'health_score': '+8'
        }
    
    if 'miso' in food_lower:
        return {
            'is_fungus': True,
            'type': 'fermented_fungus',
            'benefits': [
                '🦠 Rich in beneficial probiotics',
                '🧂 Contains essential minerals',
                '❤️ May reduce risk of certain cancers',
                '🌿 Umami flavor reduces need for salt',
                '🛡️ Antioxidant properties'
            ],
            'nutritional_note': 'Fermented with Aspergillus oryzae (koji)',
            'health_score': '+7'
        }
    
    if 'nutritional yeast' in food_lower or 'nooch' in food_lower:
        return {
            'is_fungus': True,
            'type': 'yeast',
            'benefits': [
                '🧀 Cheesy flavor without dairy (vegan)',
                '💊 Often fortified with vitamin B12',
                '🧬 Complete protein source',
                '🛡️ Contains beta-glucans for immunity',
                '🌿 Low sodium, gluten-free'
            ],
            'nutritional_note': 'Deactivated Saccharomyces cerevisiae yeast',
            'health_score': '+10'
        }
    
    if 'yeast' in food_lower and 'nutritional' not in food_lower:
        return {
            'is_fungus': True,
            'type': 'yeast',
            'benefits': [
                '🧬 Rich in B vitamins',
                '🦠 Supports gut health',
                '🍞 Used in baking and fermentation'
            ],
            'nutritional_note': 'Single-celled fungus used in food production',
            'health_score': '+5'
        }
    
    return {'is_fungus': False}

def get_calories_for_food(food_name):
    """Return realistic calories for common foods including fungi"""
    food_lower = food_name.lower()
    
    # ── FUNGI / MUSHROOM CATEGORY (NEW) ──
    
    # Edible Mushrooms (very low calorie)
    if 'shiitake' in food_lower: return 34
    if 'portobello' in food_lower or 'portabella' in food_lower: return 22
    if 'oyster mushroom' in food_lower: return 33
    if 'enoki' in food_lower: return 37
    if 'maitake' in food_lower: return 31
    if 'morel' in food_lower: return 31
    if 'chanterelle' in food_lower: return 38
    if 'button mushroom' in food_lower or 'white mushroom' in food_lower: return 22
    if 'cremini' in food_lower: return 22
    if 'king oyster' in food_lower: return 35
    if 'lions mane' in food_lower: return 40
    if 'mushroom' in food_lower and 'fried' not in food_lower and 'creamy' not in food_lower and 'soup' not in food_lower: 
        return 22  # Default for plain mushrooms
    
    # Mushroom-based dishes
    if 'mushroom soup' in food_lower:
        return 80  # per cup
    if 'mushroom risotto' in food_lower:
        return 350  # per serving
    if 'stuffed mushroom' in food_lower:
        return 120  # per large mushroom
    if 'mushroom pasta' in food_lower:
        return 450  # per serving
    if 'mushroom pizza' in food_lower:
        return 550  # per slice
    if 'tempura mushroom' in food_lower:
        return 250  # per serving (fried)
    if 'creamy mushroom' in food_lower:
        return 300  # per serving
    if 'fried mushroom' in food_lower:
        return 280  # per serving
    
    # Fermented fungi foods
    if 'tempeh' in food_lower:  # Fermented soy with Rhizopus mold
        return 193  # per 100g
    if 'miso' in food_lower:  # Fermented with Aspergillus
        return 200  # per 100g
    if 'koji' in food_lower:  # Aspergillus oryzae
        return 150  # per 100g
    
    # Yeast (fungus) products
    if 'nutritional yeast' in food_lower or 'nooch' in food_lower:
        return 318  # per 100g (but used in small amounts)
    if 'yeast extract' in food_lower or 'marmite' in food_lower or 'vegemite' in food_lower:
        return 185  # per 100g
    
    # High calorie - Junk foods
    if 'pizza' in food_lower: return 700
    if 'burger' in food_lower: return 650
    if 'cheeseburger' in food_lower: return 750
    if 'fries' in food_lower: return 500
    if 'cake' in food_lower: return 450
    if 'ice cream' in food_lower: return 300
    if 'chocolate' in food_lower: return 250
    if 'biryani' in food_lower: return 650
    if 'pasta' in food_lower: return 500
    if 'noodles' in food_lower: return 450
    if 'samosa' in food_lower: return 280
    if 'donut' in food_lower: return 300
    if 'pastry' in food_lower: return 400
    if 'cookie' in food_lower: return 250
    if 'brownie' in food_lower: return 350
    if 'fried chicken' in food_lower: return 600
    if 'taco' in food_lower: return 300
    if 'burrito' in food_lower: return 550
    
    # Medium calorie
    if 'naan' in food_lower: return 300
    if 'roti' in food_lower or 'chapati' in food_lower: return 120
    if 'rice' in food_lower and 'fried' not in food_lower: return 200
    if 'fried rice' in food_lower: return 350
    if 'dosa' in food_lower: return 250
    if 'idli' in food_lower: return 150
    if 'vada' in food_lower: return 200
    if 'poha' in food_lower: return 250
    if 'upma' in food_lower: return 220
    
    # Low calorie - Healthy foods
    if 'salad' in food_lower: return 150
    if 'apple' in food_lower: return 95
    if 'banana' in food_lower: return 105
    if 'orange' in food_lower: return 60
    if 'mango' in food_lower: return 150
    if 'watermelon' in food_lower: return 80
    if 'grapes' in food_lower: return 70
    if 'dal' in food_lower: return 180
    if 'sambar' in food_lower: return 100
    if 'soup' in food_lower: return 120
    
    return 220  # Default

def get_recommendations_for_bmi(bmi_cat):
    if bmi_cat == 'Underweight':
        return [
            '🥜 Increase calorie intake with nutrient-dense foods like nuts and avocado',
            '🥚 Add protein-rich foods (eggs, legumes, dairy) at every meal',
            '🍽️ Eat 5-6 smaller meals throughout the day to boost total intake',
            '🫒 Include healthy fats like olive oil, seeds, and nut butters',
            '👨‍⚕️ Consult a nutritionist for a personalized weight-gain meal plan'
        ]
    elif bmi_cat == 'Normal':
        return [
            '🥗 Maintain your balanced diet - you are in the healthy weight range',
            '🌾 Aim for 25-30g of fiber daily through vegetables, fruits, and whole grains',
            '💧 Stay hydrated with 2-3 liters of water to support metabolism',
            '🍗 Include lean proteins to support muscle maintenance and satiety',
            '🏃 Continue regular physical activity (150 min/week moderate intensity)'
        ]
    else:  # Overweight/Obese
        return [
            '📉 Reduce daily intake by 300-500 kcal below your TDEE for steady loss',
            '🥬 Prioritize high-volume, low-calorie foods like leafy greens and soups',
            '🏋️ Aim for at least 150-200 min/week of moderate cardio',
            '🍽️ Eat protein first at each meal to improve satiety',
            '📝 Track your meals for 2 weeks to identify hidden calorie sources'
        ]

def get_avoids_for_bmi(bmi_cat):
    if bmi_cat == 'Underweight':
        return [
            '❌ Avoid skipping meals - even small snacks count',
            '❌ Avoid excessive cardio without compensating with extra calories',
            '❌ Avoid low-fat or diet versions of foods',
            '❌ Avoid prolonged gaps (>4 hrs) between meals'
        ]
    elif bmi_cat == 'Normal':
        return [
            '❌ Avoid ultra-processed snacks that add empty calories',
            '❌ Avoid sugary beverages; they add calories without nutrition',
            '❌ Avoid large portions late at night - digestion slows down',
            '❌ Avoid crash diets; they disrupt your current healthy balance'
        ]
    else:  # Overweight/Obese
        return [
            '❌ Avoid refined carbohydrates (white bread, pastries, sugary cereals)',
            '❌ Avoid fried foods and fast food - calorie density is very high',
            '❌ Avoid eating while distracted (TV, phone) - leads to overconsumption',
            '❌ Avoid alcohol - it adds empty calories',
            '❌ Avoid skipping meals - paradoxically causes overeating later'
        ]

# ── MAIN RECOMMENDATION FUNCTION WITH FUNGI SUPPORT ──
def get_recommendation(calories, daily_calories, bmi, gender, food_name):
    bmi_cat = get_bmi_category(bmi)
    meal_target = daily_calories / 3
    pct = (calories / daily_calories) * 100 if daily_calories > 0 else 0
    
    # Get fungi info
    fungi_info = get_fungi_health_info(food_name)
    is_healthy_fungus = fungi_info['is_fungus']
    
    # Junk food list (but NOT including healthy fungi)
    junk_foods = ['pizza', 'burger', 'cheeseburger', 'cake', 'ice cream', 'chocolate', 
                  'fries', 'pasta', 'noodles', 'biryani', 'samosa', 'pastry', 'donut', 
                  'cookie', 'brownie', 'muffin', 'fried chicken', 'taco', 'burrito', 
                  'hot dog', 'bacon', 'sausage', 'fried mushroom', 'creamy mushroom pasta']
    
    # Override: If it's healthy fungus, it's NOT junk food
    is_junk = any(junk in food_name.lower() for junk in junk_foods) and not is_healthy_fungus
    
    # Debug print
    print(f"\n🍔 ANALYZING: {food_name}")
    print(f"   Calories: {calories}, BMI: {bmi} ({bmi_cat})")
    print(f"   Daily: {daily_calories}, Meal Target: {int(meal_target)}")
    print(f"   Is Junk Food: {is_junk}")
    print(f"   Is Healthy Fungus: {is_healthy_fungus}")
    
    # ── HEALTH STATUS LOGIC WITH FUNGI PRIORITY ──
    food_health_status = 'healthy'
    food_health_message = ''
    
    # PRIORITY 1: Healthy fungi ALWAYS get positive status
    if is_healthy_fungus:
        food_health_status = 'healthy'
        # Special message for fungi
        if bmi_cat == 'Underweight':
            food_health_message = f'✅ Excellent mushroom choice! {fungi_info["nutritional_note"]} Pair with healthy carbs for weight gain.'
        elif bmi_cat == 'Normal':
            food_health_message = f'✅ Perfect choice! {fungi_info["nutritional_note"]} {fungi_info["benefits"][0]}'
        else:  # Overweight/Obese
            food_health_message = f'✅ Great low-calorie choice! {fungi_info["nutritional_note"]} Supports your weight goals.'
    
    # PRIORITY 2: Regular food logic for non-fungi
    elif bmi_cat == 'Underweight':
        if is_junk:
            food_health_status = 'neutral'
            food_health_message = '⚠️ Junk food gives calories, but choose nutrient-dense options instead'
        elif calories > meal_target:
            food_health_status = 'healthy'
            food_health_message = '✅ Good! High-calorie foods help you gain healthy weight'
        else:
            food_health_status = 'neutral'
            food_health_message = '⚠️ Consider adding more calories to reach your weight goals'
            
    elif bmi_cat == 'Normal':
        if is_junk:
            food_health_status = 'unhealthy'
            food_health_message = '🔴 Junk food - eat occasionally only!'
        elif calories > meal_target * 1.2:
            food_health_status = 'unhealthy'
            food_health_message = f'🔴 Too many calories ({calories} kcal) for one meal'
        elif calories > meal_target:
            food_health_status = 'neutral'
            food_health_message = '⚠️ Moderate - watch your portions'
        else:
            food_health_status = 'healthy'
            food_health_message = '✅ Healthy choice! Good balance'
            
    else:  # Overweight or Obese
        if is_junk:
            food_health_status = 'unhealthy'
            food_health_message = '🔴 Junk food - avoid for weight loss!'
        elif calories > meal_target:
            food_health_status = 'unhealthy'
            food_health_message = f'🔴 Too many calories ({calories} kcal) for your weight goal'
        elif calories > meal_target * 0.8:
            food_health_status = 'neutral'
            food_health_message = '⚠️ Moderate - okay occasionally'
        else:
            food_health_status = 'healthy'
            food_health_message = '✅ Great low-calorie choice! Supports weight loss'
    
    # Status for UI progress bar
    if calories <= meal_target:
        status = 'success'
        status_text = 'Safe meal - within target'
    elif calories <= meal_target * 1.2:
        status = 'warning'
        status_text = 'Moderate - slightly above target'
    else:
        status = 'danger'
        status_text = 'High calorie alert'
    
    print(f"   ✅ Health Status: {food_health_status}")
    print(f"   Message: {food_health_message}\n")
    
    return {
        'status': status,
        'status_text': status_text,
        'meal_pct': round(pct, 1),
        'food_health_status': food_health_status,
        'food_health_message': food_health_message,
        'recommendations': get_recommendations_for_bmi(bmi_cat),
        'avoids': get_avoids_for_bmi(bmi_cat),
        'bmi_category': bmi_cat,
        'is_fungus': is_healthy_fungus,
        'fungus_info': fungi_info if is_healthy_fungus else None
    }

# Try to load AI model
try:
    from tflite_loader import analyze_food_tflite as analyze_food_local
    print("✅ MobileNetV2 model loaded successfully")
except ImportError:
    print("⚠️ tflite_loader not found, using mock AI")
    def analyze_food_local(image_bytes):
        return {
            'food_name': 'Food',
            'calories': 200,
            'description': 'Food detected from image',
            'confidence': 'medium',
            'estimated_portion': 'medium'
        }, None
except Exception as e:
    print(f"⚠️ Error loading AI model: {e}")
    def analyze_food_local(image_bytes):
        return {
            'food_name': 'Food',
            'calories': 200,
            'description': 'Food detected from image',
            'confidence': 'low',
            'estimated_portion': 'medium'
        }, None

# ── API ROUTES ─────────────────────────────────────────

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'mode': 'Food Classification API with Fungi Detection'}), 200

@app.route('/api/test-model', methods=['GET'])
def test_model():
    try:
        return jsonify({'status': 'success', 'model': 'MobileNetV2 TFLite'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/uploads/<path:filename>', methods=['GET'])
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ── AUTH ROUTES ─────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    full_name = data.get('full_name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    dob = data.get('dob', '')
    gender = data.get('gender', 'male')
    
    print(f"\n📝 Registering user: {email}")
    
    if not all([full_name, username, email, password, dob]):
        return jsonify({'error': 'All fields are required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    age = calculate_age_from_dob(dob)
    
    if users_col is None:
        # Mock registration
        return jsonify({
            'user_id': 'mock_' + str(int(datetime.now().timestamp())),
            'full_name': full_name,
            'age': age,
            'message': 'Registered successfully (Demo Mode)'
        }), 201
    
    # Check existing users
    if users_col.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400
    if users_col.find_one({'username': username}):
        return jsonify({'error': 'Username already taken'}), 400
    
    try:
        result = users_col.insert_one({
            'full_name': full_name,
            'username': username,
            'email': email,
            'password_hash': hash_password(password),
            'dob': dob,
            'age': age,
            'gender': gender,
            'created_at': datetime.utcnow(),
        })
        print(f"   ✅ User created with ID: {result.inserted_id}")
        return jsonify({
            'user_id': str_id(result.inserted_id),
            'full_name': full_name,
            'age': age,
            'message': 'Registered successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    print(f"\n🔐 Login attempt: {email}")
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if users_col is None:
        # Mock login
        return jsonify({
            'user_id': 'mock_user',
            'full_name': 'Demo User',
            'username': 'demouser',
            'email': email,
            'gender': 'male',
            'age': 25,
            'message': 'Login successful (Demo Mode)'
        }), 200
    
    user = users_col.find_one({'email': email, 'password_hash': hash_password(password)})
    
    if user:
        print(f"   ✅ User found: {user.get('full_name')}")
        return jsonify({
            'user_id': str_id(user['_id']),
            'full_name': user.get('full_name', 'User'),
            'username': user.get('username', 'user'),
            'email': user.get('email', ''),
            'gender': user.get('gender', 'male'),
            'age': user.get('age', 25),
            'message': 'Login successful'
        }), 200
    else:
        print(f"   ❌ Invalid credentials")
        return jsonify({'error': 'Invalid email or password'}), 401

# ── USER METRICS ─────────────────────────────────────────

@app.route('/api/users/<user_id>/metrics', methods=['POST'])
def save_user_metrics(user_id):
    try:
        data = request.json
        print(f"\n📊 Saving metrics for user: {user_id}")
        
        h = float(data['height_cm'])
        w = float(data['weight_kg'])
        age = int(data.get('age', 25))
        gen = data.get('gender', 'male')
        act = data.get('activity_level', 'active')
        
        bmi = calculate_bmi(h, w)
        dc = calculate_tdee(w, h, age, gen, act)
        
        if metrics_col is not None:
            metrics_col.insert_one({
                'user_id': user_id,
                'height_cm': h,
                'weight_kg': w,
                'age': age,
                'gender': gen,
                'bmi': bmi,
                'daily_calories': dc,
                'activity_level': act,
                'recorded_at': datetime.utcnow(),
            })
            print(f"   ✅ Metrics saved to DB! BMI: {bmi}, Daily Calories: {dc}")
        else:
            print(f"   ✅ Metrics calculated (Demo): BMI: {bmi}, Daily Calories: {dc}")
        
        return jsonify({
            'bmi': bmi,
            'bmi_category': get_bmi_category(bmi),
            'daily_calories': dc,
            'message': 'Metrics saved successfully'
        }), 201
        
    except Exception as e:
        print(f"❌ Error saving metrics: {e}")
        return jsonify({'error': str(e)}), 400

# ── USER PROFILE ─────────────────────────────────────────

@app.route('/api/users/<user_id>/profile', methods=['GET'])
def get_user_profile(user_id):
    try:
        print(f"\n👤 Fetching profile for user: {user_id}")
        
        result = {
            'user_id': user_id,
            'full_name': 'User',
            'username': 'user',
            'email': 'user@example.com',
            'gender': 'male',
            'age': 25,
        }
        
        if users_col is not None:
            try:
                user = users_col.find_one({'_id': ObjectId(user_id)})
                if user:
                    result.update({
                        'full_name': user.get('full_name', 'User'),
                        'username': user.get('username', 'user'),
                        'email': user.get('email', ''),
                        'gender': user.get('gender', 'male'),
                        'age': user.get('age', 25),
                    })
            except:
                pass
            
            # Get latest metrics
            if metrics_col is not None:
                metrics = metrics_col.find_one(
                    {'user_id': user_id},
                    sort=[('recorded_at', DESCENDING)]
                )
                if metrics:
                    result.update({
                        'height': metrics['height_cm'],
                        'weight': metrics['weight_kg'],
                        'bmi': metrics['bmi'],
                        'daily_calories': metrics['daily_calories'],
                        'activity': metrics['activity_level'],
                    })
        
        print(f"   ✅ Profile fetched: {result.get('full_name')}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return jsonify({'error': str(e)}), 500

# ── USER HISTORY ─────────────────────────────────────────

@app.route('/api/users/<user_id>/history', methods=['GET'])
def get_user_history(user_id):
    try:
        print(f"\n📜 Fetching history for user: {user_id}")
        
        records = []
        if records_col is not None:
            records = list(records_col.find(
                {'user_id': user_id},
                sort=[('created_at', DESCENDING)],
                limit=50
            ))
        
        result = [{
            'food_name': r.get('food_name', ''),
            'calories': r.get('calories', 0),
            'estimated_portion': r.get('estimated_portion', 'medium'),
            'bmi': r.get('bmi', 0),
            'bmi_category': get_bmi_category(r.get('bmi', 22)),
            'daily_calories': r.get('daily_calories', 0),
            'recommendation': r.get('recommendation', ''),
            'is_fungus': r.get('is_fungus', False),
            'created_at': str(r.get('created_at', '')),
            'image_path': r.get('image_path', ''),
        } for r in records]
        
        print(f"   ✅ Found {len(result)} records")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return jsonify({'error': str(e)}), 500

# ── CLASSIFY FOOD (MAIN ENDPOINT WITH FUNGI SUPPORT) ─────────────────────────

@app.route('/api/classify-food', methods=['POST'])
def classify_food():
    print("\n" + "="*50)
    print("📸 NEW FOOD ANALYSIS REQUEST")
    print("="*50)
    
    try:
        # Get form data
        user_id = request.form.get('user_id', 'test')
        h = float(request.form.get('height_cm', 170))
        w = float(request.form.get('weight_kg', 70))
        age = int(request.form.get('age', 25))
        gender = request.form.get('gender', 'male')
        activity = request.form.get('activity_level', 'active')
        food_override = request.form.get('food_name_override', '')
        
        print(f"📊 User: {user_id}")
        print(f"   Height={h}cm, Weight={w}kg, Age={age}, Gender={gender}")
        print(f"🍔 Selected Food: {food_override if food_override else 'None'}")
        
        # Process image
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        image_bytes = file.read()
        
        # Get AI analysis
        ai_result, _ = analyze_food_local(image_bytes)
        
        if ai_result and not food_override:
            food_name = ai_result.get('food_name', 'Food')
            calories = float(ai_result.get('calories', 200))
            description = ai_result.get('description', '')
            confidence = ai_result.get('confidence', 'medium')
            estimated_portion = ai_result.get('estimated_portion', 'medium')
        else:
            food_name = 'Food'
            calories = 200
            description = ''
            confidence = 'low'
            estimated_portion = 'medium'
        
        # Override with user selection
        if food_override:
            food_name = food_override
            calories = get_calories_for_food(food_name)
        
        # Calculate metrics
        bmi = calculate_bmi(h, w)
        bmi_cat = get_bmi_category(bmi)
        daily_calories = calculate_tdee(w, h, age, gender, activity)
        
        # Get recommendation (includes fungi detection)
        rec = get_recommendation(calories, daily_calories, bmi, gender, food_name)
        
        # Save to database (if real user and DB available)
        if records_col is not None and user_id and user_id != 'test' and user_id != 'mock_user':
            try:
                # Save image
                img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
                fname = secure_filename(f"{user_id}_{datetime.now().timestamp()}.jpg")
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
                
                # Save record with fungi info
                record_data = {
                    'user_id': user_id,
                    'food_name': food_name,
                    'calories': calories,
                    'estimated_portion': estimated_portion,
                    'image_path': fname,
                    'bmi': bmi,
                    'daily_calories': daily_calories,
                    'recommendation': rec['status_text'],
                    'is_fungus': rec.get('is_fungus', False),
                    'created_at': datetime.utcnow(),
                }
                
                # Add fungus type if applicable
                if rec.get('is_fungus') and rec.get('fungus_info'):
                    record_data['fungus_type'] = rec['fungus_info'].get('type', 'unknown')
                    record_data['fungus_benefits'] = rec['fungus_info'].get('benefits', [])
                
                records_col.insert_one(record_data)
                print(f"   💾 Saved to database with fungi detection: {rec.get('is_fungus')}")
            except Exception as db_error:
                print(f"   ⚠️ Could not save to DB: {db_error}")
        
        # Build response with fungi data
        response = {
            "food_name": food_name,
            "calories": calories,
            "estimated_portion": estimated_portion,
            "description": description,
            "confidence": confidence,
            "bmi": bmi,
            "bmi_category": bmi_cat,
            "daily_calories": daily_calories,
            "meal_target": round(daily_calories / 3, 1),
            "meal_pct": rec['meal_pct'],
            "recommendation": rec['status_text'],
            "recommendations": rec['recommendations'],
            "avoids": rec['avoids'],
            "status": rec['status'],
            "food_health_status": rec['food_health_status'],
            "food_health_message": rec['food_health_message'],
            # Fungi-specific fields
            "is_fungus": rec.get('is_fungus', False),
            "fungus_benefits": rec.get('fungus_info', {}).get('benefits', []) if rec.get('is_fungus') else [],
            "fungus_type": rec.get('fungus_info', {}).get('type', 'none') if rec.get('is_fungus') else 'none',
            "fungus_nutritional_note": rec.get('fungus_info', {}).get('nutritional_note', '') if rec.get('is_fungus') else ''
        }
        
        print(f"\n✅ SENDING RESPONSE:")
        print(f"   Food: {response['food_name']}")
        print(f"   Health Status: {response['food_health_status']}")
        print(f"   Message: {response['food_health_message']}")
        print(f"   Is Fungus: {response['is_fungus']}")
        if response['is_fungus']:
            print(f"   Fungus Type: {response['fungus_type']}")
            print(f"   Benefits: {response['fungus_benefits'][0] if response['fungus_benefits'] else 'None'}")
        print("="*50 + "\n")
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ ERROR: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# ── INIT DB ENDPOINT ─────────────────────────────────────────

@app.route('/api/init-db', methods=['POST'])
def init_db():
    return jsonify({'message': 'MongoDB auto-initializes on first insert'}), 200

# ── NEW ENDPOINT: GET FUNGI INFO ─────────────────────────────────────────

@app.route('/api/fungi-info', methods=['GET'])
def get_fungi_info():
    """Return information about all supported fungi foods"""
    fungi_foods = {
        "mushrooms": {
            "types": ["Shiitake", "Portobello", "Oyster", "Enoki", "Maitake", "Button", "Cremini"],
            "avg_calories": "22-37 per 100g",
            "benefits": ["Vitamin D", "Immune support", "Antioxidants", "Low calorie"]
        },
        "fermented_fungi": {
            "types": ["Tempeh", "Miso", "Koji"],
            "avg_calories": "150-200 per 100g",
            "benefits": ["Probiotics", "Complete protein", "Gut health"]
        },
        "yeast_products": {
            "types": ["Nutritional Yeast", "Yeast Extract"],
            "avg_calories": "185-318 per 100g",
            "benefits": ["B vitamins", "B12 fortified", "Cheesy flavor"]
        }
    }
    return jsonify(fungi_foods), 200

# ── RUN SERVER ─────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"\n🚀 Server running on http://{host}:{port}")
    print(f"📍 API Base URL: http://localhost:{port}/api")
    print(f"📍 Test with: http://localhost:{port}/api/health")
    print(f"📍 Fungi Info: http://localhost:{port}/api/fungi-info")
    print("\n🍄 FUNGI DETECTION NOW ACTIVE!")
    print("   Supported fungi: Mushrooms, Tempeh, Miso, Nutritional Yeast")
    print("\n📋 Testing Guide:")
    print("   - Underweight (BMI < 18.5): Height 170, Weight 50 → Mushrooms = HEALTHY")
    print("   - Normal (BMI 18.5-24.9): Height 170, Weight 70 → Mushrooms = HEALTHY")
    print("   - Overweight (BMI 25-29.9): Height 170, Weight 85 → Mushrooms = HEALTHY")
    print("\n🍄 Fungi always get HEALTHY status regardless of BMI!")
    print("\n✅ Ready for requests...\n")
    
    app.run(debug=debug, host=host, port=port)
