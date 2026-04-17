import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './History.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
const IMG_BASE = (process.env.REACT_APP_API_URL || 'http://localhost:5000/api').replace('/api', '') + '/uploads';

function getBMICategory(bmi) {
  if (bmi < 18.5) return { text: 'Underweight', emoji: '📉', cls: 'bmi-info' };
  if (bmi < 25)   return { text: 'Normal',      emoji: '✅', cls: 'bmi-success' };
  if (bmi < 30)   return { text: 'Overweight',  emoji: '⚠️', cls: 'bmi-warning' };
  return                  { text: 'Obese',       emoji: '🔴', cls: 'bmi-danger' };
}

function getStatusClass(rec = '') {
  const r = rec.toLowerCase();
  if (r.includes('safe'))     return 'status-success';
  if (r.includes('moderate')) return 'status-warning';
  if (r.includes('high'))     return 'status-danger';
  return 'status-info';
}

// ✅ Safely parse any date format (MongoDB UTC string, ISO, etc.)
function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    // MongoDB returns dates like "2024-03-01 12:34:56.789000" — replace space with T for ISO
    const iso = String(dateStr).replace(' ', 'T');
    const d   = new Date(iso);
    if (isNaN(d.getTime())) return dateStr; // fallback: show raw string
    return d.toLocaleString();
  } catch {
    return String(dateStr);
  }
}

function History({ userId }) {
  const [history,  setHistory]  = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState('');
  const [lightbox, setLightbox] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, [userId]);

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_BASE}/users/${userId}/history`);
      setHistory(res.data);
    } catch {
      setError('Failed to load history. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="hist-loading">
        <div className="hist-spinner" />
        <p>Loading your food history…</p>
      </div>
    );
  }

  return (
    <div className="hist-container">
      <div className="hist-header">
        <h2>📊 Your Food History</h2>
        <span className="hist-count">{history.length} record{history.length !== 1 ? 's' : ''}</span>
      </div>

      {error && <div className="hist-alert">{error}</div>}

      {history.length === 0 ? (
        <div className="hist-empty">
          <div className="hist-empty-icon">🥗</div>
          <h3>No records yet</h3>
          <p>Start uploading food photos on the Dashboard to build your history!</p>
        </div>
      ) : (
        <div className="hist-grid">
          {history.map((item, idx) => {
            const bmi       = getBMICategory(item.bmi || 22);
            const statusCls = getStatusClass(item.recommendation);
            const imgSrc    = item.image_path ? `${IMG_BASE}/${item.image_path}` : null;
            // ✅ Use food_name directly — always present from backend
            const foodName  = item.food_name || 'Unknown Food';

            return (
              <div className="hist-card" key={idx}>

                {/* ── Food Image ── */}
                <div
                  className={`hist-img-wrap ${!imgSrc ? 'hist-img-placeholder' : ''}`}
                  onClick={() => imgSrc && setLightbox(imgSrc)}
                  title={imgSrc ? 'Click to enlarge' : 'No image'}
                >
                  {imgSrc ? (
                    <>
                      <img src={imgSrc} alt={foodName} className="hist-img" />
                      <div className="hist-img-overlay">🔍 View</div>
                    </>
                  ) : (
                    <div className="hist-no-img">
                      <span>🍽️</span>
                      <small>No photo</small>
                    </div>
                  )}
                </div>

                {/* ── Card Body ── */}
                <div className="hist-card-body">
                  {/* ✅ Food name always shows correctly */}
                  <div className="hist-food-name">{foodName}</div>
                  <div className="hist-time">
                    🕐 {formatDate(item.created_at)}
                  </div>

                  <div className="hist-stats">
                    <div className="hist-stat">
                      <span className="hist-stat-label">Calories</span>
                      <span className="hist-stat-val">{item.calories} <em>kcal</em></span>
                    </div>
                    <div className="hist-stat">
                      <span className="hist-stat-label">BMI</span>
                      <span className={`hist-stat-val hist-bmi ${bmi.cls}`}>
                        {(item.bmi || 0).toFixed(1)} {bmi.emoji}
                      </span>
                    </div>
                    <div className="hist-stat">
                      <span className="hist-stat-label">Daily Target</span>
                      <span className="hist-stat-val">{Math.round(item.daily_calories || 0)} <em>kcal</em></span>
                    </div>
                    <div className="hist-stat">
                      <span className="hist-stat-label">BMI Status</span>
                      <span className={`bmi-badge ${bmi.cls}`}>{bmi.text}</span>
                    </div>
                  </div>

                  <div className={`hist-reco ${statusCls}`}>
                    {item.recommendation || '—'}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── Lightbox ── */}
      {lightbox && (
        <div className="hist-lightbox" onClick={() => setLightbox(null)}>
          <div className="hist-lightbox-inner" onClick={(e) => e.stopPropagation()}>
            <button className="hist-lightbox-close" onClick={() => setLightbox(null)}>✕</button>
            <img src={lightbox} alt="Food preview" className="hist-lightbox-img" />
          </div>
        </div>
      )}
    </div>
  );
}

export default History;