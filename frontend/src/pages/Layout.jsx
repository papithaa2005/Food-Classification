import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import './Layout.css';

const NAV_ITEMS = [
  { to: '/dashboard', icon: '🍔', label: 'Dashboard' },
  { to: '/history',   icon: '📊', label: 'History' },
];

function Layout({ children, user, onLogout }) {
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    onLogout();
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  return (
    <div className={`layout-root ${collapsed ? 'sidebar-collapsed' : ''}`}>
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="sidebar-brand">
            <span className="sidebar-logo">🥗</span>
            {!collapsed && <span className="sidebar-name">FoodFit</span>}
          </div>
          <button className="sidebar-toggle" onClick={() => setCollapsed(c => !c)}>
            {collapsed ? '›' : '‹'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map(({ to, icon, label }) => (
            <NavLink key={to} to={to} className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`}>
              <span className="sidebar-icon">{icon}</span>
              {!collapsed && <span className="sidebar-label">{label}</span>}
            </NavLink>
          ))}
        </nav>

        {!collapsed && user && (
          <div className="sidebar-user">
            <div className="sidebar-avatar">{initials}</div>
            <div className="sidebar-user-info">
              <span className="sidebar-user-name">{user.full_name}</span>
              <span className="sidebar-user-role">Member</span>
            </div>
          </div>
        )}
      </aside>

      {/* ── Main ── */}
      <div className="layout-main">
        {/* Topbar */}
        <header className="topbar">
          <div className="topbar-left">
            <h2 className="topbar-title">
              {NAV_ITEMS.find(n => window.location.pathname.startsWith(n.to))?.label || 'FoodFit'}
            </h2>
          </div>
          <div className="topbar-right">
            {/* Profile dropdown */}
            <div className="profile-wrap">
              <button className="profile-btn" onClick={() => setProfileOpen(o => !o)}>
                <div className="profile-avatar">{initials}</div>
                <div className="profile-info">
                  <span className="profile-name">{user?.full_name || 'User'}</span>
                  <span className="profile-email">{user?.email || ''}</span>
                </div>
                <span className="profile-caret">{profileOpen ? '▲' : '▼'}</span>
              </button>

              {profileOpen && (
                <div className="profile-dropdown">
                  <div className="profile-dropdown-header">
                    <div className="profile-avatar-lg">{initials}</div>
                    <div>
                      <div className="pd-name">{user?.full_name}</div>
                      <div className="pd-email">{user?.email}</div>
                    </div>
                  </div>
                  <div className="profile-dropdown-stats">
                    <div className="pd-stat">
                      <span>Gender</span>
                      <strong>{user?.gender || '—'}</strong>
                    </div>
                    <div className="pd-stat">
                      <span>Age</span>
                      <strong>{user?.age ? `${user.age} yrs` : '—'}</strong>
                    </div>
                  </div>
                  <button className="pd-logout" onClick={handleLogout}>
                    🚪 Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="layout-content">
          {children}
        </main>
      </div>
    </div>
  );
}

export default Layout;