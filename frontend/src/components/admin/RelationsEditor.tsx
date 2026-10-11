import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowLeft, ArrowRight, Plus, Trash2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useTaxonomy } from "@/hooks/useData";
import { Relation } from "@/types";
import { tone, cn } from "@/lib/utils";
import { ViewModel } from "@/components/student/viewModel";
import { EmptyState } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function RelationsEditor({ nodeId, vm, relations }: { nodeId: string; vm: ViewModel; relations: Relation[] }) {
  const qc = useQueryClient();
  const { list, find } = useTaxonomy();
  const [f, setF] = useState({ type: "prerequisite", target_id: "", enforced: false, note: "" });
  const refresh = () => ["node", "tree", "validate"].forEach((k) => qc.invalidateQueries({ queryKey: [k] }));
  const candidates = vm.flat.filter((n) => n.id !== nodeId);

  const add = async () => {
    if (!f.target_id) return toast.error("Selecione o item relacionado");
    try { await api.post("/relations", { ...f, node_id: nodeId }); refresh(); setF({ ...f, target_id: "", note: "" }); toast.success("Relação criada"); }
    catch (e) { toast.error(apiError(e)); }
  };
  const toggle = async (id: string, enforced: boolean) => {
    try { await api.put(`/relations/${id}`, { enforced }); refresh(); toast.success(enforced ? "Relação agora é bloqueante" : "Relação agora é apenas visual"); }
    catch (e) { toast.error(apiError(e)); }
  };
  const remove = async (id: string) => {
    try { await api.delete(`/relations/${id}`); refresh(); toast.success("Relação removida"); } catch (e) { toast.error(apiError(e)); }
  };

  return (
    <div className="space-y-6" data-testid="relations-editor">
      {!vm.track.settings.enforce_prerequisites && (
        <p data-testid="relations-free-mode-hint" className="rounded-lg border border-slate-800 bg-slate-900/40 px-4 py-2.5 text-xs text-slate-400">
          Esta trilha está em progressão livre: relações bloqueantes ficam apenas informativas até ativar "Pré-requisitos bloqueantes" em Configurações → Regras.
        </p>
      )}
      <div className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/40 p-5">
        <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">nova relação: este item →</p>
        <div className="grid gap-3 sm:grid-cols-[180px_1fr]">
          <Select value={f.type} onValueChange={(v) => setF({ ...f, type: v })}>
            <SelectTrigger data-testid="relation-type-select"><SelectValue /></SelectTrigger>
            <SelectContent>{list("relation_type").map((t) => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}</SelectContent>
          </Select>
          <Select value={f.target_id} onValueChange={(v) => setF({ ...f, target_id: v })}>
            <SelectTrigger data-testid="relation-target-select"><SelectValue placeholder="Selecione o item" /></SelectTrigger>
            <SelectContent>{candidates.map((n) => <SelectItem key={n.id} value={n.id}>{"— ".repeat(n.level)}{vm.label(n.kind)}: {n.title}</SelectItem>)}</SelectContent>
          </Select>
        </div>
        <Input data-testid="relation-note-input" placeholder="Nota (opcional)" value={f.note} onChange={(e) => setF({ ...f, note: e.target.value })} />
        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 text-xs text-slate-400">
            <Switch data-testid="relation-enforced-switch" checked={f.enforced} onCheckedChange={(v) => setF({ ...f, enforced: v })} />
            Bloqueante (trava o acesso quando a trilha usa progressão bloqueante)
          </label>
          <Button size="sm" className="rounded-full" data-testid="relation-add-button" onClick={add}><Plus />Adicionar</Button>
        </div>
      </div>
      {relations.length === 0 ? <EmptyState icon="GitBranch" title="Sem relações" description="Defina pré-requisitos, complementos e revisitas para criar trilhas não-lineares." /> : (
        <ul className="space-y-2">
          {relations.map((r) => {
            const t = find("relation_type", r.type);
            const out = r.direction === "outgoing";
            return (
              <li key={r.id} data-testid={`relation-item-${r.id}`} className="flex items-center gap-3 rounded-lg border border-slate-800 bg-slate-900/40 px-4 py-3">
                {out ? <ArrowRight className="h-4 w-4 text-slate-500" /> : <ArrowLeft className="h-4 w-4 text-slate-500" />}
                <span className={cn("rounded-md border px-2 py-0.5 text-[11px]", tone(t?.color))}>{out ? t?.label : `${t?.label} de (entrada)`}</span>
                <span className="min-w-0 flex-1 truncate text-sm text-slate-200">{r.other?.title}</span>
                {r.type === "prerequisite" && out && (
                  <label className="flex items-center gap-1.5 font-mono text-[10px] uppercase text-slate-500">
                    <Switch data-testid={`relation-enforced-toggle-${r.id}`} checked={r.enforced} onCheckedChange={(v) => toggle(r.id, v)} />
                    <span className={r.enforced ? "text-rose-300" : ""}>{r.enforced ? "bloqueante" : "visual"}</span>
                  </label>
                )}
                {r.type === "prerequisite" && !out && r.enforced && <span className="font-mono text-[10px] uppercase text-rose-400">bloqueante</span>}
                {r.note && <span className="hidden truncate text-xs text-slate-500 md:inline">{r.note}</span>}
                <button data-testid={`relation-delete-${r.id}`} onClick={() => remove(r.id)} className="text-slate-500 hover:text-rose-400"><Trash2 className="h-3.5 w-3.5" /></button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
