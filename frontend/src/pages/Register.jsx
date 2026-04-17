import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import './Auth.css';

function Register({ onUserCreated }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [showPw, setShowPw] = useState(false);
  const [showCPw, setShowCPw] = useState(false);
  const [form, setForm] = useState({
    full_name: '', username: '', email: '',
    dob: '', age: '', gender: 'male',
    password: '', confirm_password: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...form, [name]: value };
    if (name === 'dob' && value) {
      const dob = new Date(value);
      const today = new Date();
      let age = today.getFullYear() - dob.getFullYear();
      const m = today.getMonth() - dob.getMonth();
      if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--;
      updated.age = age > 0 ? age : '';
    }
    setForm(updated);
  };

  const validate = () => {
    if (!form.full_name.trim()) return 'Full name is required';
    if (!form.username.trim()) return 'Username is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return 'Enter a valid email';
    if (!form.dob) return 'Date of birth is required';
    if (!form.age || form.age < 5) return 'Invalid date of birth';
    if (form.password.length < 6) return 'Password must be at least 6 characters';
    if (form.password !== form.confirm_password) return 'Passwords do not match';
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const err = validate();
    if (err) { toast.error(err, { icon: '⚠️' }); return; }
    setLoading(true);
    try {
      const res = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/register`, {
        full_name: form.full_name,
        username: form.username,
        email: form.email,
        password: form.password,
        dob: form.dob,
        gender: form.gender,
      });
      const { user_id, full_name } = res.data;
      onUserCreated(user_id, { full_name, email: form.email, gender: form.gender, age: form.age });
      toast.success(`Welcome, ${full_name}! 🎉`, { duration: 2000 });
      setTimeout(() => navigate(`/metrics/${user_id}`), 1200);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Registration failed', { icon: '❌' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-bg">
      <div className="auth-card">
        <div className="auth-brand">
          <span className="auth-logo">🥗</span>
          <h1>FoodFit</h1>
        </div>
        <h2 className="auth-title">Create Account</h2>
        <p className="auth-sub">Start your nutrition journey today</p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-row">
            <div className="auth-field">
              <label>Full Name</label>
              <input name="full_name" value={form.full_name} onChange={handleChange}
                placeholder="Jane Doe" required className="auth-input" />
            </div>
            <div className="auth-field">
              <label>Username</label>
              <input name="username" value={form.username} onChange={handleChange}
                placeholder="janedoe" required className="auth-input" />
            </div>
          </div>

          <div className="auth-field">
            <label>Email Address</label>
            <input type="email" name="email" value={form.email} onChange={handleChange}
              placeholder="jane@example.com" required className="auth-input" />
          </div>

          <div className="auth-row">
            <div className="auth-field">
              <label>Date of Birth</label>
              <input type="date" name="dob" value={form.dob} onChange={handleChange}
                max={new Date().toISOString().split('T')[0]} required className="auth-input" />
            </div>
            <div className="auth-field">
              <label>Age (auto)</label>
              <input value={form.age ? `${form.age} years` : ''} readOnly
                placeholder="Auto calculated" className="auth-input auth-readonly" />
            </div>
          </div>

          <div className="auth-field">
            <label>Gender</label>
            <div className="gender-tabs">
              {['male', 'female', 'other'].map(g => (
                <button key={g} type="button"
                  className={`gender-tab ${form.gender === g ? 'active' : ''}`}
                  onClick={() => setForm(f => ({ ...f, gender: g }))}>
                  {g === 'male' ? '♂ Male' : g === 'female' ? '♀ Female' : '⊕ Other'}
                </button>
              ))}
            </div>
          </div>

          <div className="auth-row">
            <div className="auth-field">
              <label>Password</label>
              <div className="pw-wrap">
                <input type={showPw ? 'text' : 'password'} name="password"
                  value={form.password} onChange={handleChange}
                  placeholder="Min 6 characters" required className="auth-input" />
                <button type="button" className="pw-eye" onClick={() => setShowPw(p => !p)}>
                  {showPw ? '🙈' : '👁️'}
                </button>
              </div>
            </div>
            <div className="auth-field">
              <label>Confirm Password</label>
              <div className="pw-wrap">
                <input type={showCPw ? 'text' : 'password'} name="confirm_password"
                  value={form.confirm_password} onChange={handleChange}
                  placeholder="Repeat password" required className="auth-input" />
                <button type="button" className="pw-eye" onClick={() => setShowCPw(p => !p)}>
                  {showCPw ? '🙈' : '👁️'}
                </button>
              </div>
              {form.confirm_password && form.password !== form.confirm_password && (
                <span className="pw-mismatch">❌ Passwords don't match</span>
              )}
              {form.confirm_password && form.password === form.confirm_password && form.confirm_password.length >= 6 && (
                <span className="pw-match">✅ Passwords match</span>
              )}
            </div>
          </div>

          <button type="submit" className="auth-btn" disabled={loading}>
            {loading ? <span className="auth-spinner" /> : 'Create Account →'}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
}

export default Register;