import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { User } from "@/types";
import App from "@/App";

describe("App smoke test", () => {
  beforeEach(() => {
    vi.spyOn(api, "get").mockRejectedValue(new Error("not signed in"));
    window.history.replaceState({}, "", "/login");
  });

  it("renders the login screen within the application providers", async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: "Entrar" })).toBeInTheDocument();
    expect(screen.getByTestId("login-form")).toBeInTheDocument();
  });

  it("loads a lazy protected page for an authenticated user", async () => {
    const user: User = {
      id: "user-1",
      email: "student@example.com",
      name: "Student",
      role: "student",
      permissions: ["track.read"],
    };
    vi.spyOn(api, "get").mockResolvedValue({ data: user } as never);
    window.history.replaceState({}, "", "/perfil");

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: "Seu perfil" })).toBeInTheDocument();
    expect(screen.getByTestId("profile-name-input")).toHaveValue("Student");
  });

  it("registers without creating a session and explains email confirmation", async () => {
    vi.spyOn(api, "post").mockResolvedValue({ data: { message: "If eligible, check your inbox." } } as never);
    window.history.replaceState({}, "", "/cadastro");
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(<QueryClientProvider client={queryClient}><App /></QueryClientProvider>);

    fireEvent.change(await screen.findByTestId("register-name-input"), { target: { value: "New Student" } });
    fireEvent.change(screen.getByTestId("register-email-input"), { target: { value: "new@example.com" } });
    fireEvent.change(screen.getByTestId("register-password-input"), { target: { value: "long-passphrase-12" } });
    fireEvent.click(screen.getByTestId("register-submit-button"));

    expect(await screen.findByRole("status")).toHaveTextContent("link de confirmação");
    expect(api.post).toHaveBeenCalledWith("/auth/register", {
      name: "New Student", email: "new@example.com", password: "long-passphrase-12",
    });
  });

  it("requires an explicit action to consume the email token", async () => {
    vi.spyOn(api, "post").mockResolvedValue({ data: { message: "E-mail confirmado. Você já pode entrar." } } as never);
    window.history.replaceState({}, "", "/auth/confirm-email?token=sample-token");
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(<QueryClientProvider client={queryClient}><App /></QueryClientProvider>);

    expect(screen.getByRole("button", { name: "Confirmar e-mail" })).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Confirmar e-mail" }));
    expect(await screen.findByText("E-mail confirmado. Você já pode entrar.")).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith("/auth/verify-email", { token: "sample-token" });
  });
});
