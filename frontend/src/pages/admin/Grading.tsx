import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { api } from "@/lib/api";
import { useMeta } from "@/hooks/useData";
import { Submission, Track } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { EmptyState, Loader, PageHeader } from "@/components/common";
import { SubmissionBadge } from "@/components/common/SubmissionBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { GradingPanel } from "@/components/admin/GradingPanel";
const STATUS_TABS: [string, string][] = [["submitted", "Enviadas"], ["in_review", "Em correção"], ["returned", "Devolvidas"], ["graded", "Corrigidas"]];
const ALL = "__all";

export default function Grading() {
  const { data: meta } = useMeta();
  const [status, setStatus] = useState("submitted");
  const [trackId, setTrackId] = useState(ALL);
  const [type, setType] = useState(ALL);
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const tracks = useQuery({ queryKey: ["tracks", "admin"], queryFn: () => api.get<Track[]>("/tracks").then((r) => r.data) });
  const params = { status, track_id: trackId === ALL ? undefined : trackId, block_type: type === ALL ? undefined : type, q: q || undefined };
  const { data, isLoading } = useQuery({
    queryKey: ["submissions", "staff", params],
    queryFn: () => api.get<{ items: Submission[]; counts: Record<string, number> }>("/submissions", { params }).then((r) => r.data),
  });
  const types = (meta?.block_types || []).filter((b) => b.capabilities?.includes("submission"));
  return (
    <div className="min-w-0 max-w-7xl">
      <PageHeader eyebrow="operação editorial" title="Correções" description="Fila de respostas enviadas. Corrija com rubrica, devolva para ajuste ou aprove." />
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Tabs value={status} onValueChange={(v) => { setStatus(v); setSelected(null); }}>
          <TabsList className="h-auto max-w-full flex-wrap justify-start bg-slate-900">
            {STATUS_TABS.map(([k, l]) => <TabsTrigger key={k} value={k} data-testid={`grading-tab-${k}`}>{l} <span className="ml-1.5 font-mono text-[10px] text-slate-500">{data?.counts[k] || 0}</span></TabsTrigger>)}
          </TabsList>
        </Tabs>
        <Select value={trackId} onValueChange={setTrackId}>
          <SelectTrigger data-testid="grading-filter-track" className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value={ALL}>Todas as trilhas</SelectItem>{(tracks.data || []).map((t) => <SelectItem key={t.id} value={t.id}>{t.title}</SelectItem>)}</SelectContent>
        </Select>
        <Select value={type} onValueChange={setType}>
          <SelectTrigger data-testid="grading-filter-type" className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value={ALL}>Todos os tipos</SelectItem>{types.map((t) => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}</SelectContent>
        </Select>
        <div className="relative w-56"><Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <Input data-testid="grading-search" placeholder="Aluno ou tópico" value={q} onChange={(e) => setQ(e.target.value)} className="pl-9" /></div>
      </div>
      <div className="grid min-w-0 grid-cols-[minmax(0,1fr)] gap-6 lg:grid-cols-[380px_minmax(0,1fr)]">
        <div className="min-w-0 space-y-2">
          {isLoading ? <Loader /> : !data?.items.length ? <EmptyState icon="ClipboardCheck" title="Nada por aqui" description="Nenhuma submissão com estes filtros." /> : data.items.map((s) => (
            <button key={s.id} data-testid={`grading-item-${s.id}`} onClick={() => setSelected(s.id)}
              className={cn("min-w-0 w-full rounded-xl border px-4 py-3 text-left transition-colors", selected === s.id ? "border-emerald-500/40 bg-emerald-500/5" : "border-slate-800 bg-slate-900/50 hover:border-slate-600")}>
              <div className="flex min-w-0 items-center justify-between gap-2"><span className="min-w-0 truncate text-sm font-medium text-slate-100">{s.user_name}</span><SubmissionBadge status={s.status} testId={`grading-item-status-${s.id}`} /></div>
              <p className="truncate text-xs text-slate-400">{s.orphaned && <span data-testid={`grading-item-orphan-${s.id}`} className="mr-1.5 rounded border border-slate-600 px-1 font-mono text-[9px] uppercase text-slate-400">órfão</span>}{s.node_title} · {s.block_title || s.block_type}</p>
              <p className="font-mono text-[10px] text-slate-600">#{s.attempt} · {formatDate(s.submitted_at)}</p>
            </button>
          ))}
        </div>
        <div className="min-w-0">{selected ? <GradingPanel key={selected} id={selected} onDone={() => undefined} /> : <EmptyState icon="MousePointerClick" title="Selecione uma submissão" description="Abra uma resposta da fila para corrigir." />}</div>
      </div>
    </div>
  );
}

