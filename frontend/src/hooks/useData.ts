import { useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, apiError } from "@/lib/api";
import { createOperationId } from "@/lib/operationId";
import { Meta, NodeDetail, ProgressRecord, ProgressStatus, TrackProgress, TreeResponse } from "@/types";

export function useMeta() {
  return useQuery({ queryKey: ["meta"], queryFn: () => api.get<Meta>("/meta").then((r) => r.data) });
}

export function useTaxonomy() {
  const { data } = useMeta();
  const find = (group: string, key?: string) => data?.taxonomies[group]?.find((t) => t.key === key);
  const list = (group: string) => data?.taxonomies[group] || [];
  return { meta: data, find, list };
}

export function useTree(trackId?: string) {
  return useQuery({
    queryKey: ["tree", trackId],
    enabled: !!trackId,
    queryFn: () => api.get<TreeResponse>(`/tracks/${trackId}/tree`).then((r) => r.data),
  });
}

export function useNodeDetail(nodeId?: string | null) {
  return useQuery({
    queryKey: ["node", nodeId],
    enabled: !!nodeId,
    queryFn: () => api.get<NodeDetail>(`/nodes/${nodeId}`).then((r) => r.data),
  });
}

export function useTrackProgress(trackId?: string) {
  return useQuery({
    queryKey: ["progress", trackId],
    enabled: !!trackId,
    queryFn: () => api.get<TrackProgress>(`/progress/tracks/${trackId}`).then((r) => r.data),
  });
}

export function useSetProgress(trackId?: string) {
  const qc = useQueryClient();
  const queues = useRef(new Map<string, Promise<ProgressRecord>>());
  return useMutation({
    mutationFn: (body: {
      node_id: string; status: ProgressStatus; block_id?: string; data?: Record<string, unknown>; attempt_id?: string;
    }) => {
      const operationKey = `${body.node_id}:${body.block_id || "node"}`;
      const previous = queues.current.get(operationKey);
      const task = (previous ? previous.catch(() => undefined) : Promise.resolve(undefined)).then(async () => {
        const cached = trackId ? qc.getQueryData<TrackProgress>(["progress", trackId]) : undefined;
        const current = body.block_id ? cached?.blocks[body.block_id] : cached?.nodes[body.node_id];
        const payload = {
          ...body,
          operation_id: createOperationId(),
          ...(cached ? { expected_revision: current?.revision ?? 0 } : {}),
        };
        const { data } = await api.post<ProgressRecord>("/progress", payload);
        if (cached) {
          qc.setQueryData<TrackProgress>(["progress", trackId], {
            ...cached,
            nodes: body.block_id ? cached.nodes : { ...cached.nodes, [body.node_id]: data },
            blocks: body.block_id ? { ...cached.blocks, [body.block_id]: data } : cached.blocks,
          });
        }
        return data;
      });
      let queued: Promise<ProgressRecord>;
      queued = task.finally(() => {
        if (queues.current.get(operationKey) === queued) queues.current.delete(operationKey);
      });
      queues.current.set(operationKey, queued);
      return queued;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["progress", trackId] });
      qc.invalidateQueries({ queryKey: ["overview"] });
      qc.invalidateQueries({ queryKey: ["node"] });
    },
    onError: (error) => {
      const status = (error as { response?: { status?: number } }).response?.status;
      toast.error(status === 409
        ? "O progresso mudou em outro dispositivo. Atualizamos o estado; tente novamente."
        : apiError(error));
      qc.invalidateQueries({ queryKey: ["progress", trackId] });
    },
  });
}
