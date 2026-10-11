import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowDown, ArrowUp, Copy, Eye, MoreHorizontal, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { Track } from "@/types";
import { EmptyState, Loader, PageHeader, StatusBadge } from "@/components/common";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { TrackFormDialog } from "@/components/admin/TrackFormDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { formatDate } from "@/lib/utils";

export default function AdminTracks() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [status, setStatus] = useState("all");
  const [q, setQ] = useState("");
  const [creating, setCreating] = useState(false);
  const [toDelete, setToDelete] = useState<Track | null>(null);
  const { data, isLoading } = useQuery({ queryKey: ["tracks", "admin"], queryFn: () => api.get<Track[]>("/tracks").then((r) => r.data) });
  const all = data || [];
  const tracks = all.filter((t) => (status === "all" || t.status === status) && (!q || t.title.toLowerCase().includes(q.toLowerCase())));
  const refresh = () => qc.invalidateQueries({ queryKey: ["tracks"] });

  const run = async (fn: () => Promise<unknown>, msg: string) => {
    try { await fn(); refresh(); toast.success(msg); } catch (e) { toast.error(apiError(e)); }
  };
  const move = (t: Track, dir: -1 | 1) => {
    const ids = all.map((x) => x.id);
    const i = ids.indexOf(t.id);
    if (i + dir < 0 || i + dir >= ids.length) return;
    [ids[i], ids[i + dir]] = [ids[i + dir], ids[i]];
    run(() => api.put("/tracks/reorder", { ordered_ids: ids }), "Ordem atualizada");
  };

  return (
    <div className="max-w-6xl">
      <PageHeader eyebrow="estrutura" title="Trilhas" description="Crie, duplique, reordene e publique trilhas. Trilhas derivadas mantêm vínculo com a original."
        actions={<Button data-testid="create-track-button" className="rounded-full" onClick={() => setCreating(true)}><Plus />Nova trilha</Button>} />
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Tabs value={status} onValueChange={setStatus}>
          <TabsList className="bg-slate-900">
            {[["all", "Todas"], ["draft", "Rascunhos"], ["published", "Publicadas"], ["archived", "Arquivadas"]].map(([k, l]) => (
              <TabsTrigger key={k} value={k} data-testid={`tracks-filter-${k}`}>{l}</TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <Input data-testid="tracks-search-input" placeholder="Buscar trilha" value={q} onChange={(e) => setQ(e.target.value)} className="pl-9" />
        </div>
      </div>
      {isLoading ? <Loader /> : tracks.length === 0 ? (
        <EmptyState icon="Route" title="Nenhuma trilha encontrada" description="Crie a primeira trilha ou ajuste os filtros."
          action={<Button size="sm" variant="outline" onClick={() => setCreating(true)}><Plus />Criar trilha</Button>} />
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-800">
          {tracks.map((t) => (
            <div key={t.id} data-testid={`admin-track-row-${t.slug}`} className="flex items-center gap-4 border-b border-slate-800 bg-slate-900/40 px-5 py-4 last:border-0 hover:bg-slate-900/80">
              <div className="flex flex-col">
                <button data-testid={`track-up-${t.id}`} onClick={() => move(t, -1)} className="text-slate-600 hover:text-slate-200"><ArrowUp className="h-3.5 w-3.5" /></button>
                <button data-testid={`track-down-${t.id}`} onClick={() => move(t, 1)} className="text-slate-600 hover:text-slate-200"><ArrowDown className="h-3.5 w-3.5" /></button>
              </div>
              <Link to={`/admin/trilhas/${t.id}`} className="min-w-0 flex-1" data-testid={`admin-track-open-${t.slug}`}>
                <div className="flex items-center gap-2">
                  <p className="truncate font-semibold text-slate-100">{t.title}</p>
                  <StatusBadge status={t.status} />
                  {t.visibility === "private" && <span className="font-mono text-[10px] uppercase text-slate-500">privada</span>}
                  {t.derived_from && <span className="font-mono text-[10px] uppercase text-violet-400">derivada</span>}
                </div>
                <p className="mt-1 font-mono text-[11px] text-slate-500">
                  v{t.version} · {t.hierarchy.map((k) => `${t.counts?.[k] || 0} ${(t.level_labels[k] || k).toLowerCase()}`).join(" · ")} · atualizada {formatDate(t.updated_at)}
                </p>
              </Link>
              <DropdownMenu>
                <DropdownMenuTrigger asChild><Button variant="ghost" size="icon" data-testid={`track-actions-${t.id}`}><MoreHorizontal /></Button></DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="border-slate-800 bg-slate-900">
                  <DropdownMenuItem data-testid={`track-edit-${t.id}`} onClick={() => navigate(`/admin/trilhas/${t.id}`)}><Pencil className="mr-2 h-4 w-4" />Editar estrutura</DropdownMenuItem>
                  <DropdownMenuItem data-testid={`track-preview-${t.id}`} onClick={() => navigate(`/trilhas/${t.id}`)}><Eye className="mr-2 h-4 w-4" />Pré-visualizar</DropdownMenuItem>
                  <DropdownMenuItem data-testid={`track-duplicate-${t.id}`} onClick={() => run(() => api.post(`/tracks/${t.id}/duplicate`), "Trilha duplicada como rascunho")}><Copy className="mr-2 h-4 w-4" />Duplicar / derivar</DropdownMenuItem>
                  <DropdownMenuItem data-testid={`track-delete-${t.id}`} className="text-rose-400" onClick={() => setToDelete(t)}><Trash2 className="mr-2 h-4 w-4" />Excluir</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ))}
        </div>
      )}
      {creating && <TrackFormDialog open={creating} onOpenChange={setCreating} onSaved={(t) => navigate(`/admin/trilhas/${t.id}`)} />}
      <ConfirmDialog open={!!toDelete} onOpenChange={(v) => !v && setToDelete(null)} title={`Excluir "${toDelete?.title}"?`}
        description="Toda a estrutura, blocos, relações, versões e progresso desta trilha serão removidos. Considere arquivar."
        confirmLabel="Excluir definitivamente" onConfirm={() => toDelete && run(() => api.delete(`/tracks/${toDelete.id}`), "Trilha excluída")} />
    </div>
  );
}
