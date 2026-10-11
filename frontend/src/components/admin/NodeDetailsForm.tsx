import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Save } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useMeta } from "@/hooks/useData";
import { TrackNode } from "@/types";
import { cn, STATUS_META, tone } from "@/lib/utils";
import { flatten } from "@/lib/tree";
import { ViewModel } from "@/components/student/viewModel";
import { NONE, TaxSelect } from "@/components/admin/CreateNodeDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const FIELDS = ["title", "summary", "description", "guidance", "notes", "pedagogical_type", "requirement", "depth", "status",
  "estimated_minutes", "tag_ids", "parent_id"] as const;

function Field({ label, hint, children, className }: { label: string; hint?: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("space-y-1.5", className)}>
      <Label className="text-xs text-slate-400">{label}</Label>{children}
      {hint && <p className="text-[11px] text-slate-500">{hint}</p>}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <fieldset className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/40 p-5">
      <legend className="px-2 font-mono text-[10px] uppercase tracking-widest text-slate-500">{title}</legend>{children}
    </fieldset>
  );
}

export function NodeDetailsForm({ node, vm }: { node: TrackNode; vm: ViewModel }) {
  const qc = useQueryClient();
  const { data: meta } = useMeta();
  const pick = (n: TrackNode) => Object.fromEntries(FIELDS.map((k) => [k, n[k] ?? ""])) as Pick<TrackNode, typeof FIELDS[number]>;
  const [f, setF] = useState(() => pick(node));
  const [saving, setSaving] = useState(false);
  const dirty = JSON.stringify(f) !== JSON.stringify(pick(node));
  const set = <K extends keyof typeof f>(k: K, v: (typeof f)[K]) => setF({ ...f, [k]: v });
  const h = vm.track.hierarchy;
  const self = vm.byId.get(node.id);
  const excluded = new Set(self ? flatten([self]).map((n) => n.id) : [node.id]);
  const parents = vm.flat.filter((n) => !excluded.has(n.id) && h.indexOf(n.kind) < h.indexOf(node.kind));

  const save = async () => {
    setSaving(true);
    try {
      await api.put(`/nodes/${node.id}`, { ...f, parent_id: f.parent_id || null, estimated_minutes: Number(f.estimated_minutes) || 0 });
      qc.invalidateQueries({ queryKey: ["tree", node.track_id] });
      qc.invalidateQueries({ queryKey: ["node", node.id] });
      toast.success("Alterações salvas");
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6" data-testid="node-details-form">
      <Section title="identidade">
        <Field label="Título"><Input data-testid="node-title-input" value={f.title} onChange={(e) => set("title", e.target.value)} /></Field>
        <Field label="Resumo curto"><Input data-testid="node-summary-input" value={f.summary} onChange={(e) => set("summary", e.target.value)} /></Field>
        <Field label="Descrição (Markdown)"><Textarea data-testid="node-description-input" rows={5} value={f.description} onChange={(e) => set("description", e.target.value)} /></Field>
      </Section>
      <Section title="pedagogia">
        <div className="grid gap-4 sm:grid-cols-3">
          <Field label="Tipo pedagógico"><TaxSelect group="pedagogical_type" value={f.pedagogical_type} onChange={(v) => set("pedagogical_type", v)} testId="node-pedagogical-type-select" placeholder="Tipo" /></Field>
          <Field label="Caráter"><TaxSelect group="requirement" value={f.requirement} onChange={(v) => set("requirement", v)} testId="node-requirement-select" placeholder="Caráter" /></Field>
          <Field label="Profundidade"><TaxSelect group="depth" value={f.depth} onChange={(v) => set("depth", v)} testId="node-depth-select" placeholder="Profundidade" /></Field>
        </div>
        <Field label="Orientação de estudo (visível ao aluno)"><Textarea data-testid="node-guidance-input" rows={3} value={f.guidance} onChange={(e) => set("guidance", e.target.value)} /></Field>
        <Field label="Notas internas (apenas equipe)" hint="Nunca exibidas ao estudante."><Textarea data-testid="node-notes-input" rows={3} value={f.notes} onChange={(e) => set("notes", e.target.value)} /></Field>
        <Field label="Tags">
          <div className="flex flex-wrap gap-2">
            {(meta?.tags || []).map((t) => {
              const on = f.tag_ids.includes(t.id);
              return (
                <button key={t.id} type="button" data-testid={`node-tag-toggle-${t.slug}`}
                  onClick={() => set("tag_ids", on ? f.tag_ids.filter((x) => x !== t.id) : [...f.tag_ids, t.id])}
                  className={cn("rounded-full border px-3 py-1 text-xs transition-colors", on ? tone(t.color) : "border-slate-800 text-slate-500 hover:text-slate-300")}>
                  #{t.name}
                </button>
              );
            })}
            {!meta?.tags.length && <span className="text-xs text-slate-500">Crie tags em Taxonomias.</span>}
          </div>
        </Field>
      </Section>
      <Section title="organização e publicação">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Status editorial">
            <Select value={f.status} onValueChange={(v) => set("status", v as TrackNode["status"])}>
              <SelectTrigger data-testid="node-status-select"><SelectValue /></SelectTrigger>
              <SelectContent>{Object.entries(STATUS_META).map(([k, m]) => <SelectItem key={k} value={k}>{m.label}</SelectItem>)}</SelectContent>
            </Select>
          </Field>
          <Field label="Pai (mover na hierarquia)">
            <Select value={f.parent_id || NONE} onValueChange={(v) => set("parent_id", v === NONE ? null : v)}>
              <SelectTrigger data-testid="node-parent-select"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value={NONE}>(raiz da trilha)</SelectItem>
                {parents.map((p) => <SelectItem key={p.id} value={p.id}>{"— ".repeat(p.level)}{vm.label(p.kind)}: {p.title}</SelectItem>)}
              </SelectContent>
            </Select>
          </Field>
          <Field label="Tempo estimado (min)"><Input data-testid="node-minutes-input" type="number" value={f.estimated_minutes} onChange={(e) => set("estimated_minutes", Number(e.target.value))} /></Field>
          <div className="flex items-end pb-2 text-[11px] text-slate-500" data-testid="node-release-coming-soon">
            <span className="mr-2 rounded-full border border-slate-700 px-2 py-0.5 font-mono text-[10px] uppercase">em breve</span>liberação por data
          </div>
        </div>
      </Section>
      <div className="sticky bottom-0 flex items-center justify-end gap-3 border-t border-slate-800 bg-[#090D16]/90 py-4 backdrop-blur">
        {dirty && <span data-testid="node-unsaved-indicator" className="text-xs text-amber-400">Alterações não salvas</span>}
        <Button data-testid="node-save-button" className="rounded-full" disabled={!dirty || saving} onClick={save}><Save />Salvar</Button>
      </div>
    </div>
  );
}
