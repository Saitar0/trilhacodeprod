import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowDown, ArrowUp, ChevronDown, Eye, Plus, Save, Trash2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useMeta } from "@/hooks/useData";
import { BlockType, ContentBlock } from "@/types";
import { cn, STATUS_META } from "@/lib/utils";
import { DynamicIcon, EmptyState, StatusBadge } from "@/components/common";
import { BlockFieldsForm, cleanBlockData } from "@/components/blocks/BlockFieldsForm";
import { BlockRenderer } from "@/components/blocks/BlockRenderer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const CATEGORY: Record<string, string> = { teoria: "Teoria", pratica: "Prática", avaliacao: "Avaliação", recurso: "Recursos", orientacao: "Orientação" };

function BlockItem({ block, type, open, toggle, move, onSaved, onDelete }: {
  block: ContentBlock; type?: BlockType; open: boolean; toggle: () => void; move: (d: -1 | 1) => void; onSaved: () => void; onDelete: () => void;
}) {
  const [title, setTitle] = useState(block.title);
  const [data, setData] = useState(block.data);
  const [status, setStatus] = useState(block.status);
  const [preview, setPreview] = useState(false);
  const save = async () => {
    try {
      await api.put(`/blocks/${block.id}`, { title, status, data: cleanBlockData(type?.fields || [], data) });
      toast.success("Bloco salvo");
      onSaved();
    } catch (e) { toast.error(apiError(e)); }
  };
  return (
    <div data-testid={`block-item-${block.id}`} className={cn("rounded-xl border bg-slate-900/50", open ? "border-slate-700" : "border-slate-800")}>
      <div className="flex items-center gap-3 px-4 py-3">
        <DynamicIcon name={type?.icon} className="h-4 w-4 text-emerald-400" />
        <button onClick={toggle} data-testid={`block-toggle-${block.id}`} className="flex min-w-0 flex-1 items-center gap-2 text-left">
          <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{type?.label || block.type}</span>
          <span className="truncate text-sm text-slate-200">{block.title || "Sem título"}</span>
          <ChevronDown className={cn("h-3.5 w-3.5 text-slate-500 transition-transform", open && "rotate-180")} />
        </button>
        <StatusBadge status={block.status} testId={`block-status-${block.id}`} />
        <button data-testid={`block-up-${block.id}`} onClick={() => move(-1)} className="text-slate-500 hover:text-slate-100"><ArrowUp className="h-3.5 w-3.5" /></button>
        <button data-testid={`block-down-${block.id}`} onClick={() => move(1)} className="text-slate-500 hover:text-slate-100"><ArrowDown className="h-3.5 w-3.5" /></button>
        <button data-testid={`block-delete-${block.id}`} onClick={onDelete} className="text-slate-500 hover:text-rose-400"><Trash2 className="h-3.5 w-3.5" /></button>
      </div>
      {open && (
        <div className="space-y-4 border-t border-slate-800 p-4">
          <div className="grid gap-3 sm:grid-cols-[1fr_160px]">
            <Input data-testid={`block-title-${block.id}`} placeholder="Título do bloco (opcional)" value={title} onChange={(e) => setTitle(e.target.value)} />
            <Select value={status} onValueChange={(v) => setStatus(v as ContentBlock["status"])}>
              <SelectTrigger data-testid={`block-status-select-${block.id}`}><SelectValue /></SelectTrigger>
              <SelectContent>{Object.entries(STATUS_META).map(([k, m]) => <SelectItem key={k} value={k}>{m.label}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          {preview ? <BlockRenderer block={{ ...block, title, data: cleanBlockData(type?.fields || [], data) }} type={type} />
            : <BlockFieldsForm fields={type?.fields || []} value={data} onChange={setData} idPrefix={`block-${block.id}`} />}
          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" data-testid={`block-preview-${block.id}`} onClick={() => setPreview(!preview)}><Eye />{preview ? "Editar" : "Pré-visualizar"}</Button>
            <Button size="sm" className="rounded-full" data-testid={`block-save-${block.id}`} onClick={save}><Save />Salvar bloco</Button>
          </div>
        </div>
      )}
    </div>
  );
}

export function BlocksEditor({ nodeId, trackId, blocks }: { nodeId: string; trackId: string; blocks: ContentBlock[] }) {
  const qc = useQueryClient();
  const { data: meta } = useMeta();
  const [openId, setOpenId] = useState<string | null>(null);
  const types = (meta?.block_types || []).filter((b) => b.enabled);
  const categories = Array.from(new Set(types.map((t) => t.category)));
  const refresh = () => { qc.invalidateQueries({ queryKey: ["node", nodeId] }); qc.invalidateQueries({ queryKey: ["tree", trackId] }); };

  const add = async (t: BlockType) => {
    try {
      const { data } = await api.post<ContentBlock>("/blocks", { node_id: nodeId, type: t.key, title: "", data: {} });
      refresh();
      setOpenId(data.id);
      toast.success(`Bloco "${t.label}" adicionado`);
    } catch (e) { toast.error(apiError(e)); }
  };
  const move = async (i: number, d: -1 | 1) => {
    const ids = blocks.map((b) => b.id);
    if (i + d < 0 || i + d >= ids.length) return;
    [ids[i], ids[i + d]] = [ids[i + d], ids[i]];
    await api.post("/blocks/reorder", { ordered_ids: ids });
    refresh();
  };
  const remove = async (id: string) => {
    try { await api.delete(`/blocks/${id}`); refresh(); toast.success("Bloco removido"); } catch (e) { toast.error(apiError(e)); }
  };

  return (
    <div className="space-y-4" data-testid="blocks-editor">
      {blocks.length === 0 && <EmptyState icon="Boxes" title="Nenhum bloco de conteúdo" description="Blocos são reutilizáveis e tipados: teoria, checklist, quiz, código, vídeo e mais." />}
      {blocks.map((b, i) => (
        <BlockItem key={b.id} block={b} type={meta?.block_types.find((t) => t.key === b.type)} open={openId === b.id}
          toggle={() => setOpenId(openId === b.id ? null : b.id)} move={(d) => move(i, d)} onSaved={refresh} onDelete={() => remove(b.id)} />
      ))}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="w-full border-dashed" data-testid="add-block-button"><Plus />Adicionar bloco</Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="max-h-96 w-72 overflow-y-auto border-slate-800 bg-slate-900">
          {categories.map((c, ci) => (
            <React.Fragment key={c}>
              {ci > 0 && <DropdownMenuSeparator />}
              <DropdownMenuLabel className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{CATEGORY[c] || c}</DropdownMenuLabel>
              {types.filter((t) => t.category === c).map((t) => (
                <DropdownMenuItem key={t.key} data-testid={`add-block-type-${t.key}`} onClick={() => add(t)}>
                  <DynamicIcon name={t.icon} className="mr-2 h-4 w-4 text-emerald-400" />{t.label}
                </DropdownMenuItem>
              ))}
            </React.Fragment>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
