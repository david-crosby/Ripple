import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { MockLocalStorage, mockUser, createMockError } from '../test/testUtils.jsx';
import * as api from '../services/api';

// Mock the API module
vi.mock('../services/api');

// Mock localStorage
global.localStorage = new MockLocalStorage();

/**
 * Helper function to render the useAuth hook with AuthProvider
 */
const renderUseAuth = () => {
  return renderHook(() => useAuth(), {
    wrapper: AuthProvider,
  });
};

describe('AuthContext', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    // Clear all mocks
    vi.clearAllMocks();
  });

  /**
   * Test: Hook throws error when used outside provider
   */
  it('throws error when used outside AuthProvider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');
    
    consoleSpy.mockRestore();
  });

  /**
   * Test: Initial state is correct
   */
  it('provides initial auth state', async () => {
    api.getCurrentUser.mockRejectedValue(new Error('No token'));
    
    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBeNull();
  });

  /**
   * Test: Loads user from localStorage on mount
   */
  it('loads user from localStorage on mount if token exists', async () => {
    // Set up localStorage with existing token and user
    localStorage.setItem('token', 'existing-token');
    localStorage.setItem('user', JSON.stringify(mockUser));
    
    // Mock API call to validate token
    api.getCurrentUser.mockResolvedValue(mockUser);

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(api.getCurrentUser).toHaveBeenCalled();
  });

  /**
   * Test: Clears storage if token validation fails
   */
  it('clears storage if token validation fails on mount', async () => {
    // Set up localStorage with invalid token
    localStorage.setItem('token', 'invalid-token');
    localStorage.setItem('user', JSON.stringify(mockUser));
    
    // Mock API call to reject (invalid token)
    api.getCurrentUser.mockRejectedValue(createMockError(401, 'Invalid token'));

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  /**
   * Test: Successful login
   */
  it('successfully logs in user', async () => {
    api.login.mockResolvedValue({ access_token: 'new-token' });
    api.getCurrentUser.mockResolvedValue(mockUser);

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Perform login
    await act(async () => {
      await result.current.login('test@example.com', 'password123');
    });

    // Verify state updated
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.error).toBeNull();

    // Verify localStorage updated
    expect(localStorage.getItem('token')).toBe('new-token');
    expect(JSON.parse(localStorage.getItem('user'))).toEqual(mockUser);

    // Verify API calls
    expect(api.login).toHaveBeenCalledWith('test@example.com', 'password123');
    expect(api.getCurrentUser).toHaveBeenCalled();
  });

  /**
   * Test: Failed login sets error
   */
  it('sets error on failed login', async () => {
    api.login.mockRejectedValue(createMockError(401, 'Invalid credentials'));

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Attempt login
    await act(async () => {
      try {
        await result.current.login('test@example.com', 'wrongpassword');
      } catch (err) {
        // Expected to throw
      }
    });

    // Verify error is set
    expect(result.current.error).toBe('Invalid credentials');
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);

    // Verify localStorage not updated
    expect(localStorage.getItem('token')).toBeNull();
  });

  /**
   * Test: Successful registration
   */
  it('successfully registers user', async () => {
    api.register.mockResolvedValue({
      access_token: 'new-token',
      user: mockUser,
    });

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Perform registration
    const registrationData = {
      email: 'test@example.com',
      password: 'password123',
      first_name: 'Test',
      last_name: 'User',
    };

    await act(async () => {
      await result.current.register(registrationData);
    });

    // Verify state updated
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.error).toBeNull();

    // Verify localStorage updated
    expect(localStorage.getItem('token')).toBe('new-token');
    expect(JSON.parse(localStorage.getItem('user'))).toEqual(mockUser);

    // Verify API call
    expect(api.register).toHaveBeenCalledWith(registrationData);
  });

  /**
   * Test: Failed registration sets error
   */
  it('sets error on failed registration', async () => {
    api.register.mockRejectedValue(createMockError(400, 'Email already exists'));

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Attempt registration
    await act(async () => {
      try {
        await result.current.register({
          email: 'existing@example.com',
          password: 'password123',
          first_name: 'Test',
          last_name: 'User',
        });
      } catch (err) {
        // Expected to throw
      }
    });

    // Verify error is set
    expect(result.current.error).toBe('Email already exists');
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  /**
   * Test: Logout clears all data
   */
  it('clears all data on logout', async () => {
    // Set up authenticated state
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user', JSON.stringify(mockUser));
    api.getCurrentUser.mockResolvedValue(mockUser);

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
    });

    // Perform logout
    act(() => {
      result.current.logout();
    });

    // Verify state cleared
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.error).toBeNull();

    // Verify localStorage cleared
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  /**
   * Test: updateUser updates state and storage
   */
  it('updates user data in state and localStorage', async () => {
    // Set up authenticated state
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user', JSON.stringify(mockUser));
    api.getCurrentUser.mockResolvedValue(mockUser);

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
    });

    // Update user
    const updatedUser = {
      ...mockUser,
      first_name: 'Updated',
      last_name: 'Name',
    };

    act(() => {
      result.current.updateUser(updatedUser);
    });

    // Verify state updated
    expect(result.current.user).toEqual(updatedUser);

    // Verify localStorage updated
    expect(JSON.parse(localStorage.getItem('user'))).toEqual(updatedUser);
  });

  /**
   * Test: clearError clears error state
   */
  it('clears error state', async () => {
    // Cause an error
    api.login.mockRejectedValue(createMockError(401, 'Test error'));

    const { result } = renderUseAuth();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Trigger error
    await act(async () => {
      try {
        await result.current.login('test@example.com', 'wrong');
      } catch (err) {
        // Expected
      }
    });

    expect(result.current.error).toBe('Test error');

    // Clear error
    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });
});
