import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { ActivityAttempt, ActivityAttemptList, PublishedActivity } from "@/types";
import { MultipleChoiceActivity } from "./MultipleChoiceActivity";

const activity: PublishedActivity = {
  activity_id: "block-1",
  activity_schema_version: 1,
  published_version_id: "published-1",
  activity_revision: 1,
  prompt: "Qual alternativa?",
  options: [{ id: "a", label: "Alternativa A" }, { id: "b", label: "Alternativa B" }],
  completion_policy: "responded",
  max_attempts: 2,
  evaluator_version: "multiple-choice.v1",
};

function makeAttempt(overrides: Partial<ActivityAttempt> = {}): ActivityAttempt {
  return {
    id: "attempt-1",
    user_id: "student-1",
    track_id: "track-1",
    node_id: "node-1",
    activity_id: "block-1",
    published_version_id: "published-1",
    activity_revision: 1,
    attempt_number: 1,
    state: "draft",
    response: null,
    revision: 0,
    result: null,
    feedback: null,
    projection_status: "complete",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    activity,
    ...overrides,
  };
}

function renderActivity() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MultipleChoiceActivity activity={activity} blockId="block-1" trackId="track-1" />
    </QueryClientProvider>,
  );
}

describe("MultipleChoiceActivity", () => {
  beforeEach(() => {
    vi.spyOn(api, "get").mockResolvedValue({ data: { items: [], limit: 20, skip: 0, total: 0 } satisfies ActivityAttemptList } as never);
  });
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("starts, saves a draft, submits it, and shows only server feedback", async () => {
    const started = makeAttempt();
    const saved = makeAttempt({ response: { selected_option_id: "b" }, revision: 1 });
    const evaluated = makeAttempt({
      state: "evaluated",
      response: { selected_option_id: "b" },
      revision: 2,
      result: { is_correct: true, score: 100, evaluator_version: "multiple-choice.v1" },
      feedback: "Resposta correta.",
      attempt_number: 1,
    });
    vi.spyOn(api, "post")
      .mockResolvedValueOnce({ data: started } as never)
      .mockResolvedValueOnce({ data: evaluated } as never);
    vi.spyOn(api, "put").mockResolvedValue({ data: saved } as never);

    renderActivity();
    await screen.findByText("Atividade pronta para iniciar.");
    fireEvent.click(screen.getByRole("button", { name: "Iniciar atividade" }));
    fireEvent.click(await screen.findByRole("radio", { name: "Alternativa B" }));
    fireEvent.click(screen.getByRole("button", { name: "Salvar rascunho" }));
    await screen.findByText("Rascunho salvo no servidor.");
    fireEvent.click(screen.getByRole("button", { name: "Enviar resposta" }));
    expect(await screen.findByRole("heading", { name: "Resposta correta." })).toBeInTheDocument();
    expect(screen.queryByText("Resposta incorreta.")).not.toBeInTheDocument();
  });

  it("preserves the local selection when submission fails", async () => {
    vi.spyOn(api, "post")
      .mockResolvedValueOnce({ data: makeAttempt() } as never)
      .mockRejectedValueOnce(new Error("network unavailable"));
    renderActivity();
    fireEvent.click(await screen.findByRole("button", { name: "Iniciar atividade" }));
    const option = await screen.findByRole("radio", { name: "Alternativa A" });
    fireEvent.click(option);
    fireEvent.click(screen.getByRole("button", { name: "Enviar resposta" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("network unavailable");
    expect(option).toBeChecked();
  });

  it("reports a version conflict and reloads the server draft only after an explicit action", async () => {
    const attempt = makeAttempt();
    const get = vi.spyOn(api, "get").mockResolvedValueOnce({ data: { items: [attempt], limit: 20, skip: 0 } } as never);
    vi.spyOn(api, "put").mockRejectedValue({ response: { status: 409, data: { error: { message: "Conflito de revisão" } } } });
    renderActivity();
    await screen.findByRole("radio", { name: "Alternativa A" });
    fireEvent.click(screen.getByRole("radio", { name: "Alternativa B" }));
    fireEvent.click(screen.getByRole("button", { name: "Salvar rascunho" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Conflito de revisão");
    get.mockResolvedValueOnce({ data: makeAttempt({ response: { selected_option_id: "a" }, revision: 1 }) } as never);
    fireEvent.click(screen.getByRole("button", { name: "Recarregar rascunho do servidor" }));
    await waitFor(() => expect(screen.getByRole("radio", { name: "Alternativa A" })).toBeChecked());
    expect(screen.getByRole("radio", { name: "Alternativa B" })).not.toBeChecked();
  });

  it("resumes a persisted draft after the component is mounted again", async () => {
    vi.spyOn(api, "get").mockResolvedValueOnce({
      data: {
        items: [makeAttempt({ response: { selected_option_id: "a" }, revision: 1 })],
        limit: 20,
        skip: 0,
        total: 1,
      } satisfies ActivityAttemptList,
    } as never);
    renderActivity();
    expect(await screen.findByRole("radio", { name: "Alternativa A" })).toBeChecked();
    expect(screen.getByText("Tentativa 1 de 2 · sua resposta é avaliada no servidor.")).toBeInTheDocument();
  });
});
