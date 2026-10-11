import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const TONES: Record<string, string> = {
  sky: "bg-sky-500/10 text-sky-300 border-sky-500/30",
  emerald: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30",
  amber: "bg-amber-500/10 text-amber-300 border-amber-500/30",
  violet: "bg-violet-500/10 text-violet-300 border-violet-500/30",
  rose: "bg-rose-500/10 text-rose-300 border-rose-500/30",
  cyan: "bg-cyan-500/10 text-cyan-300 border-cyan-500/30",
  slate: "bg-slate-500/10 text-slate-300 border-slate-500/30",
};

export const DOTS: Record<string, string> = {
  sky: "bg-sky-400", emerald: "bg-emerald-400", amber: "bg-amber-400", violet: "bg-violet-400",
  rose: "bg-rose-400", cyan: "bg-cyan-400", slate: "bg-slate-400",
};

export const TONE_KEYS = Object.keys(TONES);
export const tone = (c?: string) => TONES[c || "slate"] || TONES.slate;

export const STATUS_META: Record<string, { label: string; cls: string; dot: string }> = {
  draft: { label: "Rascunho", cls: "bg-slate-800/80 text-slate-300 border-slate-700", dot: "bg-slate-400" },
  published: { label: "Publicado", cls: "bg-emerald-950/60 text-emerald-300 border-emerald-800", dot: "bg-emerald-400" },
  archived: { label: "Arquivado", cls: "bg-rose-950/60 text-rose-300 border-rose-800", dot: "bg-rose-400" },
};

export const PROGRESS_META: Record<string, string> = {
  not_started: "Não iniciado",
  in_progress: "Em andamento",
  completed: "Concluído",
};

export const ROLE_LABELS: Record<string, string> = { admin: "Admin", editor: "Editor", student: "Estudante" };

export function formatDate(iso?: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
}
