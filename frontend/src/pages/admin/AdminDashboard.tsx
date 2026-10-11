import React from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, Boxes, GitBranch, History, Layers, Route, Users } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader, Loader } from "@/components/common";
import { HistoryList } from "@/components/admin/HistoryList";
import { Button } from "@/components/ui/button";

interface Stats {
  tracks: Record<string, number>; nodes: Record<string, number>; node_status: Record<string, number>;
  blocks: Record<string, number>; users: Record<string, number>; relations: number; versions: number;
}
const sum = (o: Record<string, number>) => Object.values(o).reduce((a, b) => a + b, 0);

function Stat({ icon: Icon, label, value, hint, testId }: { icon: React.ElementType; label: string; value: number; hint?: string; testId: string }) {
  return (
    <div data-testid={testId} className="rounded-xl border border-slate-800 bg-slate-900/60 p-5 fade-up">
      <Icon className="h-4 w-4 text-emerald-400" />
      <p className="mt-4 font-heading text-3xl font-bold text-slate-50">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
      {hint && <p className="mt-1 font-mono text-[10px] text-slate-500">{hint}</p>}
    </div>
  );
}

export default function AdminDashboard() {
  const { data, isLoading } = useQuery({ queryKey: ["stats"], queryFn: () => api.get<Stats>("/admin/stats").then((r) => r.data) });
  return (
    <div className="max-w-6xl">
      <PageHeader eyebrow="painel administrativo" title="Visão geral editorial"
        description="Estado da estrutura pedagógica, publicação e atividade recente."
        actions={<Button asChild className="rounded-full" data-testid="dashboard-manage-tracks"><Link to="/admin/trilhas">Gerenciar trilhas <ArrowRight /></Link></Button>} />
      {isLoading || !data ? <Loader /> : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <Stat testId="stat-tracks" icon={Route} label="Trilhas" value={sum(data.tracks)} hint={`${data.tracks.published || 0} publicadas · ${data.tracks.draft || 0} rascunhos`} />
          <Stat testId="stat-nodes" icon={Layers} label="Itens na estrutura" value={sum(data.nodes)} hint={`${data.node_status.draft || 0} em rascunho`} />
          <Stat testId="stat-blocks" icon={Boxes} label="Blocos de conteúdo" value={sum(data.blocks)} hint={`${Object.keys(data.blocks).length} tipos em uso`} />
          <Stat testId="stat-relations" icon={GitBranch} label="Relações pedagógicas" value={data.relations} />
          <Stat testId="stat-versions" icon={History} label="Versões publicadas" value={data.versions} />
          <Stat testId="stat-users" icon={Users} label="Usuários" value={sum(data.users)} hint={`${data.users.student || 0} estudantes`} />
        </div>
      )}
      <section className="mt-14 max-w-3xl">
        <h2 className="mb-6 text-lg font-semibold text-slate-200">Atividade recente</h2>
        <HistoryList limit={15} />
      </section>
    </div>
  );
}
