import React from "react";
import { cn } from "@/lib/utils";

export const SUBMISSION_META: Record<string, { label: string; cls: string }> = {
  not_started: { label: "Não iniciado", cls: "border-slate-700 text-slate-400" },
  draft: { label: "Rascunho", cls: "border-slate-600 bg-slate-800/60 text-slate-200" },
  submitted: { label: "Enviado", cls: "border-sky-500/40 bg-sky-500/10 text-sky-200" },
  in_review: { label: "Em correção", cls: "border-amber-500/40 bg-amber-500/10 text-amber-200" },
  graded: { label: "Corrigido", cls: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200" },
  returned: { label: "Devolvido para ajuste", cls: "border-violet-500/40 bg-violet-500/10 text-violet-200" },
};

export const RESULT_META: Record<string, { label: string; cls: string }> = {
  approved: { label: "Aprovado", cls: "text-emerald-300" },
  rejected: { label: "Reprovado", cls: "text-rose-300" },
  returned: { label: "Devolvido", cls: "text-violet-300" },
};

export function SubmissionBadge({ status, testId }: { status: string; testId?: string }) {
  const m = SUBMISSION_META[status] || SUBMISSION_META.not_started;
  return (
    <span data-testid={testId || `submission-status-${status}`} className={cn("inline-flex rounded-full border px-2.5 py-0.5 text-[11px] font-medium", m.cls)}>
      {m.label}
    </span>
  );
}
