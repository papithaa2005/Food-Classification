import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import './Navigation.css';

function Navigation({ userId }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path ? 'active' : '';

  const handleDashboardClick = (e) => {
    if (!userId) {
      e.preventDefault();
      toast.error('Please login or sign up to access the Dashboard!', {
        icon: '🔒',
        duration: 3000,
        style: {
          borderRadius: '10px',
          background: '#1e293b',
          color: '#f1f5f9',
          fontWeight: '500',
        },
      });
      navigate('/register');
    }
  };

  const handleGetStartedClick = (e) => {
    if (userId) {
      e.preventDefault();
      toast('You are already signed in! 👤', {
        icon: '✅',
        duration: 3000,
        style: {
          borderRadius: '10px',
          background: '#0f172a',
          color: '#e0f2fe',
          fontWeight: '500',
        },
      });
    }
  };

  return (
    <nav className="navbar">
      {/* ── Desktop: 3-column grid ── */}
      <div className="navbar-container">

        {/* Col 1 — Brand (left) */}
        <Link to="/" className="navbar-brand">
          🍔 FoodFit
        </Link>

        {/* Col 2 — Links (center) */}
        <ul className="navbar-menu">
          <li>
            <Link to="/" className={`nav-link ${isActive('/')}`}>
              Home
            </Link>
          </li>
          <li>
            <Link
              to="/dashboard"
              className={`nav-link ${isActive('/dashboard')}`}
              onClick={handleDashboardClick}
            >
              Dashboard
            </Link>
          </li>
          {userId && (
            <li>
              <Link to="/history" className={`nav-link ${isActive('/history')}`}>
                History
              </Link>
            </li>
          )}
        </ul>

        {/* Col 3 — Action (right) */}
        <div className="navbar-right">
          <Link
            to="/register"
            className="btn-nav"
            onClick={handleGetStartedClick}
          >
            Login / Get Started
          </Link>
        </div>
      </div>

      {/* ── Mobile: separate bar below ── */}
      <div className="navbar-mobile">
        <Link to="/" className="navbar-brand">
          🍔 FoodFit
        </Link>

        <div className="mobile-right">
          <Link
            to="/register"
            className="btn-nav"
            onClick={handleGetStartedClick}
          >
            Get Started
          </Link>

          <button
            className="hamburger"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
          >
            <span className={menuOpen ? 'open' : ''}></span>
            <span className={menuOpen ? 'open' : ''}></span>
            <span className={menuOpen ? 'open' : ''}></span>
          </button>
        </div>
      </div>

      {/* ── Mobile dropdown menu ── */}
      {menuOpen && (
        <div className="mobile-menu">
          <Link
            to="/"
            className={`mobile-link ${isActive('/')}`}
            onClick={() => setMenuOpen(false)}
          >
            Home
          </Link>
          <Link
            to="/dashboard"
            className={`mobile-link ${isActive('/dashboard')}`}
            onClick={(e) => {
              setMenuOpen(false);
              handleDashboardClick(e);
            }}
          >
            Dashboard
          </Link>
          {userId && (
            <Link
              to="/history"
              className={`mobile-link ${isActive('/history')}`}
              onClick={() => setMenuOpen(false)}
            >
              History
            </Link>
          )}
        </div>
      )}
    </nav>
  );
}

export default Navigation;