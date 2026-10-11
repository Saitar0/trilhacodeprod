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

const STATE_LABEL = { idle: "", saving: "salvando…", saved: "salvo" };

export function NoteEditor({ nodeId, blockId, initial, testId, rows = 6 }: { nodeId: string; blockId: string | null; initial: string; testId: string; rows?: number }) {
  const { body, setBody, state } = useAutosaveNote(nodeId, blockId, initial);
  return (
    <div className="space-y-1">
      <Textarea data-testid={testId} rows={rows} value={body} placeholder="Suas anotações privadas (salvamento automático)" onChange={(e) => setBody(e.target.value)}
        className="border-amber-500/20 bg-amber-500/[0.03] text-sm" />
      <p className="h-4 text-right font-mono text-[10px] text-slate-500" data-testid={`${testId}-state`}>{STATE_LABEL[state]}</p>
    </div>
  );
}

export function useNodeNotes(nodeId: string) {
  const { data } = useNotes({ node_id: nodeId });
  return (blockId: string | null) => (data || []).find((n) => n.block_id === blockId)?.body || "";
}

export function BlockNote({ nodeId, blockId, initial }: { nodeId: string; blockId: string; initial: string }) {
  const [open, setOpen] = useState(!!initial);
  useEffect(() => { if (initial) setOpen(true); }, [initial]);
  return (
    <div className="mt-4">
      {open ? <NoteEditor nodeId={nodeId} blockId={blockId} initial={initial} testId={`block-note-${blockId}`} rows={3} /> : (
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
