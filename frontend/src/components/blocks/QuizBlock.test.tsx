import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ContentBlock } from "@/types";
import { QuizBlock } from "./BlockRendererParts";

describe("legacy QuizBlock", () => {
  it("renders legacy questions as static content without client-side grading", () => {
    const block: ContentBlock = {
      id: "legacy-quiz",
      node_id: "node-1",
      type: "quiz",
      title: "Question",
      data: {
        question: "Which option is correct?",
        options: ["A", "B"],
        correct_index: 1,
      },
      status: "published",
      order: 0,
    };
    const onProgress = vi.fn();

    render(<QuizBlock block={block} onProgress={onProgress} />);

    expect(screen.getByText("Which option is correct?")).toBeInTheDocument();
    expect(screen.getByText("A")).toBeInTheDocument();
    expect(screen.getByText("B")).toBeInTheDocument();
    expect(screen.getByText("Esta atividade ainda não tem uma avaliação publicada.")).toBeInTheDocument();
    expect(screen.queryByRole("radio")).not.toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(onProgress).not.toHaveBeenCalled();
  });
});
