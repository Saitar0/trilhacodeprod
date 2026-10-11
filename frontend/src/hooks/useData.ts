import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Meta, NodeDetail, ProgressStatus, TrackProgress, TreeResponse } from "@/types";

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
  return useMutation({
    mutationFn: (body: { node_id: string; status: ProgressStatus; block_id?: string; data?: Record<string, unknown> }) =>
      api.post("/progress", body).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["progress", trackId] });
      qc.invalidateQueries({ queryKey: ["overview"] });
      qc.invalidateQueries({ queryKey: ["node"] });
    },
  });
}
