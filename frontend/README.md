# FoodFit Frontend — Production Ready

## Stack
- React 18
- React Router v6
- Axios
- Bootstrap 5

## Setup

### Local Development
```bash
npm install
# Set REACT_APP_API_URL in .env to http://localhost:5000/api
npm start
```

### Deploy to Vercel
1. Push this frontend folder to GitHub
2. Go to vercel.com → New Project
3. Import GitHub repo
4. Set Environment Variable:
   - REACT_APP_API_URL = https://your-backend-name.onrender.com/api
5. Deploy!

## After Backend Deploy
Update .env.production:
REACT_APP_API_URL=https://your-actual-render-url.onrender.com/api
