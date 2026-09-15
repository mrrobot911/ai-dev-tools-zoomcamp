import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { User } from '@/types';
import { service } from '@/services';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string, invitationToken?: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const u = await service.getCurrentUser();
      setUser(u);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialize on mount
  useState(() => {
    refreshUser();
  });

  const login = useCallback(async (email: string, password: string) => {
    const { user: u } = await service.login({ email, password });
    setUser(u);
  }, []);

  const register = useCallback(
    async (email: string, password: string, name: string, invitationToken?: string) => {
      const { user: u } = await service.register({ email, password, name, invitationToken });
      setUser(u);
    },
    []
  );

  const logout = useCallback(async () => {
    await service.logout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
