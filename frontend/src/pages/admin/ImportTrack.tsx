import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { AlertTriangle, CheckCircle2, FileUp, FlaskConical, Upload, XCircle } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { Track } from "@/types";
import { PageHeader } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface Issue { path: string; message: string }
interface Report {
  ok: boolean; dry_run: boolean; errors: Issue[]; warnings: Issue[]; track?: Track;
  summary: { track: string; nodes_create: number; nodes_update: number; nodes_untouched: number; blocks: number; relations: number; tags_create: string[] };
}

const EXAMPLE = {
  track: { slug: "minha-trilha", title: "Minha trilha", subtitle: "", description: "", visibility: "public",
    level_labels: { phase: "Fase", module: "Módulo", submodule: "Submódulo", topic: "Tópico" }, settings: { enforce_prerequisites: true } },
  options: { create_missing_tags: true },
  nodes: [{ ref: "f1", kind: "phase", title: "Fase 1", status: "draft", children: [
    { ref: "f1-m1", kind: "module", title: "Módulo 1", children: [
      { ref: "f1-m1-t1", kind: "topic", title: "Tópico 1", pedagogical_type: "solo", requirement: "obrigatorio", depth: "alta",
        estimated_minutes: 30, tags: ["fundamentos"], summary: "", blocks: [{ ref: "intro", type: "theory_text", data: { body: "## Introdução" } }] },
      { ref: "f1-m1-t2", kind: "topic", title: "Tópico 2" }] }] }],
  relations: [{ from: "f1-m1-t2", to: "f1-m1-t1", type: "prerequisite", enforced: true }],
};

function IssueList({ items, tone }: { items: Issue[]; tone: "error" | "warning" }) {
  if (!items.length) return null;
  const Icon = tone === "error" ? XCircle : AlertTriangle;
  return (
    <ul data-testid={`import-${tone}s`} className="max-h-72 space-y-1.5 overflow-y-auto scrollbar-thin">
      {items.map((i, k) => (
        <li key={k} className={tone === "error" ? "flex gap-2 text-xs text-rose-200" : "flex gap-2 text-xs text-amber-200"}>
          <Icon className="mt-0.5 h-3.5 w-3.5 shrink-0" /><span className="font-mono text-slate-500">{i.path}</span>{i.message}
        </li>
      ))}
    </ul>
  );
}

export default function ImportTrack() {
  const qc = useQueryClient();
  const [text, setText] = useState("");
  const [report, setReport] = useState<Report | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async (dry: boolean) => {
    let payload: unknown;
    try { payload = JSON.parse(text); } catch (e) { return toast.error(`JSON inválido: ${(e as Error).message}`); }
    setBusy(true);
    try {
      const { data } = await api.post<Report>(`/import/track?dry_run=${dry}`, payload);
      setReport(data);
      if (!dry && !data.dry_run) {
        qc.invalidateQueries({ queryKey: ["tracks"] });
        qc.invalidateQueries({ queryKey: ["meta"] });
        toast.success("Importação concluída");
      } else toast.info(data.ok ? "Simulação válida — revise e confirme" : "Há erros a corrigir");
    } catch (e) { toast.error(apiError(e)); } finally { setBusy(false); }
  };
  const onFile = async (f?: File) => { if (f) { setText(await f.text()); setReport(null); } };
  const s = report?.summary;

  return (
    <div className="max-w-6xl">
      <PageHeader eyebrow="cadastro em lote" title="Importar estrutura"
        description="Cole ou envie um JSON com trilha, itens, relações e blocos. Sempre simule antes; reimportar o mesmo arquivo atualiza em vez de duplicar (chave: track.slug + ref de cada item)." />
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-3" data-testid="import-form">
          <div className="flex flex-wrap gap-2">
            <label className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-slate-700 px-4 py-1.5 text-sm text-slate-200 hover:border-slate-500">
              <Upload className="h-4 w-4" />Enviar arquivo .json
              <input data-testid="import-file-input" type="file" accept=".json,application/json" className="hidden" onChange={(e) => onFile(e.target.files?.[0])} />
            </label>
            <Button variant="ghost" size="sm" data-testid="import-load-example" onClick={() => { setText(JSON.stringify(EXAMPLE, null, 2)); setReport(null); }}>Carregar modelo</Button>
          </div>
          <label htmlFor="import-json-input" className="text-sm font-medium text-slate-200">JSON da trilha</label>
          <Textarea id="import-json-input" data-testid="import-json-input" rows={24} className="font-mono text-xs" placeholder="{ &quot;track&quot;: {...}, &quot;nodes&quot;: [...], &quot;relations&quot;: [...] }"
            value={text} onChange={(e) => { setText(e.target.value); setReport(null); }} />
          <div className="flex justify-end gap-2">
            <Button variant="outline" disabled={!text || busy} data-testid="import-dry-run-button" onClick={() => run(true)}><FlaskConical />Simular</Button>
            <Button className="rounded-full" disabled={!report?.ok || !report.dry_run || busy} data-testid="import-confirm-button" onClick={() => run(false)}><FileUp />Confirmar importação</Button>
          </div>
        </div>
        <aside className="space-y-4" data-testid="import-report">
          {!report ? <p className="rounded-xl border border-dashed border-slate-700 p-5 text-sm text-slate-400">O relatório da simulação aparece aqui. A importação só é liberada sem erros.</p> : (
            <>
              <p data-testid="import-status" className={report.ok ? "flex items-center gap-2 text-sm font-semibold text-emerald-300" : "flex items-center gap-2 text-sm font-semibold text-rose-300"}>
                {report.ok ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                {!report.dry_run ? "Importado" : report.ok ? "Simulação válida" : `${report.errors.length} erro(s)`}
              </p>
              {s && (
                <dl className="grid grid-cols-2 gap-2 rounded-xl border border-slate-800 bg-slate-900/50 p-4 font-mono text-xs text-slate-400" data-testid="import-summary">
                  <dt>trilha</dt><dd className="text-slate-100">{s.track}</dd>
                  <dt>itens novos</dt><dd className="text-slate-100">{s.nodes_create}</dd>
                  <dt>itens atualizados</dt><dd className="text-slate-100">{s.nodes_update}</dd>
                  <dt>fora do arquivo</dt><dd className="text-slate-100">{s.nodes_untouched}</dd>
                  <dt>blocos</dt><dd className="text-slate-100">{s.blocks}</dd>
                  <dt>relações</dt><dd className="text-slate-100">{s.relations}</dd>
                  <dt>tags novas</dt><dd className="text-slate-100">{s.tags_create.join(", ") || "—"}</dd>
                </dl>
              )}
              <IssueList items={report.errors} tone="error" />
              <IssueList items={report.warnings} tone="warning" />
              {report.track && <Button asChild variant="outline" size="sm" data-testid="import-open-track"><Link to={`/admin/trilhas/${report.track.id}`}>Abrir no editor</Link></Button>}
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
