import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">🍔 FoodFit</h1>
          <p className="hero-subtitle">Smart Nutrition Tracking with AI</p>
          <p className="hero-description">
            Classify your food instantly, track calories accurately, and achieve
            your health goals with personalized recommendations.
          </p>
          <Link to="/register" className="hero-btn">
            Get Started Free
          </Link>
        </div>
      </div>

      {/* Cards Grid Section */}
      <div className="cards-section">
        <div className="container">
          <div className="row g-4 justify-content-center">
            {/* Card 1 */}
            <div className="col-12 col-md-6 col-lg-4">
              <div className="card feature-card h-100">
                <div className="card-body text-center p-4">
                  <div className="card-icon">📸</div>
                  <h3>Smart Recognition</h3>
                  <p>
                    Snap a photo of your meal and get instant accurate calorie
                    analysis using AI technology.
                  </p>
                  <div className="card-stats">
                    <span className="stat-badge">98% Accurate</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 2 */}
            <div className="col-12 col-md-6 col-lg-4">
              <div className="card feature-card h-100">
                <div className="card-body text-center p-4">
                  <div className="card-icon">💪</div>
                  <h3>Personal Goals</h3>
                  <p>
                    Track your daily intake based on your body metrics and reach your
                    fitness goals faster.
                  </p>
                  <div className="card-stats">
                    <span className="stat-badge">10K+ Users</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 3 */}
            <div className="col-12 col-md-6 col-lg-4">
              <div className="card feature-card h-100">
                <div className="card-body text-center p-4">
                  <div className="card-icon">📊</div>
                  <h3>Smart Analytics</h3>
                  <p>
                    Get personalized recommendations based on your BMI and daily
                    energy requirements.
                  </p>
                  <div className="card-stats">
                    <span className="stat-badge">Real-time</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 4 */}
            <div className="col-12 col-md-6 col-lg-4">
              <div className="card feature-card h-100">
                <div className="card-body text-center p-4">
                  <div className="card-icon">📱</div>
                  <h3>Mobile Friendly</h3>
                  <p>
                    Access from anywhere, anytime with fully responsive design
                    optimized for all devices.
                  </p>
                  <div className="card-stats">
                    <span className="stat-badge">All Devices</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 5 */}
            <div className="col-12 col-md-6 col-lg-4">
              <div className="card feature-card h-100">
                <div className="card-body text-center p-4">
                  <div className="card-icon">🎯</div>
                  <h3>Meal Planning</h3>
                  <p>
                    Smart meal suggestions and recommendations to help you stay on
                    track with your nutrition.
                  </p>
                  <div className="card-stats">
                    <span className="stat-badge">Daily Tips</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 6 */}
            <div className="col-12 col-md-6 col-lg-4">
              <div className="card feature-card h-100">
                <div className="card-body text-center p-4">
                  <div className="card-icon">🔒</div>
                  <h3>Secure & Private</h3>
                  <p>
                    Your health data is encrypted and secure. We never share your
                    personal information.
                  </p>
                  <div className="card-stats">
                    <span className="stat-badge">100% Safe</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="stats-section">
        <div className="container">
          <div className="row g-4 justify-content-center text-center">
            <div className="col-12 col-md-4">
              <div className="stat-item">
                <h4>50K+</h4>
                <p>Foods Recognized</p>
              </div>
            </div>
            <div className="col-12 col-md-4">
              <div className="stat-item">
                <h4>10K+</h4>
                <p>Active Users</p>
              </div>
            </div>
            <div className="col-12 col-md-4">
              <div className="stat-item">
                <h4>1M+</h4>
                <p>Meals Tracked</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="cta-section">
        <h2>Ready to Transform Your Nutrition?</h2>
        <p>Join thousands of users tracking their health goals</p>
        <Link to="/register" className="cta-btn">
          Get Started Free
        </Link>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>
          &copy; 2026 FoodFit. All rights reserved. | Smart Nutrition Tracking
        </p>
      </footer>
    </div>
  );
}

export default Home;