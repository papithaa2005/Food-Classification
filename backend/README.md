# FoodFit Backend — Production Ready

## Stack
- Flask (Python)
- MongoDB Atlas (cloud database)
- TFLite MobileNetV2 (food classification)
- Gunicorn (production server)

## Setup

### 1. MongoDB Atlas Setup
1. Go to https://mongodb.com/atlas → Create free account
2. Create a cluster (free tier M0)
3. Create database user (username + password)
4. Whitelist IP: 0.0.0.0/0 (allow all for Render)
5. Click "Connect" → "Connect your application"
6. Copy the connection string → paste in .env as MONGO_URI

### 2. Local Development
```bash
pip install -r requirements.txt
# Update .env with your MONGO_URI
python app.py
```

### 3. Deploy to Render
1. Push this backend folder to GitHub
2. Go to render.com → New Web Service
3. Connect GitHub repo
4. Set:
   - Build Command: pip install -r requirements.txt
   - Start Command: gunicorn app:app
5. Add Environment Variables from .env
6. Deploy!

## MongoDB Collections
- users         → user accounts
- user_metrics  → BMI and body measurements
- food_records  → food classification history

## API Endpoints
- GET  /api/health
- POST /api/register
- POST /api/login
- POST /api/users/<id>/metrics
- GET  /api/users/<id>/profile
- GET  /api/users/<id>/history
- POST /api/classify-food
