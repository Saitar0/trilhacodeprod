import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { QuizApiError, quizApi } from "@/lib/quizApi";
import { QuizApiSession } from "./QuizApiSession";

vi.mock("@/lib/quizApi", () => ({
  QuizApiError: class MockQuizApiError extends Error {
    constructor(
      message: string,
      readonly status: number | null,
      readonly retryAfterMs: number | null,
      readonly retryable: boolean,
    ) {
      super(message);
    }
  },
  quizApi: {
    getPublic: vi.fn(),
    submit: vi.fn(),
    getHistory: vi.fn(),
    recover: vi.fn(),
    getReview: vi.fn(),
  },
}));

const publicQuiz = (overrides: Record<string, unknown> = {}) => ({
  quiz_id: "node-1",
  version_id: "0123456789abcdef01234567",
  curriculum_ref: "f1.q1",
  title: "Quiz de fundamentos",
  questions: [
    {
      question_id: "q1",
      order: 0,
      prompt: "Qual opção foi ensinada?",
      options: [{ option_id: "a", text: "Alternativa A" }, { option_id: "b", text: "Alternativa B" }],
    },
    {
      question_id: "q2",
      order: 1,
      prompt: "Qual é a segunda resposta?",
      options: [{ option_id: "c", text: "Alternativa C" }, { option_id: "d", text: "Alternativa D" }],
    },
  ],
  attempts_used: 0,
  attempts_remaining: 3,
  passed: false,
  best_score_percent: null,
  review_available: false,
  ...overrides,
});

const attempt = (overrides: Record<string, unknown> = {}) => ({
  attempt_id: "attempt-1",
  quiz_id: "node-1",
  version_id: "0123456789abcdef01234567",
  attempt_number: 1,
  total_questions: 2,
  score_percent: 50,
  passed: false,
  attempts_used: 1,
  attempts_remaining: 2,
  best_score_percent: 50,
  review_available: false,
  submitted_at: "2026-10-27T12:00:00Z",
  ...overrides,
});

function configureDefaults(quiz = publicQuiz()) {
  vi.mocked(quizApi.getPublic).mockResolvedValue(quiz as never);
  vi.mocked(quizApi.getHistory).mockResolvedValue({ items: [], total: 0, limit: 100, skip: 0 });
  vi.mocked(quizApi.recover).mockResolvedValue({
    state: "unknown",
    quiz_id: "node-1",
    version_id: "0123456789abcdef01234567",
    attempts_used: 0,
    attempts_remaining: 3,
    review_available: false,
    attempt: null,
    may_still_be_processing: true,
  });
  vi.mocked(quizApi.getReview).mockResolvedValue({
    quiz_id: "node-1",
    version_id: "0123456789abcdef01234567",
    title: "Quiz de fundamentos",
    questions: [],
  });
  vi.mocked(quizApi.submit).mockResolvedValue(attempt() as never);
}

async function ready(quiz = publicQuiz()) {
  configureDefaults(quiz);
  render(<QuizApiSession quizId="node-1" />);
  await screen.findByRole("heading", { name: "Quiz de fundamentos" });
}

function chooseFirstAnswer() {
  fireEvent.click(screen.getByTestId("quiz-option-node-1-q1-0"));
}

function submit() {
  fireEvent.click(screen.getByTestId("quiz-submit-node-1"));
}

describe("QuizApiSession", () => {
  afterEach(() => cleanup());

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    vi.mocked(quizApi.recover).mockResolvedValue({
      state: "unknown",
      quiz_id: "node-1",
      version_id: "0123456789abcdef01234567",
      attempts_used: 0,
      attempts_remaining: 3,
      review_available: false,
      attempt: null,
      may_still_be_processing: true,
    });
  });

  it("carrega o quiz público e renderiza perguntas e alternativas", async () => {
    await ready();
    expect(quizApi.getPublic).toHaveBeenCalledWith("node-1");
    expect(screen.getByText("Qual opção foi ensinada?")).toBeInTheDocument();
    expect(screen.getByText("Alternativa A")).toBeInTheDocument();
    expect(screen.getByText("Alternativa D")).toBeInTheDocument();
  });

  it("não mostra gabarito nem explicação antes da liberação do servidor", async () => {
    await ready();
    expect(quizApi.getReview).not.toHaveBeenCalled();
    expect(screen.queryByText("Resposta correta")).not.toBeInTheDocument();
    expect(screen.queryByText("Explicação protegida")).not.toBeInTheDocument();
  });

  it("submete respostas sem enviar nota nem aprovação do cliente", async () => {
    await ready();
    chooseFirstAnswer();
    submit();
    await screen.findByTestId("quiz-result");
    const [, , answers] = vi.mocked(quizApi.submit).mock.calls[0];
    expect(answers).toEqual([{ question_id: "q1", option_id: "a" }]);
    expect(answers).not.toHaveProperty("score");
    expect(answers).not.toHaveProperty("passed");
  });

  it("exibe aprovação e nota devolvidas pelo servidor", async () => {
    vi.mocked(quizApi.getPublic).mockResolvedValue(publicQuiz() as never);
    vi.mocked(quizApi.getHistory).mockResolvedValue({ items: [], total: 0, limit: 100, skip: 0 });
    vi.mocked(quizApi.submit).mockResolvedValue(attempt({ score_percent: 70, passed: true, best_score_percent: 70 }) as never);
    render(<QuizApiSession quizId="node-1" />);
    await screen.findByRole("heading", { name: "Quiz de fundamentos" });
    chooseFirstAnswer();
    submit();
    expect(await screen.findByText(/Aprovado · nota 70/)).toBeInTheDocument();
  });

  it("exibe reprovação sem correção local", async () => {
    await ready();
    chooseFirstAnswer();
    submit();
    expect(await screen.findByText(/Ainda não aprovado · nota 50/)).toBeInTheDocument();
    expect(screen.queryByText("Correto.")).not.toBeInTheDocument();
  });

  it("continua permitindo tentativas após aprovação e usa o melhor resultado do servidor", async () => {
    await ready();
    vi.mocked(quizApi.submit).mockResolvedValue(attempt({
      score_percent: 70,
      passed: true,
      best_score_percent: 90,
      attempts_remaining: 2,
    }) as never);
    chooseFirstAnswer();
    submit();
    await screen.findByTestId("quiz-result");
    expect(screen.getByText(/melhor nota 90/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Iniciar próxima tentativa" })).toBeEnabled();
  });

  it("representa a primeira, segunda e terceira tentativa com os valores do backend", async () => {
    const cases = [
      { attempt_number: 1, attempts_used: 1, attempts_remaining: 2 },
      { attempt_number: 2, attempts_used: 2, attempts_remaining: 1 },
      { attempt_number: 3, attempts_used: 3, attempts_remaining: 0, review_available: true },
    ];
    for (const expected of cases) {
      vi.clearAllMocks();
      localStorage.clear();
      sessionStorage.clear();
      await ready(publicQuiz({ attempts_used: expected.attempts_used - 1, attempts_remaining: 4 - expected.attempts_used }));
      vi.mocked(quizApi.submit).mockResolvedValue(attempt(expected) as never);
      chooseFirstAnswer();
      submit();
      expect(await screen.findByTestId("quiz-result")).toBeInTheDocument();
      expect(screen.getByText(new RegExp("Tentativa " + expected.attempt_number + " de 3"))).toBeInTheDocument();
      cleanup();
    }
  });

  it("bloqueia nova tentativa quando o servidor informa tentativas esgotadas", async () => {
    await ready(publicQuiz({ attempts_used: 3, attempts_remaining: 0, review_available: false }));
    expect(screen.queryByTestId("quiz-submit-node-1")).not.toBeInTheDocument();
    expect(screen.getByText("As três tentativas desta versão foram utilizadas.")).toBeInTheDocument();
  });

  it("carrega a revisão somente quando a API libera após a terceira tentativa", async () => {
    const finalAttempt = attempt({ attempt_number: 3, attempts_used: 3, attempts_remaining: 0, review_available: true });
    const review = {
      quiz_id: "node-1",
      version_id: "0123456789abcdef01234567",
      title: "Quiz de fundamentos",
      questions: [{
        question_id: "q1",
        order: 0,
        prompt: "Qual opção foi ensinada?",
        options: [
          { option_id: "a", text: "Alternativa A", correct: true },
          { option_id: "b", text: "Alternativa B", correct: false },
        ],
        explanation: "Explicação protegida.",
      }],
    };
    vi.mocked(quizApi.getPublic).mockResolvedValue(publicQuiz({ attempts_used: 2, attempts_remaining: 1 }) as never);
    vi.mocked(quizApi.getHistory).mockResolvedValue({ items: [], total: 0, limit: 100, skip: 0 });
    vi.mocked(quizApi.submit).mockResolvedValue(finalAttempt as never);
    vi.mocked(quizApi.getReview).mockResolvedValue(review as never);
    render(<QuizApiSession quizId="node-1" />);
    await screen.findByRole("heading", { name: "Quiz de fundamentos" });
    chooseFirstAnswer();
    submit();
    expect(await screen.findByText("Explicação protegida.")).toBeInTheDocument();
    expect(quizApi.getReview).toHaveBeenCalledWith("node-1", "0123456789abcdef01234567");
  });

  it("mostra o histórico retornado pela API", async () => {
    vi.mocked(quizApi.getPublic).mockResolvedValue(publicQuiz() as never);
    vi.mocked(quizApi.getHistory).mockResolvedValue({
      items: [attempt({ attempt_number: 2, score_percent: 75, passed: true }) as never],
      total: 1,
      limit: 100,
      skip: 0,
    });
    render(<QuizApiSession quizId="node-1" />);
    await screen.findByText(/Histórico de tentativas \(1\)/);
    expect(screen.getByText(/Tentativa 2 · aprovada/)).toBeInTheDocument();
  });

  it("recupera a submissão confirmada pela mesma chave sem reenviá-la", async () => {
    const storedIntent = {
      version_id: "0123456789abcdef01234567",
      idempotency_key: "intent-key-1234567890",
      answers: [{ question_id: "q1", option_id: "a" }],
    };
    localStorage.setItem("trilhacode:quiz-intent:anonymous:node-1", JSON.stringify(storedIntent));
    vi.mocked(quizApi.recover).mockResolvedValue({
      state: "confirmed",
      quiz_id: "node-1",
      version_id: storedIntent.version_id,
      attempts_used: 1,
      attempts_remaining: 2,
      review_available: false,
      attempt: attempt({ attempts_used: 1, attempts_remaining: 2 }) as never,
      may_still_be_processing: false,
    });

    render(<QuizApiSession quizId="node-1" />);

    expect(await screen.findByTestId("quiz-result")).toBeInTheDocument();
    expect(screen.getByText(/O servidor confirmou o envio anterior pela mesma chave/)).toBeInTheDocument();
    expect(quizApi.recover).toHaveBeenCalledWith("node-1", storedIntent.version_id, storedIntent.idempotency_key);
    expect(quizApi.submit).not.toHaveBeenCalled();
    expect(localStorage.getItem("trilhacode:quiz-intent:anonymous:node-1")).toBeNull();
  });

  it("recupera a última tentativa do servidor sem fingir que conhece a intenção do navegador", async () => {
    vi.mocked(quizApi.recover).mockResolvedValue({
      state: "latest_confirmed",
      quiz_id: "node-1",
      version_id: "0123456789abcdef01234567",
      attempts_used: 1,
      attempts_remaining: 2,
      review_available: false,
      attempt: attempt({ attempts_used: 1, attempts_remaining: 2 }) as never,
      may_still_be_processing: false,
    });

    render(<QuizApiSession quizId="node-1" />);

    expect(await screen.findByTestId("quiz-result")).toBeInTheDocument();
    expect(screen.getByText(/tentativa mais recente registrada pelo servidor/)).toBeInTheDocument();
    expect(quizApi.submit).not.toHaveBeenCalled();
  });

  it("mostra estado desconhecido sem criar tentativa quando o servidor ainda não localiza o envio", async () => {
    await ready();
    fireEvent.click(screen.getByRole("button", { name: "Recuperar última tentativa no servidor" }));

    expect(await screen.findByText(/Nenhuma tentativa concluída foi encontrada/)).toHaveAttribute("role", "status");
    expect(quizApi.submit).not.toHaveBeenCalled();
    expect(screen.getByTestId("quiz-submit-node-1")).toBeEnabled();
  });

  it("preserva a chave idempotente após timeout e reutiliza no retry", async () => {
    await ready();
    vi.mocked(quizApi.submit)
      .mockRejectedValueOnce(new QuizApiError("A conexão demorou para responder. Suas respostas foram mantidas; tente novamente.", null, null, true))
      .mockResolvedValueOnce(attempt({ attempts_remaining: 2 }) as never);
    chooseFirstAnswer();
    submit();
    fireEvent.click(await screen.findByRole("button", { name: "Reenviar esta tentativa" }));
    await screen.findByTestId("quiz-result");
    const calls = vi.mocked(quizApi.submit).mock.calls;
    expect(calls).toHaveLength(2);
    expect(calls[0][3]).toBe(calls[1][3]);
  });

  it("restaura respostas e a mesma chave após remontagem", async () => {
    await ready();
    vi.mocked(quizApi.submit).mockRejectedValueOnce(new QuizApiError("Não foi possível conectar. Suas respostas foram mantidas; tente novamente.", null, null, true));
    chooseFirstAnswer();
    submit();
    await screen.findByRole("button", { name: "Reenviar esta tentativa" });
    const stored = JSON.parse(localStorage.getItem("trilhacode:quiz-intent:anonymous:node-1") || "null");
    expect(stored.answers).toEqual([{ question_id: "q1", option_id: "a" }]);
    expect(Object.keys(stored).sort()).toEqual(["answers", "idempotency_key", "version_id"]);
    cleanup();
    vi.mocked(quizApi.getPublic).mockResolvedValue(publicQuiz() as never);
    vi.mocked(quizApi.getHistory).mockResolvedValue({ items: [], total: 0, limit: 100, skip: 0 });
    vi.mocked(quizApi.submit).mockResolvedValue(attempt({ attempts_remaining: 2 }) as never);
    render(<QuizApiSession quizId="node-1" />);
    await screen.findByRole("button", { name: "Reenviar esta tentativa" });
    fireEvent.click(screen.getByRole("button", { name: "Reenviar esta tentativa" }));
    await screen.findByTestId("quiz-result");
    expect(vi.mocked(quizApi.submit).mock.calls[1][3]).toBe(stored.idempotency_key);
  });

  it("impede cliques duplicados enquanto o envio está pendente", async () => {
    await ready();
    let resolveSubmission: (value: unknown) => void = () => undefined;
    vi.mocked(quizApi.submit).mockImplementation(() => new Promise((resolve) => { resolveSubmission = resolve; }) as never);
    chooseFirstAnswer();
    const button = screen.getByTestId("quiz-submit-node-1");
    fireEvent.click(button);
    fireEvent.click(button);
    expect(quizApi.submit).toHaveBeenCalledTimes(1);
    resolveSubmission(attempt({ attempts_remaining: 2 }));
    await screen.findByTestId("quiz-result");
  });

  it("respeita Retry-After e mantém a intenção bloqueada durante o limite", async () => {
    await ready();
    vi.mocked(quizApi.submit).mockRejectedValueOnce(new QuizApiError("Muitas solicitações. Aguarde antes de tentar novamente.", 429, 30_000, true));
    chooseFirstAnswer();
    submit();
    const retry = await screen.findByRole("button", { name: /Tente novamente em 30 s/ });
    expect(retry).toBeDisabled();
    expect(screen.getByText("Muitas solicitações. Aguarde antes de tentar novamente.")).toBeInTheDocument();
    expect(quizApi.submit).toHaveBeenCalledTimes(1);
  });

  it("mostra mensagem de sessão expirada sem detalhes internos", async () => {
    await ready();
    vi.mocked(quizApi.submit).mockRejectedValueOnce(new QuizApiError("Sua sessão expirou. Entre novamente para continuar.", 401, null, false));
    chooseFirstAnswer();
    submit();
    expect(await screen.findByText("Sua sessão expirou. Entre novamente para continuar.")).toBeInTheDocument();
    expect(screen.queryByText(/stack trace|internal_error/i)).not.toBeInTheDocument();
  });

  it("trata autorização negada e não tenta revelar o gabarito", async () => {
    vi.mocked(quizApi.getPublic).mockRejectedValue(new QuizApiError("Você não tem autorização para acessar este quiz.", 403, null, false));
    vi.mocked(quizApi.getHistory).mockResolvedValue({ items: [], total: 0, limit: 100, skip: 0 });
    render(<QuizApiSession quizId="node-1" />);
    expect(await screen.findByText("Você não tem autorização para acessar este quiz.")).toBeInTheDocument();
    expect(quizApi.getReview).not.toHaveBeenCalled();
  });

  it("retoma a mesma intenção antiga sem transferi-la nem apagá-la ao mudar a versão", async () => {
    sessionStorage.setItem("trilhacode:quiz-intent:anonymous:node-1", JSON.stringify({
      version_id: "old-version",
      idempotency_key: "old-idempotency-key-123",
      answers: [{ question_id: "old-q", option_id: "old-option" }],
    }));
    await ready(publicQuiz({ version_id: "new-version" }));
    expect(screen.getByText(/tentativa sem confirmação da versão old-version/)).toBeInTheDocument();
    expect(quizApi.submit).not.toHaveBeenCalled();
    expect(localStorage.getItem("trilhacode:quiz-intent:anonymous:node-1")).toContain("old-idempotency-key-123");
    vi.mocked(quizApi.submit).mockResolvedValue(attempt({ version_id: "old-version", attempts_remaining: 2 }) as never);
    fireEvent.click(screen.getByRole("button", { name: "Confirmar envio anterior" }));
    await screen.findByTestId("quiz-result");
    expect(vi.mocked(quizApi.submit).mock.calls[0]).toEqual([
      "node-1", "old-version", [{ question_id: "old-q", option_id: "old-option" }], "old-idempotency-key-123",
    ]);
    expect(localStorage.getItem("trilhacode:quiz-intent:anonymous:node-1")).toBeNull();
  });

  it("não envia uma tentativa quando o navegador não consegue persistir a intenção", async () => {
    await ready();
    chooseFirstAnswer();
    const setItem = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("Quota exceeded", "QuotaExceededError");
    });
    submit();
    expect(await screen.findByRole("alert")).toHaveTextContent("nenhuma resposta foi enviada");
    expect(quizApi.submit).not.toHaveBeenCalled();
    setItem.mockRestore();
  });

  it("promove uma intenção antiga de sessionStorage para armazenamento durável", async () => {
    sessionStorage.setItem("trilhacode:quiz-intent:anonymous:node-1", JSON.stringify({
      version_id: "0123456789abcdef01234567",
      idempotency_key: "legacy-session-key-123",
      answers: [{ question_id: "q1", option_id: "a" }],
    }));
    await ready();
    expect(localStorage.getItem("trilhacode:quiz-intent:anonymous:node-1")).toContain("legacy-session-key-123");
    expect(sessionStorage.getItem("trilhacode:quiz-intent:anonymous:node-1")).toBeNull();
  });

  it("mantém a indisponibilidade como erro recuperável, sem corrigir localmente", async () => {
    vi.mocked(quizApi.getPublic).mockRejectedValue(new QuizApiError("Não foi possível conectar. Suas respostas foram mantidas; tente novamente.", null, null, true));
    vi.mocked(quizApi.getHistory).mockResolvedValue({ items: [], total: 0, limit: 100, skip: 0 });
    render(<QuizApiSession quizId="node-1" />);
    expect(await screen.findByText(/conectar/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Carregar quiz novamente" })).toBeEnabled();
  });
});
