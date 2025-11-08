import axios from 'axios';

// Base API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Create axios instance with default configuration
 */
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor to add authentication token to all requests
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle common error scenarios
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear local storage and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// Authentication API
// ============================================================================

/**
 * Register a new user account
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User's email address
 * @param {string} userData.password - User's password
 * @param {string} userData.first_name - User's first name
 * @param {string} userData.last_name - User's last name
 * @param {string} [userData.phone] - User's phone number (optional)
 * @returns {Promise<Object>} Response with user data and token
 */
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};

/**
 * Login with email and password
 * @param {string} email - User's email address
 * @param {string} password - User's password
 * @returns {Promise<Object>} Response with access token
 */
export const login = async (email, password) => {
  // FastAPI OAuth2PasswordRequestForm expects form data
  const formData = new URLSearchParams();
  formData.append('username', email); // OAuth2 uses 'username' field
  formData.append('password', password);

  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

/**
 * Get current authenticated user information
 * @returns {Promise<Object>} Current user data
 */
export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// ============================================================================
// Giver Profile API
// ============================================================================

/**
 * Get the current user's giver profile
 * @returns {Promise<Object>} Giver profile data
 */
export const getMyGiverProfile = async () => {
  const response = await api.get('/givers/me');
  return response.data;
};

/**
 * Update the current user's giver profile
 * @param {Object} profileData - Profile data to update
 * @param {string} [profileData.first_name] - First name
 * @param {string} [profileData.last_name] - Last name
 * @param {string} [profileData.email] - Email address
 * @param {string} [profileData.phone] - Phone number
 * @param {string} [profileData.address_line1] - Address line 1
 * @param {string} [profileData.address_line2] - Address line 2
 * @param {string} [profileData.city] - City
 * @param {string} [profileData.state] - State/Province
 * @param {string} [profileData.postal_code] - Postal code
 * @param {string} [profileData.country] - Country
 * @returns {Promise<Object>} Updated giver profile
 */
export const updateMyGiverProfile = async (profileData) => {
  const response = await api.put('/givers/me', profileData);
  return response.data;
};

/**
 * Get a giver profile by ID
 * @param {number} giverId - Giver profile ID
 * @returns {Promise<Object>} Giver profile data
 */
export const getGiverProfile = async (giverId) => {
  const response = await api.get(`/givers/${giverId}`);
  return response.data;
};

/**
 * Get donation history for current user
 * @param {number} [skip=0] - Number of records to skip for pagination
 * @param {number} [limit=20] - Maximum number of records to return
 * @returns {Promise<Array>} List of donations
 */
export const getMyDonations = async (skip = 0, limit = 20) => {
  const response = await api.get(`/givers/me/donations?skip=${skip}&limit=${limit}`);
  return response.data;
};

// ============================================================================
// Campaign API
// ============================================================================

/**
 * Get all campaigns with optional filtering
 * @param {Object} params - Query parameters
 * @param {number} [params.skip=0] - Number of records to skip
 * @param {number} [params.limit=20] - Maximum number of records to return
 * @param {string} [params.status] - Filter by campaign status
 * @param {string} [params.campaign_type] - Filter by campaign type
 * @returns {Promise<Array>} List of campaigns
 */
export const getCampaigns = async (params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const response = await api.get(`/campaigns?${queryString}`);
  return response.data;
};

/**
 * Get a single campaign by ID
 * @param {number} campaignId - Campaign ID
 * @returns {Promise<Object>} Campaign data
 */
export const getCampaign = async (campaignId) => {
  const response = await api.get(`/campaigns/${campaignId}`);
  return response.data;
};

/**
 * Create a new campaign
 * @param {Object} campaignData - Campaign data
 * @returns {Promise<Object>} Created campaign
 */
export const createCampaign = async (campaignData) => {
  const response = await api.post('/campaigns', campaignData);
  return response.data;
};

/**
 * Update a campaign
 * @param {number} campaignId - Campaign ID
 * @param {Object} campaignData - Updated campaign data
 * @returns {Promise<Object>} Updated campaign
 */
export const updateCampaign = async (campaignId, campaignData) => {
  const response = await api.put(`/campaigns/${campaignId}`, campaignData);
  return response.data;
};

/**
 * Delete a campaign
 * @param {number} campaignId - Campaign ID
 * @returns {Promise<void>}
 */
export const deleteCampaign = async (campaignId) => {
  await api.delete(`/campaigns/${campaignId}`);
};

/**
 * Get donations for a specific campaign
 * @param {number} campaignId - Campaign ID
 * @param {number} [skip=0] - Number of records to skip
 * @param {number} [limit=20] - Maximum number of records to return
 * @returns {Promise<Array>} List of donations
 */
export const getCampaignDonations = async (campaignId, skip = 0, limit = 20) => {
  const response = await api.get(`/campaigns/${campaignId}/donations?skip=${skip}&limit=${limit}`);
  return response.data;
};

// ============================================================================
// Donation API
// ============================================================================

/**
 * Create a new donation
 * @param {Object} donationData - Donation data
 * @param {number} donationData.campaign_id - Campaign ID
 * @param {number} donationData.amount - Donation amount
 * @param {string} [donationData.message] - Optional message
 * @param {boolean} [donationData.is_anonymous] - Whether donation is anonymous
 * @returns {Promise<Object>} Created donation
 */
export const createDonation = async (donationData) => {
  const response = await api.post('/donations', donationData);
  return response.data;
};

/**
 * Get a single donation by ID
 * @param {number} donationId - Donation ID
 * @returns {Promise<Object>} Donation data
 */
export const getDonation = async (donationId) => {
  const response = await api.get(`/donations/${donationId}`);
  return response.data;
};

/**
 * Complete a donation (mark as paid)
 * @param {number} donationId - Donation ID
 * @param {Object} paymentData - Payment confirmation data
 * @param {string} [paymentData.payment_intent_id] - Stripe payment intent ID
 * @returns {Promise<Object>} Updated donation
 */
export const completeDonation = async (donationId, paymentData) => {
  const response = await api.post(`/donations/${donationId}/complete`, paymentData);
  return response.data;
};

/**
 * Cancel a donation
 * @param {number} donationId - Donation ID
 * @returns {Promise<Object>} Updated donation
 */
export const cancelDonation = async (donationId) => {
  const response = await api.post(`/donations/${donationId}/cancel`);
  return response.data;
};

export default api;
