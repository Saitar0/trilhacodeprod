import { describe, expect, it } from "vitest";
import { apiError } from "./api";

describe("apiError", () => {
  it("uses the application error envelope message", () => {
    const error = {
      message: "Request failed with status code 400",
      response: { data: { error: { code: "bad_request", message: "A resposta está vazia" } } },
    };

    expect(apiError(error)).toBe("A resposta está vazia");
  });

  it("keeps support for FastAPI detail strings", () => {
    expect(apiError({ response: { data: { detail: "Permissão insuficiente" } } }))
      .toBe("Permissão insuficiente");
  });
});
