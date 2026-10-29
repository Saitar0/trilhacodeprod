import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { ContentBlock } from "@/types";
import { ExerciseSubmission } from "./ExerciseSubmission";
import { ExerciseBlock } from "./BlockRendererParts";

vi.mock("@/hooks/useStudy", () => ({
  useMySubmissions: () => ({ data: [], isLoading: false }),
}));

const block: ContentBlock = {
  id: "exercise-1", node_id: "node-1", type: "exercise_open", title: "Prática",
  data: { prompt: "Explique o conceito", instructions: "Use suas palavras." }, status: "published", order: 0,
};

function renderExercise() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const result = render(
    <QueryClientProvider client={client}><ExerciseSubmission block={block} /></QueryClientProvider>,
  );
  return { ...result, client };
}

describe("ExerciseSubmission", () => {
  afterEach(() => vi.restoreAllMocks());

  it("renders the public instructions", () => {
    render(<ExerciseBlock block={block} />);
    expect(screen.getByText("Use suas palavras.")).toBeInTheDocument();
  });

  it("reuses the same idempotency key after a retry", async () => {
    const post = vi.spyOn(api, "post")
      .mockRejectedValueOnce(new Error("temporary network failure"))
      .mockResolvedValueOnce({ data: { id: "submission-1", status: "submitted" } } as never);
    const { client } = renderExercise();

    fireEvent.change(screen.getByTestId("exercise-answer-exercise-1"), {
      target: { value: "Uma resposta do aluno." },
    });
    fireEvent.click(screen.getByTestId("exercise-submit-exercise-1"));
    await waitFor(() => expect(post).toHaveBeenCalledTimes(1));
    fireEvent.click(screen.getByTestId("exercise-submit-exercise-1"));
    await waitFor(() => expect(post).toHaveBeenCalledTimes(2));

    const firstKey = post.mock.calls[0][2]?.headers?.["Idempotency-Key"];
    const retryKey = post.mock.calls[1][2]?.headers?.["Idempotency-Key"];
    expect(firstKey).toBeTruthy();
    expect(retryKey).toBe(firstKey);
    client.clear();
  });
});
