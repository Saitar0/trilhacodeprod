import React from "react";
import { Link } from "react-router-dom";
import { Eye } from "lucide-react";
import { useNodeDetail } from "@/hooks/useData";
import { Loader, StatusBadge } from "@/components/common";
import { ViewModel } from "@/components/student/viewModel";
import { NodeDetailsForm } from "@/components/admin/NodeDetailsForm";
import { BlocksEditor } from "@/components/admin/BlocksEditor";
import { RelationsEditor } from "@/components/admin/RelationsEditor";
import { HistoryList } from "@/components/admin/HistoryList";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function NodeEditor({ nodeId, vm }: { nodeId: string; vm: ViewModel }) {
  const { data, isLoading } = useNodeDetail(nodeId);
  if (isLoading || !data) return <Loader />;
  const { node, blocks, relations, ancestors } = data;
  return (
    <div key={node.id} className="mx-auto max-w-3xl space-y-6 fade-up" data-testid="node-editor">
      <header className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] text-slate-500">{ancestors.map((a) => a.title).join(" / ") || "raiz"}</p>
          <div className="mt-1 flex items-center gap-3">
            <span className="rounded bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest text-emerald-300">{vm.label(node.kind)}</span>
            <StatusBadge status={node.status} testId="node-editor-status" />
          </div>
          <h2 data-testid="node-editor-title" className="mt-2 text-2xl font-bold text-slate-50">{node.title}</h2>
        </div>
        <Button asChild variant="outline" size="sm" className="rounded-full" data-testid="node-preview-button">
          <Link to={`/trilhas/${vm.track.id}/n/${node.id}`}><Eye />Ver como aluno</Link>
        </Button>
      </header>
      <Tabs defaultValue="details">
        <TabsList className="bg-slate-900">
          <TabsTrigger value="details" data-testid="node-tab-details">Detalhes</TabsTrigger>
          <TabsTrigger value="blocks" data-testid="node-tab-blocks">Blocos ({blocks.length})</TabsTrigger>
          <TabsTrigger value="relations" data-testid="node-tab-relations">Relações ({relations.length})</TabsTrigger>
          <TabsTrigger value="history" data-testid="node-tab-history">Histórico</TabsTrigger>
        </TabsList>
        <TabsContent value="details" className="pt-4"><NodeDetailsForm key={node.id + node.updated_at} node={node} vm={vm} /></TabsContent>
        <TabsContent value="blocks" className="pt-4"><BlocksEditor nodeId={node.id} trackId={vm.track.id} blocks={blocks} /></TabsContent>
        <TabsContent value="relations" className="pt-4"><RelationsEditor nodeId={node.id} vm={vm} relations={relations} /></TabsContent>
        <TabsContent value="history" className="pt-4"><HistoryList trackId={vm.track.id} entityId={node.id} limit={200} /></TabsContent>
      </Tabs>
    </div>
  );
}
