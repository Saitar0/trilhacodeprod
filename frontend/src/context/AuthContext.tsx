import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { User } from "@/types";

type AuthState = User | null | false;

function isUserResponse(value: unknown): value is User {
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const candidate = value as Partial<User>;
  return typeof candidate.id === "string"
    && typeof candidate.email === "string"
    && typeof candidate.name === "string"
    && (candidate.role === "admin" || candidate.role === "editor" || candidate.role === "student")
    && Array.isArray(candidate.permissions)
    && candidate.permissions.every((permission) => typeof permission === "string");
}

interface AuthCtx {
  user: AuthState;
  login: (email: string, password: string) => Promise<User>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (u: User) => void;
  can: (perm: string) => boolean;
}

const AuthContext = createContext<AuthCtx | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<AuthState>(null);

  useEffect(() => {
    api.get<unknown>("/auth/me").then((r) => {
      if (!isUserResponse(r.data)) {
        // A SPA fallback can return index.html with HTTP 200 for a misrouted API request.
        // Never treat an incompatible response as an authenticated user.
        console.error("A API /auth/me retornou um formato inválido; sessão não aceita.");
        setUserState(false);
        return;
      }
      setUserState(r.data);
    }).catch((error: { response?: { status?: number } }) => {
      const status = error?.response?.status;
      if (status === undefined || status >= 500) {
        console.error("Não foi possível validar a sessão em /auth/me.", {
          status: status ?? "network_error",
        });
      }
      setUserState(false);
    });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await api.post<User>("/auth/login", { email, password });
    setUserState(data);
    return data;
  }, []);

  const register = useCallback(async (name: string, email: string, password: string) => {
    await api.post("/auth/register", { name, email, password });
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
