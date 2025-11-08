import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Register Page Component
 * Handles new user registration with comprehensive validation
 * Mobile-first responsive design
 */
const Register = () => {
  const navigate = useNavigate();
  const { register, error, clearError } = useAuth();
  
  // Form state
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

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
    
    // Clear field-specific validation error when user starts typing
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    
    // Clear auth error when user modifies form
    if (error) {
      clearError();
    }
  };

  /**
   * Validate form data before submission
   * @returns {boolean} True if form is valid, false otherwise
   */
  const validateForm = () => {
    const errors = {};
    
    // Username validation
    if (!formData.username.trim()) {
      errors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    } else if (formData.username.length > 50) {
      errors.username = 'Username must be less than 50 characters';
    }
    
    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    }
    
    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle form submission
   * @param {Event} e - Form submit event
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Prepare data for API (exclude confirmPassword)
      const { confirmPassword, ...registrationData } = formData;
      
      // Remove full_name if empty (it's optional)
      if (!registrationData.full_name || !registrationData.full_name.trim()) {
        delete registrationData.full_name;
      }
      
      // Debug: Log the data being sent
      console.log('Sending registration data:', registrationData);
      
      await register(registrationData);
      // Navigation will happen automatically via ProtectedRoute
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration failed:', err);
      console.error('Error response:', err.response?.data);
      // Error is already set in AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="logo">Ripple</h1>
          <p className="text-muted">Create your account</p>
        </div>

        {/* Display authentication error */}
        {error && (
          <div className="alert alert-error">
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {/* Username field */}
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              className={`form-input ${validationErrors.username ? 'error' : ''}`}
              value={formData.username}
              onChange={handleChange}
              disabled={loading}
              placeholder="johndoe"
            />
            {validationErrors.username && (
              <p className="form-error">{validationErrors.username}</p>
            )}
            <p className="form-help">3-50 characters, used for login</p>
          </div>

          {/* Full name field (optional) */}
          <div className="form-group">
            <label htmlFor="full_name" className="form-label">
              Full Name (optional)
            </label>
            <input
              id="full_name"
              name="full_name"
              type="text"
              autoComplete="name"
              className={`form-input ${validationErrors.full_name ? 'error' : ''}`}
              value={formData.full_name}
              onChange={handleChange}
              disabled={loading}
              placeholder="John Doe"
            />
            {validationErrors.full_name && (
              <p className="form-error">{validationErrors.full_name}</p>
            )}
          </div>

          {/* Email field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              className={`form-input ${validationErrors.email ? 'error' : ''}`}
              value={formData.email}
              onChange={handleChange}
              disabled={loading}
              placeholder="you@example.com"
            />
            {validationErrors.email && (
              <p className="form-error">{validationErrors.email}</p>
            )}
          </div>

          {/* Password field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="new-password"
              required
              className={`form-input ${validationErrors.password ? 'error' : ''}`}
              value={formData.password}
              onChange={handleChange}
              disabled={loading}
              placeholder="Minimum 8 characters"
            />
            {validationErrors.password && (
              <p className="form-error">{validationErrors.password}</p>
            )}
          </div>

          {/* Confirm password field */}
          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              autoComplete="new-password"
              required
              className={`form-input ${validationErrors.confirmPassword ? 'error' : ''}`}
              value={formData.confirmPassword}
              onChange={handleChange}
              disabled={loading}
              placeholder="Re-enter your password"
            />
            {validationErrors.confirmPassword && (
              <p className="form-error">{validationErrors.confirmPassword}</p>
            )}
          </div>

          {/* Submit button */}
          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        {/* Login link */}
        <div className="auth-footer">
          <p>
            Already have an account?{' '}
            <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
