import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, ArrowRight, Check, Clock3, Compass, Lock, NotebookPen, RotateCcw } from "lucide-react";
import { api } from "@/lib/api";
import { useMeta, useNodeDetail, useSetProgress } from "@/hooks/useData";
import { Loader, StatusBadge, TaxBadge, EmptyState } from "@/components/common";
import { Markdown } from "@/components/common/Markdown";
import { BlockRenderer } from "@/components/blocks/BlockRenderer";
import { Button } from "@/components/ui/button";
import { TrackProgress } from "@/types";
import { ViewModel } from "./viewModel";
import { BlockNote, NoteEditor, ReviewMenu, useNodeNotes } from "./StudyTools";
import { ExerciseSubmission } from "@/components/blocks/ExerciseSubmission";
import { Breadcrumbs, ChildrenList, LockedPanel } from "./NodeReaderParts";
import { isLearnable } from "@/lib/tree";
export function NodeReader({ vm, nodeId, progress, staff }: { vm: ViewModel; nodeId: string; progress?: TrackProgress; staff: boolean }) {
  const { data, isLoading } = useNodeDetail(nodeId);
  const { data: meta } = useMeta();
  const qc = useQueryClient();
  const setProgress = useSetProgress(vm.track.id);
  const tn = vm.byId.get(nodeId);
  const learnable = tn ? isLearnable(tn, vm.lastKind, vm.blockCounts) : false;
  const lock = vm.locks[nodeId];
  const noteFor = useNodeNotes(nodeId);
  const [showNotes, setShowNotes] = useState(false);

  useEffect(() => {
    if (!learnable || (lock && !staff)) return;
    api.post("/progress/visit", { node_id: nodeId }).then(() => qc.invalidateQueries({ queryKey: ["progress", vm.track.id] }));
  }, [nodeId, learnable, qc, vm.track.id, lock, staff]);

  if (isLoading || !data) return <Loader />;
  const { node, blocks, ancestors } = data;
  const status = vm.statuses[nodeId]?.status || "not_started";
  const idx = vm.learnables.findIndex((n) => n.id === nodeId);
  const prev = idx > 0 ? vm.learnables[idx - 1] : undefined;
  const next = idx >= 0 ? vm.learnables[idx + 1] : undefined;
  const blockType = (k: string) => meta?.block_types.find((b) => b.key === k);

  return (
    <article key={nodeId} className="mx-auto max-w-3xl space-y-8 px-6 py-10 fade-up" data-testid="node-reader">
      <Breadcrumbs vm={vm} ancestors={ancestors} title={node.title} />
      <header className="space-y-4">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-emerald-400">{vm.label(node.kind)}</p>
        <h1 data-testid="reader-title" className="text-3xl font-bold text-slate-50 sm:text-4xl">{node.title}</h1>
        <div className="flex flex-wrap items-center gap-2">
          <TaxBadge group="pedagogical_type" value={node.pedagogical_type} />
          <TaxBadge group="requirement" value={node.requirement} />
          <TaxBadge group="depth" value={node.depth} />
          {node.estimated_minutes > 0 && <span className="flex items-center gap-1 text-xs text-slate-400"><Clock3 className="h-3 w-3" />~{node.estimated_minutes} min de estudo</span>}
          {staff && node.status !== "published" && <StatusBadge status={node.status} />}
        </div>
        {node.summary && <p className="text-lg leading-relaxed text-slate-300">{node.summary}</p>}
        {(!lock || staff) && (
          <div className="flex flex-wrap gap-2 pt-1">
            <Button variant="outline" size="sm" className={showNotes ? "rounded-full border-amber-500/40 text-amber-200" : "rounded-full"}
              data-testid="topic-notes-toggle" onClick={() => setShowNotes(!showNotes)}><NotebookPen />{noteFor(null) ? "Minha anotação" : "Anotar"}</Button>
            <ReviewMenu nodeId={nodeId} />
          </div>
        )}
        {showNotes && <NoteEditor nodeId={nodeId} blockId={null} initial={noteFor(null)} testId="topic-note-editor" />}
      </header>
      {lock && <LockedPanel vm={vm} lock={lock} staff={staff} />}
      {node.description && <Markdown>{node.description}</Markdown>}
      {node.guidance && (
        <div className="flex gap-3 rounded-xl border border-cyan-500/25 bg-cyan-500/5 p-5" data-testid="reader-guidance">
          <Compass className="h-5 w-5 shrink-0 text-cyan-400" />
          <div><p className="mb-1 text-sm font-semibold text-cyan-200">Orientação de estudo</p><Markdown className="text-sm">{node.guidance}</Markdown></div>
        </div>
      )}
      {blocks.length > 0 && (
        <div className="space-y-5">
          {blocks.map((b) => (
            <BlockRenderer key={b.id} block={b} type={blockType(b.type)} progress={progress?.blocks[b.id]}
              onProgress={(s, d) => setProgress.mutate({ node_id: nodeId, block_id: b.id, status: s, data: d })}
              actions={<ReviewMenu nodeId={nodeId} blockId={b.id} compact />}
              footer={<>
                {blockType(b.type)?.capabilities?.includes("submission") && <ExerciseSubmission block={b} />}
                <BlockNote nodeId={nodeId} blockId={b.id} initial={noteFor(b.id)} />
              </>} />
          ))}
        </div>
      )}
      {tn && tn.children.length > 0 && <ChildrenList vm={vm} nodeId={nodeId} />}
      {learnable && !lock && blocks.length === 0 && (
        <EmptyState icon="FileText" title="Conteúdo em preparação" description="Este tópico já faz parte da estrutura, mas os blocos de conteúdo ainda serão adicionados." />
      )}
      {learnable && (
        <footer className="sticky bottom-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800 bg-slate-900/90 p-3 backdrop-blur-xl">
          <Button variant="ghost" size="sm" disabled={!prev} asChild={!!prev} data-testid="reader-prev-button">
            {prev ? <Link to={`/trilhas/${vm.track.id}/n/${prev.id}`}><ArrowLeft />Anterior</Link> : <span className="inline-flex items-center gap-2"><ArrowLeft />Anterior</span>}
          </Button>
          <div className="flex gap-2">
            {lock && !staff ? (
              <span data-testid="topic-locked-indicator" className="inline-flex items-center gap-2 px-3 text-sm text-rose-300"><Lock className="h-4 w-4" />Bloqueado</span>
            ) : status === "completed" ? (
              <Button variant="outline" size="sm" className="rounded-full" data-testid="topic-reset-button"
                onClick={() => setProgress.mutate({ node_id: nodeId, status: "in_progress" })}><RotateCcw />Reabrir</Button>
            ) : (
              <Button size="sm" className="rounded-full font-semibold" data-testid="topic-mark-completed-button" disabled={setProgress.isPending}
                onClick={() => setProgress.mutate({ node_id: nodeId, status: "completed" })}><Check />Marcar como concluído</Button>
            )}
          </div>
          <Button variant="ghost" size="sm" disabled={!next} asChild={!!next} data-testid="reader-next-button">
            {next ? <Link to={`/trilhas/${vm.track.id}/n/${next.id}`}>Próximo<ArrowRight /></Link> : <span className="inline-flex items-center gap-2">Próximo<ArrowRight /></span>}
          </Button>
        </footer>
      )}
    </article>
  );
}


