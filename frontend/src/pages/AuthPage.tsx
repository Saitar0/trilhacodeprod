import React, { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { api, apiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Logo } from "@/components/layout/TopBar";

const HERO = "https://images.unsplash.com/photo-1547658719-da2b51169166?crop=entropy&cs=srgb&fm=jpg&q=85&w=1600";

export default function AuthPage({ mode }: { mode: "login" | "register" }) {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  if (user) return <Navigate to="/" replace />;
  const isLogin = mode === "login";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isLogin) {
        await login(form.email, form.password);
        navigate((location.state as { from?: string })?.from || "/", { replace: true });
      } else {
        await register(form.name, form.email, form.password);
        setNotice("Se o cadastro puder ser concluído, enviaremos um link de confirmação. Confira sua caixa de entrada e o spam.");
      }
    } catch (err) {
      setError(apiError(err));
    } finally {
      setLoading(false);
    }
  };
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [k]: e.target.value });

  const resend = async () => {
    setError("");
    try {
      await api.post("/auth/resend-verification", { email: form.email });
      setNotice("Se houver uma conta pendente para esse endereço, enviaremos um novo link.");
    } catch (err) {
      setError(apiError(err));
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-[1.1fr_1fr]">
      <aside className="relative hidden overflow-hidden border-r border-slate-800 lg:block">
        <img src={HERO} alt="" className="absolute inset-0 h-full w-full object-cover opacity-30" />
        <div className="absolute inset-0 bg-[#090D16]/70 grid-bg" />
        <div className="relative flex h-full flex-col justify-between p-12">
          <Logo />
          <div className="max-w-lg fade-up">
            <p className="mb-4 font-mono text-xs uppercase tracking-[0.25em] text-emerald-400">plataforma modular de estudo</p>
            <h1 className="text-4xl font-extrabold leading-tight text-slate-50 lg:text-5xl">
              Estrutura antes do conteúdo. Profundidade antes da pressa.
            </h1>
            <p className="mt-5 text-slate-400">Trilhas não-lineares, dependências pedagógicas, camadas de profundidade e progresso detalhado.</p>
          </div>
          <div className="flex gap-6 font-mono text-[11px] text-slate-500">
            <span>fases → módulos → tópicos → blocos</span>
          </div>
        </div>
      </aside>
      <main className="flex items-center justify-center px-6 py-16">
        <form onSubmit={submit} data-testid={`${mode}-form`} className="w-full max-w-sm space-y-6 fade-up">
          <div className="lg:hidden"><Logo /></div>
          <div>
            <h2 className="text-2xl font-bold text-slate-50">{isLogin ? "Entrar" : "Criar conta"}</h2>
            <p className="mt-1 text-sm text-slate-400">{isLogin ? "Retome seus estudos de onde parou." : "Comece sua trilha de estudos."}</p>
          </div>
          {!isLogin && (
            <div className="space-y-2">
              <Label htmlFor="name">Nome</Label>
              <Input id="name" data-testid="register-name-input" value={form.name} onChange={set("name")} required />
            </div>
          )}
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" data-testid={`${mode}-email-input`} value={form.email} onChange={set("email")} required />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <Input id="password" type="password" data-testid={`${mode}-password-input`} value={form.password} onChange={set("password")} minLength={isLogin ? undefined : 12} autoComplete={isLogin ? "current-password" : "new-password"} required />
          </div>
          {error && <p data-testid="auth-error" className="rounded-md border border-rose-900 bg-rose-950/40 px-3 py-2 text-sm text-rose-300">{error}</p>}
          {notice && <div role="status" className="space-y-2 rounded-md border border-emerald-900 bg-emerald-950/30 px-3 py-2 text-sm text-emerald-200"><p>{notice}</p>{!isLogin && <button type="button" onClick={resend} className="underline">Reenviar confirmação</button>}</div>}
          <Button type="submit" disabled={loading} data-testid={`${mode}-submit-button`} className="h-11 w-full rounded-full font-semibold">
            {loading ? <Loader2 className="animate-spin" /> : <>{isLogin ? "Entrar" : "Criar conta"} <ArrowRight /></>}
          </Button>
          <p className="text-sm text-slate-400">
            {isLogin ? "Ainda não tem conta? " : "Já tem conta? "}
            <Link to={isLogin ? "/cadastro" : "/login"} data-testid="auth-switch-link" className="text-emerald-400 hover:underline">
              {isLogin ? "Cadastre-se" : "Entrar"}
            </Link>
          </p>
          {isLogin && <Link to="/recuperar-senha" className="block text-sm text-emerald-400 hover:underline">Esqueci minha senha</Link>}
        </form>
      </main>
    </div>
  );
}
