import { describe, expect, it } from "vitest";
import { isQuizApiEnabled, quizBlockMode } from "./quizFeature";

describe("quiz API feature flag", () => {
  it("fica desativada quando não há configuração", () => {
    expect(isQuizApiEnabled(undefined)).toBe(false);
    expect(isQuizApiEnabled("false")).toBe(false);
  });

  it("só ativa com o valor explícito true", () => {
    expect(isQuizApiEnabled("true")).toBe(true);
    expect(isQuizApiEnabled("1")).toBe(false);
  });
});

describe("quiz block routing", () => {
  it("marca o quiz indisponível quando a flag está ausente ou desligada", () => {
    expect(quizBlockMode("quiz", "q1", isQuizApiEnabled(undefined), "q1")).toBe("unavailable");
    expect(quizBlockMode("quiz", "q2", isQuizApiEnabled(undefined), "q1")).toBe("hidden");
    expect(quizBlockMode("quiz", "q1", isQuizApiEnabled("false"), "q1")).toBe("unavailable");
  });

  it("renderiza uma única sessão API para as questões do mesmo tópico", () => {
    expect(quizBlockMode("quiz", "q1", true, "q1")).toBe("api");
    expect(quizBlockMode("quiz", "q2", true, "q1")).toBe("hidden");
    expect(quizBlockMode("theory_text", "t1", true, "q1")).toBe("legacy");
  });
});
