import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { User } from "@/types";

type AuthState = User | null | false;

interface AuthCtx {
  user: AuthState;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string) => Promise<User>;
  logout: () => Promise<void>;
  setUser: (u: User) => void;
  can: (perm: string) => boolean;
}

const AuthContext = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<AuthState>(null);

  useEffect(() => {
    api.get<User>("/auth/me").then((r) => setUserState(r.data)).catch(() => setUserState(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<User>("/auth/login", { email, password });
    setUserState(data);
    return data;
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    const { data } = await api.post<User>("/auth/register", { name, email, password });
    setUserState(data);
    return data;
  }, []);

  const logout = useCallback(async () => {
    await api.post("/auth/logout").catch(() => undefined);
    setUserState(false);
  }, []);

  const can = useCallback((perm: string) => !!user && user.permissions.includes(perm), [user]);

  return (
    <AuthContext.Provider value={{ user, login, register, logout, setUser: setUserState, can }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth fora do AuthProvider");
  return ctx;
}
