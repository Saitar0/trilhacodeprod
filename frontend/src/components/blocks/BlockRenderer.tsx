import React from "react";
import { Check } from "lucide-react";
import { DynamicIcon } from "@/components/common";
import { BlockProps } from "./BlockProps";
import { CalloutBlock, ChecklistBlock, CodeBlock, ExerciseBlock, FlashcardBlock, GenericBlock, LinkBlock, MarkdownBlock, QuizBlock, VideoBlock } from "./BlockRendererParts";

const forType = (Renderer: React.FC<BlockProps>): React.FC<BlockProps> => function TypeBlock(props) {
  return <Renderer {...props} />;
};

const RENDERERS: Record<string, React.FC<BlockProps>> = {
  theory_text: forType(MarkdownBlock),
  summary: forType(MarkdownBlock),
  review: forType(MarkdownBlock),
  instructor_note: forType(CalloutBlock),
  checklist: forType(ChecklistBlock),
  quiz: forType(QuizBlock),
  flashcard: forType(FlashcardBlock),
  code_snippet: forType(CodeBlock),
  video_embed: forType(VideoBlock),
  external_link: forType(LinkBlock),
  supplementary: forType(LinkBlock),
  reference: forType(LinkBlock),
  exercise_objective: forType(ExerciseBlock),
  exercise_open: forType(ExerciseBlock),
  practical_challenge: forType(ExerciseBlock),
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
      {props.contentOverride ?? <Renderer {...props} />}
      {props.footer}
    </section>
  );
}

