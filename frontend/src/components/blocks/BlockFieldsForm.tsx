import React from "react";
import { BlockField } from "@/types";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface Props {
  fields: BlockField[];
  value: Record<string, any>;
  onChange: (v: Record<string, any>) => void;
  idPrefix: string;
}

function FieldInput({ field, value, onChange, testId }: { field: BlockField; value: any; onChange: (v: any) => void; testId: string }) {
  switch (field.type) {
    case "textarea":
    case "markdown":
      return <Textarea data-testid={testId} rows={field.type === "markdown" ? 8 : 3} value={value || ""}
        placeholder={field.type === "markdown" ? "Suporta Markdown" : ""} onChange={(e) => onChange(e.target.value)} />;
    case "code":
      return <Textarea data-testid={testId} rows={8} className="font-mono text-xs" value={value || ""} onChange={(e) => onChange(e.target.value)} />;
    case "number":
      return <Input data-testid={testId} type="number" value={value ?? ""} onChange={(e) => onChange(e.target.value === "" ? null : Number(e.target.value))} />;
    case "boolean":
      return <Switch data-testid={testId} checked={!!value} onCheckedChange={onChange} />;
    case "list":
      return <Textarea data-testid={testId} rows={4} placeholder="Um item por linha" value={(value || []).join("\n")}
        onChange={(e) => onChange(e.target.value.split("\n"))} />;
    case "select":
      return (
        <Select value={value || ""} onValueChange={onChange}>
          <SelectTrigger data-testid={testId}><SelectValue placeholder="Selecione" /></SelectTrigger>
          <SelectContent>{(field.options || []).map((o) => <SelectItem key={o} value={o}>{o}</SelectItem>)}</SelectContent>
        </Select>
      );
    default:
      return <Input data-testid={testId} type={field.type === "url" ? "url" : "text"} value={value || ""} onChange={(e) => onChange(e.target.value)} />;
  }
}

export function BlockFieldsForm({ fields, value, onChange, idPrefix }: Props) {
  return (
    <div className="grid gap-4">
      {fields.map((f) => (
        <div key={f.name} className="space-y-1.5">
          <Label className="text-xs text-slate-400">{f.label}</Label>
          <FieldInput field={f} value={value[f.name]} testId={`${idPrefix}-field-${f.name}`}
            onChange={(v) => onChange({ ...value, [f.name]: v })} />
        </div>
      ))}
    </div>
  );
}

export function cleanBlockData(fields: BlockField[], data: Record<string, any>) {
  const out = { ...data };
  fields.filter((f) => f.type === "list").forEach((f) => {
    out[f.name] = (out[f.name] || []).map((s: string) => s.trim()).filter(Boolean);
  });
  return out;
}
