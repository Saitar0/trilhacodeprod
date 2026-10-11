import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Plus, Trash2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useMeta } from "@/hooks/useData";
import { TaxonomyItem } from "@/types";
import { cn, TONE_KEYS, tone } from "@/lib/utils";
import { DynamicIcon, Loader, PageHeader } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const GROUPS: [string, string][] = [["pedagogical_type", "Tipos pedagógicos"], ["requirement", "Caráter"], ["depth", "Profundidade"], ["relation_type", "Tipos de relação"]];

function ColorSelect({ value, onChange, testId }: { value: string; onChange: (v: string) => void; testId: string }) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger data-testid={testId} className="w-32"><SelectValue /></SelectTrigger>
      <SelectContent>{TONE_KEYS.map((c) => <SelectItem key={c} value={c}>{c}</SelectItem>)}</SelectContent>
    </Select>
  );
}

function TaxRow({ t, editable, onChange }: { t: TaxonomyItem; editable: boolean; onChange: () => void }) {
  const [label, setLabel] = useState(t.label);
  const update = async (body: Partial<TaxonomyItem>) => {
    try { await api.put(`/taxonomies/${t.id}`, body); onChange(); toast.success("Taxonomia atualizada"); } catch (e) { toast.error(apiError(e)); }
  };
  return (
    <div data-testid={`taxonomy-row-${t.group}-${t.key}`} className="flex items-center gap-3 border-b border-slate-800 px-4 py-3 last:border-0">
      <span className={cn("rounded-md border px-2 py-0.5 text-[11px]", tone(t.color))}>{t.label}</span>
      <span className="font-mono text-[11px] text-slate-500">{t.key}</span>
      <span className="hidden flex-1 truncate text-xs text-slate-400 md:block">{t.description}</span>
      {editable && (
        <div className="ml-auto flex items-center gap-2">
          <Input value={label} onChange={(e) => setLabel(e.target.value)} onBlur={() => label !== t.label && update({ label })} className="h-8 w-40 text-xs" data-testid={`taxonomy-label-${t.key}`} />
          <ColorSelect value={t.color} onChange={(color) => update({ color })} testId={`taxonomy-color-${t.key}`} />
          <button data-testid={`taxonomy-delete-${t.key}`} onClick={async () => { await api.delete(`/taxonomies/${t.id}`); onChange(); }} className="text-slate-500 hover:text-rose-400"><Trash2 className="h-4 w-4" /></button>
        </div>
      )}
    </div>
  );
}

function AddTax({ group, onDone }: { group: string; onDone: () => void }) {
  const [f, setF] = useState({ key: "", label: "", color: "slate", description: "" });
  const add = async () => {
    try { await api.post("/taxonomies", { ...f, group, order: 99 }); setF({ key: "", label: "", color: "slate", description: "" }); onDone(); toast.success("Item criado"); }
    catch (e) { toast.error(apiError(e)); }
  };
  return (
    <div className="flex flex-wrap items-center gap-2 border-t border-slate-800 bg-slate-950/40 px-4 py-3">
      <Input placeholder="chave" value={f.key} onChange={(e) => setF({ ...f, key: e.target.value })} className="h-8 w-32 font-mono text-xs" data-testid={`taxonomy-new-key-${group}`} />
      <Input placeholder="Rótulo" value={f.label} onChange={(e) => setF({ ...f, label: e.target.value })} className="h-8 w-44 text-xs" data-testid={`taxonomy-new-label-${group}`} />
      <Input placeholder="Descrição" value={f.description} onChange={(e) => setF({ ...f, description: e.target.value })} className="h-8 flex-1 text-xs" />
      <ColorSelect value={f.color} onChange={(color) => setF({ ...f, color })} testId={`taxonomy-new-color-${group}`} />
      <Button size="sm" onClick={add} data-testid={`taxonomy-add-${group}`}><Plus />Adicionar</Button>
    </div>
  );
}

export default function Taxonomies() {
  const { data: meta, isLoading } = useMeta();
  const { can } = useAuth();
  const qc = useQueryClient();
  const [tag, setTag] = useState("");
  const refresh = () => qc.invalidateQueries({ queryKey: ["meta"] });
  const admin = can("taxonomy.manage");
  if (isLoading || !meta) return <Loader />;

  return (
    <div className="max-w-5xl">
      <PageHeader eyebrow="modelo pedagógico" title="Taxonomias & blocos"
        description="Vocabulário editorial orientado a dados: renomeie, recolora e expanda sem alterar código." />
      <Tabs defaultValue="pedagogical_type">
        <TabsList className="flex-wrap bg-slate-900">
          {GROUPS.map(([k, l]) => <TabsTrigger key={k} value={k} data-testid={`taxonomy-tab-${k}`}>{l}</TabsTrigger>)}
          <TabsTrigger value="tags" data-testid="taxonomy-tab-tags">Tags</TabsTrigger>
          <TabsTrigger value="blocks" data-testid="taxonomy-tab-blocks">Tipos de bloco</TabsTrigger>
        </TabsList>
        {GROUPS.map(([k]) => (
          <TabsContent key={k} value={k} className="mt-6 overflow-hidden rounded-xl border border-slate-800 bg-slate-900/40">
            {(meta.taxonomies[k] || []).map((t) => <TaxRow key={t.id} t={t} editable={admin} onChange={refresh} />)}
            {admin && <AddTax group={k} onDone={refresh} />}
          </TabsContent>
        ))}
        <TabsContent value="tags" className="mt-6 space-y-4">
          <div className="flex gap-2">
            <Input data-testid="tag-new-input" placeholder="Nova tag" value={tag} onChange={(e) => setTag(e.target.value)} className="max-w-xs" />
            <Button data-testid="tag-add-button" onClick={async () => {
              try { await api.post("/tags", { name: tag }); setTag(""); refresh(); toast.success("Tag criada"); } catch (e) { toast.error(apiError(e)); }
            }}><Plus />Criar tag</Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {meta.tags.map((t) => (
              <span key={t.id} data-testid={`tag-chip-${t.slug}`} className={cn("flex items-center gap-2 rounded-full border px-3 py-1 text-xs", tone(t.color))}>
                #{t.name}<button data-testid={`tag-delete-${t.slug}`} onClick={async () => { await api.delete(`/tags/${t.id}`); refresh(); }}><Trash2 className="h-3 w-3" /></button>
              </span>
            ))}
          </div>
        </TabsContent>
        <TabsContent value="blocks" className="mt-6 grid gap-3 md:grid-cols-2">
          {meta.block_types.map((b) => (
            <div key={b.id} data-testid={`block-type-card-${b.key}`} className="rounded-xl border border-slate-800 bg-slate-900/40 p-4">
              <div className="flex items-center gap-3">
                <DynamicIcon name={b.icon} className="h-4 w-4 text-emerald-400" />
                <span className="font-medium text-slate-100">{b.label}</span>
                <span className="font-mono text-[10px] text-slate-500">{b.key}</span>
                {admin && <Switch className="ml-auto" data-testid={`block-type-enabled-${b.key}`} checked={b.enabled}
                  onCheckedChange={async (v) => { await api.put(`/block-types/${b.id}`, { enabled: v }); refresh(); }} />}
              </div>
              <p className="mt-3 font-mono text-[11px] text-slate-500">{b.fields.map((f) => `${f.name}:${f.type}`).join(" · ")}</p>
            </div>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}
