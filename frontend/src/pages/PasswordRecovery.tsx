import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { api, apiError } from "@/lib/api";

export default function PasswordRecovery() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError("");
    try { const response = await api.post("/auth/password-reset-request", { email }); setMessage(response.data.message); }
    catch (err) { setError(apiError(err)); }
  };

  return <main className="mx-auto max-w-md px-6 py-24"><h1 className="text-2xl font-bold">Recuperar senha</h1><p className="mt-2 text-sm text-slate-400">Informe o endereço da conta para receber instruções, se ela puder ser recuperada.</p><form onSubmit={submit} className="mt-6 space-y-4"><label className="block text-sm" htmlFor="recovery-email">E-mail</label><input id="recovery-email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2" /><button className="w-full rounded bg-emerald-500 px-4 py-2 font-semibold text-slate-950">Enviar instruções</button></form>{error && <p role="alert" className="mt-4 text-rose-300">{error}</p>}{message && <p role="status" className="mt-4 text-emerald-300">{message}</p>}<Link className="mt-6 inline-block text-emerald-400 underline" to="/login">Voltar para entrar</Link></main>;
}
