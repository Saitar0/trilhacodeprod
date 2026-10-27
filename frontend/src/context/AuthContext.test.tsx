import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import type { User } from "@/types";

const user: User = {
  id: "user-1",
  email: "student@example.com",
  name: "Student",
  role: "student",
  permissions: ["track.read"],
};

describe("AuthContext", () => {
  beforeEach(() => {
    vi.spyOn(api, "get").mockResolvedValue({ data: user } as never);
  });

  it("loads the current user and checks permissions", async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    await waitFor(() => expect(result.current.user).toEqual(user));
    expect(result.current.can("track.read")).toBe(true);
    expect(result.current.can("users.manage")).toBe(false);
  });

  it("sets the signed-in user and can log out", async () => {
    vi.spyOn(api, "post").mockResolvedValue({ data: user } as never);
    const { result } = renderHook(() => useAuth(), {
      wrapper: ({ children }) => <AuthProvider>{children}</AuthProvider>,
    });

    await waitFor(() => expect(result.current.user).toEqual(user));
    await act(async () => result.current.logout());
    expect(result.current.user).toBe(false);
  });
});
