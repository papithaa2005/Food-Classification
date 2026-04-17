import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import './Metrics.css';

function Metrics({ onUserCreated, user }) {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    height: '',
    weight: '',
    age: user?.age ? String(user.age) : '',
    gender: user?.gender || 'male',
    activity: 'active',
  });

  // Auto-fetch saved metrics to pre-fill form (for returning users)
  useEffect(() => {
    if (!userId) return;
    axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/users/${userId}/profile`)
      .then(res => {
        const d = res.data;
        setForm(f => ({
          height:   d.height   ? String(d.height)   : (d.height_cm ? String(d.height_cm) : f.height),
          weight:   d.weight   ? String(d.weight)   : (d.weight_kg ? String(d.weight_kg) : f.weight),
          age:      d.age      ? String(d.age)      : f.age,
          gender:   d.gender   || f.gender,
          activity: d.activity || f.activity,
        }));
      })
      .catch(() => {}); // silently ignore if no metrics yet
  }, [userId]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  // Live BMI preview
  const liveBMI = form.height && form.weight
    ? (parseFloat(form.weight) / Math.pow(parseFloat(form.height) / 100, 2)).toFixed(1)
    : null;

  const getBMICat = (b) => {
    if (b < 18.5) return { text: 'Underweight', color: '#38bdf8' };
    if (b < 25)   return { text: 'Normal',      color: '#4ade80' };
    if (b < 30)   return { text: 'Overweight',  color: '#fbbf24' };
    return               { text: 'Obese',        color: '#f87171' };
  };

  const bmiCat = liveBMI ? getBMICat(parseFloat(liveBMI)) : null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.height || !form.weight || !form.age) {
      toast.error('Please fill in all fields'); return;
    }
    setLoading(true);
    try {
      const res = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/users/${userId}/metrics`, {
        height_cm:      parseFloat(form.height),
        weight_kg:      parseFloat(form.weight),
        age:            parseInt(form.age),
        gender:         form.gender,
        activity_level: form.activity,
      });
      toast.success(`Metrics saved! BMI: ${res.data.bmi} (${res.data.bmi_category}) ✅`);
      if (onUserCreated) onUserCreated(userId);
      setTimeout(() => navigate('/dashboard'), 1500);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to save metrics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="met-bg">
      <div className="met-card">
        <div className="met-header">
          <span className="met-logo">📏</span>
          <h2>Body Metrics</h2>
          <p>Used to calculate your BMI and daily calorie target</p>
        </div>

        {/* Live BMI preview */}
        {liveBMI && bmiCat && (
          <div className="bmi-preview" style={{ borderColor: bmiCat.color + '44' }}>
            <div className="bmi-preview-val" style={{ color: bmiCat.color }}>
              BMI: {liveBMI}
            </div>
            <div className="bmi-preview-cat" style={{ color: bmiCat.color }}>
              {bmiCat.text}
            </div>
            <div className="bmi-preview-formula">
              Formula: weight(kg) ÷ height(m)²  •  WHO Standard
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="met-form">
          <div className="met-row">
            <div className="met-field">
              <label>Height (cm)</label>
              <input type="number" name="height" value={form.height}
                onChange={handleChange} placeholder="170" required className="met-input" />
            </div>
            <div className="met-field">
              <label>Weight (kg)</label>
              <input type="number" name="weight" value={form.weight}
                onChange={handleChange} placeholder="75" required className="met-input" />
            </div>
          </div>

          <div className="met-row">
            <div className="met-field">
              <label>Age</label>
              <input type="number" name="age" value={form.age}
                onChange={handleChange} placeholder="25" required className="met-input" />
            </div>
            <div className="met-field">
              <label>Gender</label>
              <div className="met-gender">
                {['male', 'female'].map(g => (
                  <button key={g} type="button"
                    className={`met-gpill ${form.gender === g ? 'active' : ''}`}
                    onClick={() => setForm(f => ({ ...f, gender: g }))}>
                    {g === 'male' ? '♂ Male' : '♀ Female'}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="met-field met-field-full">
            <label>Activity Level</label>
            <select name="activity" value={form.activity}
              onChange={handleChange} className="met-input">
              <option value="sedentary">Sedentary (desk job, no exercise)</option>
              <option value="lightly_active">Lightly Active (1–3 days/week)</option>
              <option value="active">Active (3–5 days/week)</option>
              <option value="very_active">Very Active (6–7 days/week)</option>
              <option value="extra_active">Extra Active (athlete / physical job)</option>
            </select>
            <span className="met-hint">Used for Mifflin-St Jeor TDEE formula (doctor-standard)</span>
          </div>

          <button type="submit" className="met-btn" disabled={loading}>
            {loading ? <span className="met-spinner" /> : 'Save & Go to Dashboard →'}
          </button>
        </form>

        <p className="met-note">You can update these anytime from the dashboard</p>
      </div>
    </div>
  );
}

export default Metrics;