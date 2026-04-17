import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import axios from 'axios';

import Layout    from './pages/Layout';
import Home      from './pages/Home';
import Register  from './pages/Register';
import Login     from './pages/Login';
import Metrics   from './pages/Metrics';
import Dashboard from './pages/Dashboard';
import History   from './pages/History';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [userId, setUserId] = useState(() => localStorage.getItem('userId') || null);
  const [user,   setUser]   = useState(() => {
    try { return JSON.parse(localStorage.getItem('user')) || null; }
    catch { return null; }
  });

  // On page refresh: re-fetch profile so user data is always fresh
  useEffect(() => {
    if (!userId) return;
    axios.get(`${API}/users/${userId}/profile`)
      .then(res => {
        const profile = res.data;
        setUser(profile);
        localStorage.setItem('user', JSON.stringify(profile));
      })
      .catch(err => console.warn('Profile fetch failed:', err.message));
  }, [userId]);

  const handleUserCreated = (id, userInfo) => {
    const uid = String(id);
    // Set user immediately from login/register response — name shows right away
    setUserId(uid);
    setUser(userInfo || null);
    localStorage.setItem('userId', uid);
    if (userInfo) localStorage.setItem('user', JSON.stringify(userInfo));

    // Fetch full profile in background to merge metrics (height/weight/etc)
    axios.get(`${API}/users/${uid}/profile`)
      .then(res => {
        const merged = { ...(userInfo || {}), ...res.data };
        setUser(merged);
        localStorage.setItem('user', JSON.stringify(merged));
      })
      .catch(() => {});
  };

  const handleLogout = () => {
    setUserId(null);
    setUser(null);
    localStorage.removeItem('userId');
    localStorage.removeItem('user');
  };

  const ProtectedRoute = ({ children }) => {
    if (!userId) return <Navigate to="/login" replace />;
    return (
      <Layout user={user} onLogout={handleLogout}>
        {children}
      </Layout>
    );
  };

  return (
    <BrowserRouter>
      <Toaster position="top-right" toastOptions={{
        style: { background: '#1e293b', color: '#e0f2fe', border: '1px solid rgba(255,255,255,0.08)' },
        duration: 3000,
      }} />
      <Routes>
        <Route path="/"         element={<Home />} />
        <Route path="/register" element={<Register onUserCreated={handleUserCreated} />} />
        <Route path="/login"    element={<Login    onUserCreated={handleUserCreated} />} />
        <Route path="/metrics/:userId" element={
          <Metrics onUserCreated={handleUserCreated} user={user} />
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard userId={userId} user={user} />
          </ProtectedRoute>
        } />
        <Route path="/history" element={
          <ProtectedRoute>
            <History userId={userId} />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;