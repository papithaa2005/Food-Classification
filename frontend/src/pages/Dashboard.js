import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import './Dashboard.css';

const FOOD_LIST = [
  // Western
  'Pizza','Burger','Hot Dog','Sandwich','Pasta','Steak','Fried Chicken','BBQ Ribs',
  'Caesar Salad','French Fries','Tacos','Burrito','Sushi','Ramen','Fried Rice',
  // Indian - North
  'Butter Chicken','Biryani','Paneer Tikka','Dal Makhani','Naan','Chole Bhature',
  'Rajma','Aloo Paratha','Palak Paneer','Kadai Paneer','Tandoori Chicken','Samosa',
  // Indian - South
  'Idli','Dosa','Vada','Sambar','Rasam','Curd Rice','Pongal','Uttapam',
  'Bisi Bele Bath','Tamarind Rice','Lemon Rice','Kootu','Appam','Puttu',
  // Indian - East
  'Macher Jhol','Luchi','Sandesh','Rasgulla','Khichdi','Pakhala Bhat',
  // Indian - West
  'Pav Bhaji','Vada Pav','Misal Pav','Puran Poli','Dhokla','Thepla',
  // East Asian
  'Pad Thai','Pho','Dim Sum','Peking Duck','Kung Pao Chicken','Spring Roll',
  // Fruits & Snacks
  'Banana','Apple','Orange','Mango','Watermelon','Grapes','Dates','Nuts Mix',
  'Poha','Upma','Paratha','Chapati','Rice','Dal',
  // Desserts
  'Ice Cream','Gulab Jamun','Halwa','Kheer','Chocolate Cake','Brownie','Cheesecake',
].sort();

const BMI_INFO = {
  Underweight: {
    color: '#38bdf8', emoji: '📉',
    why: 'Your BMI is below 18.5 kg/m². This means your body weight is lower than what is considered healthy for your height. It may indicate insufficient caloric intake, malnutrition, or an underlying health condition.',
    risks: ['Weakened immune system', 'Nutritional deficiencies', 'Fatigue and low energy', 'Bone density loss', 'Hormonal imbalances'],
  },
  Normal: {
    color: '#4ade80', emoji: '✅',
    why: 'Your BMI is between 18.5–24.9 kg/m². This is the healthy weight range defined by the World Health Organization (WHO). Your weight is proportionate to your height.',
    risks: ['Lowest risk of weight-related disease', 'Healthy cardiovascular function', 'Normal hormonal balance', 'Good energy levels', 'Optimal metabolic rate'],
  },
  Overweight: {
    color: '#fbbf24', emoji: '⚠️',
    why: 'Your BMI is between 25–29.9 kg/m². You carry excess body weight relative to your height. This category increases risk of several chronic conditions if not addressed.',
    risks: ['Increased risk of type 2 diabetes', 'Elevated blood pressure', 'Joint stress and pain', 'Sleep apnea risk', 'Higher cardiovascular risk'],
  },
  Obese: {
    color: '#f87171', emoji: '🔴',
    why: 'Your BMI is 30 kg/m² or higher. Obesity is a medical condition with significant health implications. BMI ≥30 is associated with substantially elevated risk of metabolic and cardiovascular disease.',
    risks: ['High risk of type 2 diabetes', 'Heart disease and stroke', 'Sleep apnea', 'Certain cancers', 'Severe joint problems'],
  },
};

function Dashboard({ userId, user }) {
  const [form, setForm] = useState({
    height: '',
    weight: '',
    age:    '',
    gender: 'male',
    activity: 'active',
    selected_food: '',
  });

  // Auto-fetch latest saved metrics so dashboard is pre-filled
  useEffect(() => {
    if (!userId) return;
    axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/users/${userId}/profile`)
      .then(res => {
        const d = res.data;
        setForm(f => ({
          ...f,
          height:   d.height   ? String(d.height)   : (d.height_cm ? String(d.height_cm) : f.height || '170'),
          weight:   d.weight   ? String(d.weight)   : (d.weight_kg ? String(d.weight_kg) : f.weight || '75'),
          age:      d.age      ? String(d.age)      : f.age || '25',
          gender:   d.gender   || f.gender,
          activity: d.activity || f.activity,
        }));
      })
      .catch(err => console.warn('Could not load metrics:', err.message));
  }, [userId]);

  const [image, setImage]     = useState(null);
  const [preview, setPreview] = useState('');
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = ev => setPreview(ev.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = ev => setPreview(ev.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleClassify = async () => {
    if (!image)  { toast.error('Please select a food image!', { icon: '📸' }); return; }
    if (!userId) { toast.error('Please login first!', { icon: '🔒' }); return; }
    if (!form.height || !form.weight) { toast.error('Enter height and weight!', { icon: '⚠️' }); return; }

    setLoading(true);
    setResult(null);

    const t = toast.loading('🤖 AI is analyzing your food...', {
      style: { borderRadius: '10px', background: '#1e293b', color: '#e0f2fe' },
    });

    try {
      const fd = new FormData();
      fd.append('user_id',        userId);
      fd.append('height_cm',      form.height);
      fd.append('weight_kg',      form.weight);
      fd.append('age',            form.age);
      fd.append('gender',         form.gender);
      fd.append('activity_level', form.activity);
      fd.append('image',          image);
      // ✅ Send selected_food to backend so it saves the correct name in MongoDB
      if (form.selected_food) {
        fd.append('food_name_override', form.selected_food);
      }

      const res        = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:5000/api'}/classify-food`, fd
      );
      const resultData = { ...res.data };

      // Use selected food name in result display too
      if (form.selected_food) {
        resultData.food_name = form.selected_food;
      }

      setResult(resultData);
      toast.dismiss(t);
      toast.success(`Detected: ${resultData.food_name}! 🍽️`, { duration: 3000 });
    } catch (err) {
      toast.dismiss(t);
      toast.error(err.response?.data?.error || 'Analysis failed. Try again.', { icon: '❌' });
    } finally {
      setLoading(false);
    }
  };

  const bmiInfo = result ? BMI_INFO[result.bmi_category] || BMI_INFO.Normal : null;
  const mealPct = result ? Math.min((result.calories / result.daily_calories) * 100, 100) : 0;

  return (
    <div className="dash">
      <div className="dash-grid">

        {/* ── COL 1: METRICS ── */}
        <aside className="dash-panel metrics-panel">
          <div className="panel-hdr">
            <span>📊</span><h3>Your Metrics</h3>
          </div>
          <div className="panel-body">
            {[
              { label: 'Height (cm)', name: 'height', type: 'number', placeholder: '170' },
              { label: 'Weight (kg)', name: 'weight', type: 'number', placeholder: '75' },
              { label: 'Age (years)', name: 'age',    type: 'number', placeholder: '25' },
            ].map(f => (
              <div className="field" key={f.name}>
                <label>{f.label}</label>
                <input type={f.type} name={f.name} value={form[f.name]}
                  onChange={handleChange} placeholder={f.placeholder} className="field-input" />
              </div>
            ))}

            <div className="field">
              <label>Gender</label>
              <div className="gender-pills">
                {['male','female'].map(g => (
                  <button key={g} type="button"
                    className={`gpill ${form.gender === g ? 'active' : ''}`}
                    onClick={() => setForm(f => ({ ...f, gender: g }))}>
                    {g === 'male' ? '♂ Male' : '♀ Female'}
                  </button>
                ))}
              </div>
            </div>

            <div className="field">
              <label>Activity Level</label>
              <select name="activity" value={form.activity} onChange={handleChange} className="field-input">
                <option value="sedentary">Sedentary</option>
                <option value="lightly_active">Lightly Active</option>
                <option value="active">Active</option>
                <option value="very_active">Very Active</option>
                <option value="extra_active">Extra Active</option>
              </select>
            </div>

            <div className="field">
              <label>Food Name Override {form.selected_food && <span className="optional-tag" style={{background:'rgba(34,211,238,0.15)',color:'#22d3ee'}}>active</span>}</label>
              <select name="selected_food" value={form.selected_food} onChange={handleChange} className="field-input">
                <option value="">— Let AI detect automatically —</option>
                {FOOD_LIST.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
              <span className="field-hint">{form.selected_food ? `✅ "${form.selected_food}" will be saved in history` : 'Select to override AI detected food name'}</span>
            </div>
          </div>
        </aside>

        {/* ── COL 2: UPLOAD ── */}
        <section className="dash-panel upload-panel">
          <div className="panel-hdr">
            <span>🍔</span><h3>Classify Food</h3>
          </div>
          <div className="panel-body upload-body">
            <div
              className={`dropzone ${preview ? 'has-img' : ''}`}
              onDragOver={e => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => !preview && document.getElementById('imgInput').click()}
            >
              {preview ? (
                <img src={preview} alt="preview" className="food-img" />
              ) : (
                <div className="drop-hint">
                  <div className="drop-icon">📸</div>
                  <p className="drop-t">Drop your food image here</p>
                  <p className="drop-s">PNG, JPG, GIF, BMP, WEBP</p>
                  <p className="drop-s">🤖 MobileNetV2 AI identifies food & calories from image</p>
                </div>
              )}
            </div>

            <input type="file" id="imgInput" accept="image/*"
              onChange={handleImageChange} style={{ display: 'none' }} />

            <div className="upload-actions">
              <button className="btn-choose"
                onClick={() => document.getElementById('imgInput').click()}>
                {preview ? '🔄 Change Image' : '📂 Choose Image'}
              </button>
              <button className="btn-analyze" onClick={handleClassify}
                disabled={!image || loading}>
                {loading ? '⏳ Analyzing...' : '🚀 Analyze Food'}
              </button>
            </div>

            <div className="ai-badge">
              🤖 Powered by MobileNetV2 — calories calculated from image + your body metrics
            </div>
          </div>
        </section>

        {/* ── COL 3: RESULTS ── */}
        <aside className="dash-panel results-panel">
          <div className="panel-hdr">
            <span>✨</span><h3>Analysis</h3>
          </div>
          <div className="panel-body">
            {!result ? (
              <div className="empty-state">
                <div className="empty-icon">🥗</div>
                <p>Upload a food image and click Analyze to see your personalized nutrition breakdown</p>
                <p className="empty-hint">AI detects any food from the photo</p>
              </div>
            ) : (
              <div className="results-scroll">

                {result.description && (
                  <div className="detect-info">
                    <span className="detect-text">{result.description}</span>
                    <span className={`conf-tag conf-${result.confidence}`}>
                      {result.confidence === 'high' ? '🟢' : result.confidence === 'medium' ? '🟡' : '🟠'} {result.confidence}
                    </span>
                  </div>
                )}

                <div className="stat-grid">
                  <div className="stat-card">
                    <span className="s-label">Detected Food</span>
                    <span className="s-val food-val">{result.food_name}</span>
                  </div>
                  <div className="stat-card">
                    <span className="s-label">Calories</span>
                    <span className="s-val">{result.calories}<em> kcal</em></span>
                  </div>
                  <div className="stat-card">
                    <span className="s-label">BMI</span>
                    <span className="s-val">{result.bmi}
                      <span className="bmi-badge" style={{ color: bmiInfo?.color }}>
                        {bmiInfo?.emoji} {result.bmi_category}
                      </span>
                    </span>
                  </div>
                  <div className="stat-card">
                    <span className="s-label">Daily Need</span>
                    <span className="s-val">{Math.round(result.daily_calories)}<em> kcal</em></span>
                  </div>
                </div>

                <div className="progress-section">
                  <div className="prog-header">
                    <span className="prog-title">Meal vs Daily Target</span>
                    <span className="prog-pct">{result.meal_pct}%</span>
                  </div>
                  <div className="prog-track">
                    <div className="prog-bar" style={{
                      width: `${mealPct}%`,
                      background: result.status === 'success' ? '#4ade80'
                        : result.status === 'warning' ? '#fbbf24' : '#f87171'
                    }} />
                    <div className="prog-marker" style={{ left: '33.3%' }} title="1/3 daily target" />
                  </div>
                  <div className="prog-labels">
                    <span>This meal: <strong>{result.calories} kcal</strong></span>
                    <span>Meal target: <strong>{Math.round(result.meal_target)} kcal</strong></span>
                    <span>Remaining: <strong>{Math.max(0, Math.round(result.daily_calories - result.calories))} kcal</strong></span>
                  </div>
                </div>

                <div className="bmi-explain" style={{ borderColor: bmiInfo?.color + '44' }}>
                  <div className="bmi-explain-hdr" style={{ color: bmiInfo?.color }}>
                    {bmiInfo?.emoji} Why {result.bmi_category}?
                  </div>
                  <p className="bmi-explain-why">{bmiInfo?.why}</p>
                  <div className="bmi-risks">
                    {bmiInfo?.risks.map((r, i) => (
                      <span key={i} className="bmi-risk-tag"
                        style={{ borderColor: bmiInfo?.color + '44', color: bmiInfo?.color }}>
                        {r}
                      </span>
                    ))}
                  </div>
                </div>

              </div>
            )}
          </div>
        </aside>

      </div>

      {/* ── FULL-WIDTH HORIZONTAL CARDS ── */}
      {result && (
        <div className="insight-strip">
          <div className="insight-strip-hdr">
            <span className="insight-strip-title">
              <span>🧠</span> Personalized Insights
            </span>
            <span className={`insight-status-pill pill-${result.status}`}>
              {result.status === 'success' ? '✅ Safe Meal' : result.status === 'warning' ? '⚠️ Moderate' : '🔴 High Calorie'}
            </span>
          </div>

          <div className="insight-cards-row">

            <div className="insight-card ic-reco">
              <div className="ic-header">
                <div className="ic-icon-wrap ic-icon-reco">
                  {result.status === 'success' ? '✅' : result.status === 'warning' ? '⚠️' : '🔴'}
                </div>
                <div>
                  <div className="ic-title">Recommendations</div>
                  <div className="ic-subtitle">{result.recommendation}</div>
                </div>
              </div>
              <div className="ic-items">
                {result.recommendations?.map((r, i) => (
                  <div key={i} className="ic-item ic-item-reco">
                    <span className="ic-dot ic-dot-reco">{i + 1}</span>
                    <span>{r}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="insight-card ic-avoid">
              <div className="ic-header">
                <div className="ic-icon-wrap ic-icon-avoid">🚫</div>
                <div>
                  <div className="ic-title">What to Avoid</div>
                  <div className="ic-subtitle">Based on your BMI & calorie intake</div>
                </div>
              </div>
              <div className="ic-items">
                {result.avoids?.map((a, i) => (
                  <div key={i} className="ic-item ic-item-avoid">
                    <span className="ic-dot ic-dot-avoid">✕</span>
                    <span>{a}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="insight-card ic-suggest">
              <div className="ic-header">
                <div className="ic-icon-wrap ic-icon-suggest">💡</div>
                <div>
                  <div className="ic-title">Smart Suggestions</div>
                  <div className="ic-subtitle">Tips for {result.bmi_category} BMI</div>
                </div>
              </div>
              <div className="ic-items">
                {bmiInfo?.risks.map((r, i) => (
                  <div key={i} className="ic-item ic-item-suggest">
                    <span className="ic-dot ic-dot-suggest">→</span>
                    <span>Monitor: <strong>{r}</strong></span>
                  </div>
                ))}
                <div className="ic-item ic-item-suggest">
                  <span className="ic-dot ic-dot-suggest">📊</span>
                  <span>Your meal is <strong>{result.meal_pct}%</strong> of daily target</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default Dashboard;