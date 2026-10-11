import React, { useState } from "react";
import { Check, Copy, ExternalLink, Info, RotateCcw, X } from "lucide-react";
import { BlockType, ContentBlock, ProgressRecord, ProgressStatus } from "@/types";
import { DynamicIcon, Markdown } from "@/components/common";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";

export interface BlockProps {
  block: ContentBlock;
  type?: BlockType;
  progress?: ProgressRecord;
  onProgress?: (status: ProgressStatus, data: Record<string, unknown>) => void;
  footer?: React.ReactNode;
  actions?: React.ReactNode;
}

const list = (v: unknown): string[] => (Array.isArray(v) ? v.map(String) : []);

function MarkdownBlock({ block }: BlockProps) {
  return <Markdown>{block.data.body}</Markdown>;
}

function CalloutBlock({ block }: BlockProps) {
  return (
    <div className="flex gap-3 rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
      <Info className="mt-1 h-4 w-4 shrink-0 text-amber-400" />
      <Markdown>{block.data.body}</Markdown>
    </div>
  );
}

function ChecklistBlock({ block, progress, onProgress }: BlockProps) {
  const items = list(block.data.items);
  const [checked, setChecked] = useState<number[]>((progress?.data?.checked as number[]) || []);
  const toggle = (i: number) => {
    const next = checked.includes(i) ? checked.filter((x) => x !== i) : [...checked, i];
    setChecked(next);
    onProgress?.(next.length === items.length ? "completed" : "in_progress", { checked: next });
  };
  return (
    <ul className="space-y-2">
      {items.map((it, i) => (
        <li key={i} className="flex items-center gap-3 rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2.5">
          <Checkbox data-testid={`checklist-item-${block.id}-${i}`} checked={checked.includes(i)} onCheckedChange={() => toggle(i)} />
          <span className={cn("text-sm", checked.includes(i) ? "text-slate-500 line-through" : "text-slate-200")}>{it}</span>
        </li>
      ))}
    </ul>
  );
}

function QuizBlock({ block, progress, onProgress }: BlockProps) {
  const options = list(block.data.options);
  const correct = Number(block.data.correct_index ?? -1);
  const [selected, setSelected] = useState<number | null>((progress?.data?.selected as number) ?? null);
  const pick = (i: number) => {
    setSelected(i);
    onProgress?.("completed", { selected: i, correct: i === correct });
  };
  return (
    <div className="space-y-3">
      <p className="font-medium text-slate-100">{block.data.question}</p>
      <div className="grid gap-2">
        {options.map((o, i) => {
          const state = selected === null ? "" : i === correct ? "ok" : i === selected ? "bad" : "";
          return (
            <button key={i} data-testid={`quiz-option-${block.id}-${i}`} onClick={() => pick(i)}
              className={cn("flex items-center justify-between rounded-lg border px-4 py-2.5 text-left text-sm transition-colors",
                state === "ok" ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-200"
                  : state === "bad" ? "border-rose-500/60 bg-rose-500/10 text-rose-200"
                    : "border-slate-800 bg-slate-950/40 text-slate-200 hover:border-slate-600")}>
              {o}
              {state === "ok" && <Check className="h-4 w-4" />}
              {state === "bad" && <X className="h-4 w-4" />}
            </button>
          );
        })}
      </div>
      {selected !== null && (
        <div data-testid={`quiz-feedback-${block.id}`} className="rounded-md bg-slate-950/60 p-3 text-sm">
          <p className={selected === correct ? "text-emerald-400" : "text-rose-400"}>{selected === correct ? "Correto." : "Ainda não."}</p>
          <Markdown className="text-sm">{block.data.explanation}</Markdown>
          <button onClick={() => setSelected(null)} className="mt-2 inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-200">
            <RotateCcw className="h-3 w-3" /> Tentar de novo
          </button>
        </div>
      )}
    </div>
  );
}

function FlashcardBlock({ block }: BlockProps) {
  const [flipped, setFlipped] = useState(false);
  return (
    <button data-testid={`flashcard-${block.id}`} onClick={() => setFlipped(!flipped)}
      className="flex min-h-[120px] w-full flex-col items-start justify-center rounded-lg border border-slate-700 bg-slate-950/50 p-5 text-left hover:border-emerald-500/40">
      <span className="mb-2 font-mono text-[10px] uppercase tracking-widest text-slate-500">{flipped ? "verso" : "frente — clique para virar"}</span>
      <span className="text-slate-100">{flipped ? block.data.back : block.data.front}</span>
    </button>
  );
}

function CodeBlock({ block }: BlockProps) {
  const [copied, setCopied] = useState(false);
  const code = block.data.code || block.data.starter_code || "";
  return (
    <figure className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950">
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-2 font-mono text-[11px] text-slate-500">
        <span>{block.data.language || "code"}</span>
        <button data-testid={`code-copy-${block.id}`} onClick={() => { navigator.clipboard?.writeText(code); setCopied(true); }}
          className="flex items-center gap-1 hover:text-slate-200"><Copy className="h-3 w-3" />{copied ? "copiado" : "copiar"}</button>
      </div>
      <pre className="overflow-x-auto p-4 font-mono text-[13px] leading-6 text-emerald-300"><code>{code}</code></pre>
      {block.data.caption && <figcaption className="border-t border-slate-800 px-4 py-2 text-xs text-slate-400">{block.data.caption}</figcaption>}
    </figure>
  );
}

function toEmbed(url: string) {
  const yt = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)/);
  if (yt) return `https://www.youtube.com/embed/${yt[1]}`;
  const vimeo = url.match(/vimeo\.com\/(\d+)/);
  return vimeo ? `https://player.vimeo.com/video/${vimeo[1]}` : null;
}

function VideoBlock({ block }: BlockProps) {
  const embed = block.data.url ? toEmbed(block.data.url) : null;
  if (!embed) return <LinkBlock block={{ ...block, data: { ...block.data, label: "Abrir vídeo" } }} />;
  return (
    <div className="space-y-2">
      <div className="aspect-video overflow-hidden rounded-lg border border-slate-800">
        <iframe src={embed} title={block.title} className="h-full w-full" allowFullScreen />
      </div>
      {block.data.caption && <p className="text-xs text-slate-400">{block.data.caption}</p>}
    </div>
  );
}

function LinkBlock({ block }: BlockProps) {
  if (!block.data.url) return <Markdown>{block.data.body || block.data.citation}</Markdown>;
  return (
    <div className="space-y-2">
      {block.data.body && <Markdown>{block.data.body}</Markdown>}
      <a href={block.data.url} target="_blank" rel="noreferrer" data-testid={`link-block-${block.id}`}
        className="group flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-3 hover:border-cyan-500/40">
        <div>
          <p className="text-sm font-medium text-cyan-300">{block.data.label || block.data.citation || block.data.url}</p>
          {block.data.description && <p className="text-xs text-slate-400">{block.data.description}</p>}
        </div>
        <ExternalLink className="h-4 w-4 text-slate-500 group-hover:text-cyan-300" />
      </a>
    </div>
  );
}

function ExerciseBlock({ block }: BlockProps) {
  const options = list(block.data.options);
  const acceptance = list(block.data.acceptance);
  return (
    <div className="space-y-3">
      <Markdown>{block.data.prompt}</Markdown>
      {options.length > 0 && (
        <ol className="list-[upper-alpha] space-y-1 pl-6 text-sm text-slate-300">{options.map((o, i) => <li key={i}>{o}</li>)}</ol>
      )}
      {block.data.starter_code && <CodeBlock block={block} />}
      {acceptance.length > 0 && (
        <ul className="space-y-1 text-sm text-slate-400">{acceptance.map((a, i) => <li key={i}>✓ {a}</li>)}</ul>
      )}
      <p className="rounded-md border border-dashed border-slate-700 px-3 py-2 font-mono text-[11px] text-slate-500">
        correção: {block.data.grading || "manual"}{Array.isArray(block.data.criteria) && block.data.criteria.length > 0 && ` · ${block.data.criteria.length} critério(s) de rubrica`}
      </p>
    </div>
  );
}

function GenericBlock({ block, type }: BlockProps) {
  return (
    <dl className="space-y-3">
      {(type?.fields || Object.keys(block.data).map((k) => ({ name: k, label: k, type: "text" as const }))).map((f) => (
        <div key={f.name}>
          <dt className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{f.label}</dt>
          <dd className="text-sm text-slate-200">
            {f.type === "markdown" ? <Markdown>{block.data[f.name]}</Markdown> : String(block.data[f.name] ?? "—")}
          </dd>
        </div>
      ))}
    </dl>
  );
}

const RENDERERS: Record<string, React.FC<BlockProps>> = {
  theory_text: MarkdownBlock, summary: MarkdownBlock, review: MarkdownBlock, instructor_note: CalloutBlock,
  checklist: ChecklistBlock, quiz: QuizBlock, flashcard: FlashcardBlock, code_snippet: CodeBlock,
  video_embed: VideoBlock, external_link: LinkBlock, supplementary: LinkBlock, reference: LinkBlock,
  exercise_objective: ExerciseBlock, exercise_open: ExerciseBlock, practical_challenge: ExerciseBlock,
};

export function BlockRenderer(props: BlockProps) {
  const Renderer = RENDERERS[props.block.type] || GenericBlock;
  const done = props.progress?.status === "completed";
  return (
    <section data-testid={`content-block-${props.block.id}`} className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 sm:p-6">
      <header className="mb-4 flex items-center gap-2">
        <DynamicIcon name={props.type?.icon} className="h-4 w-4 text-emerald-400" />
        <span className="font-mono text-[10px] uppercase tracking-widest text-slate-500">{props.type?.label || props.block.type}</span>
        {props.block.title && <span className="text-sm font-semibold text-slate-200">· {props.block.title}</span>}
        <span className="ml-auto flex items-center gap-2">
          {props.actions}
          {done && <Check className="h-4 w-4 text-emerald-400" />}
        </span>
      </header>
      <Renderer {...props} />
      {props.footer}
    </section>
  );
}
