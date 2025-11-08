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
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
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
    
    // First name validation
    if (!formData.first_name.trim()) {
      errors.first_name = 'First name is required';
    }
    
    // Last name validation
    if (!formData.last_name.trim()) {
      errors.last_name = 'Last name is required';
    }
    
    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }
    
    // Phone validation (optional, but validate format if provided)
    if (formData.phone && !/^\+?[\d\s-()]+$/.test(formData.phone)) {
      errors.phone = 'Please enter a valid phone number';
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
      
      // Remove phone if empty
      if (!registrationData.phone) {
        delete registrationData.phone;
      }
      
      await register(registrationData);
      // Navigation will happen automatically via ProtectedRoute
      navigate('/dashboard');
    } catch (err) {
      console.error('Registration failed:', err);
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
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {/* First name field */}
          <div className="form-group">
            <label htmlFor="first_name" className="form-label">
              First Name
            </label>
            <input
              id="first_name"
              name="first_name"
              type="text"
              autoComplete="given-name"
              required
              className={`form-input ${validationErrors.first_name ? 'error' : ''}`}
              value={formData.first_name}
              onChange={handleChange}
              disabled={loading}
              placeholder="John"
            />
            {validationErrors.first_name && (
              <p className="form-error">{validationErrors.first_name}</p>
            )}
          </div>

          {/* Last name field */}
          <div className="form-group">
            <label htmlFor="last_name" className="form-label">
              Last Name
            </label>
            <input
              id="last_name"
              name="last_name"
              type="text"
              autoComplete="family-name"
              required
              className={`form-input ${validationErrors.last_name ? 'error' : ''}`}
              value={formData.last_name}
              onChange={handleChange}
              disabled={loading}
              placeholder="Smith"
            />
            {validationErrors.last_name && (
              <p className="form-error">{validationErrors.last_name}</p>
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

          {/* Phone field (optional) */}
          <div className="form-group">
            <label htmlFor="phone" className="form-label">
              Phone Number (optional)
            </label>
            <input
              id="phone"
              name="phone"
              type="tel"
              autoComplete="tel"
              className={`form-input ${validationErrors.phone ? 'error' : ''}`}
              value={formData.phone}
              onChange={handleChange}
              disabled={loading}
              placeholder="+44 20 1234 5678"
            />
            {validationErrors.phone && (
              <p className="form-error">{validationErrors.phone}</p>
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
