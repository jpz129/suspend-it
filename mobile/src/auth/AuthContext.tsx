import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';

import { api, ApiError, type User } from '../api/client';
import { clearStoredToken, getStoredToken, setStoredToken } from './tokenStorage';

type AuthContextValue = {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string | null) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const hydrate = useCallback(async () => {
    try {
      const stored = await getStoredToken();
      if (!stored) {
        setUser(null);
        setToken(null);
        return;
      }
      const me = await api.me(stored);
      setToken(stored);
      setUser(me);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        await clearStoredToken();
      }
      setUser(null);
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  const login = useCallback(async (email: string, password: string) => {
    const result = await api.login({ email, password });
    await setStoredToken(result.access_token);
    const me = await api.me(result.access_token);
    setToken(result.access_token);
    setUser(me);
  }, []);

  const register = useCallback(async (email: string, password: string, name: string | null) => {
    await api.register({ email, password, name });
    await login(email, password);
  }, [login]);

  const logout = useCallback(async () => {
    await clearStoredToken();
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout }),
    [user, token, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return value;
}

export function useRequiredToken(): string {
  const { token } = useAuth();
  if (!token) {
    throw new Error('Not authenticated');
  }
  return token;
}
