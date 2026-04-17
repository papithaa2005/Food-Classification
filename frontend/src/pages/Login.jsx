import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import './Auth.css';

function Login({ onUserCreated }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) { toast.error('Please fill in all fields', { icon: '⚠️' }); return; }
    setLoading(true);
    try {
      const res = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/login`, { email, password });
      const { user_id, full_name, gender, age } = res.data;
      onUserCreated(user_id, { full_name, email, gender, age });
      toast.success(`Welcome back, ${full_name}! 👋`, { duration: 2000 });
      setTimeout(() => navigate('/dashboard'), 1200);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Login failed', { icon: '❌' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-bg">
      <div className="auth-card auth-card-sm">
        <div className="auth-brand">
          <span className="auth-logo">🥗</span>
          <h1>FoodFit</h1>
        </div>
        <h2 className="auth-title">Welcome Back</h2>
        <p className="auth-sub">Sign in to continue tracking your nutrition</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label>Email Address</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="jane@example.com" required className="auth-input" />
          </div>

          <div className="auth-field">
            <label>Password</label>
            <div className="pw-wrap">
              <input type={showPw ? 'text' : 'password'} value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="Your password" required className="auth-input" />
              <button type="button" className="pw-eye" onClick={() => setShowPw(p => !p)}>
                {showPw ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? <span className="auth-spinner" /> : 'Sign In →'}
          </button>
        </form>

        <p className="auth-switch">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}

export default Login;