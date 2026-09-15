import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { _setCurrentUserId } from '@/services/mockService';

function TestComponent() {
  const { user, login, register, logout } = useAuth();
  return (
    <div>
      <p data-testid="user">{user ? user.name : 'no user'}</p>
      <button onClick={() => login('demo@example.com', 'password')}>Login</button>
      <button onClick={() => register('new@example.com', 'pass1234', 'New User')}>
        Register
      </button>
      <button onClick={() => logout()}>Logout</button>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    _setCurrentUserId(null);
  });

  it('starts with no user', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('no user');
    });
  });

  it('logs in existing user', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('no user'));
    await userEvent.click(screen.getByText('Login'));
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('Demo User');
    });
  });

  it('registers a new user', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('no user'));
    await userEvent.click(screen.getByText('Register'));
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('New User');
    });
  });

  it('logs out', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    await waitFor(() => expect(screen.getByTestId('user').textContent).toBe('no user'));
    await userEvent.click(screen.getByText('Login'));
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('Demo User');
    });
    await userEvent.click(screen.getByText('Logout'));
    await waitFor(() => {
      expect(screen.getByTestId('user').textContent).toBe('no user');
    });
  });
});
