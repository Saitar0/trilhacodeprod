import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { PrerequisiteEvaluationGate, requiresPrerequisiteEvaluationGate } from "./PrerequisiteEvaluationGate";

describe("prerequisite evaluation gate", () => {
  it("fails closed for enforced tracks until the server returns an evaluation", () => {
    expect(requiresPrerequisiteEvaluationGate(true, false, true, false, false)).toBe(true);
    expect(requiresPrerequisiteEvaluationGate(true, false, false, true, false)).toBe(true);
    expect(requiresPrerequisiteEvaluationGate(true, false, false, false, false)).toBe(true);
    expect(requiresPrerequisiteEvaluationGate(true, false, false, false, true)).toBe(false);
  });

  it("does not gate staff or tracks without enforced prerequisites", () => {
    expect(requiresPrerequisiteEvaluationGate(false, false, true, false, false)).toBe(false);
    expect(requiresPrerequisiteEvaluationGate(true, true, true, false, false)).toBe(false);
  });

  it("presents an accessible retry when the server evaluation is unavailable", () => {
    const retry = vi.fn();
    render(<PrerequisiteEvaluationGate
      enforced staff={false} loading={false} failed hasEvaluation={false} onRetry={retry}
    />);
    expect(screen.getByRole("alert")).toHaveTextContent("O conteúdo permanece protegido");
    fireEvent.click(screen.getByRole("button", { name: "Tentar novamente" }));
    expect(retry).toHaveBeenCalledOnce();
  });
});
