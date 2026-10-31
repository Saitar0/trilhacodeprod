import React, { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCircle2, MessageSquare, Send, Save, XCircle } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useMySubmissions } from "@/hooks/useStudy";
import { createOperationId } from "@/lib/operationId";
import { ContentBlock, Submission } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { Markdown } from "@/components/common/Markdown";
import { RESULT_META, SubmissionBadge } from "@/components/common/SubmissionBadge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

function Feedback({ sub }: { sub: Submission }) {
  const g = sub.grading;
  if (!g) return null;
  const criteria = g.criteria || [];
  return (
    <div data-testid={`submission-feedback-${sub.id}`} className="space-y-3 rounded-lg border border-slate-700 bg-slate-950/60 p-4">
      <p className={cn("flex items-center gap-2 text-sm font-semibold", RESULT_META[g.result]?.cls)}>
        <MessageSquare className="h-4 w-4" />{RESULT_META[g.result]?.label} · {g.graded_by_name} · {formatDate(g.graded_at)}
        {g.score != null && <span className="ml-auto font-mono text-xs">nota {g.score}</span>}
      </p>
      {g.feedback && <Markdown className="text-sm">{g.feedback}</Markdown>}
      {criteria.length > 0 && (
        <ul className="space-y-1.5">
          {criteria.map((c, i) => (
            <li key={i} className="flex gap-2 text-sm">
              {c.met === false ? <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-rose-400" /> : <CheckCircle2 className={cn("mt-0.5 h-4 w-4 shrink-0", c.met ? "text-emerald-400" : "text-slate-600")} />}
              <span className="text-slate-300">{c.criterion}{c.comment && <span className="text-slate-500"> — {c.comment}</span>}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AnswerInput({ block, answer, setAnswer, disabled }: {
  block: ContentBlock; answer: Submission["answer"]; setAnswer: (a: Submission["answer"]) => void; disabled: boolean;
}) {
  const options: string[] = Array.isArray(block.data.options) ? block.data.options : [];
  if (block.type === "exercise_objective" && options.length > 0) {
    return (
      <div className="grid gap-2">
        {options.map((o, i) => (
          <button key={i} disabled={disabled} data-testid={`exercise-choice-${block.id}-${i}`} onClick={() => setAnswer({ ...answer, choice: i, text: o })}
            className={cn("rounded-lg border px-4 py-2.5 text-left text-sm transition-colors disabled:opacity-60",
              answer.choice === i ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-100" : "border-slate-800 bg-slate-950/40 text-slate-300 hover:border-slate-600")}>
            <span className="mr-2 font-mono text-xs text-slate-500">{String.fromCharCode(65 + i)}</span>{o}
          </button>
        ))}
      </div>
    );
  }
  return (
    <div className="space-y-3">
      <label htmlFor={`exercise-answer-input-${block.id}`} className="sr-only">Sua resposta para {block.title || "o exercício"}</label>
      <Textarea id={`exercise-answer-input-${block.id}`} data-testid={`exercise-answer-${block.id}`} rows={5} disabled={disabled} placeholder="Escreva sua resposta (Markdown)"
        value={answer.text || ""} onChange={(e) => setAnswer({ ...answer, text: e.target.value })} />
      {block.type === "practical_challenge" && (
        <>
          <label htmlFor={`exercise-code-input-${block.id}`} className="sr-only">Código da resposta para {block.title || "o exercício"}</label>
          <Textarea id={`exercise-code-input-${block.id}`} data-testid={`exercise-code-${block.id}`} rows={8} disabled={disabled} className="font-mono text-xs" placeholder={block.data.starter_code || "Seu código"}
            value={answer.code ?? ""} onChange={(e) => setAnswer({ ...answer, code: e.target.value })} />
        </>
      )}
    </div>
  );
}

export function ExerciseSubmission({ block }: { block: ContentBlock }) {
  const qc = useQueryClient();
  const { data } = useMySubmissions(block.node_id);
  const attempts = (data || []).filter((s) => s.block_id === block.id);
  const current = attempts[0];
  const approved = current?.status === "graded" && current.grading?.result === "approved";
  const canRetry = current?.status === "graded" && !approved && block.data.allow_resubmit !== false;
  const editable = !current || ["draft", "submitted", "returned"].includes(current.status);
  const [answer, setAnswer] = useState<Submission["answer"]>({});
  const [retrying, setRetrying] = useState(false);
  const submitOperation = useRef<{ fingerprint: string; id: string } | null>(null);
  useEffect(() => { if (current && editable) setAnswer(current.answer || {}); }, [current?.id, current?.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const send = async (kind: "draft" | "submit") => {
    try {
      if (kind === "draft") await api.put("/submissions/draft", { block_id: block.id, answer });
      else {
        const fingerprint = JSON.stringify(answer);
        if (submitOperation.current?.fingerprint !== fingerprint) {
          submitOperation.current = { fingerprint, id: createOperationId() };
        }
        await api.post("/submissions/submit", { block_id: block.id, answer }, {
          headers: { "Idempotency-Key": submitOperation.current.id },
        });
        submitOperation.current = null;
      }
      qc.invalidateQueries({ queryKey: ["submissions", "mine"] });
      setRetrying(false);
      toast.success(kind === "draft" ? "Rascunho salvo" : "Resposta enviada para correção");
    } catch (e) { toast.error(apiError(e)); }
  };
  const open = editable || retrying;

  return (
    <div className="space-y-4 border-t border-slate-800 pt-4" data-testid={`exercise-submission-${block.id}`}>
      <div className="flex items-center gap-2">
        <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">sua resposta</span>
        <SubmissionBadge status={current?.status || "not_started"} testId={`exercise-status-${block.id}`} />
        {current && <span className="font-mono text-[10px] text-slate-500">tentativa {current.attempt}</span>}
      </div>
      {current?.status === "returned" && <Feedback sub={current} />}
      {open ? (
        <>
          <AnswerInput block={block} answer={answer} setAnswer={setAnswer} disabled={false} />
          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" data-testid={`exercise-save-draft-${block.id}`} onClick={() => send("draft")}><Save />Salvar rascunho</Button>
            <Button size="sm" className="rounded-full" data-testid={`exercise-submit-${block.id}`} onClick={() => send("submit")}>
              <Send />{current?.status === "submitted" ? "Atualizar envio" : "Enviar resposta"}
            </Button>
          </div>
        </>
      ) : (
        <>
          <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-4 text-sm text-slate-300">
            <Markdown>{current?.answer.text}</Markdown>
            {current?.answer.code && <pre className="mt-3 overflow-x-auto font-mono text-xs text-emerald-300">{current.answer.code}</pre>}
          </div>
          {current?.status === "in_review" && <p className="text-xs text-amber-300">Em correção por {current.reviewer_name || "equipe"} — edição bloqueada.</p>}
          {current?.status === "graded" && <Feedback sub={current} />}
          {canRetry && <Button size="sm" variant="outline" data-testid={`exercise-retry-${block.id}`} onClick={() => { setAnswer({}); setRetrying(true); }}>Nova tentativa</Button>}
        </>
      )}
      {attempts.length > 1 && (
        <details className="text-xs text-slate-500" data-testid={`exercise-attempts-${block.id}`}>
          <summary className="cursor-pointer">Histórico de tentativas ({attempts.length})</summary>
          <ol className="mt-2 space-y-1 border-l border-slate-800 pl-4">
            {attempts.map((a) => (
              <li key={a.id}>Tentativa {a.attempt} · <SubmissionBadge status={a.status} testId={`attempt-${a.id}`} /> {a.grading && <span className={RESULT_META[a.grading.result]?.cls}>{RESULT_META[a.grading.result]?.label}</span>} · {formatDate(a.submitted_at || a.updated_at)}</li>
            ))}
          </ol>
        </details>
      )}
    </div>
  );
}
