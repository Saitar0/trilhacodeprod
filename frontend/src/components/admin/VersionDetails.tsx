import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowRight, Minus, Pencil, Plus, RotateCcw } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { DiffGroup, FieldChange, TrackVersion } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
const FIELD_LABELS: Record<string, string> = {
  title: "título", kind: "nível", parent_id: "pai (movido)", order: "ordem", status: "status", summary: "resumo", description: "descrição",
  guidance: "orientação", notes: "notas internas", pedagogical_type: "tipo pedagógico", requirement: "caráter", depth: "profundidade",
  estimated_minutes: "tempo", tag_ids: "tags", release: "liberação", data: "conteúdo", type: "tipo", enforced: "bloqueante", note: "nota",
  node_id: "tópico", settings: "regras", level_labels: "nomenclatura", visibility: "visibilidade", subtitle: "subtítulo", hierarchy: "hierarquia",
};
export const KIND_LABEL: Record<string, string> = { publish: "publicação", backup: "backup", restore: "restauração" };

const fmt = (v: unknown) => {
  const s = typeof v === "string" ? v : JSON.stringify(v);
  return !s ? "∅" : s.length > 140 ? `${s.slice(0, 140)}…` : s;
};

export function Changes({ changes }: { changes: FieldChange[] }) {
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

export function Group({ title, group, id }: { title: string; group: DiffGroup; id: string }) {
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

export function RestoreDialog({ trackId, version, onClose }: { trackId: string; version: TrackVersion; onClose: () => void }) {
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


