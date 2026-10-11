import React, { useMemo, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowDown, ArrowUp, ChevronRight, Copy, GripVertical, MoreHorizontal, Plus, Search, Trash2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { TrackNode, TreeNode } from "@/types";
import { filterTree } from "@/lib/tree";
import { cn, STATUS_META } from "@/lib/utils";
import { ViewModel } from "@/components/student/viewModel";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { CreateNodeDialog } from "@/components/admin/CreateNodeDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Actions {
  select: (id: string) => void;
  addChild: (n: TreeNode | null) => void;
  move: (n: TreeNode, dir: -1 | 1) => void;
  drop: (dragId: string, target: TreeNode) => void;
  duplicate: (n: TreeNode) => void;
  remove: (n: TreeNode) => void;
}

function Row({ node, vm, selected, actions, dragId, setDragId }: {
  node: TreeNode; vm: ViewModel; selected?: string | null; actions: Actions; dragId: string | null; setDragId: (id: string | null) => void;
}) {
  const [open, setOpen] = useState(true);
  const [over, setOver] = useState(false);
  const h = vm.track.hierarchy;
  const canHaveChildren = h.indexOf(node.kind) < h.length - 1;
  const blocks = vm.blockCounts[node.id] || 0;
  return (
    <li>
      <div draggable data-testid={`admin-tree-node-${node.id}`}
        onDragStart={() => setDragId(node.id)} onDragEnd={() => { setDragId(null); setOver(false); }}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }} onDragLeave={() => setOver(false)}
        onDrop={(e) => { e.preventDefault(); setOver(false); if (dragId && dragId !== node.id) actions.drop(dragId, node); }}
        className={cn("group flex items-center gap-1 rounded-lg py-1 pr-1 text-sm transition-colors",
          selected === node.id ? "bg-emerald-500/10 text-emerald-100 ring-1 ring-emerald-500/30" : "text-slate-300 hover:bg-slate-800/60",
          over && "ring-1 ring-cyan-400/60")}
        style={{ paddingLeft: `${node.level * 16 + 2}px` }}>
        <GripVertical className="h-3.5 w-3.5 shrink-0 cursor-grab text-slate-700 group-hover:text-slate-500" />
        <button onClick={() => setOpen(!open)} className={cn("p-0.5 text-slate-500", !node.children.length && "invisible")}>
          <ChevronRight className={cn("h-3.5 w-3.5 transition-transform", open && "rotate-90")} />
        </button>
        <button onClick={() => actions.select(node.id)} data-testid={`admin-tree-select-${node.id}`} className="flex min-w-0 flex-1 items-center gap-2 text-left">
          <span className={cn("h-1.5 w-1.5 shrink-0 rounded-full", STATUS_META[node.status]?.dot)} title={STATUS_META[node.status]?.label} />
          <span className="shrink-0 rounded bg-slate-800 px-1 font-mono text-[9px] uppercase text-slate-400">{vm.label(node.kind).slice(0, 3)}</span>
          <span className="truncate">{node.title}</span>
          {blocks > 0 && <span className="font-mono text-[10px] text-slate-600">{blocks}b</span>}
        </button>
        <div className="hidden group-hover:flex">
          <button data-testid={`reorder-node-up-button-${node.id}`} onClick={() => actions.move(node, -1)} className="p-1 text-slate-500 hover:text-slate-100"><ArrowUp className="h-3.5 w-3.5" /></button>
          <button data-testid={`reorder-node-down-button-${node.id}`} onClick={() => actions.move(node, 1)} className="p-1 text-slate-500 hover:text-slate-100"><ArrowDown className="h-3.5 w-3.5" /></button>
          {canHaveChildren && <button data-testid={`admin-tree-add-child-${node.id}`} onClick={() => actions.addChild(node)} className="p-1 text-slate-500 hover:text-emerald-300"><Plus className="h-3.5 w-3.5" /></button>}
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger data-testid={`admin-tree-actions-${node.id}`} className="rounded p-1 text-slate-500 hover:text-slate-100"><MoreHorizontal className="h-3.5 w-3.5" /></DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="border-slate-800 bg-slate-900">
            {canHaveChildren && <DropdownMenuItem onClick={() => actions.addChild(node)}><Plus className="mr-2 h-4 w-4" />Adicionar filho</DropdownMenuItem>}
            <DropdownMenuItem data-testid={`admin-tree-duplicate-${node.id}`} onClick={() => actions.duplicate(node)}><Copy className="mr-2 h-4 w-4" />Duplicar (com filhos)</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem data-testid={`admin-tree-delete-${node.id}`} className="text-rose-400" onClick={() => actions.remove(node)}><Trash2 className="mr-2 h-4 w-4" />Excluir</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      {open && node.children.length > 0 && (
        <ul>{node.children.map((c) => React.createElement(Row, { key: c.id, node: c, vm, selected, actions, dragId, setDragId }))}</ul>
      )}
    </li>
  );
}

export function AdminTree({ vm, selected, onSelect }: { vm: ViewModel; selected: string | null; onSelect: (id: string | null) => void }) {
  const qc = useQueryClient();
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("all");
  const [creating, setCreating] = useState<{ parent: TreeNode | null } | null>(null);
  const [toDelete, setToDelete] = useState<TreeNode | null>(null);
  const [dragId, setDragId] = useState<string | null>(null);
  const h = vm.track.hierarchy;
  const refresh = () => qc.invalidateQueries({ queryKey: ["tree", vm.track.id] });

  const tree = useMemo(() => (!q && status === "all") ? vm.tree : filterTree(vm.tree, (n) =>
    (!q || n.title.toLowerCase().includes(q.toLowerCase())) && (status === "all" || n.status === status)), [vm.tree, q, status]);

  const siblingsOf = (n: TreeNode) => (n.parent_id ? vm.byId.get(n.parent_id)?.children : vm.tree) || [];
  const reorder = async (ids: string[]) => {
    try { await api.post("/nodes/reorder", { ordered_ids: ids }); refresh(); } catch (e) { toast.error(apiError(e)); }
  };
  const actions: Actions = {
    select: onSelect,
    addChild: (parent) => setCreating({ parent }),
    move: (n, dir) => {
      const ids = siblingsOf(n).map((s) => s.id);
      const i = ids.indexOf(n.id);
      if (i + dir < 0 || i + dir >= ids.length) return;
      [ids[i], ids[i + dir]] = [ids[i + dir], ids[i]];
      reorder(ids);
    },
    drop: (dragged, target) => {
      const d = vm.byId.get(dragged);
      if (!d || d.parent_id !== target.parent_id) return toast.info("Arraste entre itens do mesmo nível. Para mudar de pai, use o campo 'Pai' nos detalhes.");
      const ids = siblingsOf(target).map((s) => s.id).filter((id) => id !== dragged);
      ids.splice(ids.indexOf(target.id), 0, dragged);
      reorder(ids);
    },
    duplicate: async (n) => {
      try { const { data } = await api.post<TrackNode>(`/nodes/${n.id}/duplicate`); refresh(); onSelect(data.id); toast.success("Item duplicado como rascunho"); }
      catch (e) { toast.error(apiError(e)); }
    },
    remove: setToDelete,
  };
  const kindsFor = (p: TreeNode | null) => (p ? h.slice(h.indexOf(p.kind) + 1) : h);

  return (
    <div className="flex h-full flex-col">
      <div className="space-y-2 border-b border-slate-800 p-3">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
            <Input data-testid="admin-tree-search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Buscar item" className="h-8 pl-8 text-xs" />
          </div>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger data-testid="admin-tree-status-filter" className="h-8 w-32 text-xs"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              {Object.entries(STATUS_META).map(([k, m]) => <SelectItem key={k} value={k}>{m.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>
        <Button size="sm" variant="outline" className="w-full justify-start border-dashed" data-testid="admin-tree-add-root-button" onClick={() => setCreating({ parent: null })}>
          <Plus />Adicionar {vm.label(h[0]).toLowerCase()}
        </Button>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 scrollbar-thin">
        {tree.length === 0 ? <p className="p-4 text-xs text-slate-500">{vm.tree.length ? "Nenhum item corresponde." : "Estrutura vazia. Comece adicionando o primeiro nível."}</p> : (
          <ul className="space-y-0.5" data-testid="admin-tree">
            {tree.map((n) => <Row key={n.id} node={n} vm={vm} selected={selected} actions={actions} dragId={dragId} setDragId={setDragId} />)}
          </ul>
        )}
      </nav>
      {creating && (
        <CreateNodeDialog trackId={vm.track.id} parent={creating.parent} kinds={kindsFor(creating.parent)} label={vm.label}
          onClose={() => setCreating(null)} onCreated={(n) => { setCreating(null); onSelect(n.id); }} />
      )}
      <ConfirmDialog open={!!toDelete} onOpenChange={(v) => !v && setToDelete(null)} title={`Excluir "${toDelete?.title}"?`}
        description="Todos os itens filhos, blocos, relações e progresso associados também serão removidos." confirmLabel="Excluir"
        onConfirm={async () => {
          if (!toDelete) return;
          try { await api.delete(`/nodes/${toDelete.id}`); refresh(); if (selected === toDelete.id) onSelect(null); toast.success("Item excluído"); }
          catch (e) { toast.error(apiError(e)); }
        }} />
    </div>
  );
}
