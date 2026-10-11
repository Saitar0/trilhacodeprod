import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, PlayCircle } from "lucide-react";
import { learnablesOf, progressFor } from "@/lib/tree";
import { EmptyState, Markdown, ProgressBar } from "@/components/common";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";
import { TrackProgress } from "@/types";
import { nextLearnable, ViewModel } from "./viewModel";

export function TrackOverview({ vm, progress }: { vm: ViewModel; progress?: TrackProgress }) {
  const total = progressFor(vm.learnables, vm.statuses);
  const state = progress?.state;
  const next = nextLearnable(vm);
  return (
    <div className="mx-auto max-w-4xl space-y-12 px-6 py-10" data-testid="track-overview">
      <header className="space-y-5 fade-up">
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-emerald-400">trilha · v{vm.track.version}</p>
        <h1 data-testid="track-title" className="text-4xl font-extrabold text-slate-50 sm:text-5xl">{vm.track.title}</h1>
        {vm.track.subtitle && <p className="text-lg text-slate-300">{vm.track.subtitle}</p>}
        <Markdown className="text-slate-400">{vm.track.description}</Markdown>
        <div className="flex flex-wrap items-center gap-3 pt-2">
          {state?.last_node_id && vm.byId.has(state.last_node_id) ? (
            <Button asChild className="rounded-full font-semibold" data-testid="track-resume-button">
              <Link to={`/trilhas/${vm.track.id}/n/${state.last_node_id}`}><PlayCircle />Retomar: {vm.byId.get(state.last_node_id)?.title}</Link>
            </Button>
          ) : next && (
            <Button asChild className="rounded-full font-semibold" data-testid="track-start-button">
              <Link to={`/trilhas/${vm.track.id}/n/${next.id}`}><PlayCircle />Começar trilha</Link>
            </Button>
          )}
          {state?.last_at && <span className="text-xs text-slate-500">Última atividade {formatDate(state.last_at)}</span>}
        </div>
      </header>
      <div className="grid gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6 sm:grid-cols-[1fr_auto] sm:items-center">
        <div className="space-y-2">
          <p className="text-sm text-slate-400">{total.completed} de {total.total} itens concluídos</p>
          <ProgressBar value={total.pct} testId="track-overview-progress" />
        </div>
        <span className="font-heading text-4xl font-bold text-emerald-400">{total.pct}%</span>
      </div>
      {vm.tree.length === 0 ? (
        <EmptyState icon="Route" title="Estrutura ainda vazia" description="Esta trilha ainda não possui itens publicados." />
      ) : (
        <div className="space-y-4">
          {vm.tree.map((n, i) => {
            const p = progressFor(learnablesOf(n, vm.lastKind, vm.blockCounts), vm.statuses);
            return (
              <Link key={n.id} to={`/trilhas/${vm.track.id}/n/${n.id}`} data-testid={`overview-root-${n.id}`} style={{ animationDelay: `${i * 70}ms` }}
                className="group grid gap-4 rounded-xl border border-slate-800 bg-slate-900/40 p-6 hover:border-emerald-500/40 sm:grid-cols-[56px_1fr_180px] sm:items-center fade-up">
                <span className="font-mono text-2xl font-bold text-slate-700 group-hover:text-emerald-500/70">{String(i + 1).padStart(2, "0")}</span>
                <div>
                  <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{vm.label(n.kind)} · {n.children.length} itens</p>
                  <p className="text-lg font-semibold text-slate-100">{n.title}</p>
                  {n.summary && <p className="text-sm text-slate-400">{n.summary}</p>}
                </div>
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-slate-500"><span>{p.completed}/{p.total}</span><ArrowRight className="h-3.5 w-3.5" /></div>
                  <ProgressBar value={p.pct} />
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
