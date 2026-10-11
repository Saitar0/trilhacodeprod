import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeft, ArrowRight, Minus, Pencil, Plus, RotateCcw } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useTree } from "@/hooks/useData";
import { CompareResult, DiffGroup, FieldChange, TrackVersion } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { EmptyState, Loader, PageHeader } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";

const FIELD_LABELS: Record<string, string> = {
  title: "título", kind: "nível", parent_id: "pai (movido)", order: "ordem", status: "status", summary: "resumo", description: "descrição",
  guidance: "orientação", notes: "notas internas", pedagogical_type: "tipo pedagógico", requirement: "caráter", depth: "profundidade",
  estimated_minutes: "tempo", tag_ids: "tags", release: "liberação", data: "conteúdo", type: "tipo", enforced: "bloqueante", note: "nota",
  node_id: "tópico", settings: "regras", level_labels: "nomenclatura", visibility: "visibilidade", subtitle: "subtítulo", hierarchy: "hierarquia",
};
const KIND_LABEL: Record<string, string> = { publish: "publicação", backup: "backup", restore: "restauração" };

const fmt = (v: unknown) => {
  const s = typeof v === "string" ? v : JSON.stringify(v);
  return !s ? "∅" : s.length > 140 ? `${s.slice(0, 140)}…` : s;
};

function Changes({ changes }: { changes: FieldChange[] }) {
  return (
    <ul className="mt-2 space-y-1.5">
      {changes.map((c) => (
        <li key={c.field} className="grid gap-1 font-mono text-[11px] sm:grid-cols-[110px_1fr]">
          <span className="text-slate-500">{FIELD_LABELS[c.field] || c.field}</span>
          <span className="break-all"><span className="bg-rose-500/10 text-rose-300 line-through decoration-rose-500/40">{fmt(c.from)}</span>
            <ArrowRight className="mx-1.5 inline h-3 w-3 text-slate-600" /><span className="bg-emerald-500/10 text-emerald-300">{fmt(c.to)}</span></span>
        </li>
      ))}
    </ul>
  );
}

function Group({ title, group, id }: { title: string; group: DiffGroup; id: string }) {
  const n = group.added.length + group.removed.length + group.changed.length;
  if (!n) return null;
  const row = (icon: React.ReactNode, cls: string) => (it: DiffGroup["added"][number]) => (
    <li key={it.id} className={cn("rounded-lg border px-4 py-3", cls)}>
      <p className="flex items-center gap-2 text-sm text-slate-100">{icon}{it.title}
        <span className="font-mono text-[10px] text-slate-500">{it.kind || it.type}{it.parent && ` · em ${it.parent}`}{it.node && ` · ${it.node}`}</span></p>
      {it.changes && <Changes changes={it.changes} />}
    </li>
  );
  return (
    <section data-testid={`diff-section-${id}`} className="space-y-2">
      <h3 className="font-mono text-[11px] uppercase tracking-widest text-slate-400">{title} · {n}</h3>
      <ul className="space-y-2">
        {group.added.map(row(<Plus className="h-4 w-4 text-emerald-400" />, "border-emerald-500/30 bg-emerald-500/[0.04]"))}
        {group.removed.map(row(<Minus className="h-4 w-4 text-rose-400" />, "border-rose-500/30 bg-rose-500/[0.04]"))}
        {group.changed.map(row(<Pencil className="h-3.5 w-3.5 text-amber-400" />, "border-amber-500/25 bg-amber-500/[0.03]"))}
      </ul>
    </section>
  );
}

function RestoreDialog({ trackId, version, onClose }: { trackId: string; version: TrackVersion; onClose: () => void }) {
  const qc = useQueryClient();
  const [confirm, setConfirm] = useState("");
  const [note, setNote] = useState("");
  const expected = `v${version.version}`;
  const restore = async () => {
    try {
      const { data } = await api.post(`/tracks/${trackId}/versions/${version.id}/restore`, { confirm, note });
      ["versions", "tree", "tracks", "compare"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
      toast.success(`Restaurada — nova versão v${data.version} publicada`);
      onClose();
    } catch (e) { toast.error(apiError(e)); }
  };
  return (
    <Dialog open onOpenChange={(v) => !v && onClose()}>
      <DialogContent data-testid="restore-dialog" className="border-rose-500/30 bg-slate-900">
        <DialogHeader>
          <DialogTitle>Restaurar {expected}?</DialogTitle>
          <DialogDescription>
            A estrutura atual (itens, blocos e relações) será substituída pelo conteúdo de {expected}. Antes disso, um backup automático do estado atual é salvo,
            e a restauração gera uma <b>nova versão publicada</b> — o histórico não é apagado. Itens criados depois de {expected} deixam de existir na trilha.
          </DialogDescription>
        </DialogHeader>
        <Input data-testid="restore-note-input" placeholder="Motivo da restauração (opcional)" value={note} onChange={(e) => setNote(e.target.value)} />
        <div className="space-y-1.5">
          <p className="text-xs text-slate-400">Digite <span className="font-mono text-rose-300">{expected}</span> para confirmar</p>
          <Input data-testid="restore-confirm-input" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="font-mono" />
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button data-testid="restore-confirm-button" disabled={confirm.trim().toLowerCase() !== expected} className="bg-rose-600 text-white hover:bg-rose-500" onClick={restore}><RotateCcw />Restaurar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

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
