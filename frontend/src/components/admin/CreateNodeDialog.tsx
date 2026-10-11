import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, apiError } from "@/lib/api";
import { useTaxonomy } from "@/hooks/useData";
import { TrackNode, TreeNode } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export const NONE = "__none";

export function TaxSelect({ group, value, onChange, testId, placeholder }: {
  group: string; value: string; onChange: (v: string) => void; testId: string; placeholder: string;
}) {
  const { list } = useTaxonomy();
  return (
    <Select value={value || NONE} onValueChange={(v) => onChange(v === NONE ? "" : v)}>
      <SelectTrigger data-testid={testId}><SelectValue placeholder={placeholder} /></SelectTrigger>
      <SelectContent>
        <SelectItem value={NONE}>— {placeholder}</SelectItem>
        {list(group).map((t) => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}
      </SelectContent>
    </Select>
  );
}

export function CreateNodeDialog({ trackId, parent, kinds, label, onClose, onCreated }: {
  trackId: string; parent: TreeNode | null; kinds: string[]; label: (k: string) => string;
  onClose: () => void; onCreated: (n: TrackNode) => void;
}) {
  const qc = useQueryClient();
  const [f, setF] = useState({ title: "", kind: kinds[0], pedagogical_type: "", requirement: "", depth: "" });
  const [count, setCount] = useState(0);
  const set = (k: keyof typeof f) => (v: string) => setF({ ...f, [k]: v });

  const create = async (another: boolean) => {
    if (!f.title.trim()) return toast.error("Informe um título");
    try {
      const { data } = await api.post<TrackNode>("/nodes", { ...f, track_id: trackId, parent_id: parent?.id || null });
      qc.invalidateQueries({ queryKey: ["tree", trackId] });
      toast.success(`${label(f.kind)} criado`);
      setCount(count + 1);
      if (another) setF({ ...f, title: "" });
      else onCreated(data);
    } catch (e) {
      toast.error(apiError(e));
    }
  };

  return (
    <Dialog open onOpenChange={(v) => !v && onClose()}>
      <DialogContent data-testid="create-node-dialog" className="border-slate-800 bg-slate-900">
        <DialogHeader>
          <DialogTitle>Adicionar {label(f.kind).toLowerCase()}</DialogTitle>
          <DialogDescription>{parent ? `Dentro de "${parent.title}"` : "Na raiz da trilha"}{count > 0 && ` · ${count} criado(s) nesta sessão`}</DialogDescription>
        </DialogHeader>
        <form className="grid gap-4" onSubmit={(e) => { e.preventDefault(); create(false); }}>
          <div className="space-y-1.5"><Label className="text-xs text-slate-400">Título</Label>
            <Input autoFocus data-testid="create-node-title" value={f.title} onChange={(e) => set("title")(e.target.value)} /></div>
          {kinds.length > 1 && (
            <div className="space-y-1.5"><Label className="text-xs text-slate-400">Nível</Label>
              <Select value={f.kind} onValueChange={set("kind")}>
                <SelectTrigger data-testid="create-node-kind"><SelectValue /></SelectTrigger>
                <SelectContent>{kinds.map((k) => <SelectItem key={k} value={k}>{label(k)}</SelectItem>)}</SelectContent>
              </Select></div>
          )}
          <div className="grid gap-3 sm:grid-cols-3">
            <TaxSelect group="pedagogical_type" value={f.pedagogical_type} onChange={set("pedagogical_type")} testId="create-node-type" placeholder="Tipo" />
            <TaxSelect group="requirement" value={f.requirement} onChange={set("requirement")} testId="create-node-requirement" placeholder="Caráter" />
            <TaxSelect group="depth" value={f.depth} onChange={set("depth")} testId="create-node-depth" placeholder="Profundidade" />
          </div>
          <DialogFooter className="gap-2">
            <Button type="button" variant="outline" data-testid="create-node-another" onClick={() => create(true)}>Criar e adicionar outro</Button>
            <Button type="submit" className="rounded-full" data-testid="create-node-submit">Criar</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
