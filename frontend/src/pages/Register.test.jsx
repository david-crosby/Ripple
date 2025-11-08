import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Register from '../pages/Register';
import { renderWithProviders, createMockError, MockLocalStorage } from '../test/testUtils.jsx';
import * as api from '../services/api';

// Mock the API module
vi.mock('../services/api');

// Mock localStorage
global.localStorage = new MockLocalStorage();

describe('Register Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear all mocks
    vi.clearAllMocks();
  });

  /**
   * Test: Component renders correctly with all form elements
   */
  it('renders registration form with all required fields', () => {
    renderWithProviders(<Register />);
    
    expect(screen.getByText('Ripple')).toBeInTheDocument();
    expect(screen.getByText('Create your account')).toBeInTheDocument();
    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
  });

  /**
   * Test: Successful registration flow
   */
  it('successfully registers with valid data', async () => {
    const user = userEvent.setup();
    
    // Mock successful API response
    api.register.mockResolvedValueOnce({
      access_token: 'test-token',
      user: {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
      },
    });

    renderWithProviders(<Register />);

    // Fill in form
    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/full name/i), 'Test User');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Verify API was called with correct data
    await waitFor(() => {
      expect(api.register).toHaveBeenCalledWith({
        username: 'testuser',
        full_name: 'Test User',
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  /**
   * Test: Shows validation errors for empty required fields
   */
  it('displays validation errors for empty required fields', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Register />);

    // Try to submit empty form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
      expect(screen.getByText(/please confirm your password/i)).toBeInTheDocument();
    });

    // Verify API was not called
    expect(api.register).not.toHaveBeenCalled();
  });

  /**
   * Test: Validates email format
   */
  it('displays validation error for invalid email format', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Register />);

    // Fill in form with invalid email
    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/email address/i), 'notanemail');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Validates password length
   */
  it('displays validation error for short password', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Register />);

    // Fill in form with short password
    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'short');
    await user.type(screen.getByLabelText(/confirm password/i), 'short');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Validates password confirmation match
   */
  it('displays validation error when passwords do not match', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Register />);

    // Fill in form with mismatched passwords
    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'differentpassword');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Full name is optional
   */
  it('successfully registers without full name', async () => {
    const user = userEvent.setup();
    
    // Mock successful API response
    api.register.mockResolvedValueOnce({
      access_token: 'test-token',
      user: { id: 1, email: 'test@example.com', username: 'testuser' },
    });

    renderWithProviders(<Register />);

    // Fill in form without full name
    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Verify API was called without full_name
    await waitFor(() => {
      expect(api.register).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  /**
   * Test: Validates username length
   */
  it('displays validation error for short username', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Register />);

    // Fill in form with short username
    await user.type(screen.getByLabelText(/username/i), 'ab');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/username must be at least 3 characters/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Displays error message from API
   */
  it('displays error message when registration fails', async () => {
    const user = userEvent.setup();
    
    // Mock failed API response
    api.register.mockRejectedValueOnce(
      createMockError(400, 'Username already exists')
    );

    renderWithProviders(<Register />);

    // Fill in form
    await user.type(screen.getByLabelText(/username/i), 'existinguser');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');

    // Submit form
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(/username already exists/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Clears validation errors when user types
   */
  it('clears validation errors when user starts typing', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Register />);

    // Submit empty form to trigger validation
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Verify error appears
    await waitFor(() => {
      expect(screen.getByText(/username is required/i)).toBeInTheDocument();
    });

    // Start typing in username field
    await user.type(screen.getByLabelText(/username/i), 't');

    // Verify error is cleared
    await waitFor(() => {
      expect(screen.queryByText(/username is required/i)).not.toBeInTheDocument();
    });
  });

  /**
   * Test: Disables form during submission
   */
  it('disables form fields during registration', async () => {
    const user = userEvent.setup();
    
    // Mock a slow API response
    api.register.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ 
        access_token: 'test',
        user: { id: 1 }
      }), 100))
    );

    renderWithProviders(<Register />);

    // Fill and submit form
    await user.type(screen.getByLabelText(/username/i), 'testuser');
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/^password$/i), 'password123');
    await user.type(screen.getByLabelText(/confirm password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /create account/i }));

    // Check that button shows loading state
    expect(screen.getByRole('button', { name: /creating account/i })).toBeDisabled();
  });

  /**
   * Test: Link to login page exists
   */
  it('has a link to the login page', () => {
    renderWithProviders(<Register />);
    
    const loginLink = screen.getByRole('link', { name: /sign in/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink).toHaveAttribute('href', '/login');
  });
});
