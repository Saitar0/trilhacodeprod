import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, Check, ChevronRight, Lock as LockIcon } from "lucide-react";
import { EmptyState, ProgressBar } from "@/components/common";
import { learnablesOf, progressFor } from "@/lib/tree";
import { Lock as LockT } from "@/types";
import { ViewModel } from "./viewModel";
import { StatusIcon } from "./StudentTree";
export function LockedPanel({ vm, lock, staff }: { vm: ViewModel; lock: LockT; staff: boolean }) {
  const via = lock.via ? vm.byId.get(lock.via) : undefined;
  const requirements = lock.pending_requirements || [];
  const requirementByTarget = new Map(requirements.map((item) => [item.target_id, item]));
  return (
    <div data-testid="locked-panel" className="space-y-4 rounded-xl border border-rose-500/30 bg-rose-500/[0.04] p-6">
      <p className="flex items-center gap-2 font-heading text-lg font-semibold text-rose-100"><LockIcon className="h-5 w-5 text-rose-300" />
        {staff ? "Alunos veem este conteúdo bloqueado" : "Conteúdo ainda bloqueado"}</p>
      <p className="text-sm text-slate-400">
        {via ? `O ${vm.label(via.kind).toLowerCase()} "${via.title}" exige ` : "Este item exige "}atender aos pré-requisitos abaixo. O servidor libera o conteúdo quando todos forem confirmados.
      </p>
      <ul className="space-y-2">
        {lock.pending.map((id) => {
          const n = vm.byId.get(id);
          const requirement = requirementByTarget.get(id);
          const requirementText = requirement?.status === "unavailable"
            ? "verificação indisponível"
            : requirement?.prerequisite_kind === "quiz_passed"
              ? "quiz ainda não aprovado"
              : requirement?.prerequisite_kind === "content_completed"
                ? "leitura pendente"
                : "pré-requisito pendente";
          return n && (
            <li key={id}>
              <Link to={`/trilhas/${vm.track.id}/n/${id}`} data-testid={`locked-pending-${id}`}
                className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3 text-sm text-slate-200 hover:border-slate-600">
                <StatusIcon status={vm.statuses[id]?.status} locked={!!vm.locks[id]} />
                <span className="flex-1">{n.title}</span>
                {requirement && <span className="text-xs text-amber-200">{requirementText}</span>}
                <span className="font-mono text-[10px] uppercase text-slate-500">{vm.label(n.kind)}</span>
                <ArrowRight className="h-4 w-4 text-slate-500" />
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export function Breadcrumbs({ vm, ancestors, title }: { vm: ViewModel; ancestors: { id: string; title: string }[]; title: string }) {
  return (
    <nav data-testid="reader-breadcrumbs" className="flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
      <Link to={`/trilhas/${vm.track.id}`} className="hover:text-slate-200">{vm.track.title}</Link>
      {ancestors.map((a) => (
        <React.Fragment key={a.id}>
          <ChevronRight className="h-3 w-3" />
          <Link to={`/trilhas/${vm.track.id}/n/${a.id}`} className="hover:text-slate-200">{a.title}</Link>
        </React.Fragment>
      ))}
      <ChevronRight className="h-3 w-3" /><span className="text-slate-300">{title}</span>
    </nav>
  );
}

export function ChildrenList({ vm, nodeId }: { vm: ViewModel; nodeId: string }) {
  const node = vm.byId.get(nodeId)!;
  return (
    <div className="grid gap-3" data-testid="reader-children">
      {node.children.map((c) => {
        const p = c.children.length ? progressFor(learnablesOf(c, vm.lastKind, vm.blockCounts), vm.statuses) : null;
        const done = vm.statuses[c.id]?.status === "completed";
        return (
          <Link key={c.id} to={`/trilhas/${vm.track.id}/n/${c.id}`} data-testid={`reader-child-${c.id}`}
            className="group flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 p-4 hover:border-slate-600">
            <div className="min-w-0 flex-1">
              <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{vm.label(c.kind)}</p>
              <p className="font-medium text-slate-100">{c.title}</p>
              {c.summary && <p className="truncate text-sm text-slate-400">{c.summary}</p>}
              {p && p.total > 0 && <ProgressBar value={p.pct} className="mt-3 max-w-xs" />}
            </div>
            {done && <Check className="h-4 w-4 text-emerald-400" />}
            <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-slate-200" />
          </Link>
        );
      })}
    </div>
  );
}


