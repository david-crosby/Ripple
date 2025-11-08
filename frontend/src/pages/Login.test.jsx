import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Login from '../pages/Login';
import { renderWithProviders, createMockError, MockLocalStorage } from '../test/testUtils';
import * as api from '../services/api';

// Mock the API module
vi.mock('../services/api');

// Mock localStorage
global.localStorage = new MockLocalStorage();

describe('Login Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear all mocks
    vi.clearAllMocks();
  });

  /**
   * Test: Component renders correctly with all form elements
   */
  it('renders login form with all required fields', () => {
    renderWithProviders(<Login />);
    
    expect(screen.getByText('Ripple')).toBeInTheDocument();
    expect(screen.getByText('Sign in to your account')).toBeInTheDocument();
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
  });

  /**
   * Test: Successful login flow
   */
  it('successfully logs in with valid credentials', async () => {
    const user = userEvent.setup();
    
    // Mock successful API responses
    api.login.mockResolvedValueOnce({ access_token: 'test-token' });
    api.getCurrentUser.mockResolvedValueOnce({
      id: 1,
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
    });

    renderWithProviders(<Login />);

    // Fill in form
    const emailInput = screen.getByLabelText(/email address/i);
    const passwordInput = screen.getByLabelText(/password/i);
    
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'password123');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);

    // Verify API was called with correct data
    await waitFor(() => {
      expect(api.login).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  /**
   * Test: Shows validation errors for empty fields
   */
  it('displays validation errors for empty fields', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Login />);

    // Try to submit empty form
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);

    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });

    // Verify API was not called
    expect(api.login).not.toHaveBeenCalled();
  });

  /**
   * Test: Shows validation error for invalid email format
   */
  it('displays validation error for invalid email format', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Login />);

    // Enter invalid email
    const emailInput = screen.getByLabelText(/email address/i);
    await user.type(emailInput, 'notanemail');

    // Submit form
    const submitButton = screen.getByRole('button', { name: /sign in/i });
    await user.click(submitButton);

    // Check for validation error
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Displays error message from API
   */
  it('displays error message when login fails', async () => {
    const user = userEvent.setup();
    
    // Mock failed API response
    api.login.mockRejectedValueOnce(
      createMockError(401, 'Invalid email or password')
    );

    renderWithProviders(<Login />);

    // Fill in form
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');

    // Submit form
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    // Check for error message
    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });

  /**
   * Test: Clears validation errors when user types
   */
  it('clears validation errors when user starts typing', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<Login />);

    // Submit empty form to trigger validation
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    // Verify error appears
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });

    // Start typing in email field
    const emailInput = screen.getByLabelText(/email address/i);
    await user.type(emailInput, 't');

    // Verify error is cleared
    await waitFor(() => {
      expect(screen.queryByText(/email is required/i)).not.toBeInTheDocument();
    });
  });

  /**
   * Test: Disables form during submission
   */
  it('disables form fields during login', async () => {
    const user = userEvent.setup();
    
    // Mock a slow API response
    api.login.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ access_token: 'test' }), 100))
    );
    api.getCurrentUser.mockResolvedValue({ id: 1, email: 'test@example.com' });

    renderWithProviders(<Login />);

    // Fill and submit form
    await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    // Check that button shows loading state
    expect(screen.getByRole('button', { name: /signing in/i })).toBeDisabled();
  });

  /**
   * Test: Link to register page exists
   */
  it('has a link to the register page', () => {
    renderWithProviders(<Login />);
    
    const registerLink = screen.getByRole('link', { name: /create one/i });
    expect(registerLink).toBeInTheDocument();
    expect(registerLink).toHaveAttribute('href', '/register');
  });
});
