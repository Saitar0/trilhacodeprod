import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

export const api = axios.create({
  baseURL: `${process.env.REACT_APP_BACKEND_URL}/api`,
  withCredentials: true,
});

let refreshing: Promise<unknown> | null = null;

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    const url = original?.url || "";
    if (error.response?.status === 401 && original && !original._retry && !/auth\/(login|refresh|register)/.test(url)) {
      original._retry = true;
      refreshing = refreshing || api.post("/auth/refresh").finally(() => (refreshing = null));
      try {
        await refreshing;
        return api(original);
      } catch {
        /* sessão expirada */
      }
    }
    return Promise.reject(error);
  },
);

export function apiError(e: unknown): string {
  const detail = (e as AxiosError<{ detail?: unknown }>)?.response?.data?.detail;
  if (detail == null) return (e as Error)?.message || "Algo deu errado. Tente novamente.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((d) => (d && typeof d.msg === "string" ? d.msg : JSON.stringify(d))).join(" ");
  return String(detail);
}
