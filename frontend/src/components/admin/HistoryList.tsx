import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { HistoryItem } from "@/types";
import { EmptyState, Loader } from "@/components/common";
import { formatDate } from "@/lib/utils";

const ACTIONS: Record<string, string> = {
  created: "criou", updated: "editou", deleted: "excluiu", duplicated: "duplicou", published: "publicou", role_changed: "alterou papel",
};
const ENTITIES: Record<string, string> = { track: "trilha", node: "item", block: "bloco", relation: "relação", user: "usuário" };

export function HistoryList({ trackId, entityId, limit = 30 }: { trackId?: string; entityId?: string; limit?: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ["history", trackId, limit],
    queryFn: () => api.get<HistoryItem[]>("/history", { params: { track_id: trackId, limit } }).then((r) => r.data),
  });
  if (isLoading) return <Loader />;
  const items = (data || []).filter((h) => !entityId || h.entity_id === entityId);
  if (!items.length) return <EmptyState icon="History" title="Sem histórico ainda" description="Edições aparecerão aqui." />;
  return (
    <ol className="relative space-y-4 border-l border-slate-800 pl-5" data-testid="history-list">
      {items.map((h) => (
        <li key={h.id} className="relative">
          <span className="absolute -left-[25px] top-1.5 h-2 w-2 rounded-full bg-slate-600 ring-4 ring-[#090D16]" />
          <p className="text-sm text-slate-300">
            <span className="font-medium text-slate-100">{h.user_name || "Alguém"}</span> {ACTIONS[h.action] || h.action} {ENTITIES[h.entity] || h.entity}
            {h.summary && <span className="text-slate-400"> — {h.summary}</span>}
          </p>
          <p className="font-mono text-[10px] text-slate-500">{formatDate(h.at)}</p>
        </li>
      ))}
    </ol>
  );
}
