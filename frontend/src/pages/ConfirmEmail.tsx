import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, apiError } from "@/lib/api";

export default function ConfirmEmail() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [message, setMessage] = useState("");
  const [failed, setFailed] = useState(false);
  const [loading, setLoading] = useState(false);

  const confirm = async () => {
    setLoading(true);
    setFailed(false);
    try {
      const response = await api.post("/auth/verify-email", { token });
      setMessage(response.data.message);
    } catch (error) {
      setMessage(apiError(error));
      setFailed(true);
    } finally {
      setLoading(false);
    }
  };

  return <main className="mx-auto max-w-lg px-6 py-24 text-center"><h1 className="text-2xl font-bold">Confirmação de e-mail</h1><p className="mt-4 text-slate-300">Confirme para ativar sua conta.</p>{token && !message && <button type="button" onClick={confirm} disabled={loading} className="mt-6 rounded bg-emerald-500 px-5 py-2 font-semibold text-slate-950">{loading ? "Confirmando…" : "Confirmar e-mail"}</button>}{!token && <p role="alert" className="mt-4 text-rose-300">Link inválido ou expirado.</p>}{message && <p role="status" className={failed ? "mt-4 text-rose-300" : "mt-4 text-emerald-300"}>{message}</p>}<Link className="mt-6 inline-block text-emerald-400 underline" to="/login">Ir para entrar</Link></main>;
}
