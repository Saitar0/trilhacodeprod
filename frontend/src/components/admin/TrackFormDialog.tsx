import React, { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, apiError } from "@/lib/api";
import { useMeta } from "@/hooks/useData";
import { Track } from "@/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type Form = Pick<Track, "title" | "subtitle" | "description" | "cover_url" | "visibility" | "difficulty" | "level_labels" | "settings"> & {
  audience: string; status: string;
};

function initial(track?: Track, labels?: Record<string, string>): Form {
  return {
    title: track?.title || "", subtitle: track?.subtitle || "", description: track?.description || "",
    cover_url: track?.cover_url || "", visibility: track?.visibility || "public", difficulty: track?.difficulty || "",
    audience: (track?.audience || []).join(", "), status: track?.status || "draft",
    level_labels: track?.level_labels || labels || {}, settings: track?.settings || { enforce_prerequisites: false, unlock_strategy: "free", visual_style: "default" },
  };
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-1.5"><Label className="text-xs text-slate-400">{label}</Label>{children}</div>;
}

export function TrackFormDialog({ open, onOpenChange, track, onSaved }: {
  open: boolean; onOpenChange: (v: boolean) => void; track?: Track; onSaved?: (t: Track) => void;
}) {
  const { data: meta } = useMeta();
  const qc = useQueryClient();
  const [f, setF] = useState<Form>(() => initial(track, meta?.default_labels));
  const [saving, setSaving] = useState(false);
  const hierarchy = track?.hierarchy || meta?.default_hierarchy || [];
  const set = <K extends keyof Form>(k: K, v: Form[K]) => setF({ ...f, [k]: v });

  const save = async () => {
    if (!f.title.trim()) return toast.error("Informe o título da trilha");
    setSaving(true);
    const body: Record<string, unknown> = { ...f, audience: f.audience.split(",").map((s) => s.trim()).filter(Boolean) };
    if (track?.status === "published" || f.status === "published") delete body.status;
    try {
      const { data } = track ? await api.put<Track>(`/tracks/${track.id}`, body) : await api.post<Track>("/tracks", body);
      qc.invalidateQueries({ queryKey: ["tracks"] });
      qc.invalidateQueries({ queryKey: ["tree", data.id] });
      toast.success(track ? "Trilha atualizada" : "Trilha criada");
      onSaved?.(data);
      onOpenChange(false);
    } catch (e) {
      toast.error(apiError(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent data-testid="track-form-dialog" className="max-h-[90vh] max-w-2xl overflow-y-auto border-slate-800 bg-slate-900">
        <DialogHeader>
          <DialogTitle>{track ? "Configurações da trilha" : "Nova trilha"}</DialogTitle>
          <DialogDescription>Metadados, nomenclatura e regras pedagógicas. Tudo editável depois.</DialogDescription>
        </DialogHeader>
        <Tabs defaultValue="geral">
          <TabsList className="bg-slate-950">
            <TabsTrigger value="geral" data-testid="track-form-tab-general">Geral</TabsTrigger>
            <TabsTrigger value="nomenclatura" data-testid="track-form-tab-labels">Nomenclatura</TabsTrigger>
            <TabsTrigger value="regras" data-testid="track-form-tab-rules">Regras</TabsTrigger>
          </TabsList>
          <TabsContent value="geral" className="grid gap-4 pt-4">
            <Field label="Título"><Input data-testid="track-form-title" value={f.title} onChange={(e) => set("title", e.target.value)} /></Field>
            <Field label="Subtítulo"><Input data-testid="track-form-subtitle" value={f.subtitle} onChange={(e) => set("subtitle", e.target.value)} /></Field>
            <Field label="Descrição (Markdown)"><Textarea data-testid="track-form-description" rows={4} value={f.description} onChange={(e) => set("description", e.target.value)} /></Field>
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="URL da capa"><Input data-testid="track-form-cover" value={f.cover_url} onChange={(e) => set("cover_url", e.target.value)} /></Field>
              <Field label="Dificuldade"><Input data-testid="track-form-difficulty" value={f.difficulty} onChange={(e) => set("difficulty", e.target.value)} /></Field>
              <Field label="Público-alvo (separado por vírgula)"><Input data-testid="track-form-audience" value={f.audience} onChange={(e) => set("audience", e.target.value)} /></Field>
              <Field label="Visibilidade">
                <Select value={f.visibility} onValueChange={(v) => set("visibility", v as Form["visibility"])}>
                  <SelectTrigger data-testid="track-form-visibility"><SelectValue /></SelectTrigger>
                  <SelectContent><SelectItem value="public">Pública (catálogo)</SelectItem><SelectItem value="private">Privada (só equipe)</SelectItem></SelectContent>
                </Select>
              </Field>
              {track?.status !== "published" && (
                <Field label="Status editorial">
                  <Select value={f.status} onValueChange={(v) => set("status", v)}>
                    <SelectTrigger data-testid="track-form-status"><SelectValue /></SelectTrigger>
                    <SelectContent><SelectItem value="draft">Rascunho</SelectItem><SelectItem value="archived">Arquivado</SelectItem></SelectContent>
                  </Select>
                </Field>
              )}
            </div>
          </TabsContent>
          <TabsContent value="nomenclatura" className="grid gap-4 pt-4 sm:grid-cols-2">
            {hierarchy.map((k, i) => (
              <Field key={k} label={`Nível ${i + 1} (${k})`}>
                <Input data-testid={`track-form-label-${k}`} value={f.level_labels[k] || ""} onChange={(e) => set("level_labels", { ...f.level_labels, [k]: e.target.value })} />
              </Field>
            ))}
          </TabsContent>
          <TabsContent value="regras" className="grid gap-5 pt-4">
            <label className="flex items-center justify-between gap-4 rounded-lg border border-slate-800 p-4">
              <span><span className="block text-sm font-medium text-slate-200">Pré-requisitos bloqueantes</span>
                <span className="text-xs text-slate-400">Quando ativo, tópicos com pré-requisitos marcados como bloqueantes ficam travados para alunos até serem cumpridos.</span></span>
              <Switch data-testid="track-form-enforce" checked={!!f.settings.enforce_prerequisites} onCheckedChange={(v) => set("settings", { ...f.settings, enforce_prerequisites: v })} />
            </label>
            <p data-testid="track-form-coming-soon" className="rounded-lg border border-dashed border-slate-700 p-4 text-xs text-slate-400">
              <span className="mr-2 rounded-full border border-slate-600 px-2 py-0.5 font-mono text-[10px] uppercase text-slate-300">em breve</span>
              Liberação sequencial ou por datas e estilos visuais de trilha ainda não estão ativos e por isso não aparecem aqui.
            </p>
          </TabsContent>
        </Tabs>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)}>Cancelar</Button>
          <Button data-testid="track-form-save" className="rounded-full" disabled={saving} onClick={save}>{track ? "Salvar alterações" : "Criar trilha"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
