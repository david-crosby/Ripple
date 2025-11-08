import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getMyGiverProfile, updateMyGiverProfile, getMyDonations } from '../services/api';

/**
 * Profile Page Component
 * Allows users to view and update their giver profile information
 * Displays donation history
 * Mobile-first responsive design
 */
const Profile = () => {
  const { user, updateUser } = useAuth();
  
  // Profile data state
  const [profile, setProfile] = useState(null);
  const [donations, setDonations] = useState([]);
  
  // Form state
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
  });
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [validationErrors, setValidationErrors] = useState({});

  /**
   * Load giver profile and donation history on component mount
   */
  useEffect(() => {
    loadProfileData();
  }, []);

  /**
   * Load profile and donation data from API
   */
  const loadProfileData = async () => {
    setLoading(true);
    try {
      // Load giver profile
      const profileData = await getMyGiverProfile();
      setProfile(profileData);
      
      // Populate form with existing data
      setFormData({
        first_name: profileData.first_name || '',
        last_name: profileData.last_name || '',
        email: profileData.email || '',
        phone: profileData.phone || '',
        address_line1: profileData.address_line1 || '',
        address_line2: profileData.address_line2 || '',
        city: profileData.city || '',
        state: profileData.state || '',
        postal_code: profileData.postal_code || '',
        country: profileData.country || '',
      });
      
      // Load donation history
      const donationData = await getMyDonations(0, 10);
      setDonations(donationData);
    } catch (error) {
      console.error('Error loading profile:', error);
      setMessage({
        type: 'error',
        text: 'Failed to load profile data. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle input field changes
   * @param {Event} e - Input change event
   */
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific validation error
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    // Clear message when user modifies form
    if (message.text) {
      setMessage({ type: '', text: '' });
    }
  };

  /**
   * Validate form data before submission
   * @returns {boolean} True if form is valid
   */
  const validateForm = () => {
    const errors = {};
    
    // Required fields
    if (!formData.first_name.trim()) {
      errors.first_name = 'First name is required';
    }
    
    if (!formData.last_name.trim()) {
      errors.last_name = 'Last name is required';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    // Optional phone validation
    if (formData.phone && !/^\+?[\d\s-()]+$/.test(formData.phone)) {
      errors.phone = 'Please enter a valid phone number';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission to update profile
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    setMessage({ type: '', text: '' });
    
    try {
      // Prepare data - remove empty optional fields
      const updateData = { ...formData };
      Object.keys(updateData).forEach(key => {
        if (!updateData[key]) {
          delete updateData[key];
        }
      });
      
      const updatedProfile = await updateMyGiverProfile(updateData);
      setProfile(updatedProfile);
      
      // Update user in auth context if name or email changed
      if (user.first_name !== updatedProfile.first_name || 
          user.last_name !== updatedProfile.last_name ||
          user.email !== updatedProfile.email) {
        updateUser({
          ...user,
          first_name: updatedProfile.first_name,
          last_name: updatedProfile.last_name,
          email: updatedProfile.email,
        });
      }
      
      setEditing(false);
      setMessage({
        type: 'success',
        text: 'Profile updated successfully!'
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to update profile. Please try again.'
      });
    } finally {
      setSaving(false);
    }
  };

  /**
   * Cancel editing and reset form to current profile data
   */
  const handleCancel = () => {
    setEditing(false);
    setValidationErrors({});
    setMessage({ type: '', text: '' });
    
    // Reset form to current profile data
    if (profile) {
      setFormData({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
        address_line1: profile.address_line1 || '',
        address_line2: profile.address_line2 || '',
        city: profile.city || '',
        state: profile.state || '',
        postal_code: profile.postal_code || '',
        country: profile.country || '',
      });
    }
  };

  /**
   * Format date for display
   * @param {string} dateString - ISO date string
   * @returns {string} Formatted date
   */
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };

  /**
   * Format currency for display
   * @param {number} amount - Amount in pounds
   * @returns {string} Formatted currency
   */
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>My Profile</h1>

      {/* Success/Error message */}
      {message.text && (
        <div className={`alert alert-${message.type}`}>
          {message.text}
        </div>
      )}

      {/* Profile Information Card */}
      <div className="card">
        <div className="card-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <h2 className="card-title">Profile Information</h2>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="btn btn-secondary"
              >
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="card-body">
          {editing ? (
            // Edit mode - show form
            <form onSubmit={handleSubmit}>
              <div className="profile-info-grid">
                {/* First name */}
                <div className="form-group">
                  <label htmlFor="first_name" className="form-label">
                    First Name *
                  </label>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    className={`form-input ${validationErrors.first_name ? 'error' : ''}`}
                    value={formData.first_name}
                    onChange={handleChange}
                    disabled={saving}
                  />
                  {validationErrors.first_name && (
                    <p className="form-error">{validationErrors.first_name}</p>
                  )}
                </div>

                {/* Last name */}
                <div className="form-group">
                  <label htmlFor="last_name" className="form-label">
                    Last Name *
                  </label>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    className={`form-input ${validationErrors.last_name ? 'error' : ''}`}
                    value={formData.last_name}
                    onChange={handleChange}
                    disabled={saving}
                  />
                  {validationErrors.last_name && (
                    <p className="form-error">{validationErrors.last_name}</p>
                  )}
                </div>

                {/* Email */}
                <div className="form-group">
                  <label htmlFor="email" className="form-label">
                    Email Address *
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    className={`form-input ${validationErrors.email ? 'error' : ''}`}
                    value={formData.email}
                    onChange={handleChange}
                    disabled={saving}
                  />
                  {validationErrors.email && (
                    <p className="form-error">{validationErrors.email}</p>
                  )}
                </div>

                {/* Phone */}
                <div className="form-group">
                  <label htmlFor="phone" className="form-label">
                    Phone Number
                  </label>
                  <input
                    id="phone"
                    name="phone"
                    type="tel"
                    className={`form-input ${validationErrors.phone ? 'error' : ''}`}
                    value={formData.phone}
                    onChange={handleChange}
                    disabled={saving}
                  />
                  {validationErrors.phone && (
                    <p className="form-error">{validationErrors.phone}</p>
                  )}
                </div>
              </div>

              {/* Address section */}
              <h3 className="mt-lg mb-md">Address</h3>
              
              <div className="form-group">
                <label htmlFor="address_line1" className="form-label">
                  Address Line 1
                </label>
                <input
                  id="address_line1"
                  name="address_line1"
                  type="text"
                  className="form-input"
                  value={formData.address_line1}
                  onChange={handleChange}
                  disabled={saving}
                />
              </div>

              <div className="form-group">
                <label htmlFor="address_line2" className="form-label">
                  Address Line 2
                </label>
                <input
                  id="address_line2"
                  name="address_line2"
                  type="text"
                  className="form-input"
                  value={formData.address_line2}
                  onChange={handleChange}
                  disabled={saving}
                />
              </div>

              <div className="profile-info-grid">
                <div className="form-group">
                  <label htmlFor="city" className="form-label">
                    City
                  </label>
                  <input
                    id="city"
                    name="city"
                    type="text"
                    className="form-input"
                    value={formData.city}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="state" className="form-label">
                    County/State
                  </label>
                  <input
                    id="state"
                    name="state"
                    type="text"
                    className="form-input"
                    value={formData.state}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="postal_code" className="form-label">
                    Postal Code
                  </label>
                  <input
                    id="postal_code"
                    name="postal_code"
                    type="text"
                    className="form-input"
                    value={formData.postal_code}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="country" className="form-label">
                    Country
                  </label>
                  <input
                    id="country"
                    name="country"
                    type="text"
                    className="form-input"
                    value={formData.country}
                    onChange={handleChange}
                    disabled={saving}
                  />
                </div>
              </div>

              {/* Form actions */}
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', flexWrap: 'wrap' }}>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="btn btn-outline"
                  disabled={saving}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            // View mode - display profile data
            <div className="profile-section">
              <h3 className="mb-md">Personal Information</h3>
              <div className="profile-info-grid">
                <div className="profile-info-item">
                  <div className="profile-info-label">Name</div>
                  <div className="profile-info-value">
                    {profile.first_name} {profile.last_name}
                  </div>
                </div>
                <div className="profile-info-item">
                  <div className="profile-info-label">Email</div>
                  <div className="profile-info-value">{profile.email}</div>
                </div>
                <div className="profile-info-item">
                  <div className="profile-info-label">Phone</div>
                  <div className="profile-info-value">
                    {profile.phone || 'Not provided'}
                  </div>
                </div>
                <div className="profile-info-item">
                  <div className="profile-info-label">Total Donations</div>
                  <div className="profile-info-value text-success">
                    {formatCurrency(profile.total_donated)}
                  </div>
                </div>
              </div>

              {(profile.address_line1 || profile.city || profile.country) && (
                <>
                  <h3 className="mt-lg mb-md">Address</h3>
                  <div className="profile-info-item">
                    <div className="profile-info-label">Full Address</div>
                    <div className="profile-info-value">
                      {profile.address_line1 && <div>{profile.address_line1}</div>}
                      {profile.address_line2 && <div>{profile.address_line2}</div>}
                      {profile.city && profile.postal_code && (
                        <div>{profile.city}, {profile.postal_code}</div>
                      )}
                      {profile.state && <div>{profile.state}</div>}
                      {profile.country && <div>{profile.country}</div>}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Donation History Card */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Donation History</h2>
        </div>
        <div className="card-body">
          {donations.length === 0 ? (
            <p className="text-muted text-center">No donations yet</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)' }}>
                    <th style={{ padding: 'var(--spacing-sm)', textAlign: 'left' }}>Date</th>
                    <th style={{ padding: 'var(--spacing-sm)', textAlign: 'left' }}>Campaign</th>
                    <th style={{ padding: 'var(--spacing-sm)', textAlign: 'right' }}>Amount</th>
                    <th style={{ padding: 'var(--spacing-sm)', textAlign: 'center' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {donations.map((donation) => (
                    <tr key={donation.id} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: 'var(--spacing-sm)' }}>
                        {formatDate(donation.created_at)}
                      </td>
                      <td style={{ padding: 'var(--spacing-sm)' }}>
                        Campaign #{donation.campaign_id}
                      </td>
                      <td style={{ padding: 'var(--spacing-sm)', textAlign: 'right', fontWeight: '500' }}>
                        {formatCurrency(donation.amount)}
                      </td>
                      <td style={{ padding: 'var(--spacing-sm)', textAlign: 'center' }}>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 'var(--font-size-sm)',
                          backgroundColor: donation.status === 'completed' ? 'var(--success)' : 'var(--border)',
                          color: donation.status === 'completed' ? 'white' : 'var(--text-primary)'
                        }}>
                          {donation.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;
