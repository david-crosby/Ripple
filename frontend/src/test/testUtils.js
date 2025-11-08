import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../contexts/AuthContext';

/**
 * Custom render function that wraps components with necessary providers
 * Useful for testing components that use routing or authentication
 * 
 * @param {React.ReactElement} ui - Component to render
 * @param {Object} options - Additional render options
 * @returns {Object} Render result from @testing-library/react
 */
export const renderWithProviders = (ui, options = {}) => {
  const AllProviders = ({ children }) => (
    <BrowserRouter>
      <AuthProvider>
        {children}
      </AuthProvider>
    </BrowserRouter>
  );

  return render(ui, { wrapper: AllProviders, ...options });
};

/**
 * Mock user data for testing
 */
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  first_name: 'Test',
  last_name: 'User',
  phone: '+44 20 1234 5678',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
};

/**
 * Mock giver profile data for testing
 */
export const mockGiverProfile = {
  id: 1,
  user_id: 1,
  first_name: 'Test',
  last_name: 'User',
  email: 'test@example.com',
  phone: '+44 20 1234 5678',
  address_line1: '123 Test Street',
  address_line2: 'Flat 4',
  city: 'London',
  state: 'Greater London',
  postal_code: 'SW1A 1AA',
  country: 'United Kingdom',
  total_donated: 250.00,
  donation_count: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

/**
 * Mock donation data for testing
 */
export const mockDonations = [
  {
    id: 1,
    campaign_id: 1,
    giver_id: 1,
    amount: 50.00,
    message: 'Great cause!',
    is_anonymous: false,
    status: 'completed',
    payment_intent_id: 'pi_123456',
    created_at: '2024-01-10T10:00:00Z',
    completed_at: '2024-01-10T10:01:00Z',
  },
  {
    id: 2,
    campaign_id: 2,
    giver_id: 1,
    amount: 100.00,
    message: 'Happy to help',
    is_anonymous: false,
    status: 'completed',
    payment_intent_id: 'pi_789012',
    created_at: '2024-01-15T14:30:00Z',
    completed_at: '2024-01-15T14:31:00Z',
  },
];

/**
 * Mock campaign data for testing
 */
export const mockCampaign = {
  id: 1,
  organiser_id: 2,
  title: 'Test Campaign',
  description: 'This is a test campaign description',
  campaign_type: 'goal',
  status: 'active',
  goal_amount: 1000.00,
  current_amount: 250.00,
  donor_count: 5,
  start_date: '2024-01-01T00:00:00Z',
  end_date: '2024-12-31T23:59:59Z',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T00:00:00Z',
};

/**
 * Mock localStorage for testing
 * Provides in-memory storage implementation for tests
 */
export class MockLocalStorage {
  constructor() {
    this.store = {};
  }

  clear() {
    this.store = {};
  }

  getItem(key) {
    return this.store[key] || null;
  }

  setItem(key, value) {
    this.store[key] = String(value);
  }

  removeItem(key) {
    delete this.store[key];
  }

  get length() {
    return Object.keys(this.store).length;
  }

  key(index) {
    const keys = Object.keys(this.store);
    return keys[index] || null;
  }
}

/**
 * Wait for a condition to be true
 * Useful for waiting for async operations in tests
 * 
 * @param {Function} callback - Function that returns true when condition is met
 * @param {number} timeout - Maximum time to wait in milliseconds
 * @returns {Promise<void>}
 */
export const waitForCondition = (callback, timeout = 3000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const checkCondition = () => {
      if (callback()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Timeout waiting for condition'));
      } else {
        setTimeout(checkCondition, 50);
      }
    };
    
    checkCondition();
  });
};

/**
 * Create a mock axios error response
 * 
 * @param {number} status - HTTP status code
 * @param {string} message - Error message
 * @returns {Object} Mock error object
 */
export const createMockError = (status, message) => ({
  response: {
    status,
    data: {
      detail: message,
    },
  },
  message,
});
