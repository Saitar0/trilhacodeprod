import React, { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { CheckCircle2, CornerUpLeft, Play, Search, XCircle } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useMeta } from "@/hooks/useData";
import { ContentBlock, CriterionGrade, Submission, Track } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { EmptyState, Loader, Markdown, PageHeader } from "@/components/common";
import { RESULT_META, SubmissionBadge } from "@/components/common/SubmissionBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const STATUS_TABS: [string, string][] = [["submitted", "Enviadas"], ["in_review", "Em correção"], ["returned", "Devolvidas"], ["graded", "Corrigidas"]];
const ALL = "__all";

interface Detail { submission: Submission; block: ContentBlock | null; attempts: Submission[] }

function RubricEditor({ criteria, setCriteria }: { criteria: CriterionGrade[]; setCriteria: (c: CriterionGrade[]) => void }) {
  const set = (i: number, patch: Partial<CriterionGrade>) => setCriteria(criteria.map((c, j) => (j === i ? { ...c, ...patch } : c)));
  return (
    <div className="space-y-2" data-testid="rubric-editor">
      {criteria.map((c, i) => (
        <div key={i} className="grid gap-2 rounded-lg border border-slate-800 bg-slate-950/40 p-3 sm:grid-cols-[1fr_auto]">
          <p className="text-sm text-slate-200">{c.criterion}</p>
          <div className="flex gap-1">
            <button data-testid={`rubric-met-${i}`} onClick={() => set(i, { met: true })} className={cn("rounded-md border px-2 py-1 text-xs", c.met === true ? "border-emerald-500/60 bg-emerald-500/15 text-emerald-200" : "border-slate-700 text-slate-400")}>Atende</button>
            <button data-testid={`rubric-unmet-${i}`} onClick={() => set(i, { met: false })} className={cn("rounded-md border px-2 py-1 text-xs", c.met === false ? "border-rose-500/60 bg-rose-500/15 text-rose-200" : "border-slate-700 text-slate-400")}>Não atende</button>
          </div>
          <Input data-testid={`rubric-comment-${i}`} placeholder="Comentário do critério" value={c.comment} onChange={(e) => set(i, { comment: e.target.value })} className="h-8 text-xs sm:col-span-2" />
        </div>
      ))}
    </div>
  );
}

function GradingPanel({ id, onDone }: { id: string; onDone: () => void }) {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["submission", id], queryFn: () => api.get<Detail>(`/submissions/${id}`).then((r) => r.data) });
  const [feedback, setFeedback] = useState("");
  const [score, setScore] = useState("");
  const [criteria, setCriteria] = useState<CriterionGrade[]>([]);
  useEffect(() => {
    if (!data) return;
    const g = data.submission.grading;
    const names: string[] = (data.block?.data.criteria as string[]) || [];
    setFeedback(g?.feedback || "");
    setScore(g?.score != null ? String(g.score) : "");
    setCriteria(names.map((n) => g?.criteria.find((c) => c.criterion === n) || { criterion: n, met: null, comment: "" }));
  }, [data]);
  if (isLoading || !data) return <Loader />;
  const { submission: s, block, attempts } = data;
  const gradable = s.status === "submitted" || s.status === "in_review";
  const refresh = () => { qc.invalidateQueries({ queryKey: ["submissions"] }); qc.invalidateQueries({ queryKey: ["submission", id] }); };
  const act = async (fn: () => Promise<unknown>, msg: string) => {
    try { await fn(); refresh(); toast.success(msg); onDone(); } catch (e) { toast.error(apiError(e)); }
  };
  const grade = (result: string) => act(() => api.post(`/submissions/${id}/grade`, { result, feedback, criteria, score: score === "" ? null : Number(score) }),
    result === "approved" ? "Aprovado" : result === "rejected" ? "Reprovado" : "Devolvido para ajuste");

  return (
    <div className="space-y-6 fade-up" data-testid="grading-panel">
      <header className="space-y-2">
        <div className="flex items-center gap-2"><SubmissionBadge status={s.status} testId="grading-status" /><span className="font-mono text-[11px] text-slate-500">tentativa {s.attempt} · enviada {formatDate(s.submitted_at)}</span></div>
        <h2 className="text-xl font-bold text-slate-50">{s.block_title || "Exercício"} <span className="text-base font-normal text-slate-400">· {s.node_title}</span></h2>
        <p className="text-sm text-slate-400">Aluno: <span className="text-slate-200">{s.user_name}</span>{s.reviewer_name && ` · corretor: ${s.reviewer_name}`}</p>
      </header>
      {!block && <p data-testid="grading-orphan-notice" className="rounded-lg border border-dashed border-slate-700 p-4 text-sm text-slate-400">Este exercício foi removido da trilha (registro órfão). A resposta é mantida para histórico; ela volta a ficar ativa se o conteúdo for restaurado.</p>}
      {block && <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-5"><p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-slate-500">enunciado</p><Markdown>{block.data.prompt}</Markdown>
        {block.data.rubric && <><p className="mb-1 mt-4 font-mono text-[10px] uppercase tracking-widest text-slate-500">orientações de correção</p><Markdown className="text-sm">{block.data.rubric}</Markdown></>}
        {block.data.answer && <p className="mt-3 text-xs text-slate-400">Resposta esperada: <span className="text-slate-200">{block.data.answer}</span></p>}</div>}
      <div className="rounded-xl border border-sky-500/20 bg-sky-500/[0.03] p-5" data-testid="grading-answer">
        <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-sky-300">resposta do aluno</p>
        <Markdown>{s.answer.text}</Markdown>
        {s.answer.code && <pre className="mt-3 overflow-x-auto rounded-lg bg-slate-950 p-4 font-mono text-xs text-emerald-300">{s.answer.code}</pre>}
      </div>
      {s.status === "submitted" && <Button variant="outline" className="rounded-full" data-testid="grading-claim-button" onClick={() => act(() => api.post(`/submissions/${id}/claim`), "Correção iniciada — o aluno não pode mais editar")}><Play />Iniciar correção</Button>}
      {gradable ? (
        <div className="space-y-4">
          {criteria.length > 0 ? <RubricEditor criteria={criteria} setCriteria={setCriteria} /> : <p className="text-xs text-slate-500">Este exercício não tem critérios de rubrica configurados.</p>}
          <div className="grid gap-3 sm:grid-cols-[1fr_140px]">
            <Textarea data-testid="grading-feedback-input" rows={4} placeholder="Feedback para o aluno (obrigatório ao reprovar ou devolver)" value={feedback} onChange={(e) => setFeedback(e.target.value)} />
            <Input data-testid="grading-score-input" type="number" placeholder={`Nota${block?.data.max_score ? ` / ${block.data.max_score}` : ""}`} value={score} onChange={(e) => setScore(e.target.value)} />
          </div>
          <div className="flex flex-wrap justify-end gap-2">
            <Button variant="outline" data-testid="grading-return-button" onClick={() => grade("returned")}><CornerUpLeft />Devolver para ajuste</Button>
            <Button variant="outline" className="border-rose-500/40 text-rose-200" data-testid="grading-reject-button" onClick={() => grade("rejected")}><XCircle />Reprovar</Button>
            <Button className="rounded-full" data-testid="grading-approve-button" onClick={() => grade("approved")}><CheckCircle2 />Aprovar</Button>
          </div>
        </div>
      ) : s.grading && (
        <div className="rounded-xl border border-slate-800 p-5 text-sm" data-testid="grading-result">
          <p className={RESULT_META[s.grading.result]?.cls}>{RESULT_META[s.grading.result]?.label} por {s.grading.graded_by_name} · {formatDate(s.grading.graded_at)}</p>
          <Markdown className="mt-2 text-sm">{s.grading.feedback}</Markdown>
        </div>
      )}
      {s.history && (
        <ol className="space-y-1 border-l border-slate-800 pl-4 text-xs text-slate-500" data-testid="grading-history">
          {s.history.map((h, i) => <li key={i}>{formatDate(h.at)} · <SubmissionBadge status={h.status} testId={`history-${i}`} /> {h.result && RESULT_META[h.result]?.label} · {h.by_name}</li>)}
        </ol>
      )}
      {attempts.length > 1 && <p className="text-xs text-slate-500">Tentativas anteriores: {attempts.filter((a) => a.id !== s.id).map((a) => `#${a.attempt} ${a.grading ? RESULT_META[a.grading.result]?.label : a.status}`).join(" · ")}</p>}
    </div>
  );
}

export default function Grading() {
  const { data: meta } = useMeta();
  const [status, setStatus] = useState("submitted");
  const [trackId, setTrackId] = useState(ALL);
  const [type, setType] = useState(ALL);
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<string | null>(null);
  const tracks = useQuery({ queryKey: ["tracks", "admin"], queryFn: () => api.get<Track[]>("/tracks").then((r) => r.data) });
  const params = { status, track_id: trackId === ALL ? undefined : trackId, block_type: type === ALL ? undefined : type, q: q || undefined };
  const { data, isLoading } = useQuery({
    queryKey: ["submissions", "staff", params],
    queryFn: () => api.get<{ items: Submission[]; counts: Record<string, number> }>("/submissions", { params }).then((r) => r.data),
  });
  const types = (meta?.block_types || []).filter((b) => b.capabilities?.includes("submission"));
  return (
    <div className="max-w-7xl">
      <PageHeader eyebrow="operação editorial" title="Correções" description="Fila de respostas enviadas. Corrija com rubrica, devolva para ajuste ou aprove." />
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <Tabs value={status} onValueChange={(v) => { setStatus(v); setSelected(null); }}>
          <TabsList className="bg-slate-900">
            {STATUS_TABS.map(([k, l]) => <TabsTrigger key={k} value={k} data-testid={`grading-tab-${k}`}>{l} <span className="ml-1.5 font-mono text-[10px] text-slate-500">{data?.counts[k] || 0}</span></TabsTrigger>)}
          </TabsList>
        </Tabs>
        <Select value={trackId} onValueChange={setTrackId}>
          <SelectTrigger data-testid="grading-filter-track" className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value={ALL}>Todas as trilhas</SelectItem>{(tracks.data || []).map((t) => <SelectItem key={t.id} value={t.id}>{t.title}</SelectItem>)}</SelectContent>
        </Select>
        <Select value={type} onValueChange={setType}>
          <SelectTrigger data-testid="grading-filter-type" className="w-48"><SelectValue /></SelectTrigger>
          <SelectContent><SelectItem value={ALL}>Todos os tipos</SelectItem>{types.map((t) => <SelectItem key={t.key} value={t.key}>{t.label}</SelectItem>)}</SelectContent>
        </Select>
        <div className="relative w-56"><Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <Input data-testid="grading-search" placeholder="Aluno ou tópico" value={q} onChange={(e) => setQ(e.target.value)} className="pl-9" /></div>
      </div>
      <div className="grid gap-6 lg:grid-cols-[380px_1fr]">
        <div className="space-y-2">
          {isLoading ? <Loader /> : !data?.items.length ? <EmptyState icon="ClipboardCheck" title="Nada por aqui" description="Nenhuma submissão com estes filtros." /> : data.items.map((s) => (
            <button key={s.id} data-testid={`grading-item-${s.id}`} onClick={() => setSelected(s.id)}
              className={cn("w-full rounded-xl border px-4 py-3 text-left transition-colors", selected === s.id ? "border-emerald-500/40 bg-emerald-500/5" : "border-slate-800 bg-slate-900/50 hover:border-slate-600")}>
              <div className="flex items-center justify-between gap-2"><span className="truncate text-sm font-medium text-slate-100">{s.user_name}</span><SubmissionBadge status={s.status} testId={`grading-item-status-${s.id}`} /></div>
              <p className="truncate text-xs text-slate-400">{s.orphaned && <span data-testid={`grading-item-orphan-${s.id}`} className="mr-1.5 rounded border border-slate-600 px-1 font-mono text-[9px] uppercase text-slate-400">órfão</span>}{s.node_title} · {s.block_title || s.block_type}</p>
              <p className="font-mono text-[10px] text-slate-600">#{s.attempt} · {formatDate(s.submitted_at)}</p>
            </button>
          ))}
        </div>
        <div className="min-w-0">{selected ? <GradingPanel key={selected} id={selected} onDone={() => undefined} /> : <EmptyState icon="MousePointerClick" title="Selecione uma submissão" description="Abra uma resposta da fila para corrigir." />}</div>
      </div>
    </div>
  );
}
