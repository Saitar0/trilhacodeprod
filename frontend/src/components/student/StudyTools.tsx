import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import { CalendarClock, NotebookPen } from "lucide-react";
import { apiError } from "@/lib/api";
import { useAutosaveNote, useNotes, useReviews, useScheduleReview } from "@/hooks/useStudy";
import { cn, formatDate } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { StudyNote } from "@/types";
import { useAuth } from "@/context/AuthContext";

const STATE_LABEL = {
  saved: "salvo no servidor",
  pending: "alterações não salvas",
  saving: "salvando…",
  error: "erro ao salvar; alterações mantidas",
  conflict: "conflito entre versões",
};

export function NoteEditor({
  nodeId, blockId, initial, ready, loadError, onRetryLoad, testId, rows = 6,
}: {
  nodeId: string;
  blockId: string | null;
  initial?: StudyNote;
  ready: boolean;
  loadError?: boolean;
  onRetryLoad?: () => void;
  testId: string;
  rows?: number;
}) {
  const { user } = useAuth();
  const userId = user && typeof user === "object" ? user.id : "anonymous";
  const { body, setBody, state, conflict, retry, reloadServerVersion, overwriteServerVersion } =
    useAutosaveNote(nodeId, blockId, initial, ready, userId);

  if (!ready) {
    return (
      <div className="space-y-1" role={loadError ? "alert" : "status"}>
        <p className="text-xs text-slate-400">{loadError ? "Não foi possível carregar a versão atual da anotação." : "Carregando anotação…"}</p>
        {loadError && <Button type="button" variant="outline" size="sm" onClick={onRetryLoad}>Tentar carregar novamente</Button>}
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <Textarea data-testid={testId} rows={rows} value={body} placeholder="Suas anotações privadas (salvamento automático)" onChange={(e) => setBody(e.target.value)}
        className="border-amber-500/20 bg-amber-500/[0.03] text-sm" aria-describedby={`${testId}-state`} />
      <div className="flex min-h-6 items-center justify-between gap-2 text-right font-mono text-[10px] text-slate-500">
        <p role={state === "error" || state === "conflict" ? "alert" : "status"} aria-live="polite" data-testid={`${testId}-state`}>
          {STATE_LABEL[state]}
        </p>
        {state === "error" && <Button type="button" variant="ghost" size="sm" className="h-6 px-2 text-[10px]" onClick={() => void retry()}>Tentar novamente</Button>}
      </div>
      {state === "conflict" && (
        <div className="space-y-2 rounded-md border border-amber-500/30 bg-amber-500/5 p-3" role="alert" data-testid={`${testId}-conflict`}>
          <p className="text-xs text-amber-100">Esta anotação mudou em outro dispositivo. Sua edição continua preservada nesta tela.</p>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="outline" size="sm" onClick={reloadServerVersion}>Usar versão do servidor</Button>
            <Button type="button" variant="outline" size="sm" onClick={() => void overwriteServerVersion()}>Manter minha edição e substituir</Button>
          </div>
          {conflict?.current && <span className="sr-only">Versão remota {conflict.current.version}</span>}
        </div>
      )}
    </div>
  );
}

export function useNodeNotes(nodeId: string) {
  const query = useNotes({ node_id: nodeId, include_deleted: true });
  const noteFor = (blockId: string | null) => query.data?.find((note) => note.block_id === blockId);
  return { ...query, noteFor };
}

export function BlockNote({
  nodeId, blockId, initial, ready, loadError, onRetryLoad,
}: {
  nodeId: string;
  blockId: string;
  initial?: StudyNote;
  ready: boolean;
  loadError?: boolean;
  onRetryLoad?: () => void;
}) {
  const [open, setOpen] = useState(!!initial?.body);
  useEffect(() => { if (initial?.body) setOpen(true); }, [initial?.body]);
  return (
    <div className="mt-4">
      {open ? <NoteEditor key={`${nodeId}:${blockId}`} nodeId={nodeId} blockId={blockId} initial={initial} ready={ready} loadError={loadError} onRetryLoad={onRetryLoad} testId={`block-note-${blockId}`} rows={3} /> : (
        <button data-testid={`block-note-open-${blockId}`} onClick={() => setOpen(true)} className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-amber-300">
          <NotebookPen className="h-3.5 w-3.5" />Anotar neste bloco
        </button>
      )}
    </div>
  );
}

export function ReviewMenu({ nodeId, blockId = null, compact }: { nodeId: string; blockId?: string | null; compact?: boolean }) {
  const { data } = useReviews();
  const schedule = useScheduleReview();
  const [custom, setCustom] = useState(false);
  const [date, setDate] = useState("");
  const pending = (data || []).find((r) => r.node_id === nodeId && r.block_id === blockId);
  const run = (when: string, due_at?: string) => schedule.mutate({ node_id: nodeId, block_id: blockId, when, due_at }, {
    onSuccess: (r) => toast.success(`Revisão agendada para ${formatDate(r.due_at)}`),
    onError: (e) => toast.error(apiError(e)),
  });
  const tid = blockId ? `review-menu-${blockId}` : "review-menu-topic";
  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" data-testid={tid} className={cn("rounded-full", pending && "border-cyan-500/40 text-cyan-200", compact && "h-7 px-2 text-xs")}>
            <CalendarClock />{pending ? `Revisão ${new Date(pending.due_at).toLocaleDateString("pt-BR")}` : "Revisar depois"}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56 border-slate-800 bg-slate-900">
          <DropdownMenuLabel className="text-xs text-slate-400">{pending ? "Reagendar revisão" : "Quando revisar?"}</DropdownMenuLabel>
          <DropdownMenuItem data-testid={`${tid}-today`} onClick={() => run("today")}>Hoje</DropdownMenuItem>
          <DropdownMenuItem data-testid={`${tid}-soon`} onClick={() => run("soon")}>Em breve (3 dias)</DropdownMenuItem>
          <DropdownMenuItem data-testid={`${tid}-later`} onClick={() => run("later")}>Depois (14 dias)</DropdownMenuItem>
          <DropdownMenuItem data-testid={`${tid}-suggested`} onClick={() => run("suggested")}>Sugerida (pela profundidade)</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem data-testid={`${tid}-custom`} onClick={() => setCustom(true)}>Escolher data…</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <Dialog open={custom} onOpenChange={setCustom}>
        <DialogContent className="max-w-sm border-slate-800 bg-slate-900">
          <DialogHeader><DialogTitle>Data da revisão</DialogTitle></DialogHeader>
          <Input type="date" data-testid={`${tid}-date-input`} value={date} onChange={(e) => setDate(e.target.value)} />
          <DialogFooter>
            <Button data-testid={`${tid}-date-confirm`} disabled={!date} onClick={() => { run("custom", `${date}T09:00:00`); setCustom(false); }}>Agendar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
