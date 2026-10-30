import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import axe from "axe-core";
import { TypedActivityRenderer } from "./TypedActivityRenderer";
import { typedActivityFixtures } from "./fixtures";
import { parsePublicTypedActivity } from "./types";

function enableFeature() {
  vi.stubEnv("VITE_TYPED_ACTIVITIES_ENABLED", "true");
}

describe("TypedActivityRenderer", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllEnvs();
    localStorage.clear();
    sessionStorage.clear();
  });

  it("mantém a feature desativada quando a flag está ausente ou false", () => {
    vi.stubEnv("VITE_TYPED_ACTIVITIES_ENABLED", "");
    const { rerender } = render(<TypedActivityRenderer activity={typedActivityFixtures[0]} />);
    expect(screen.getByText(/Atividades tipadas desativadas/)).toBeInTheDocument();
    vi.stubEnv("VITE_TYPED_ACTIVITIES_ENABLED", "false");
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[1]} />);
    expect(screen.getByText(/Atividades tipadas desativadas/)).toBeInTheDocument();
    expect(screen.queryByLabelText("Sua resposta curta")).not.toBeInTheDocument();
  });

  it("renderiza os seis tipos tipados com conteúdo público", () => {
    enableFeature();
    const { rerender } = render(<TypedActivityRenderer activity={typedActivityFixtures[0]} />);
    expect(screen.getByRole("group", { name: "Alternativas" })).toBeInTheDocument();
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[1]} />);
    expect(screen.getByLabelText("Sua resposta curta")).toBeInTheDocument();
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[2]} />);
    expect(screen.getByLabelText("Sua resposta discursiva")).toBeInTheDocument();
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[3]} />);
    expect(screen.getByLabelText("Conceito A")).toBeInTheDocument();
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[4]} />);
    expect(screen.getByRole("button", { name: "Mover Etapa demonstrativa A para cima" })).toBeDisabled();
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[5]} />);
    expect(screen.getByRole("heading", { name: "Revisão formativa" })).toBeInTheDocument();
    expect(screen.getByText(/sem pontuação/)).toBeInTheDocument();
  });

  it("usa radios nativos focáveis e não corrige a seleção no cliente", () => {
    enableFeature();
    render(<TypedActivityRenderer activity={typedActivityFixtures[0]} />);
    const first = screen.getByRole("radio", { name: /Primeira alternativa/ });
    first.focus();
    fireEvent.click(first);
    expect(first).toBeChecked();
    expect(first.tabIndex).toBe(0);
    expect(document.activeElement).toBe(first);
    expect(screen.getByText(/Nenhuma correção foi realizada/)).toBeInTheDocument();
    expect(screen.queryByText(/Correto|Incorreto|Aprovado|Reprovado/)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Enviar|Submeter/ })).not.toBeInTheDocument();
  });

  it("oferece controles de ordenação acessíveis por teclado", () => {
    enableFeature();
    render(<TypedActivityRenderer activity={typedActivityFixtures[4]} />);
    const down = screen.getByRole("button", { name: "Mover Etapa demonstrativa A para baixo" });
    down.focus();
    fireEvent.click(down);
    expect(screen.getByRole("button", { name: "Mover Etapa demonstrativa A para cima" })).toBeEnabled();
    expect(screen.getByRole("list", { name: "Itens em ordenação" })).toBeInTheDocument();
  });

  it("mantém a resposta curta textual, limitada e sem comparação automática", () => {
    enableFeature();
    render(<TypedActivityRenderer activity={typedActivityFixtures[1]} />);
    const input = screen.getByLabelText("Sua resposta curta");
    fireEvent.change(input, { target: { value: "Minha resposta" } });
    expect(input).toHaveValue("Minha resposta");
    expect(input).toHaveAttribute("maxLength", "2000");
    expect(screen.getByText(/não será avaliada/)).toBeInTheDocument();
    expect(screen.queryByText(/Correto|Incorreto/)).not.toBeInTheDocument();
  });

  it("marca como inválido um campo textual vazio após interação", () => {
    enableFeature();
    render(<TypedActivityRenderer activity={typedActivityFixtures[1]} />);
    const input = screen.getByLabelText("Sua resposta curta");
    input.focus();
    fireEvent.blur(input);
    expect(input).toHaveAttribute("aria-invalid", "true");
    expect(screen.getByRole("alert")).toHaveTextContent("Informe uma resposta");
    expect(screen.getByRole("status")).toHaveTextContent("Entrada inválida");
  });
  it("mostra estados de erro, indisponibilidade e somente leitura", () => {
    enableFeature();
    const { rerender } = render(
      <TypedActivityRenderer activity={typedActivityFixtures[1]} mode="unavailable" message="Indisponível" />,
    );
    expect(screen.getByText("Indisponível")).toHaveAttribute("role", "status");
    expect(screen.getByLabelText("Sua resposta curta")).toBeDisabled();
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[1]} mode="error" message="Falha recuperável" />);
    expect(screen.getByText("Falha recuperável")).toHaveAttribute("role", "alert");
    rerender(<TypedActivityRenderer activity={typedActivityFixtures[0]} mode="read_only" />);
    expect(screen.getByRole("radio", { name: /Primeira alternativa/ })).toBeDisabled();
    expect(screen.getByText("Somente leitura.")).toBeInTheDocument();
  });

  it("rejeita tipo desconhecido, campos privados e estruturas incompletas", () => {
    expect(() => parsePublicTypedActivity({ type: "future_type" })).toThrow(/desconhecido/);
    expect(() => parsePublicTypedActivity({
      ...typedActivityFixtures[0],
      correct_index: 0,
    })).toThrow(/não permitido/);
    expect(() => parsePublicTypedActivity({
      ...typedActivityFixtures[0],
      options: [{ option_id: "one", text: "A" }],
    })).toThrow(/2 a 100/);
    expect(() => parsePublicTypedActivity({
      ...typedActivityFixtures[0],
      options: [
        { option_id: "same", text: "A" },
        { option_id: "same", text: "B" },
      ],
    })).toThrow(/duplicados/);
  });

  it("exibe texto como texto e não interpreta HTML", () => {
    enableFeature();
    const fixture = {
      ...typedActivityFixtures[0],
      prompt: "<img src=x onerror=alert(1)> texto literal",
    };
    const { container } = render(<TypedActivityRenderer activity={fixture} />);
    expect(screen.getByText("<img src=x onerror=alert(1)> texto literal")).toBeInTheDocument();
    expect(container.querySelector("img")).toBeNull();
  });

  it("não persiste respostas nem altera progresso", () => {
    enableFeature();
    const setItem = vi.spyOn(Storage.prototype, "setItem");
    render(<TypedActivityRenderer activity={typedActivityFixtures[0]} />);
    fireEvent.click(screen.getByRole("radio", { name: /Primeira alternativa/ }));
    expect(setItem).not.toHaveBeenCalled();
    expect(screen.queryByText(/progresso concluído|quiz_passed/i)).not.toBeInTheDocument();
  });

  it("não apresenta gabaritos ou explicações vindos de campos inesperados", () => {
    enableFeature();
    const privatePayload = {
      ...typedActivityFixtures[0],
      answer_key: "PRIVATE ANSWER",
      explanation: "PRIVATE EXPLANATION",
    };
    render(<TypedActivityRenderer activity={privatePayload} />);
    expect(screen.getByRole("alert")).toHaveTextContent(/campo não permitido/);
    expect(screen.queryByText("PRIVATE ANSWER")).not.toBeInTheDocument();
    expect(screen.queryByText("PRIVATE EXPLANATION")).not.toBeInTheDocument();
  });

  it("mantém layout fluido e rótulos associados aos controles", () => {
    enableFeature();
    const { container } = render(<TypedActivityRenderer activity={typedActivityFixtures[3]} />);
    const frame = container.querySelector("section");
    expect(frame).toHaveClass("w-full", "min-w-0");
    expect(screen.getByRole("heading", { name: "Associe os conceitos" })).toBeInTheDocument();
    expect(screen.getByRole("combobox", { name: "Conceito A" })).toBeInTheDocument();
  });

  it("não apresenta violações axe-core nos seis tipos", async () => {
    enableFeature();
    const { container, rerender } = render(
      <TypedActivityRenderer activity={typedActivityFixtures[0]} />,
    );
    for (const fixture of typedActivityFixtures) {
      rerender(<TypedActivityRenderer activity={fixture} />);
      const results = await axe.run(container, {
        rules: {
          "color-contrast": { enabled: false },
          "label-content-name-mismatch": { enabled: false },
        },
      });
      expect(results.violations).toEqual([]);
    }
  });
});