import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Review, StudyNote, Submission } from "@/types";

export function useNotes(params: { node_id?: string; track_id?: string }, enabled = true) {
  return useQuery({
    queryKey: ["notes", params.node_id || params.track_id || "all"],
    enabled,
    queryFn: () => api.get<StudyNote[]>("/notes", { params }).then((r) => r.data),
  });
}

export function useAutosaveNote(nodeId: string, blockId: string | null, initial: string) {
  const qc = useQueryClient();
  const [body, setBody] = useState(initial);
  const [state, setState] = useState<"idle" | "saving" | "saved">("idle");
  const first = useRef(true);
  useEffect(() => setBody(initial), [initial]);
  useEffect(() => {
    if (first.current) { first.current = false; return; }
    if (body === initial) return;
    setState("saving");
    const t = setTimeout(async () => {
      await api.put("/notes", { node_id: nodeId, block_id: blockId, body });
      setState("saved");
      qc.invalidateQueries({ queryKey: ["notes"] });
    }, 800);
    return () => clearTimeout(t);
  }, [body]); // eslint-disable-line react-hooks/exhaustive-deps
  return { body, setBody, state };
}

export function useReviews(status = "pending") {
  return useQuery({ queryKey: ["reviews", status], queryFn: () => api.get<Review[]>("/reviews", { params: { status } }).then((r) => r.data) });
}

export function useScheduleReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { node_id: string; block_id?: string | null; when: string; due_at?: string }) => api.post<Review>("/reviews", body).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reviews"] }),
  });
}

export function useMySubmissions(nodeId?: string) {
  return useQuery({
    queryKey: ["submissions", "mine", nodeId || "all"],
    queryFn: () => api.get<Submission[]>("/submissions/mine", { params: { node_id: nodeId } }).then((r) => r.data),
  });
}
