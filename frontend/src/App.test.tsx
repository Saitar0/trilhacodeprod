import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
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
});
