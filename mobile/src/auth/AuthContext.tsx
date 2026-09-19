import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api, clearToken, loadToken, saveToken } from "../api/client";
import type { User } from "../types/api";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string | null) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const stored = await loadToken();
      if (stored) {
        try {
          const me = await api.me(stored);
          setToken(stored);
          setUser(me);
        } catch {
          await clearToken();
        }
      }
      setReady(true);
    })();
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      ready,
      login: async (email, password) => {
        const res = await api.login(email, password);
        await saveToken(res.access_token);
        const me = await api.me(res.access_token);
        setToken(res.access_token);
        setUser(me);
      },
      register: async (email, password, name) => {
        await api.register(email, password, name);
        const res = await api.login(email, password);
        await saveToken(res.access_token);
        const me = await api.me(res.access_token);
        setToken(res.access_token);
        setUser(me);
      },
      logout: async () => {
        await clearToken();
        setToken(null);
        setUser(null);
      },
    }),
    [user, token, ready],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
