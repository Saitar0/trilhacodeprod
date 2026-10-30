import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Markdown } from "@/components/common/Markdown";
import {
  PublicQuiz,
  QuizAnswer,
  QuizApiError,
  QuizAttemptResult,
  QuizHistory,
  QuizRecovery,
  QuizReview,
  quizApi,
} from "@/lib/quizApi";

interface PendingIntent {
  version_id: string;
  idempotency_key: string;
  answers: QuizAnswer[];
}

const storageKey = (quizId: string, userScope: string) =>
  "trilhacode:quiz-intent:" + encodeURIComponent(userScope) + ":" + encodeURIComponent(quizId);

function isPendingIntent(value: unknown): value is PendingIntent {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<PendingIntent>;
  return typeof candidate.version_id === "string"
    && typeof candidate.idempotency_key === "string"
    && Array.isArray(candidate.answers)
    && candidate.answers.every((answer) => (
      !!answer
      && typeof answer.question_id === "string"
      && typeof answer.option_id === "string"
    ));
}

function readPendingIntent(quizId: string, userScope: string): PendingIntent | null {
  const key = storageKey(quizId, userScope);
  try {
    const value: unknown = JSON.parse(localStorage.getItem(key) || "null");
    if (isPendingIntent(value)) return value;
  } catch { /* Continue to the legacy, tab-scoped storage below. */ }
  try {
    const value: unknown = JSON.parse(sessionStorage.getItem(key) || "null");
    if (!isPendingIntent(value)) return null;
    // Preserve pending submissions created by the earlier sessionStorage implementation.
    if (savePendingIntent(quizId, userScope, value)) sessionStorage.removeItem(key);
    return value;
  } catch {
    return null;
  }
}

function savePendingIntent(quizId: string, userScope: string, intent: PendingIntent): boolean {
  try {
    localStorage.setItem(storageKey(quizId, userScope), JSON.stringify(intent));
    try { sessionStorage.removeItem(storageKey(quizId, userScope)); } catch { /* Legacy cleanup is best effort. */ }
    return true;
  } catch {
    return false;
  }
}

function clearPendingIntent(quizId: string, userScope: string, idempotencyKey?: string) {
  try {
    const current = readPendingIntent(quizId, userScope);
    if (!idempotencyKey || current?.idempotency_key === idempotencyKey) {
      localStorage.removeItem(storageKey(quizId, userScope));
      sessionStorage.removeItem(storageKey(quizId, userScope));
    }
  } catch {
    // A stale intent only causes an idempotent replay; it cannot spend another attempt.
  }
}

function newIdempotencyKey(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2) + "-" + Math.random().toString(36).slice(2);
}

function userMessage(error: unknown): string {
  if (error instanceof QuizApiError) return error.message;
  return "Não foi possível concluir a solicitação. Tente novamente.";
}

function retryDelay(error: unknown): number {
  if (error instanceof QuizApiError && error.status === 429) {
    return Math.max(1000, error.retryAfterMs ?? 60_000);
  }
  return 0;
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + "%";
}

function formatDate(value: string): string {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("pt-BR");
}

function QuizAlert({ children }: { children: ReactNode }) {
  return (
    <div role="alert" className="relative w-full rounded-lg border border-rose-500/40 bg-rose-500/5 px-4 py-3 text-sm text-rose-200">
      <AlertCircle className="absolute left-4 top-4 h-4 w-4" />
      <div className="pl-7">{children}</div>
    </div>
  );
}

export function QuizUnavailable() {
  return (
    <div role="status" aria-live="polite" data-testid="quiz-unavailable"
      className="rounded-lg border border-amber-500/30 bg-amber-500/5 px-4 py-3 text-sm text-amber-100">
      Este quiz está temporariamente indisponível. A avaliação segura não está habilitada neste ambiente;
      nenhuma resposta será corrigida ou registrada. Os demais conteúdos deste tópico continuam disponíveis.
    </div>
  );
}

function asAnswers(values: Record<string, string>, quiz: PublicQuiz): QuizAnswer[] {
  return [...quiz.questions]
    .sort((left, right) => left.order - right.order)
    .flatMap((question) => values[question.question_id]
      ? [{ question_id: question.question_id, option_id: values[question.question_id] }]
      : []);
}

export function QuizApiSession({ quizId, userScope = "anonymous", onAuthoritativeResult }: {
  quizId: string;
  userScope?: string;
  onAuthoritativeResult?: () => void;
}) {
  const [quiz, setQuiz] = useState<PublicQuiz | null>(null);
  const [history, setHistory] = useState<QuizHistory | null>(null);
  const [review, setReview] = useState<QuizReview | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizAttemptResult | null>(null);
  const [recoveredFrom, setRecoveredFrom] = useState<"intent" | "latest" | null>(null);
  const [recovery, setRecovery] = useState<QuizRecovery | null>(null);
  const [recoveryError, setRecoveryError] = useState<string | null>(null);
  const [recoveryRequested, setRecoveryRequested] = useState(false);
  const [recovering, setRecovering] = useState(false);
  const [pending, setPending] = useState<PendingIntent | null>(null);
  const [staleIntent, setStaleIntent] = useState<PendingIntent | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitErrorStatus, setSubmitErrorStatus] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [retryAtByAction, setRetryAtByAction] = useState<Record<string, number | null>>({});
  const [clock, setClock] = useState(Date.now());
  const [reloadKey, setReloadKey] = useState(0);
  const [reviewRetryKey, setReviewRetryKey] = useState(0);
  const submittingRef = useRef(false);

  const applyRecoveredAttempt = useCallback((attempt: QuizAttemptResult, source: "intent" | "latest") => {
    setResult(attempt);
    setRecoveredFrom(source);
    setQuiz((current) => !current || current.version_id !== attempt.version_id ? current : {
      ...current,
      attempts_used: attempt.attempts_used,
      attempts_remaining: attempt.attempts_remaining,
      passed: current.passed || attempt.passed,
      best_score_percent: attempt.best_score_percent,
      review_available: attempt.review_available,
    });
    onAuthoritativeResult?.();
  }, [onAuthoritativeResult]);

  const retrySecondsFor = (action: string) => {
    const retryAt = retryAtByAction[action];
    return retryAt === null || retryAt === undefined ? 0 : Math.max(0, Math.ceil((retryAt - clock) / 1000));
  };
  const retrySeconds = retrySecondsFor("submit");
  const loadRetrySeconds = retrySecondsFor("load");
  const historyRetrySeconds = retrySecondsFor("history");
  const reviewRetrySeconds = retrySecondsFor("review");
  const scheduleRetry = useCallback((action: string, error: unknown) => {
    const delay = retryDelay(error);
    if (delay > 0) setRetryAtByAction((current) => ({ ...current, [action]: Date.now() + delay }));
  }, []);
  const clearRetry = useCallback((action: string) => {
    setRetryAtByAction((current) => ({ ...current, [action]: null }));
  }, []);

  useEffect(() => {
    if (!Object.values(retryAtByAction).some((value) => value !== null && value !== undefined)) return undefined;
    const timer = window.setInterval(() => setClock(Date.now()), 250);
    return () => window.clearInterval(timer);
  }, [retryAtByAction]);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setLoadError(null);
    setHistoryError(null);
    setReviewError(null);
    setSubmitError(null);
    setSubmitErrorStatus(null);
    setResult(null);
    setRecoveredFrom(null);
    setRecovery(null);
    setRecoveryError(null);
    setRecoveryRequested(false);
    setReview(null);

    quizApi.getPublic(quizId).then((loaded) => {
      if (!active) return;
      setQuiz(loaded);
      const saved = readPendingIntent(quizId, userScope);
      if (saved && saved.version_id === loaded.version_id) {
        setPending(saved);
        setAnswers(Object.fromEntries(saved.answers.map((answer) => [answer.question_id, answer.option_id])));
        setSubmitError("Um envio anterior não recebeu confirmação. Reenvie para consultar o mesmo resultado sem consumir outra tentativa.");
      } else if (saved) {
        setPending(null);
        setAnswers({});
        setStaleIntent(saved);
      } else {
        setPending(null);
        setAnswers({});
        setStaleIntent(null);
      }
      return quizApi.recover(
        quizId,
        saved?.version_id ?? loaded.version_id,
        saved?.idempotency_key,
      ).then((recovered) => {
        if (!active) return;
        setRecovery(recovered);
        if (recovered.state === "confirmed" && recovered.attempt && saved) {
          clearPendingIntent(quizId, userScope, saved.idempotency_key);
          setPending(null);
          setStaleIntent(null);
          setSubmitError(null);
          setSubmitErrorStatus(null);
          setRecoveryRequested(true);
          applyRecoveredAttempt(recovered.attempt, "intent");
        } else if (!saved && recovered.state === "latest_confirmed" && recovered.attempt) {
          setRecoveryRequested(true);
          applyRecoveredAttempt(recovered.attempt, "latest");
        } else if (saved && recovered.state === "unknown") {
          setRecoveryRequested(true);
          setRecoveryError("O servidor ainda não confirmou essa intenção. Ela pode estar em processamento ou não ter sido registrada; nenhuma nova tentativa foi iniciada.");
        }
      }).catch((error: unknown) => {
        if (!active) return;
        setRecoveryError(userMessage(error));
      });
    }).catch((error: unknown) => {
      if (!active) return;
      setLoadError(userMessage(error));
      scheduleRetry("load", error);
    }).finally(() => {
      if (active) setLoading(false);
    });

    quizApi.getHistory(quizId).then((loaded) => {
      if (active) {
        setHistory(loaded);
        setHistoryError(null);
      }
    }).catch((error: unknown) => {
      if (!active) return;
      setHistoryError(userMessage(error));
      scheduleRetry("history", error);
    });

    return () => { active = false; };
  }, [applyRecoveredAttempt, quizId, reloadKey, scheduleRetry, userScope]);

  const reviewAllowed = !!(quiz?.review_available || result?.review_available);
  const reviewVersion = result?.version_id || quiz?.version_id;

  const loadReview = useCallback(async () => {
    if (!quiz || !reviewAllowed || !reviewVersion) return;
    setReviewError(null);
    try {
      const loaded = await quizApi.getReview(quiz.quiz_id, reviewVersion);
      setReview(loaded);
      clearRetry("review");
    } catch (error) {
      setReviewError(userMessage(error));
      scheduleRetry("review", error);
    }
  }, [clearRetry, quiz, reviewAllowed, reviewVersion, scheduleRetry]);

  useEffect(() => {
    if (reviewAllowed && !review) void loadReview();
  }, [loadReview, review, reviewAllowed, reviewRetryKey]);

  const sortedQuestions = useMemo(
    () => [...(quiz?.questions || [])].sort((left, right) => left.order - right.order),
    [quiz],
  );

  const retryLoad = () => {
    if (loadRetrySeconds > 0) return;
    clearRetry("load");
    setReloadKey((value) => value + 1);
  };

  const startNextAttempt = () => {
    setAnswers({});
    setResult(null);
    setSubmitError(null);
    setSubmitErrorStatus(null);
  };

  const editAfterValidationError = () => {
    if (!pending) return;
    clearPendingIntent(quizId, userScope, pending.idempotency_key);
    setPending(null);
    setSubmitError(null);
    setSubmitErrorStatus(null);
  };

  const retryHistory = async () => {
    if (historyRetrySeconds > 0) return;
    try {
      setHistory(await quizApi.getHistory(quizId));
      setHistoryError(null);
      clearRetry("history");
    } catch (error) {
      setHistoryError(userMessage(error));
      scheduleRetry("history", error);
    }
  };

  const recoverLatest = async () => {
    if (!quiz || recovering) return;
    setRecovering(true);
    setRecoveryRequested(true);
    setRecoveryError(null);
    try {
      const recovered = await quizApi.recover(quiz.quiz_id, quiz.version_id);
      setRecovery(recovered);
      if (recovered.state === "latest_confirmed" && recovered.attempt) {
        applyRecoveredAttempt(recovered.attempt, "latest");
      } else {
        setRecoveryError("Nenhuma tentativa concluída foi encontrada para correlacionar. Um envio anterior ainda pode estar em processamento; esta consulta não criou nem consumiu uma tentativa.");
      }
    } catch (error) {
      setRecoveryError(userMessage(error));
    } finally {
      setRecovering(false);
    }
  };

  const sendIntent = async (intent: PendingIntent) => {
    if (!quiz || submittingRef.current || retrySeconds > 0) return;
    submittingRef.current = true;
    setSubmitting(true);
    setSubmitError(null);
    setSubmitErrorStatus(null);
    clearRetry("submit");
    try {
      const saved = await quizApi.submit(quiz.quiz_id, intent.version_id, intent.answers, intent.idempotency_key);
      clearPendingIntent(quizId, userScope, intent.idempotency_key);
      setPending(null);
      setStaleIntent(null);
      setResult(saved);
      setRecoveredFrom(null);
      setQuiz((current) => !current || current.version_id !== saved.version_id ? current : {
        ...current,
        attempts_used: saved.attempts_used,
        attempts_remaining: saved.attempts_remaining,
        passed: current.passed || saved.passed,
        best_score_percent: saved.best_score_percent,
        review_available: saved.review_available,
      });
      onAuthoritativeResult?.();
      setHistoryError(null);
      void quizApi.getHistory(quizId).then((loaded) => {
        setHistory(loaded);
        setHistoryError(null);
      }).catch((error: unknown) => {
        setHistoryError(userMessage(error));
        scheduleRetry("history", error);
      });
    } catch (error) {
      setSubmitError(userMessage(error));
      const status = error instanceof QuizApiError ? error.status : null;
      setSubmitErrorStatus(status);
      scheduleRetry("submit", error);
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!quiz || staleIntent || submittingRef.current || retrySeconds > 0) return;

    // Recheck durable storage immediately before minting a key. A reload or a
    // second mounted reader must never turn an unknown result into a new try.
    const existing = pending || readPendingIntent(quizId, userScope);
    if (quiz.attempts_remaining <= 0 && !existing) return;
    if (existing) {
      if (existing.version_id !== quiz.version_id) {
        setPending(null);
        setStaleIntent(existing);
        return;
      }
      setPending(existing);
      await sendIntent(existing);
      return;
    }

    const intent: PendingIntent = {
      version_id: quiz.version_id,
      idempotency_key: newIdempotencyKey(),
      answers: asAnswers(answers, quiz),
    };
    if (!savePendingIntent(quizId, userScope, intent)) {
      setSubmitError("Não foi possível guardar esta tentativa com segurança neste navegador. Ative o armazenamento local e tente novamente; nenhuma resposta foi enviada.");
      setSubmitErrorStatus(null);
      return;
    }
    setPending(intent);
    await sendIntent(intent);
  };

  const retryStaleIntent = async () => {
    if (!staleIntent || submittingRef.current || retrySeconds > 0) return;
    setSubmitError(null);
    setSubmitErrorStatus(null);
    await sendIntent(staleIntent);
  };

  if (loading) {
    return <p role="status" className="text-sm text-slate-400">Carregando quiz…</p>;
  }

  if (loadError || !quiz) {
    return (
      <div className="space-y-3">
        <QuizAlert>{loadError || "Quiz indisponível."}</QuizAlert>
        <Button type="button" variant="outline" size="sm" onClick={retryLoad} disabled={loadRetrySeconds > 0}>
          <RefreshCw />{loadRetrySeconds > 0 ? "Tente novamente em " + loadRetrySeconds + " s" : "Carregar quiz novamente"}
        </Button>
      </div>
    );
  }

  const allowSubmit = quiz.attempts_remaining > 0 && !staleIntent && !submitting;
  const canRetrySameIntent = !!pending && (
    submitErrorStatus === null
    || submitErrorStatus === 401
    || submitErrorStatus === 409
    || submitErrorStatus === 429
    || submitErrorStatus >= 500
  );

  return (
    <div className="space-y-5" data-testid={"quiz-api-session-" + quizId}>
      <div className="space-y-1">
        <h2 className="text-lg font-semibold text-slate-100">{quiz.title}</h2>
        <p className="text-sm text-slate-400">
          {quiz.attempts_remaining} {quiz.attempts_remaining === 1 ? "tentativa restante" : "tentativas restantes"}
          {quiz.best_score_percent !== null && " · melhor nota: " + formatPercent(quiz.best_score_percent)}
        </p>
        {quiz.passed && <p className="text-sm text-emerald-300">Você já alcançou a aprovação nesta versão. Ainda pode usar as tentativas restantes.</p>}
      </div>

      {loadError && (
        <QuizAlert>{loadError}</QuizAlert>
      )}

      {staleIntent && (
        <QuizAlert>
            Há uma tentativa sem confirmação da versão {staleIntent.version_id}. Ela não será transferida para a versão atual nem substituída por uma nova automaticamente.
            <Button type="button" variant="outline" size="sm" className="mt-3" disabled={submitting || retrySeconds > 0}
              onClick={() => void retryStaleIntent()}>
              {retrySeconds > 0 ? "Aguarde " + retrySeconds + " s" : "Confirmar envio anterior"}
            </Button>
        </QuizAlert>
      )}

      {submitError && (
        <QuizAlert>
            {submitError}
            {submitErrorStatus === 409 && !staleIntent && (
              <Button type="button" variant="outline" size="sm" className="mt-3" onClick={retryLoad}>
                Atualizar dados do quiz
              </Button>
            )}
            {pending && (canRetrySameIntent || submitErrorStatus === 429) && (
              <Button type="button" variant="outline" size="sm" className="mt-3" disabled={submitting || retrySeconds > 0}
                onClick={() => void handleSubmit(new Event("submit") as unknown as FormEvent<HTMLFormElement>)}>
                {retrySeconds > 0 ? "Tente novamente em " + retrySeconds + " s" : "Reenviar esta tentativa"}
              </Button>
            )}
            {pending && (submitErrorStatus === 400 || submitErrorStatus === 422) && (
              <Button type="button" variant="outline" size="sm" className="mt-3" onClick={editAfterValidationError}>
                Revisar respostas
              </Button>
            )}
        </QuizAlert>
      )}

      {result && (
        <div role="status" data-testid="quiz-result" className={"space-y-2 rounded-lg border p-4 " + (result.passed
          ? "border-emerald-500/30 bg-emerald-500/5"
          : "border-amber-500/30 bg-amber-500/5")}>
          <p className={"flex items-center gap-2 font-semibold " + (result.passed ? "text-emerald-300" : "text-amber-200")}>
            {result.passed ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
            {result.passed ? "Aprovado" : "Ainda não aprovado"} · nota {formatPercent(result.score_percent)}
          </p>
          <p className="text-sm text-slate-300">
            Tentativa {result.attempt_number} de 3 · melhor nota {formatPercent(result.best_score_percent)} ·
            {" "}{result.attempts_remaining} {result.attempts_remaining === 1 ? "tentativa restante" : "tentativas restantes"}
          </p>
          {recoveredFrom === "intent" && (
            <p className="text-sm text-slate-300">O servidor confirmou o envio anterior pela mesma chave de idempotência; nenhuma tentativa nova foi criada.</p>
          )}
          {recoveredFrom === "latest" && (
            <p className="text-sm text-slate-300">Esta é a tentativa mais recente registrada pelo servidor nesta versão. Ela não é apresentada como prova de uma intenção específica deste navegador.</p>
          )}
          {result.version_id !== quiz.version_id && (
            <p className="text-sm text-slate-400">Este resultado pertence à versão anterior. A versão atual do quiz é independente.</p>
          )}
          {!result.review_available && (
            <p className="text-sm text-slate-400">Respostas corretas e explicações serão liberadas após a terceira tentativa válida.</p>
          )}
          {result.attempts_remaining > 0 && (
            <Button type="button" variant="outline" size="sm" onClick={startNextAttempt} disabled={submitting}>
              Iniciar próxima tentativa
            </Button>
          )}
        </div>
      )}

      {!result && quiz.attempts_remaining === 0 && (
        <p className="rounded-lg border border-slate-700 bg-slate-950/40 p-3 text-sm text-slate-300">
          As três tentativas desta versão foram utilizadas.
        </p>
      )}

      {!result && quiz.attempts_remaining > 0 && (
        <form onSubmit={(event) => void handleSubmit(event)} className="space-y-5" aria-busy={submitting}>
          {sortedQuestions.map((question) => (
            <fieldset key={question.question_id} disabled={!allowSubmit || !!pending} className="space-y-3">
              <legend className="mb-3 font-medium leading-relaxed text-slate-100">
                <span className="mr-2 font-mono text-xs text-slate-500">{question.order + 1}.</span>{question.prompt}
              </legend>
              <div className="grid gap-2">
                {question.options.map((option, index) => (
                  <label key={option.option_id}
                    className={"flex cursor-pointer items-center gap-3 rounded-lg border px-4 py-3 text-sm transition-colors "
                      + (answers[question.question_id] === option.option_id
                        ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-100"
                        : "border-slate-800 bg-slate-950/40 text-slate-200 hover:border-slate-600")
                      + ((!allowSubmit || pending) ? " cursor-not-allowed opacity-70" : "")}>
                    <input
                      type="radio"
                      name={"quiz-" + quizId + "-" + question.question_id}
                      value={option.option_id}
                      checked={answers[question.question_id] === option.option_id}
                      disabled={!allowSubmit || !!pending}
                      onChange={() => setAnswers((current) => ({ ...current, [question.question_id]: option.option_id }))}
                      data-testid={"quiz-option-" + quizId + "-" + question.question_id + "-" + index}
                      className="h-4 w-4 accent-emerald-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400"
                    />
                    <span>{option.text}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
          <div className="flex flex-wrap items-center gap-3">
            <Button type="submit" disabled={!allowSubmit || !!pending || retrySeconds > 0}
              data-testid={"quiz-submit-" + quizId}>
              {submitting ? "Enviando…" : retrySeconds > 0 ? "Aguarde " + retrySeconds + " s" : pending ? "Envio pendente" : "Enviar tentativa"}
            </Button>
            {pending && !submitError && <span className="text-sm text-slate-400">Este envio está salvo neste navegador e será retomado com a mesma chave de idempotência.</span>}
          </div>
        </form>
      )}

      {reviewAllowed && (
        <section aria-labelledby={"quiz-review-title-" + quizId} className="space-y-4 border-t border-slate-800 pt-4" data-testid="quiz-review">
          <h3 id={"quiz-review-title-" + quizId} className="text-base font-semibold text-slate-100">Revisão liberada</h3>
          {reviewError && (
            <QuizAlert>{reviewError}</QuizAlert>
          )}
          {!review && <p role="status" className="text-sm text-slate-400">Carregando revisão…</p>}
          {!review && (
            <Button type="button" variant="outline" size="sm" onClick={() => {
              if (reviewRetrySeconds === 0) {
                clearRetry("review");
                setReviewRetryKey((value) => value + 1);
              }
            }} disabled={reviewRetrySeconds > 0}>
              {reviewRetrySeconds > 0 ? "Tente novamente em " + reviewRetrySeconds + " s" : "Carregar revisão"}
            </Button>
          )}
          {review && [...review.questions].sort((left, right) => left.order - right.order).map((question) => (
            <div key={question.question_id} className="space-y-3 rounded-lg border border-slate-800 bg-slate-950/40 p-4">
              <p className="font-medium text-slate-100">{question.prompt}</p>
              <ul className="space-y-2">
                {question.options.map((option) => (
                  <li key={option.option_id} className={"rounded-md border px-3 py-2 text-sm "
                    + (option.correct ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200" : "border-slate-800 text-slate-300")}>
                    {option.text}{option.correct && <span className="ml-2 text-xs font-semibold">Resposta correta</span>}
                  </li>
                ))}
              </ul>
              {question.explanation && <Markdown className="text-sm">{question.explanation}</Markdown>}
            </div>
          ))}
        </section>
      )}

      <details className="border-t border-slate-800 pt-4 text-sm" data-testid="quiz-history">
        <summary className="cursor-pointer text-slate-300">Histórico de tentativas{history ? " (" + history.total + ")" : ""}</summary>
        <div className="mt-3 space-y-2">
          <Button type="button" variant="outline" size="sm" onClick={() => void recoverLatest()} disabled={recovering}>
            {recovering ? "Consultando servidor…" : "Recuperar última tentativa no servidor"}
          </Button>
          {recoveryRequested && recoveryError && <p role="status" className="text-sm text-amber-200">{recoveryError}</p>}
          {recoveryRequested && recovery?.state === "unknown" && !recoveryError && (
            <p role="status" className="text-sm text-amber-200">O estado desta intenção é desconhecido. Ela pode ainda estar em processamento; não foi criada uma nova tentativa.</p>
          )}
        </div>
        {historyError && (
          <div className="mt-3 space-y-2">
            <p role="alert" className="text-sm text-rose-300">{historyError}</p>
            <Button type="button" variant="outline" size="sm" onClick={() => void retryHistory()} disabled={historyRetrySeconds > 0}>
              {historyRetrySeconds > 0 ? "Tente novamente em " + historyRetrySeconds + " s" : "Consultar histórico novamente"}
            </Button>
          </div>
        )}
        {history && (
          history.items.length > 0 ? (
            <ol className="mt-3 space-y-2">
              {history.items.map((item) => (
                <li key={item.attempt_id} className="flex flex-wrap justify-between gap-2 text-slate-400">
                  <span>Tentativa {item.attempt_number} · {item.passed ? "aprovada" : "não aprovada"}</span>
                  <span>{formatPercent(item.score_percent)} · {formatDate(item.submitted_at)}</span>
                </li>
              ))}
            </ol>
          ) : <p className="mt-3 text-slate-500">Nenhuma tentativa registrada.</p>
        )}
      </details>
    </div>
  );
}
