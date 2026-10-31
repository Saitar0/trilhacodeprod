import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { StudyNote } from "@/types";
import {
  discardPendingNoteDrafts, flushPendingNoteSaves, navigateAfterNoteSave, useAutosaveNote,
} from "./useStudy";

const makeNote = (body: string, version: number): StudyNote => ({
  id: "note-1",
  node_id: "node-1",
  block_id: null,
  track_id: "track-1",
  body,
  version,
  updated_at: new Date().toISOString(),
});

function wrapper() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useAutosaveNote", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => {
    cleanup();
    discardPendingNoteDrafts();
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("debounces edits and only reports saved after the server response", async () => {
    let resolveSave: ((response: unknown) => void) | undefined;
    vi.spyOn(api, "put").mockImplementation(() => new Promise((resolve) => { resolveSave = resolve; }) as never);
    const { result } = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });

    act(() => result.current.setBody("new note"));
    expect(result.current.state).toBe("pending");
    await act(async () => { await vi.advanceTimersByTimeAsync(799); });
    expect(api.put).not.toHaveBeenCalled();
    await act(async () => { await vi.advanceTimersByTimeAsync(1); });
    expect(result.current.state).toBe("saving");
    expect(api.put).toHaveBeenCalledWith("/notes", {
      node_id: "node-1", block_id: null, body: "new note", expected_version: 1,
    });
    await act(async () => { resolveSave?.({ data: makeNote("new note", 2) }); });
    expect(result.current.state).toBe("saved");
  });

  it("flushes a pending debounce when the editor unmounts", () => {
    const put = vi.spyOn(api, "put").mockResolvedValue({ data: makeNote("persist on unmount", 2) } as never);
    const { result, unmount } = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    act(() => result.current.setBody("persist on unmount"));
    unmount();
    expect(put).toHaveBeenCalledWith("/notes", expect.objectContaining({ body: "persist on unmount", expected_version: 1 }));
  });

  it("recovers the in-memory draft after an unmount save failure", async () => {
    const put = vi.spyOn(api, "put")
      .mockRejectedValueOnce({ response: { status: 503 } })
      .mockResolvedValueOnce({ data: makeNote("recover after unmount", 2) } as never);
    const first = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    act(() => first.result.current.setBody("recover after unmount"));
    first.unmount();
    await act(async () => { await Promise.resolve(); await Promise.resolve(); });

    const reopened = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    expect(reopened.result.current.body).toBe("recover after unmount");
    expect(reopened.result.current.state).toBe("pending");
    await act(async () => { await flushPendingNoteSaves(); });
    expect(put).toHaveBeenCalledTimes(2);
    expect(reopened.result.current.state).toBe("saved");
    expect(reopened.result.current.body).toBe("recover after unmount");
  });

  it("does not restore a pending note draft into another user's session", () => {
    vi.spyOn(api, "put").mockRejectedValue({ response: { status: 503 } });
    const firstUser = renderHook(
      () => useAutosaveNote("node-1", null, makeNote("old", 1), true, "user-a"),
      { wrapper: wrapper() },
    );
    act(() => firstUser.result.current.setBody("private draft"));
    firstUser.unmount();

    const secondUser = renderHook(
      () => useAutosaveNote("node-1", null, makeNote("server note", 1), true, "user-b"),
      { wrapper: wrapper() },
    );
    expect(secondUser.result.current.body).toBe("server note");
    expect(secondUser.result.current.state).toBe("saved");
  });

  it("retries an orphaned draft before a later navigation", async () => {
    const put = vi.spyOn(api, "put")
      .mockRejectedValueOnce({ response: { status: 503 } })
      .mockResolvedValueOnce({ data: makeNote("orphaned edit", 2) } as never);
    const { result, unmount } = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    act(() => result.current.setBody("orphaned edit"));
    unmount();
    await act(async () => { await Promise.resolve(); await Promise.resolve(); });

    await expect(flushPendingNoteSaves()).resolves.toBe(true);
    expect(put).toHaveBeenCalledTimes(2);
    expect(put.mock.calls[1][1]).toMatchObject({ body: "orphaned edit", expected_version: 1 });
  });

  it("keeps failed edits and allows an explicit retry", async () => {
    const put = vi.spyOn(api, "put")
      .mockRejectedValueOnce({ response: { status: 503 } })
      .mockResolvedValueOnce({ data: makeNote("retry me", 2) } as never);
    const { result } = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    act(() => result.current.setBody("retry me"));
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });
    expect(result.current.state).toBe("error");
    expect(result.current.body).toBe("retry me");
    await act(async () => { await result.current.retry(); });
    expect(put).toHaveBeenCalledTimes(2);
    expect(result.current.state).toBe("saved");
    expect(result.current.body).toBe("retry me");
  });

  it("serializes writes and sends the latest text after an older response", async () => {
    let resolveFirst: ((response: unknown) => void) | undefined;
    const put = vi.spyOn(api, "put")
      .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }) as never)
      .mockImplementationOnce((_url, payload) => Promise.resolve({ data: makeNote(String((payload as { body: string }).body), 3) }) as never);
    const { result } = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    act(() => result.current.setBody("version A"));
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });
    act(() => result.current.setBody("version B"));

    await act(async () => { resolveFirst?.({ data: makeNote("version A", 2) }); });
    expect(put).toHaveBeenCalledTimes(2);
    expect(put.mock.calls[1][1]).toMatchObject({ body: "version B", expected_version: 2 });
    expect(result.current.state).toBe("saved");
    expect(result.current.body).toBe("version B");
  });

  it("preserves local text on conflict and supports explicit overwrite", async () => {
    const put = vi.spyOn(api, "put")
      .mockRejectedValueOnce({ response: { status: 409, data: { error: { details: {
        code: "note_version_conflict", current: makeNote("remote edit", 2),
      } } } } })
      .mockResolvedValueOnce({ data: makeNote("local edit", 3) } as never);
    const { result } = renderHook(() => useAutosaveNote("node-1", null, makeNote("original", 1), true), { wrapper: wrapper() });
    act(() => result.current.setBody("local edit"));
    await act(async () => { await vi.advanceTimersByTimeAsync(800); });
    expect(result.current.state).toBe("conflict");
    expect(result.current.body).toBe("local edit");
    expect(result.current.conflict?.current?.body).toBe("remote edit");
    await act(async () => { await result.current.overwriteServerVersion(); });
    expect(put.mock.calls[1][1]).toMatchObject({ body: "local edit", expected_version: 2 });
    expect(result.current.state).toBe("saved");
  });

  it("flushes a pending edit before internal navigation", async () => {
    const put = vi.spyOn(api, "put").mockResolvedValue({ data: makeNote("navigate safely", 2) } as never);
    const { result } = renderHook(() => useAutosaveNote("node-1", null, makeNote("old", 1), true), { wrapper: wrapper() });
    act(() => result.current.setBody("navigate safely"));
    const navigate = vi.fn();
    await act(async () => { await navigateAfterNoteSave(navigate, "/next"); });
    expect(put).toHaveBeenCalledTimes(1);
    expect(navigate).toHaveBeenCalledWith("/next");
    expect(result.current.state).toBe("saved");
  });
});
