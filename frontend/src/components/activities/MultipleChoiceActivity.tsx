import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api, apiError } from "@/lib/api";
import { createOperationId } from "@/lib/operationId";
import type { ActivityAttempt, ActivityAttemptList, PublishedActivity } from "@/types";
import { AttemptStatus } from "./AttemptStatus";
import { FeedbackPanel } from "./FeedbackPanel";

type UiState = "loading" | "ready" | "starting" | "editing" | "saving" | "saved" | "submitting" | "completed" | "conflict" | "error";
type ErrorAction = "load" | "create" | "draft" | "submit" | null;

export function MultipleChoiceActivity({
  activity,
  blockId,
  trackId,
}: {
  activity: PublishedActivity;
  blockId: string;
  trackId: string;
}) {
  const queryClient = useQueryClient();
  const [attempt, setAttempt] = useState<ActivityAttempt | null>(null);
  const [activityView, setActivityView] = useState(activity);
  const [selected, setSelected] = useState<string | null>(null);
  const [attemptCount, setAttemptCount] = useState(0);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [uiState, setUiState] = useState<UiState>("loading");
  const [errorAction, setErrorAction] = useState<ErrorAction>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const createKey = useRef<string | null>(null);
  const draftKey = useRef<string | null>(null);
  const submitKey = useRef<string | null>(null);

  const loadAttempts = useCallback(async () => {
    setUiState("loading");
    setErrorMessage("");
    try {
      const response = await api.get<ActivityAttemptList>(`/activities/${blockId}/attempts`);
      const pendingAttempt = response.data.items.find((item) => item.state === "draft" || item.state === "submitted");
      const view = pendingAttempt?.activity || activity;
      setActivityView(view);
      const current = response.data.items.filter((item) => item.published_version_id === view.published_version_id);
      setAttemptCount(current.filter((item) => item.state === "submitted" || item.state === "evaluated").length);
      const latest = current.find((item) => item.state === "draft" || item.state === "submitted") || current[0] || null;
      setAttempt(latest);
      setSelected(latest?.response?.selected_option_id || null);
      setHasUnsavedChanges(false);
      setUiState(latest?.state === "evaluated" ? "completed" : latest ? "saved" : "ready");
      setErrorAction(null);
    } catch (error) {
      setUiState("error");
      setErrorAction("load");
      setErrorMessage(apiError(error));
    }
  }, [activity, blockId]);

  useEffect(() => {
    void loadAttempts();
  }, [loadAttempts]);

  const setError = (action: Exclude<ErrorAction, null>, error: unknown) => {
    setUiState("error");
    setErrorAction(action);
    setErrorMessage(apiError(error));
  };

  const startAttempt = async () => {
    if (!createKey.current) createKey.current = createOperationId();
    setUiState("starting");
    setErrorMessage("");
    try {
      const response = await api.post<ActivityAttempt>(
        `/activities/${blockId}/attempts`,
        { published_version_id: activityView.published_version_id },
        { headers: { "Idempotency-Key": createKey.current } },
      );
      createKey.current = null;
      setAttempt(response.data);
      setSelected(null);
      setHasUnsavedChanges(false);
      setUiState("editing");
      setErrorAction(null);
    } catch (error) {
      setError("create", error);
    }
  };

  const chooseOption = (optionId: string) => {
    if (uiState === "saving" || uiState === "submitting" || (uiState === "error" && errorAction === "submit")
      || !attempt || attempt.state !== "draft") return;
    setSelected(optionId);
    setHasUnsavedChanges(true);
    draftKey.current = null;
    submitKey.current = null;
    setUiState("editing");
    setErrorAction(null);
    setErrorMessage("");
  };

  const saveDraft = async () => {
    if (!attempt || attempt.state !== "draft") return;
    if (!draftKey.current) draftKey.current = createOperationId();
    setUiState("saving");
    setErrorMessage("");
    try {
      const response = await api.put<ActivityAttempt>(
        `/activities/${blockId}/attempts/${attempt.id}/draft`,
        { selected_option_id: selected, expected_revision: attempt.revision },
        { headers: { "Idempotency-Key": draftKey.current } },
      );
      draftKey.current = null;
      setAttempt(response.data);
      setSelected(response.data.response?.selected_option_id || null);
      setHasUnsavedChanges(false);
      setUiState("saved");
      setErrorAction(null);
    } catch (error) {
      if ((error as { response?: { status?: number } })?.response?.status === 409) {
        setUiState("conflict");
        setErrorAction(null);
        setErrorMessage(apiError(error));
      } else {
        setError("draft", error);
      }
    }
  };

  const submitAnswer = async () => {
    if (!attempt || attempt.state !== "draft" || !selected) return;
    if (!submitKey.current) submitKey.current = createOperationId();
    setUiState("submitting");
    setErrorMessage("");
    try {
      const response = await api.post<ActivityAttempt>(
        `/activities/${blockId}/attempts/${attempt.id}/submit`,
        { selected_option_id: selected, expected_revision: attempt.revision },
        { headers: { "Idempotency-Key": submitKey.current } },
      );
      submitKey.current = null;
      setAttempt(response.data);
      if (response.data.published_version_id === activityView.published_version_id) {
        setAttemptCount((count) => Math.max(count, response.data.attempt_number));
      }
      setSelected(response.data.response?.selected_option_id || null);
      setHasUnsavedChanges(false);
      setUiState(response.data.state === "evaluated" ? "completed" : "saved");
      setErrorAction(null);
      await queryClient.invalidateQueries({ queryKey: ["progress", trackId] });
      await queryClient.invalidateQueries({ queryKey: ["node"] });
    } catch (error) {
      if ((error as { response?: { status?: number } })?.response?.status === 409) {
        setUiState("conflict");
        setErrorAction(null);
        setErrorMessage(apiError(error));
      } else {
        setError("submit", error);
      }
    }
  };

  const reloadAttempt = async () => {
    if (attempt) {
      setUiState("loading");
      try {
        const response = await api.get<ActivityAttempt>(`/activities/${blockId}/attempts/${attempt.id}`);
        setAttempt(response.data);
        setSelected(response.data.response?.selected_option_id || null);
        setHasUnsavedChanges(false);
        setUiState(response.data.state === "evaluated" ? "completed" : "saved");
        setErrorAction(null);
        setErrorMessage("");
      } catch (error) {
        setError("load", error);
      }
      return;
    }
    await loadAttempts();
  };

  const retry = () => {
    if (errorAction === "load") return void (attempt ? reloadAttempt() : loadAttempts());
    if (errorAction === "create") return void startAttempt();
    if (errorAction === "draft") return void saveDraft();
    if (errorAction === "submit") return void submitAnswer();
  };

  const remainingAttempts = attemptCount < activityView.max_attempts;
  const canStart = !attempt || attempt.state === "evaluated";
  const canEdit = attempt?.state === "draft";

  return (
    <section className="space-y-4" aria-busy={uiState === "loading" || uiState === "starting" || uiState === "saving" || uiState === "submitting"}>
      <AttemptStatus state={uiState} message={uiState === "error" ? errorMessage : uiState === "conflict" ? (errorMessage || undefined) : undefined} />

      {uiState === "loading" && <p className="text-sm text-slate-400">Buscando seu rascunho e suas tentativas.</p>}

      {canEdit && attempt && (
        <div className="space-y-4">
          <fieldset className="space-y-3" disabled={uiState === "saving" || uiState === "submitting" || (uiState === "error" && errorAction === "submit")}>
            <legend className="mb-2 font-medium leading-relaxed text-slate-100">{activityView.prompt}</legend>
            {activityView.options.map((option) => (
              <label key={option.id} className="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-700 bg-slate-950/50 p-3 text-sm text-slate-200 hover:border-slate-500">
                <input
                  type="radio"
                  name={`activity-${blockId}`}
                  value={option.id}
                  checked={selected === option.id}
                  onChange={() => chooseOption(option.id)}
                  className="mt-0.5 h-4 w-4 accent-emerald-500"
                  data-testid={`activity-option-${option.id}`}
                />
                <span>{option.label}</span>
              </label>
            ))}
          </fieldset>
          {activityView.published_version_id !== activity.published_version_id && (
            <p className="text-sm text-amber-100">Esta tentativa foi iniciada em uma versão anterior e será avaliada pelos critérios daquela versão.</p>
          )}
          <p className="text-xs text-slate-400">Tentativa {attempt.attempt_number} de {activityView.max_attempts} · sua resposta é avaliada no servidor.</p>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => void saveDraft()} disabled={uiState === "saving" || uiState === "submitting" || !hasUnsavedChanges}
              className="rounded-md border border-slate-600 px-4 py-2 text-sm font-medium text-slate-100 disabled:cursor-not-allowed disabled:opacity-50">
              {uiState === "error" && errorAction === "draft" ? "Tentar salvar novamente" : "Salvar rascunho"}
            </button>
            <button type="button" onClick={() => void submitAnswer()} disabled={!selected || uiState === "saving" || uiState === "submitting"}
              className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50">
              {uiState === "error" && errorAction === "submit" ? "Tentar enviar novamente" : "Enviar resposta"}
            </button>
          </div>
        </div>
      )}

      {attempt?.state === "evaluated" && <FeedbackPanel attempt={attempt} />}

      {uiState === "conflict" && attempt && (
        <button type="button" onClick={() => void reloadAttempt()} className="rounded-md border border-amber-400/50 px-4 py-2 text-sm text-amber-100">
          Recarregar rascunho do servidor
        </button>
      )}

      {canStart && remainingAttempts && uiState !== "loading" && uiState !== "error" && uiState !== "conflict" && (
        <button type="button" onClick={() => void startAttempt()} disabled={uiState === "starting" || uiState === "saving" || uiState === "submitting"}
          className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50">
          {uiState === "completed" ? "Iniciar nova tentativa" : "Iniciar atividade"}
        </button>
      )}

      {attempt && attempt.state === "submitted" && (
        <button type="button" onClick={() => void reloadAttempt()} className="rounded-md border border-slate-600 px-4 py-2 text-sm text-slate-100">
          Consultar resultado enviado
        </button>
      )}

      {attemptCount >= activityView.max_attempts && attempt?.state === "evaluated" && (
        <p className="text-sm text-slate-400">O limite de tentativas desta versão foi atingido.</p>
      )}

      {uiState === "error" && (
        <div className="space-y-2">
          <p className="text-sm text-amber-200">{errorMessage || "Sua resposta local foi preservada. Verifique a conexão e tente novamente."}</p>
          <button type="button" onClick={retry} className="rounded-md border border-amber-400/50 px-4 py-2 text-sm text-amber-100">
            Tentar novamente
          </button>
        </div>
      )}
    </section>
  );
}
