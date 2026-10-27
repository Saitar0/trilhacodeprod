import type { ActivityAttempt } from "@/types";

export function FeedbackPanel({ attempt }: { attempt: ActivityAttempt }) {
  if (attempt.state !== "evaluated" || !attempt.result) return null;
  const correct = attempt.result.is_correct;
  return (
    <section
      aria-labelledby={`activity-feedback-${attempt.id}`}
      className="space-y-2 rounded-lg border border-slate-700 bg-slate-950/60 p-4"
      data-testid="activity-feedback"
      role="status"
    >
      <h3 id={`activity-feedback-${attempt.id}`} className="font-semibold text-slate-100">
        {correct ? "Resposta correta." : "Resposta incorreta."}
      </h3>
      <p className="text-sm text-slate-300">
        Tentativa {attempt.attempt_number} · {correct ? "100 pontos nesta avaliação" : "0 pontos nesta avaliação"}
      </p>
      {attempt.feedback && <p className="text-sm leading-relaxed text-slate-200">{attempt.feedback}</p>}
    </section>
  );
}
