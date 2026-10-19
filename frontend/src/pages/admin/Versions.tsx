import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, RotateCcw } from "lucide-react";
import { api } from "@/lib/api";
import { useTree } from "@/hooks/useData";
import { CompareResult, TrackVersion } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { EmptyState, Loader, PageHeader } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Changes, Group, KIND_LABEL, RestoreDialog } from "@/components/admin/VersionDetails";

export default function Versions() {
  const { trackId } = useParams();
  const tree = useTree(trackId);
  const versions = useQuery({ queryKey: ["versions", trackId], queryFn: () => api.get<TrackVersion[]>(`/tracks/${trackId}/versions`).then((r) => r.data) });
  const [base, setBase] = useState("");
  const [target, setTarget] = useState("current");
  const [restoring, setRestoring] = useState<TrackVersion | null>(null);
  useEffect(() => { if (!base && versions.data?.length) setBase(versions.data[0].id); }, [versions.data, base]);
  const diff = useQuery({
    queryKey: ["compare", trackId, base, target], enabled: !!base && base !== target,
    queryFn: () => api.get<CompareResult>(`/tracks/${trackId}/compare`, { params: { base, target } }).then((r) => r.data),
  });
  const list = versions.data || [];
  const options = [{ id: "current", label: "Estado atual (editor)" }, ...list.map((v) => ({ id: v.id, label: `v${v.version} · ${KIND_LABEL[v.kind || "publish"]} · ${formatDate(v.created_at)}` }))];
  const picker = (value: string, set: (v: string) => void, tid: string) => (
    <Select value={value} onValueChange={set}>
      <SelectTrigger data-testid={tid} className="w-72"><SelectValue placeholder="Selecione" /></SelectTrigger>
      <SelectContent>{options.map((o) => <SelectItem key={o.id} value={o.id}>{o.label}</SelectItem>)}</SelectContent>
    </Select>
  );

  return (
    <div className="mx-auto max-w-7xl px-6 py-10">
      <Link to={`/admin/trilhas/${trackId}`} data-testid="versions-back-link" className="mb-6 inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-100"><ArrowLeft className="h-4 w-4" />Voltar ao editor</Link>
      <PageHeader eyebrow="versionamento" title={`Versões — ${tree.data?.track.title || ""}`} description="Compare snapshots e restaure com segurança. Toda restauração gera nova versão e é auditada." />
      <div className="grid gap-8 lg:grid-cols-[340px_1fr]">
        <aside className="space-y-2" data-testid="versions-list">
          {versions.isLoading ? <Loader /> : !list.length ? <EmptyState icon="History" title="Nenhuma versão" description="Publique a trilha para criar a primeira versão." /> : list.map((v) => (
            <div key={v.id} data-testid={`version-row-${v.id}`} className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
              <div className="flex items-center gap-2">
                <span className="font-heading text-lg font-bold text-emerald-400">v{v.version}</span>
                <span className={cn("rounded-full border px-2 py-0.5 font-mono text-[10px] uppercase", v.kind === "backup" ? "border-slate-700 text-slate-400" : v.kind === "restore" ? "border-violet-500/40 text-violet-300" : "border-emerald-500/30 text-emerald-300")}>{KIND_LABEL[v.kind || "publish"]}</span>
                <Button variant="ghost" size="sm" className="ml-auto h-7 text-xs" data-testid={`version-restore-${v.id}`} onClick={() => setRestoring(v)}><RotateCcw />Restaurar</Button>
              </div>
              <p className="mt-1 text-sm text-slate-300">{v.note || "Sem notas"}{v.restored_from_version && ` (de v${v.restored_from_version})`}</p>
              <p className="font-mono text-[10px] text-slate-500">{formatDate(v.created_at)} · {v.created_by_name} · {v.stats.nodes} itens · {v.stats.blocks} blocos{v.packed_bytes != null && ` · ${(v.packed_bytes / 1024).toFixed(1)} KB`}</p>
            </div>
          ))}
        </aside>
        <main className="min-w-0 space-y-6">
          <div className="flex flex-wrap items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/40 p-4">
            <span className="text-xs text-slate-400">Comparar</span>{picker(base, setBase, "compare-base-select")}
            <ArrowRight className="h-4 w-4 text-slate-500" />{picker(target, setTarget, "compare-target-select")}
          </div>
          {base === target ? <EmptyState icon="GitCompare" title="Selecione duas versões diferentes" /> : diff.isLoading || !diff.data ? <Loader /> : (
            <div className="space-y-8" data-testid="diff-view">
              <p data-testid="diff-summary" className="text-sm text-slate-400"><span className="font-semibold text-slate-100">{diff.data.total_changes}</span> mudança(s) de {diff.data.base} para {diff.data.target}</p>
              {diff.data.total_changes === 0 && <EmptyState icon="CheckCheck" title="Sem diferenças" />}
              {diff.data.track.length > 0 && (
                <section data-testid="diff-section-track" className="rounded-lg border border-amber-500/25 bg-amber-500/[0.03] px-4 py-3">
                  <h3 className="font-mono text-[11px] uppercase tracking-widest text-slate-400">trilha</h3><Changes changes={diff.data.track} />
                </section>
              )}
              <Group title="Estrutura (itens)" group={diff.data.nodes} id="nodes" />
              <Group title="Blocos de conteúdo" group={diff.data.blocks} id="blocks" />
              <Group title="Relações pedagógicas" group={diff.data.relations} id="relations" />
            </div>
          )}
        </main>
      </div>
      {restoring && trackId && <RestoreDialog trackId={trackId} version={restoring} onClose={() => setRestoring(null)} />}
    </div>
  );
}


