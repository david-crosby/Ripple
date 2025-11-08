import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Header Component
 * Main navigation header with logo and user menu
 * Displays different navigation options based on authentication status
 */
const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  /**
   * Handle user logout
   * Clears authentication and redirects to login page
   */
  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          {/* Logo */}
          <Link to="/dashboard" className="logo">
            Ripple
          </Link>

          {/* Navigation */}
          <nav className="nav">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/profile">Profile</Link>
            {user && (
              <span className="text-muted hide-mobile">
                {user.first_name} {user.last_name}
              </span>
            )}
            <button onClick={handleLogout} className="btn btn-outline">
              Logout
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
