import React, { useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeft, Copy, Eye, History, Rocket, Settings2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useTree } from "@/hooks/useData";
import { Track } from "@/types";
import { EmptyState, Loader, StatusBadge } from "@/components/common";
import { useViewModel } from "@/components/student/viewModel";
import { AdminTree } from "@/components/admin/AdminTree";
import { NodeEditor } from "@/components/admin/NodeEditor";
import { TrackSummary } from "@/components/admin/TrackSummary";
import { TrackFormDialog } from "@/components/admin/TrackFormDialog";
import { PublishDialog } from "@/components/admin/Publishing";
import { Button } from "@/components/ui/button";

const EMPTY = {};

export default function TrackEditor() {
  const { trackId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [params, setParams] = useSearchParams();
  const selected = params.get("node");
  const tree = useTree(trackId);
  const vm = useViewModel(tree.data, EMPTY, false);
  const [dialog, setDialog] = useState<"settings" | "publish" | null>(null);

  if (tree.isLoading) return <Loader />;
  if (!vm) return <div className="p-10"><EmptyState icon="SearchX" title="Trilha não encontrada" /></div>;
  const select = (id: string | null) => setParams(id ? { node: id } : {});
  const duplicate = async () => {
    try {
      const { data } = await api.post<Track>(`/tracks/${vm.track.id}/duplicate`);
      qc.invalidateQueries({ queryKey: ["tracks"] });
      toast.success("Trilha derivada criada");
      navigate(`/admin/trilhas/${data.id}`);
    } catch (e) { toast.error(apiError(e)); }
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <header className="flex flex-wrap items-center gap-4 border-b border-slate-800 bg-slate-950/60 px-5 py-3 backdrop-blur">
        <Link to="/admin/trilhas" data-testid="editor-back-link" className="text-slate-500 hover:text-slate-100"><ArrowLeft className="h-4 w-4" /></Link>
        <button onClick={() => select(null)} className="min-w-0 text-left" data-testid="editor-track-title">
          <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">editor de trilha · v{vm.track.version}</p>
          <p className="truncate font-heading text-lg font-semibold text-slate-50">{vm.track.title}</p>
        </button>
        <StatusBadge status={vm.track.status} testId="editor-track-status" />
        <div className="ml-auto flex flex-wrap gap-2">
          <Button variant="ghost" size="sm" data-testid="editor-preview-button" asChild><Link to={`/trilhas/${vm.track.id}`}><Eye />Pré-visualizar</Link></Button>
          <Button variant="ghost" size="sm" data-testid="editor-versions-button" asChild><Link to={`/admin/trilhas/${vm.track.id}/versoes`}><History />Versões</Link></Button>
          <Button variant="ghost" size="sm" data-testid="editor-duplicate-button" onClick={duplicate}><Copy />Derivar</Button>
          <Button variant="outline" size="sm" data-testid="editor-settings-button" onClick={() => setDialog("settings")}><Settings2 />Configurações</Button>
          <Button size="sm" className="rounded-full" data-testid="editor-publish-button" onClick={() => setDialog("publish")}><Rocket />Publicar</Button>
        </div>
      </header>
      <div className="grid min-h-0 flex-1 md:grid-cols-[380px_1fr]">
        <aside className="min-h-0 border-r border-slate-800 bg-sidebar"><AdminTree vm={vm} selected={selected} onSelect={select} /></aside>
        <main className="min-h-0 overflow-y-auto px-6 py-8 scrollbar-thin">
          {selected && vm.byId.has(selected) ? <NodeEditor nodeId={selected} vm={vm} /> : <TrackSummary vm={vm} />}
        </main>
      </div>
      {dialog === "settings" && <TrackFormDialog open track={vm.track} onOpenChange={(v) => !v && setDialog(null)} />}
      <PublishDialog track={vm.track} open={dialog === "publish"} onOpenChange={(v) => setDialog(v ? "publish" : null)} />
    </div>
  );
}
