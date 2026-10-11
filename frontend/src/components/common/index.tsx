import React from "react";
import * as Icons from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { LucideIcon } from "lucide-react";
import { cn, DOTS, STATUS_META, tone } from "@/lib/utils";
import { useTaxonomy } from "@/hooks/useData";

export function DynamicIcon({ name, className }: { name?: string; className?: string }) {
  const Icon = ((name && (Icons as unknown as Record<string, LucideIcon>)[name]) || Icons.Square) as LucideIcon;
  return <Icon className={className} />;
}

export function Markdown({ children, className }: { children?: string; className?: string }) {
  if (!children) return null;
  return (
    <div className={cn("md", className)}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{children}</ReactMarkdown>
    </div>
  );
}

export function StatusBadge({ status, testId }: { status: string; testId?: string }) {
  const m = STATUS_META[status] || STATUS_META.draft;
  return (
    <span data-testid={testId || `status-badge-${status}`}
      className={cn("inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[11px] font-medium", m.cls)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", m.dot)} />
      {m.label}
    </span>
  );
}

export function TaxBadge({ group, value, className }: { group: string; value?: string; className?: string }) {
  const { find } = useTaxonomy();
  const item = find(group, value);
  if (!value) return null;
  return (
    <span data-testid={`tax-badge-${group}-${value}`} title={item?.description}
      className={cn("inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-medium", tone(item?.color), className)}>
      {item?.label || value}
    </span>
  );
}

export function Dot({ color, className }: { color?: string; className?: string }) {
  return <span className={cn("inline-block h-2 w-2 rounded-full", DOTS[color || "slate"], className)} />;
}

export function EmptyState({ icon = "Inbox", title, description, action, testId }: {
  icon?: string; title: string; description?: string; action?: React.ReactNode; testId?: string;
}) {
  return (
    <div data-testid={testId || "empty-state"}
      className="flex flex-col items-start gap-3 rounded-xl border border-dashed border-slate-800 bg-slate-900/30 p-8 fade-up">
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-2.5 text-slate-400">
        <DynamicIcon name={icon} className="h-5 w-5" />
      </div>
      <div>
        <p className="font-heading text-base font-semibold text-slate-100">{title}</p>
        {description && <p className="mt-1 max-w-md text-sm text-slate-400">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function PageHeader({ eyebrow, title, description, actions }: {
  eyebrow?: string; title: string; description?: string; actions?: React.ReactNode;
}) {
  return (
    <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between fade-up">
      <div>
        {eyebrow && <p className="mb-2 font-mono text-[11px] uppercase tracking-[0.2em] text-emerald-400">{eyebrow}</p>}
        <h1 data-testid="page-title" className="text-3xl font-bold text-slate-50 sm:text-4xl">{title}</h1>
        {description && <p className="mt-2 max-w-2xl text-sm text-slate-400 sm:text-base">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function ProgressBar({ value, className, testId }: { value: number; className?: string; testId?: string }) {
  return (
    <div data-testid={testId} className={cn("h-1.5 w-full overflow-hidden rounded-full bg-slate-800", className)}>
      <div className="h-full rounded-full bg-emerald-500 transition-[width] duration-500" style={{ width: `${value}%` }} />
    </div>
  );
}

export function Loader({ label = "Carregando..." }: { label?: string }) {
  return (
    <div data-testid="loader" className="flex items-center gap-3 p-8 text-sm text-slate-400">
      <Icons.Loader2 className="h-4 w-4 animate-spin text-emerald-400" /> {label}
    </div>
  );
}
