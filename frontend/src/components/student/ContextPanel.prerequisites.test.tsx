import { cleanup, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";
import { ContextPanel } from "./ContextPanel";
import { ViewModel } from "./viewModel";

function viewModel(
  status: "pending" | "satisfied",
  prerequisiteKind: "content_completed" | "quiz_passed" = "quiz_passed",
): ViewModel {
  const target = { id: "quiz-node", title: "Quiz de base", kind: "topic", children: [] };
  const dependent = { id: "locked-node", title: "Conteúdo seguinte", kind: "topic", children: [] };
  return {
    track: {
      id: "track-1", title: "Trilha", settings: { enforce_prerequisites: true },
    } as ViewModel["track"],
    tree: [],
    flat: [],
    learnables: [],
    byId: new Map([[target.id, target], [dependent.id, dependent]]) as unknown as ViewModel["byId"],
    relations: [{
      id: "relation-1", track_id: "track-1", node_id: dependent.id, target_id: target.id,
      type: "prerequisite", enforced: true, prerequisite_kind: prerequisiteKind, note: "",
    }],
    blockCounts: {},
    lastKind: "topic",
    statuses: {},
    locks: status === "pending" ? { [dependent.id]: { pending: [target.id], via: null } } : {},
    prerequisiteStates: {
      [dependent.id]: [{ target_id: target.id, prerequisite_kind: prerequisiteKind, status }],
    },
    label: () => "Tópico",
  } as ViewModel;
}

afterEach(cleanup);

describe("ContextPanel prerequisite state", () => {
  it("distinguishes an unapproved quiz from reading completion", () => {
    render(<MemoryRouter><ContextPanel vm={viewModel("pending")} nodeId="locked-node" /></MemoryRouter>);
    expect(screen.getByTestId("context-prerequisite-states")).toHaveTextContent("Conteúdo bloqueado");
    expect(screen.getByTestId("context-prerequisite-states")).toHaveTextContent("Quiz ainda não aprovado");
    expect(screen.queryByText("Leitura pendente")).not.toBeInTheDocument();
  });

  it("shows the quiz as approved only from the server-provided state", () => {
    render(<MemoryRouter><ContextPanel vm={viewModel("satisfied")} nodeId="locked-node" /></MemoryRouter>);
    expect(screen.getByTestId("context-prerequisite-states")).toHaveTextContent("Conteúdo liberado");
    expect(screen.getByTestId("context-prerequisite-states")).toHaveTextContent("Quiz aprovado");
  });

  it("labels declared reading completion separately from quiz approval", () => {
    render(
      <MemoryRouter>
        <ContextPanel vm={viewModel("pending", "content_completed")} nodeId="locked-node" />
      </MemoryRouter>,
    );
    expect(screen.getByTestId("context-prerequisite-states")).toHaveTextContent("Leitura pendente");
    expect(screen.queryByText("Quiz ainda não aprovado")).not.toBeInTheDocument();
  });
});
