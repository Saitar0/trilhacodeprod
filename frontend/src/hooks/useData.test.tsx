import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "@/lib/api";
import type { ProgressRecord, TrackProgress } from "@/types";
import { useSetProgress } from "./useData";

function makeRecord(status: ProgressRecord["status"], revision: number): ProgressRecord {
  return {
    node_id: "node-1", block_id: null, status, revision, attempts: 0,
    started_at: null, completed_at: null, updated_at: new Date().toISOString(), data: {},
  };
}

describe("useSetProgress", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("serializes updates and sends each expected revision from the server response", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const cache: TrackProgress = { nodes: {}, blocks: {}, state: null, locks: {} };
    client.setQueryData(["progress", "track-1"], cache);
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    let resolveFirst: ((response: unknown) => void) | undefined;
    const post = vi.spyOn(api, "post")
      .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }) as never)
      .mockResolvedValueOnce({ data: makeRecord("completed", 2) } as never);
    const { result } = renderHook(() => useSetProgress("track-1"), { wrapper });

    let first!: Promise<ProgressRecord>;
    let second!: Promise<ProgressRecord>;
    act(() => {
      first = result.current.mutateAsync({ node_id: "node-1", status: "in_progress" });
      second = result.current.mutateAsync({
        node_id: "node-1", status: "completed", attempt_id: "attempt-identifier-0001",
      });
    });
    await act(async () => { await Promise.resolve(); });
    expect(post).toHaveBeenCalledTimes(1);
    expect(post.mock.calls[0][1]).toMatchObject({ status: "in_progress", expected_revision: 0 });

    await act(async () => {
      resolveFirst?.({ data: makeRecord("in_progress", 1) });
      await Promise.all([first, second]);
    });
    expect(post).toHaveBeenCalledTimes(2);
    expect(post.mock.calls[1][1]).toMatchObject({
      status: "completed", expected_revision: 1, attempt_id: "attempt-identifier-0001",
    });
    expect(post.mock.calls[0][1]).toEqual(expect.objectContaining({ operation_id: expect.any(String) }));
    expect(post.mock.calls[1][1]).toEqual(expect.objectContaining({ operation_id: expect.any(String) }));
    const firstPayload = post.mock.calls[0][1] as { operation_id: string };
    const secondPayload = post.mock.calls[1][1] as { operation_id: string };
    expect(firstPayload.operation_id).not.toBe(secondPayload.operation_id);
    expect(client.getQueryData<TrackProgress>(["progress", "track-1"])?.nodes["node-1"]).toMatchObject({
      status: "completed", revision: 2,
    });
    client.clear();
  });
});
