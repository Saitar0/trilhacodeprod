import axios, { AxiosError } from "axios";
import { api } from "@/lib/api";

export interface QuizOption {
  option_id: string;
  text: string;
}

export interface QuizQuestion {
  question_id: string;
  order: number;
  prompt: string;
  options: QuizOption[];
}

export interface PublicQuiz {
  quiz_id: string;
  version_id: string;
  curriculum_ref: string | null;
  title: string;
  questions: QuizQuestion[];
  attempts_used: number;
  attempts_remaining: number;
  passed: boolean;
  best_score_percent: number | null;
  review_available: boolean;
}

export interface QuizAnswer {
  question_id: string;
  option_id: string;
}

export interface QuizAttemptResult {
  attempt_id: string;
  quiz_id: string;
  version_id: string;
  attempt_number: number;
  total_questions: number;
  score_percent: number;
  passed: boolean;
  attempts_used: number;
  attempts_remaining: number;
  best_score_percent: number;
  review_available: boolean;
  submitted_at: string;
}

export interface QuizRecovery {
  state: "confirmed" | "latest_confirmed" | "unknown";
  quiz_id: string;
  version_id: string;
  attempts_used: number;
  attempts_remaining: number;
  review_available: boolean;
  attempt: QuizAttemptResult | null;
  may_still_be_processing: boolean;
}

export interface QuizHistory {
  items: QuizAttemptResult[];
  total: number;
  limit: number;
  skip: number;
}

export interface QuizReviewQuestion extends QuizQuestion {
  options: Array<QuizOption & { correct: boolean }>;
  explanation: string | null;
}

export interface QuizReview {
  quiz_id: string;
  version_id: string;
  title: string;
  questions: QuizReviewQuestion[];
}

export class QuizApiError extends Error {
  constructor(
    message: string,
    readonly status: number | null,
    readonly retryAfterMs: number | null,
    readonly retryable: boolean,
  ) {
    super(message);
    this.name = "QuizApiError";
  }
}

function retryAfterMs(error: AxiosError): number | null {
  const raw = error.response?.headers?.["retry-after"];
  if (raw === undefined) return null;
  const seconds = Number(raw);
  if (Number.isFinite(seconds) && seconds >= 0) return Math.ceil(seconds * 1000);
  const date = Date.parse(String(raw));
  return Number.isNaN(date) ? null : Math.max(0, date - Date.now());
}

export function toQuizApiError(error: unknown): QuizApiError {
  if (!axios.isAxiosError(error)) {
    return new QuizApiError("Não foi possível conectar. Suas respostas foram mantidas; tente novamente.", null, null, true);
  }

  const status = error.response?.status ?? null;
  if (status === 429) {
    return new QuizApiError("Muitas solicitações. Aguarde antes de tentar novamente.", status, retryAfterMs(error), true);
  }
  if (status === 401) return new QuizApiError("Sua sessão expirou. Entre novamente para continuar.", status, null, false);
  if (status === 403) return new QuizApiError("Você não tem autorização para acessar este quiz.", status, null, false);
  if (status === 404) return new QuizApiError("Este quiz ou versão não está disponível.", status, null, false);
  if (status === 409) return new QuizApiError("O quiz mudou ou esta tentativa já foi processada. Atualize os dados do quiz.", status, null, false);
  if (status === 400 || status === 422) {
    return new QuizApiError("Não foi possível validar o envio. Confira as respostas e atualize o quiz.", status, null, false);
  }
  if (status !== null && status >= 500) {
    return new QuizApiError("O serviço está temporariamente indisponível. Suas respostas foram mantidas; tente novamente.", status, null, true);
  }
  if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT" || status === null) {
    return new QuizApiError("A conexão demorou para responder. Suas respostas foram mantidas; tente novamente.", status, null, true);
  }
  return new QuizApiError("Não foi possível concluir a solicitação. Tente novamente.", status, null, false);
}

async function request<T>(operation: () => Promise<{ data: T }>): Promise<T> {
  try {
    return (await operation()).data;
  } catch (error) {
    throw toQuizApiError(error);
  }
}

const path = (quizId: string) => "/quizzes/" + encodeURIComponent(quizId);

export const quizApi = {
  getPublic: (quizId: string) =>
    request<PublicQuiz>(() => api.get(path(quizId), { timeout: 20_000 })),

  submit: (quizId: string, versionId: string, answers: QuizAnswer[], idempotencyKey: string) =>
    request<QuizAttemptResult>(() =>
      api.post(path(quizId) + "/attempts", { version_id: versionId, answers }, {
        headers: { "Idempotency-Key": idempotencyKey },
        timeout: 20_000,
      }),
    ),

  getHistory: (quizId: string) =>
    request<QuizHistory>(() => api.get(path(quizId) + "/attempts", { timeout: 20_000 })),

  recover: (quizId: string, versionId: string, idempotencyKey?: string) =>
    request<QuizRecovery>(() => api.post(path(quizId) + "/recovery", {
      version_id: versionId,
      ...(idempotencyKey ? { idempotency_key: idempotencyKey } : {}),
    }, { timeout: 20_000 })),

  getReview: (quizId: string, versionId: string) =>
    request<QuizReview>(() =>
      api.get(path(quizId) + "/versions/" + encodeURIComponent(versionId) + "/review", { timeout: 20_000 }),
    ),
};
