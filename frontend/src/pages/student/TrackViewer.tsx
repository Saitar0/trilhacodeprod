import React from "react";
import { Link, useParams } from "react-router-dom";
import { Eye } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useTrackProgress, useTree } from "@/hooks/useData";
import { EmptyState, Loader } from "@/components/common";
import { StudentTree } from "@/components/student/StudentTree";
import { ContextPanel } from "@/components/student/ContextPanel";
import { NodeReader } from "@/components/student/NodeReader";
import { TrackOverview } from "@/components/student/TrackOverview";
import { useViewModel } from "@/components/student/viewModel";

const EMPTY = {};

export default function TrackViewer() {
  const { trackId, nodeId } = useParams();
  const { can } = useAuth();
  const staff = can("content.read");
  const tree = useTree(trackId);
  const progress = useTrackProgress(trackId);
  const vm = useViewModel(tree.data, progress.data?.nodes || EMPTY, true, progress.data?.locks);

  if (tree.isLoading) return <Loader />;
  if (tree.isError || !vm) return <div className="p-10"><EmptyState icon="SearchX" title="Trilha não encontrada" /></div>;

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      {staff && (
        <div data-testid="preview-banner" className="flex items-center gap-2 border-b border-amber-500/30 bg-amber-500/10 px-6 py-2 text-xs text-amber-200">
          <Eye className="h-3.5 w-3.5" /> Visão de equipe — itens em rascunho também aparecem (estudantes veem só o publicado).
          <Link to={`/admin/trilhas/${vm.track.id}`} className="ml-auto underline">Voltar ao editor</Link>
        </div>
      )}
      <div className="grid min-h-0 flex-1 lg:grid-cols-[300px_1fr] xl:grid-cols-[300px_1fr_300px]">
        <aside className="hidden min-h-0 border-r border-slate-800 bg-sidebar lg:block">
          <div className="border-b border-slate-800 px-4 py-3">
            <Link to={`/trilhas/${vm.track.id}`} data-testid="sidebar-track-link" className="font-heading font-semibold text-slate-100 hover:text-emerald-300">{vm.track.title}</Link>
          </div>
          <div className="h-[calc(100%-49px)]"><StudentTree vm={vm} activeId={nodeId} /></div>
        </aside>
        <main className="min-h-0 overflow-y-auto scrollbar-thin">
          {nodeId ? <NodeReader vm={vm} nodeId={nodeId} progress={progress.data} staff={staff} /> : <TrackOverview vm={vm} progress={progress.data} />}
          <div className="border-t border-slate-800 xl:hidden"><ContextPanel vm={vm} nodeId={nodeId} /></div>
        </main>
        <aside className="hidden min-h-0 overflow-y-auto border-l border-slate-800 bg-sidebar xl:block scrollbar-thin" data-testid="context-panel">
          <ContextPanel vm={vm} nodeId={nodeId} />
        </aside>
      </div>
    </div>
  );
}
