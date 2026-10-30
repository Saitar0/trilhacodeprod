import React from "react";
import { Link } from "react-router-dom";
import { AlertTriangle, ArrowRight, CheckCircle2, CircleDashed, GitBranch, Link2, Repeat2 } from "lucide-react";
import { learnablesOf, progressFor } from "@/lib/tree";
import { ProgressBar } from "@/components/common";
import { cn } from "@/lib/utils";
import { nextLearnable, ViewModel } from "./viewModel";

function NodeLink({ vm, id, testId }: { vm: ViewModel; id: string; testId: string }) {
  const n = vm.byId.get(id);
  if (!n) return null;
  const done = vm.statuses[id]?.status === "completed";
  return (
    <Link to={`/trilhas/${vm.track.id}/n/${id}`} data-testid={testId}
      className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-slate-300 hover:bg-slate-800/60 hover:text-slate-50">
      {done ? <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-400" /> : <CircleDashed className="h-3.5 w-3.5 shrink-0 text-slate-500" />}
      <span className="truncate">{n.title}</span>
    </Link>
  );
}

function Group({ title, icon: Icon, ids, vm, tid }: { title: string; icon: React.ElementType; ids: string[]; vm: ViewModel; tid: string }) {
  if (!ids.length) return null;
  return (
    <div className="space-y-1" data-testid={`context-group-${tid}`}>
      <p className="flex items-center gap-1.5 px-2 font-mono text-[10px] uppercase tracking-widest text-slate-500"><Icon className="h-3 w-3" />{title}</p>
      {ids.map((id) => <NodeLink key={id} vm={vm} id={id} testId={`context-${tid}-${id}`} />)}
    </div>
  );
}

export function dependenciesOf(vm: ViewModel, nodeId: string) {
  const out = (t: string) => vm.relations.filter((r) => r.node_id === nodeId && r.type === t).map((r) => r.target_id);
  const inc = (t: string) => vm.relations.filter((r) => r.target_id === nodeId && r.type === t).map((r) => r.node_id);
  const prereqs = out("prerequisite");
  const evaluated = new Map((vm.prerequisiteStates[nodeId] || []).map((item) => [item.target_id, item]));
  const pending = prereqs.filter((id) => {
    const state = evaluated.get(id);
    if (state) return state.status !== "satisfied";
    const relation = vm.relations.find((item) => item.node_id === nodeId && item.target_id === id
      && item.type === "prerequisite");
    return !relation?.prerequisite_kind && vm.statuses[id]?.status !== "completed";
  });
  return { prereqs, pending, unlocks: inc("prerequisite"), complements: [...out("complement"), ...inc("complement")],
    revisits: [...out("revisit"), ...inc("revisit")], related: [...out("related"), ...inc("related")] };
}

function prerequisiteLabel(kind: string, status: string): string {
  if (status === "unavailable") return "Verificação indisponível";
  if (kind === "quiz_passed") return status === "satisfied" ? "Quiz aprovado" : "Quiz ainda não aprovado";
  if (kind === "content_completed") return status === "satisfied" ? "Leitura concluída" : "Leitura pendente";
  return status === "satisfied" ? "Pré-requisito concluído" : "Pré-requisito pendente";
}

export function ContextPanel({ vm, nodeId }: { vm: ViewModel; nodeId?: string }) {
  const total = progressFor(vm.learnables, vm.statuses);
  const next = nextLearnable(vm, nodeId);
  const deps = nodeId ? dependenciesOf(vm, nodeId) : null;
  const enforcedPrereqs = nodeId ? vm.relations
    .filter((relation) => relation.node_id === nodeId && relation.type === "prerequisite" && relation.enforced)
    .map((relation) => relation.target_id) : [];
  const node = nodeId ? vm.byId.get(nodeId) : undefined;
  const local = node && node.children.length ? progressFor(learnablesOf(node, vm.lastKind, vm.blockCounts), vm.statuses) : null;
  return (
    <div className="space-y-8 p-5">
      <div className="space-y-2">
        <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">progresso da trilha</p>
        <div className="flex items-baseline justify-between">
          <span data-testid="context-track-progress" className="font-heading text-3xl font-bold text-slate-50">{total.pct}%</span>
          <span className="text-xs text-slate-400">{total.completed}/{total.total}</span>
        </div>
        <ProgressBar value={total.pct} />
        {local && <p className="text-xs text-slate-400">Neste {vm.label(node!.kind).toLowerCase()}: {local.completed}/{local.total}</p>}
      </div>
      {next && next.id !== nodeId && (
        <Link to={`/trilhas/${vm.track.id}/n/${next.id}`} data-testid="context-next-step"
          className="block rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4 hover:border-emerald-500/60">
          <p className="font-mono text-[10px] uppercase tracking-widest text-emerald-400">próximo passo</p>
          <p className="mt-1 flex items-center justify-between gap-2 text-sm font-medium text-slate-100">{next.title}<ArrowRight className="h-4 w-4 shrink-0" /></p>
        </Link>
      )}
      {deps && (
        <div className="space-y-5">
          {enforcedPrereqs.length > 0 && vm.track.settings.enforce_prerequisites && (
            <section aria-label="Estado dos pré-requisitos" data-testid="context-prerequisite-states"
              className="space-y-2 rounded-md border border-slate-700 bg-slate-900/50 p-3">
              <p className="text-xs font-semibold text-slate-200">
                {vm.locks[nodeId!] ? "Conteúdo bloqueado" : "Conteúdo liberado"}
              </p>
              <ul className="space-y-1">
                {enforcedPrereqs.map((id) => {
                  const requirement = vm.prerequisiteStates[nodeId!]?.find((item) => item.target_id === id);
                  const label = requirement
                    ? prerequisiteLabel(requirement.prerequisite_kind, requirement.status)
                    : "Verificação indisponível";
                  return <li key={id} className="text-xs text-slate-300">
                    {vm.byId.get(id)?.title || "Pré-requisito"}: {label}
                  </li>;
                })}
              </ul>
            </section>
          )}
          {vm.locks[nodeId!] ? (
            <p data-testid="context-locked" className="flex gap-2 rounded-md border border-rose-500/40 bg-rose-500/5 p-3 text-xs text-rose-200">
              <AlertTriangle className="h-4 w-4 shrink-0" />Bloqueado até atender: {vm.locks[nodeId!].pending.map((id) => vm.byId.get(id)?.title).join(", ")}.
            </p>
          ) : deps.pending.length > 0 && (
            <p data-testid="context-pending-prereqs" className={cn("flex gap-2 rounded-md border p-3 text-xs",
              vm.track.settings.enforce_prerequisites ? "border-rose-500/40 bg-rose-500/5 text-rose-200" : "border-amber-500/30 bg-amber-500/5 text-amber-200")}>
              <AlertTriangle className="h-4 w-4 shrink-0" />{deps.pending.length} pré-requisito(s) ainda não concluído(s).
            </p>
          )}
          <Group title="Pré-requisitos" icon={GitBranch} ids={deps.prereqs} vm={vm} tid="prereq" />
          <Group title="Libera" icon={ArrowRight} ids={deps.unlocks} vm={vm} tid="unlocks" />
          <Group title="Complementares" icon={Link2} ids={deps.complements} vm={vm} tid="complement" />
          <Group title="Revisitas" icon={Repeat2} ids={deps.revisits} vm={vm} tid="revisit" />
          <Group title="Relacionados" icon={Link2} ids={deps.related} vm={vm} tid="related" />
        </div>
      )}
    </div>
  );
}
