type AttemptStatusKind = "loading" | "ready" | "starting" | "editing" | "saving" | "saved" | "submitting" | "completed" | "conflict" | "error";

const LABELS: Record<AttemptStatusKind, string> = {
  loading: "Carregando atividade…",
  ready: "Atividade pronta para iniciar.",
  starting: "Iniciando tentativa…",
  editing: "Há alterações ainda não salvas.",
  saving: "Salvando resposta…",
  saved: "Rascunho salvo no servidor.",
  submitting: "Enviando resposta para avaliação…",
  completed: "Tentativa avaliada e salva.",
  conflict: "Este rascunho mudou em outro dispositivo.",
  error: "Não foi possível concluir a operação.",
};

export function AttemptStatus({ state, message }: { state: AttemptStatusKind; message?: string }) {
  const text = message || LABELS[state];
  return (
    <p
      role={state === "error" || state === "conflict" ? "alert" : "status"}
      aria-live={state === "error" || state === "conflict" ? "assertive" : "polite"}
      className={`text-sm ${state === "error" || state === "conflict" ? "text-amber-200" : "text-slate-400"}`}
      data-testid="activity-attempt-status"
    >
      {text}
    </p>
  );
}
