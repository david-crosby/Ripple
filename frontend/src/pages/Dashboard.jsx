import React from 'react';
import { useAuth } from '../contexts/AuthContext';

/**
 * Dashboard Page Component
 * Main landing page after authentication
 * Displays welcome message and quick stats
 * Mobile-first responsive design
 */
const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="container">
      <div className="card">
        <div className="card-header">
          <h1 className="card-title">
            Welcome back, {user?.first_name}!
          </h1>
        </div>
        <div className="card-body">
          <p>
            This is your Ripple dashboard. From here, you can manage your profile,
            view your donation history, and support campaigns that matter to you.
          </p>
          
          <div className="alert alert-info mt-md">
            <strong>Note:</strong> Campaign browsing and donation features are coming soon!
            For now, you can manage your profile and view your donation history.
          </div>
        </div>
      </div>

      {/* Quick stats placeholder */}
      <div className="profile-info-grid mt-lg">
        <div className="card">
          <div className="card-body text-center">
            <h3 style={{ color: 'var(--primary-green)' }}>0</h3>
            <p className="text-muted">Active Campaigns</p>
          </div>
        </div>
        
        <div className="card">
          <div className="card-body text-center">
            <h3 style={{ color: 'var(--secondary-teal)' }}>0</h3>
            <p className="text-muted">Total Donations</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
