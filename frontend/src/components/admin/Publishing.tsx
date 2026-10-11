import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ChevronDown } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { Track, TrackVersion } from "@/types";
import { formatDate } from "@/lib/utils";
import { EmptyState, Loader } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";

export function PublishDialog({ track, open, onOpenChange }: { track: Track; open: boolean; onOpenChange: (v: boolean) => void }) {
  const qc = useQueryClient();
  const [note, setNote] = useState("");
  const [children, setChildren] = useState(true);
  const publish = async () => {
    try {
      await api.post(`/tracks/${track.id}/publish`, { note, publish_children: children });
      qc.invalidateQueries({ queryKey: ["tree", track.id] });
      qc.invalidateQueries({ queryKey: ["tracks"] });
      qc.invalidateQueries({ queryKey: ["versions", track.id] });
      toast.success(`Trilha publicada — versão ${track.version + 1}`);
      onOpenChange(false);
      setNote("");
    } catch (e) { toast.error(apiError(e)); }
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="publish-dialog" className="border-slate-800 bg-slate-900">
        <DialogHeader>
          <DialogTitle>Publicar versão {track.version + 1}</DialogTitle>
          <DialogDescription>Um snapshot completo da estrutura (itens, blocos e relações) será salvo no histórico de versões.</DialogDescription>
        </DialogHeader>
        <Textarea data-testid="publish-note-input" placeholder="Notas da versão (o que mudou?)" value={note} onChange={(e) => setNote(e.target.value)} />
        <label className="flex items-center justify-between gap-4 rounded-lg border border-slate-800 p-3 text-sm text-slate-300">
          Publicar também itens e blocos em rascunho
          <Switch data-testid="publish-children-switch" checked={children} onCheckedChange={setChildren} />
        </label>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button data-testid="publish-confirm-button" className="rounded-full" onClick={publish}>Publicar</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function VersionRow({ v }: { v: TrackVersion }) {
  const [open, setOpen] = useState(false);
  const snap = useQuery({
    queryKey: ["version", v.id], enabled: open,
    queryFn: () => api.get<{ snapshot: { nodes: { id: string; title: string; kind: string; status: string }[] } }>(`/versions/${v.id}`).then((r) => r.data),
  });
  return (
    <li data-testid={`version-item-${v.version}`} className="rounded-lg border border-slate-800 bg-slate-950/40">
      <button onClick={() => setOpen(!open)} className="flex w-full items-center gap-3 p-4 text-left">
        <span className="font-heading text-lg font-bold text-emerald-400">v{v.version}</span>
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm text-slate-200">{v.note || "Sem notas"}</span>
          <span className="font-mono text-[10px] text-slate-500">{formatDate(v.created_at)} · {v.created_by_name} · {v.stats.nodes} itens · {v.stats.blocks} blocos</span>
        </span>
        <ChevronDown className="h-4 w-4 text-slate-500" />
      </button>
      {open && (
        <div className="max-h-60 overflow-y-auto border-t border-slate-800 p-4 text-xs text-slate-400 scrollbar-thin">
          {snap.isLoading ? <Loader /> : snap.data?.snapshot.nodes.map((n) => <p key={n.id}><span className="font-mono text-slate-600">{n.kind}</span> {n.title}</p>)}
        </div>
      )}
    </li>
  );
}

export function VersionsSheet({ trackId, open, onOpenChange }: { trackId: string; open: boolean; onOpenChange: (v: boolean) => void }) {
  const { data, isLoading } = useQuery({
    queryKey: ["versions", trackId], enabled: open,
    queryFn: () => api.get<TrackVersion[]>(`/tracks/${trackId}/versions`).then((r) => r.data),
  });
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent data-testid="versions-sheet" className="w-full overflow-y-auto border-slate-800 bg-slate-900 sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Versões publicadas</SheetTitle>
          <SheetDescription>Cada publicação gera um snapshot imutável. Base pronta para comparação e restauração.</SheetDescription>
        </SheetHeader>
        <div className="mt-6">
          {isLoading ? <Loader /> : !data?.length ? <EmptyState icon="History" title="Nenhuma versão ainda" description="Publique a trilha para criar a primeira versão." /> : (
            <ul className="space-y-3">{data.map((v) => <VersionRow key={v.id} v={v} />)}</ul>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
