import { FormEvent, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, apiError } from "@/lib/api";

export default function PasswordReset() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError("");
    try { const response = await api.post("/auth/password-reset", { token, password }); setMessage(response.data.message); }
    catch (err) { setError(apiError(err)); }
  };

  return <main className="mx-auto max-w-md px-6 py-24"><h1 className="text-2xl font-bold">Criar nova senha</h1><form onSubmit={submit} className="mt-6 space-y-4"><label className="block text-sm" htmlFor="new-password">Nova senha</label><input id="new-password" type="password" minLength={12} maxLength={72} autoComplete="new-password" required value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2" /><button className="w-full rounded bg-emerald-500 px-4 py-2 font-semibold text-slate-950">Alterar senha</button></form>{error && <p role="alert" className="mt-4 text-rose-300">{error}</p>}{message && <p role="status" className="mt-4 text-emerald-300">{message}</p>}<Link className="mt-6 inline-block text-emerald-400 underline" to="/login">Voltar para entrar</Link></main>;
}
