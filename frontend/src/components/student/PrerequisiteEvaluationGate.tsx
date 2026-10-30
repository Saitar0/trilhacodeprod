import { RefreshCw } from "lucide-react";

export function requiresPrerequisiteEvaluationGate(
  enforced: boolean,
  staff: boolean,
  loading: boolean,
  failed: boolean,
  hasEvaluation: boolean,
): boolean {
  return enforced && !staff && (loading || failed || !hasEvaluation);
}

export function PrerequisiteEvaluationGate({
  enforced,
  staff,
  loading,
  failed,
  hasEvaluation,
  onRetry,
}: {
  enforced: boolean;
  staff: boolean;
  loading: boolean;
  failed: boolean;
  hasEvaluation: boolean;
  onRetry: () => void;
}) {
  if (!requiresPrerequisiteEvaluationGate(enforced, staff, loading, failed, hasEvaluation)) return null;
  return (
    <main className="mx-auto max-w-xl p-8" data-testid="prerequisite-evaluation-unavailable">
      <div role="alert" className="space-y-3 rounded-xl border border-amber-500/30 bg-amber-500/5 p-5 text-amber-100">
        <h1 className="font-semibold">Não foi possível verificar os pré-requisitos</h1>
        <p className="text-sm text-amber-100/80">
          O conteúdo permanece protegido até o servidor confirmar quais etapas foram concluídas.
        </p>
        <button type="button" onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-md border border-amber-500/40 px-3 py-2 text-sm hover:bg-amber-500/10">
          <RefreshCw className="h-4 w-4" />Tentar novamente
        </button>
      </div>
    </main>
  );
}
