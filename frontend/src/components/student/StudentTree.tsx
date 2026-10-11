import React, { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CheckCircle2, ChevronRight, Circle, CircleDashed, Lock, Search, SlidersHorizontal } from "lucide-react";
import { TreeNode } from "@/types";
import { filterTree, learnablesOf, progressFor } from "@/lib/tree";
import { cn } from "@/lib/utils";
import { useTaxonomy } from "@/hooks/useData";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ViewModel } from "./viewModel";

type Filters = { pedagogical_type: string; depth: string; requirement: string; progress: string };
const EMPTY: Filters = { pedagogical_type: "all", depth: "all", requirement: "all", progress: "all" };

export function StatusIcon({ status, locked }: { status?: string; locked?: boolean }) {
  if (locked && status !== "completed") return <Lock className="h-3.5 w-3.5 shrink-0 text-rose-300/80" />;
  if (status === "completed") return <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />;
  if (status === "in_progress") return <CircleDashed className="h-4 w-4 shrink-0 text-amber-400" />;
  return <Circle className="h-4 w-4 shrink-0 text-slate-600" />;
}

function Row({ node, vm, activeId, collapsed, toggle }: {
  node: TreeNode; vm: ViewModel; activeId?: string; collapsed: Set<string>; toggle: (id: string) => void;
}) {
  const container = node.children.length > 0;
  const open = !collapsed.has(node.id);
  const p = container ? progressFor(learnablesOf(node, vm.lastKind, vm.blockCounts), vm.statuses) : null;
  const active = node.id === activeId;
  return (
    <li>
      <div className={cn("group flex items-center gap-1.5 rounded-lg pr-2 text-sm transition-colors",
        active ? "bg-emerald-500/10 text-emerald-200" : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100")}
        style={{ paddingLeft: `${node.level * 14 + 4}px` }}>
        {container ? (
          <button data-testid={`student-tree-toggle-${node.id}`} onClick={() => toggle(node.id)} className="p-1 text-slate-500 hover:text-slate-200">
            <ChevronRight className={cn("h-3.5 w-3.5 transition-transform", open && "rotate-90")} />
          </button>
        ) : <span className="w-1" />}
        <Link to={`/trilhas/${vm.track.id}/n/${node.id}`} data-testid={`student-tree-node-${node.id}`}
          className="flex min-w-0 flex-1 items-center gap-2 py-1.5">
          {!container && <StatusIcon status={vm.statuses[node.id]?.status} locked={!!vm.locks[node.id]} />}
          {container && vm.locks[node.id] && <Lock className="h-3 w-3 shrink-0 text-rose-300/80" />}
          <span className="min-w-0 flex-1">
            {container && <span className="block font-mono text-[9px] uppercase tracking-widest text-slate-500">{vm.label(node.kind)}</span>}
            <span className={cn("block truncate", container && "font-medium text-slate-200", vm.locks[node.id] && "text-slate-500")}>{node.title}</span>
          </span>
          {node.status !== "published" && <span className="font-mono text-[9px] uppercase text-amber-400">{node.status === "draft" ? "rasc." : "arq."}</span>}
          {p && p.total > 0 && <span className="font-mono text-[10px] text-slate-500">{p.completed}/{p.total}</span>}
        </Link>
      </div>
      {container && open && (
        <ul>{node.children.map((c) => React.createElement(Row, { key: c.id, node: c, vm, activeId, collapsed, toggle }))}</ul>
      )}
    </li>
  );
}

function FilterSelect({ id, value, onChange, items, placeholder }: {
  id: string; value: string; onChange: (v: string) => void; items: { key: string; label: string }[]; placeholder: string;
}) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger data-testid={`student-filter-${id}`} className="h-8 border-slate-800 bg-slate-950/60 text-xs"><SelectValue placeholder={placeholder} /></SelectTrigger>
      <SelectContent>
        <SelectItem value="all">{placeholder}: todos</SelectItem>
        {items.map((i) => <SelectItem key={i.key} value={i.key}>{i.label}</SelectItem>)}
      </SelectContent>
    </Select>
  );
}

export function StudentTree({ vm, activeId }: { vm: ViewModel; activeId?: string }) {
  const { list } = useTaxonomy();
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());
  const [q, setQ] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [f, setF] = useState<Filters>(EMPTY);
  const active = Object.values(f).filter((v) => v !== "all").length + (q ? 1 : 0);

  const tree = useMemo(() => {
    if (!active) return vm.tree;
    return filterTree(vm.tree, (n) => {
      const st = vm.locks[n.id] && vm.statuses[n.id]?.status !== "completed" ? "locked" : vm.statuses[n.id]?.status || "not_started";
      return (!q || n.title.toLowerCase().includes(q.toLowerCase()))
        && (f.pedagogical_type === "all" || n.pedagogical_type === f.pedagogical_type)
        && (f.depth === "all" || n.depth === f.depth)
        && (f.requirement === "all" || n.requirement === f.requirement)
        && (f.progress === "all" || st === f.progress);
    });
  }, [vm, f, q, active]);

  const toggle = (id: string) => setCollapsed((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  const set = (k: keyof Filters) => (v: string) => setF({ ...f, [k]: v });

  return (
    <div className="flex h-full flex-col">
      <div className="space-y-2 border-b border-slate-800 p-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <Input data-testid="student-tree-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar na trilha"
              className="h-8 border-slate-800 bg-slate-950/60 pl-8 text-xs" />
          </div>
          <button data-testid="student-filter-toggle" onClick={() => setShowFilters(!showFilters)}
            className={cn("relative rounded-md border px-2 text-slate-400 hover:text-slate-100", showFilters ? "border-emerald-500/50" : "border-slate-800")}>
            <SlidersHorizontal className="h-3.5 w-3.5" />
            {active > 0 && <span className="absolute -right-1 -top-1 grid h-4 w-4 place-items-center rounded-full bg-emerald-500 text-[9px] font-bold text-slate-950">{active}</span>}
          </button>
        </div>
        {showFilters && (
          <div className="grid gap-2 fade-up">
            <FilterSelect id="type" value={f.pedagogical_type} onChange={set("pedagogical_type")} items={list("pedagogical_type")} placeholder="Tipo" />
            <FilterSelect id="depth" value={f.depth} onChange={set("depth")} items={list("depth")} placeholder="Profundidade" />
            <FilterSelect id="requirement" value={f.requirement} onChange={set("requirement")} items={list("requirement")} placeholder="Caráter" />
            <FilterSelect id="progress" value={f.progress} onChange={set("progress")} placeholder="Status"
              items={[{ key: "not_started", label: "Não iniciado" }, { key: "in_progress", label: "Em andamento" }, { key: "completed", label: "Concluído" }, { key: "locked", label: "Bloqueado" }]} />
            {active > 0 && <button data-testid="student-filter-clear" onClick={() => { setF(EMPTY); setQ(""); }} className="text-left text-xs text-emerald-400">Limpar filtros</button>}
          </div>
        )}
      </div>
      <nav className="flex-1 overflow-y-auto p-2 scrollbar-thin" data-testid="student-tree">
        {tree.length === 0 ? <p className="p-4 text-xs text-slate-500">Nenhum item corresponde aos filtros.</p> : (
          <ul className="space-y-0.5">{tree.map((n) => <Row key={n.id} node={n} vm={vm} activeId={activeId} collapsed={collapsed} toggle={toggle} />)}</ul>
        )}
      </nav>
    </div>
  );
}
