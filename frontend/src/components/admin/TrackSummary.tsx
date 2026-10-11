import React from "react";
import { AlertTriangle, Lock, MousePointerClick, ShieldCheck } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { ViewModel } from "@/components/student/viewModel";
import { HistoryList } from "@/components/admin/HistoryList";
import { TaxBadge } from "@/components/common";
import { useTaxonomy } from "@/hooks/useData";

export function TrackSummary({ vm }: { vm: ViewModel }) {
  const { list } = useTaxonomy();
  const drafts = vm.flat.filter((n) => n.status === "draft").length;
  const blocks = Object.values(vm.blockCounts).reduce((a, b) => a + b, 0);
  const validation = useQuery({ queryKey: ["validate", vm.track.id],
    queryFn: () => api.get<{ ok: boolean; issues: { level: string; message: string }[] }>(`/tracks/${vm.track.id}/validate`).then((r) => r.data) });
  const blocking = vm.relations.filter((r) => r.type === "prerequisite" && r.enforced).length;
  return (
    <div className="mx-auto max-w-3xl space-y-10 fade-up" data-testid="track-summary">
      <div className="flex items-center gap-3 rounded-xl border border-dashed border-slate-700 p-5 text-sm text-slate-400">
        <MousePointerClick className="h-5 w-5 text-emerald-400" />
        Selecione um item na árvore para editar detalhes, blocos e relações — ou arraste para reordenar.
      </div>
      <div data-testid="track-progression-mode" className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-sm">
        <Lock className={vm.track.settings.enforce_prerequisites ? "h-4 w-4 text-rose-300" : "h-4 w-4 text-slate-500"} />
        <span className="text-slate-300">Progressão {vm.track.settings.enforce_prerequisites ? "bloqueante ativa" : "livre"} · {blocking} pré-requisito(s) bloqueante(s)</span>
      </div>
      {validation.data && (validation.data.issues.length ? (
        <ul data-testid="track-validation-issues" className="space-y-2">
          {validation.data.issues.map((i, k) => (
            <li key={k} className={i.level === "error" ? "flex gap-2 rounded-lg border border-rose-500/40 bg-rose-500/5 p-3 text-xs text-rose-200" : "flex gap-2 rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 text-xs text-amber-200"}>
              <AlertTriangle className="h-4 w-4 shrink-0" />{i.message}
            </li>
          ))}
        </ul>
      ) : <p data-testid="track-validation-ok" className="flex items-center gap-2 text-xs text-emerald-300"><ShieldCheck className="h-4 w-4" />Estrutura válida: sem ciclos nem bloqueios inconsistentes.</p>)}
      <div className="grid gap-4 sm:grid-cols-4">
        {vm.track.hierarchy.map((k) => (
          <div key={k} className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
            <p className="font-heading text-2xl font-bold text-slate-50">{vm.flat.filter((n) => n.kind === k).length}</p>
            <p className="text-xs text-slate-400">{vm.label(k)}s</p>
          </div>
        ))}
      </div>
      <div className="grid gap-4 sm:grid-cols-3 font-mono text-xs text-slate-400">
        <p><span className="text-lg text-slate-100">{blocks}</span> blocos</p>
        <p><span className="text-lg text-slate-100">{vm.relations.length}</span> relações</p>
        <p><span className="text-lg text-amber-300">{drafts}</span> itens em rascunho</p>
      </div>
      <div className="space-y-3">
        <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">legenda pedagógica</p>
        <div className="flex flex-wrap gap-2">
          {["pedagogical_type", "requirement", "depth"].flatMap((g) => list(g).map((t) => <TaxBadge key={g + t.key} group={g} value={t.key} />))}
        </div>
      </div>
      <section>
        <h3 className="mb-5 text-base font-semibold text-slate-200">Histórico de edição</h3>
        <HistoryList trackId={vm.track.id} limit={25} />
      </section>
    </div>
  );
}
