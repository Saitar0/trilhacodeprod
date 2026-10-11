import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ArrowRight, Check, Trash2 } from "lucide-react";
import { api, apiError } from "@/lib/api";
import { useMySubmissions, useNotes, useReviews } from "@/hooks/useStudy";
import { Review } from "@/types";
import { cn, formatDate } from "@/lib/utils";
import { EmptyState, Loader, Markdown, PageHeader } from "@/components/common";
import { RESULT_META, SubmissionBadge } from "@/components/common/SubmissionBadge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

const OUTCOMES: [string, string][] = [["easy", "Fácil"], ["ok", "Ok"], ["hard", "Difícil"]];

export function groupReviews(items: Review[]) {
  const end = new Date(); end.setHours(23, 59, 59, 999);
  const start = new Date(); start.setHours(0, 0, 0, 0);
  return {
    overdue: items.filter((r) => new Date(r.due_at) < start),
    today: items.filter((r) => new Date(r.due_at) >= start && new Date(r.due_at) <= end),
    upcoming: items.filter((r) => new Date(r.due_at) > end),
  };
}

function ReviewRow({ r }: { r: Review }) {
  const qc = useQueryClient();
  const act = async (fn: () => Promise<unknown>, msg: string) => {
    try { await fn(); qc.invalidateQueries({ queryKey: ["reviews"] }); toast.success(msg); } catch (e) { toast.error(apiError(e)); }
  };
  const complete = (outcome: string, reschedule?: string) =>
    act(() => api.post(`/reviews/${r.id}/complete`, { outcome, reschedule }), reschedule ? "Revisão registrada e reagendada" : "Revisão concluída");
  return (
    <li data-testid={`review-row-${r.id}`} className="flex flex-wrap items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4">
      <div className="min-w-0 flex-1">
        <p className="font-medium text-slate-100">{r.node_title}{r.block_id && <span className="text-xs text-slate-500"> · bloco</span>}</p>
        <p className="font-mono text-[11px] text-slate-500">{r.track_title} · para {formatDate(r.due_at)} · {r.review_count} revisão(ões){r.last_reviewed_at && ` · última ${formatDate(r.last_reviewed_at)}`}</p>
      </div>
      <Button asChild variant="ghost" size="sm" data-testid={`review-open-${r.id}`}><Link to={`/trilhas/${r.track_id}/n/${r.node_id}`}>Abrir<ArrowRight /></Link></Button>
      <DropdownMenu>
        <DropdownMenuTrigger asChild><Button size="sm" className="rounded-full" data-testid={`review-complete-${r.id}`}><Check />Revisei</Button></DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-60 border-slate-800 bg-slate-900">
          <DropdownMenuLabel className="text-xs text-slate-400">Como foi? (encerra a revisão)</DropdownMenuLabel>
          {OUTCOMES.map(([k, l]) => <DropdownMenuItem key={k} data-testid={`review-outcome-${k}-${r.id}`} onClick={() => complete(k)}>{l}</DropdownMenuItem>)}
          <DropdownMenuSeparator />
          <DropdownMenuLabel className="text-xs text-slate-400">Registrar e revisar de novo</DropdownMenuLabel>
          <DropdownMenuItem data-testid={`review-again-soon-${r.id}`} onClick={() => complete("hard", "soon")}>Em breve (3 dias)</DropdownMenuItem>
          <DropdownMenuItem data-testid={`review-again-later-${r.id}`} onClick={() => complete("ok", "later")}>Depois (14 dias)</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <button data-testid={`review-dismiss-${r.id}`} onClick={() => act(() => api.delete(`/reviews/${r.id}`), "Revisão removida")} className="text-slate-500 hover:text-rose-400"><Trash2 className="h-4 w-4" /></button>
    </li>
  );
}

function ReviewsTab() {
  const { data, isLoading } = useReviews();
  if (isLoading) return <Loader />;
  if (!data?.length) return <EmptyState icon="CalendarClock" title="Nenhuma revisão pendente" description="Use 'Revisar depois' em tópicos ou blocos para montar sua fila de revisão." />;
  const g = groupReviews(data);
  const sections: [string, Review[], string][] = [["Atrasadas", g.overdue, "text-rose-300"], ["Hoje", g.today, "text-emerald-300"], ["Próximas", g.upcoming, "text-slate-400"]];
  return (
    <div className="space-y-8">
      {sections.filter(([, items]) => items.length).map(([title, items, cls]) => (
        <section key={title} data-testid={`reviews-section-${title.toLowerCase()}`}>
          <h3 className={cn("mb-3 font-mono text-[11px] uppercase tracking-widest", cls)}>{title} · {items.length}</h3>
          <ul className="space-y-2">{items.map((r) => <ReviewRow key={r.id} r={r} />)}</ul>
        </section>
      ))}
    </div>
  );
}

function NotesTab() {
  const { data, isLoading } = useNotes({});
  if (isLoading) return <Loader />;
  if (!data?.length) return <EmptyState icon="NotebookPen" title="Caderno vazio" description="Suas anotações por tópico e por bloco aparecerão aqui." />;
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {data.map((n) => (
        <Link key={n.id} to={`/trilhas/${n.track_id}/n/${n.node_id}`} data-testid={`note-card-${n.id}`}
          className="rounded-xl border border-amber-500/15 bg-amber-500/[0.03] p-5 hover:border-amber-500/40">
          <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{n.track_title} · {n.block_id ? "nota de bloco" : "nota do tópico"}</p>
          <p className="mt-1 font-medium text-slate-100">{n.node_title}</p>
          <Markdown className="mt-2 line-clamp-4 text-sm">{n.body}</Markdown>
          <p className="mt-2 font-mono text-[10px] text-slate-600">{formatDate(n.updated_at)}</p>
        </Link>
      ))}
    </div>
  );
}

function SubmissionsTab() {
  const { data, isLoading } = useMySubmissions();
  if (isLoading) return <Loader />;
  const latest = (data || []).filter((s, i, arr) => arr.findIndex((x) => x.block_id === s.block_id) === i);
  if (!latest.length) return <EmptyState icon="PenLine" title="Nenhum exercício respondido" description="Exercícios respondíveis aparecem dentro dos tópicos." />;
  return (
    <ul className="space-y-2">
      {latest.map((s) => (
        <li key={s.id} data-testid={`my-submission-${s.id}`}>
          <Link to={`/trilhas/${s.track_id}/n/${s.node_id}`} className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/50 px-5 py-4 hover:border-slate-600">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-slate-100">{s.block_title || "Exercício"} <span className="text-sm text-slate-500">· {s.node_title}</span></p>
              <p className="font-mono text-[11px] text-slate-500">tentativa {s.attempt} · {formatDate(s.submitted_at || s.updated_at)}</p>
            </div>
            {s.grading && <span className={cn("text-xs", RESULT_META[s.grading.result]?.cls)}>{RESULT_META[s.grading.result]?.label}</span>}
            <SubmissionBadge status={s.status} testId={`my-submission-status-${s.id}`} />
          </Link>
        </li>
      ))}
    </ul>
  );
}

export default function MyStudy() {
  const [tab, setTab] = useState("reviews");
  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <PageHeader eyebrow="retenção e acompanhamento" title="Meu estudo" description="Revisões programadas, seu caderno de anotações e o status dos exercícios enviados." />
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList className="bg-slate-900">
          <TabsTrigger value="reviews" data-testid="mystudy-tab-reviews">Revisões</TabsTrigger>
          <TabsTrigger value="notes" data-testid="mystudy-tab-notes">Caderno</TabsTrigger>
          <TabsTrigger value="submissions" data-testid="mystudy-tab-submissions">Exercícios</TabsTrigger>
        </TabsList>
        <TabsContent value="reviews" className="pt-6"><ReviewsTab /></TabsContent>
        <TabsContent value="notes" className="pt-6"><NotesTab /></TabsContent>
        <TabsContent value="submissions" className="pt-6"><SubmissionsTab /></TabsContent>
      </Tabs>
    </div>
  );
}
