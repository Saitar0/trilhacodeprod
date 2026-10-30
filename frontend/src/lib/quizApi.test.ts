import { afterEach, describe, expect, it, vi } from "vitest";
import axios from "axios";
import { api } from "./api";
import { quizApi, toQuizApiError } from "./quizApi";

describe("quizApi", () => {
  afterEach(() => vi.restoreAllMocks());

  it("usa o endpoint público autenticado e não solicita uma chave de resposta", async () => {
    const get = vi.spyOn(api, "get").mockResolvedValueOnce({ data: { quiz_id: "node/1" } } as never);
    await quizApi.getPublic("node/1");
    expect(get).toHaveBeenCalledWith("/quizzes/node%2F1", { timeout: 20_000 });
  });

  it("envia respostas e Idempotency-Key no formato real da API", async () => {
    const post = vi.spyOn(api, "post").mockResolvedValueOnce({ data: { attempt_id: "attempt-1" } } as never);
    const answers = [{ question_id: "q1", option_id: "b" }];
    await quizApi.submit("node-1", "0123456789abcdef01234567", answers, "intent-key-123456");
    expect(post).toHaveBeenCalledWith(
      "/quizzes/node-1/attempts",
      { version_id: "0123456789abcdef01234567", answers },
      { headers: { "Idempotency-Key": "intent-key-123456" }, timeout: 20_000 },
    );
  });

  it("consulta histórico e revisão nas rotas da Etapa 13C.1", async () => {
    const get = vi.spyOn(api, "get")
      .mockResolvedValueOnce({ data: { items: [], total: 0 } } as never)
      .mockResolvedValueOnce({ data: { questions: [] } } as never);
    await quizApi.getHistory("node-1");
    await quizApi.getReview("node-1", "0123456789abcdef01234567");
    expect(get.mock.calls.map((call) => call[0])).toEqual([
      "/quizzes/node-1/attempts",
      "/quizzes/node-1/versions/0123456789abcdef01234567/review",
    ]);
  });
});

describe("toQuizApiError", () => {
  it.each([
    [400, "Não foi possível validar"],
    [401, "Sua sessão expirou"],
    [403, "não tem autorização"],
    [404, "não está disponível"],
    [409, "mudou ou esta tentativa"],
    [422, "Não foi possível validar"],
    [500, "temporariamente indisponível"],
  ])("converte HTTP %s em mensagem sem detalhe interno", (status, expected) => {
    const error = {
      response: { status, data: { error: { message: "traceback secreto" }, headers: {} } },
      isAxiosError: true,
    };
    vi.spyOn(axios, "isAxiosError").mockReturnValue(true);
    const result = toQuizApiError(error);
    expect(result.status).toBe(status);
    expect(result.message).toContain(expected);
    expect(result.message).not.toContain("traceback");
  });

  it("respeita Retry-After em segundos para HTTP 429", () => {
    vi.spyOn(axios, "isAxiosError").mockReturnValue(true);
    const result = toQuizApiError({
      response: { status: 429, headers: { "retry-after": "7" } },
      isAxiosError: true,
    });
    expect(result.retryable).toBe(true);
    expect(result.retryAfterMs).toBe(7000);
  });

  it("converte timeout e falha de rede em erros recuperáveis", () => {
    vi.spyOn(axios, "isAxiosError").mockReturnValue(true);
    const timeout = toQuizApiError({ code: "ECONNABORTED", isAxiosError: true });
    const network = toQuizApiError({ message: "Network Error", isAxiosError: true });
    expect(timeout.retryable).toBe(true);
    expect(network.retryable).toBe(true);
    expect(network.message).not.toContain("Network Error");
  });
});
