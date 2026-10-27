import React, { useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, CalendarClock, Clock3, Layers3, PlayCircle } from "lucide-react";
import { useReviews } from "@/hooks/useStudy";
import { groupReviews } from "@/lib/groupReviews";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { Track, User } from "@/types";
import { EmptyState, Loader, PageHeader, ProgressBar, StatusBadge } from "@/components/common";
import { formatDate } from "@/lib/utils";

interface Overview {
  states: { track_id: string; last_node_id?: string; last_node_title?: string; last_at?: string }[];
  completed: Record<string, number>;
}

const COVER = "https://images.unsplash.com/photo-1614741118887-7a4ee193a5fa?crop=entropy&cs=srgb&fm=jpg&q=80&w=1200";

function TrackCard({ track, completed, index }: { track: Track; completed: number; index: number }) {
  const last = track.hierarchy[track.hierarchy.length - 1];
  const total = track.counts?.[last] || 0;
  const pct = total ? Math.min(100, Math.round((completed / total) * 100)) : 0;
  return (
    <Link to={`/trilhas/${track.id}`} data-testid={`catalog-track-card-${track.slug}`} style={{ animationDelay: `${index * 60}ms` }}
      className="group flex flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900/70 backdrop-blur-md transition-colors hover:border-emerald-500/40 fade-up">
      <div className="relative h-28 overflow-hidden border-b border-slate-800">
        <img src={track.cover_url || COVER} alt="" className="h-full w-full object-cover opacity-40 transition-transform duration-500 group-hover:scale-105" />
        <div className="absolute inset-0 grid-bg" />
        {track.status !== "published" && <div className="absolute right-3 top-3"><StatusBadge status={track.status} /></div>}
      </div>
      <div className="flex flex-1 flex-col gap-4 p-5">
        <div>
          <h3 className="text-lg font-semibold text-slate-50">{track.title}</h3>
          <p className="mt-1 line-clamp-2 text-sm text-slate-400">{track.subtitle || track.description}</p>
        </div>
        <div className="flex flex-wrap gap-3 font-mono text-[11px] text-slate-500">
          {track.hierarchy.filter((k) => track.counts?.[k]).map((k) => (
            <span key={k}>{track.counts?.[k]} {(track.level_labels[k] || k).toLowerCase()}s</span>
          ))}
        </div>
        <div className="mt-auto space-y-2">
          <div className="flex justify-between text-xs text-slate-400"><span>{completed}/{total} concluídos</span><span>{pct}%</span></div>
          <ProgressBar value={pct} testId={`catalog-track-progress-${track.slug}`} />
        </div>
      </div>
    </Link>
  );
}

export default function Catalog() {
  const { user } = useAuth();
  const tracks = useQuery({ queryKey: ["tracks", "catalog"], queryFn: () => api.get<Track[]>("/tracks").then((r) => r.data) });
  const overview = useQuery({ queryKey: ["overview"], queryFn: () => api.get<Overview>("/progress/overview").then((r) => r.data) });
  const visible = useMemo(() => (tracks.data || []).filter((t) => t.status !== "archived"), [tracks.data]);
  const resume = overview.data?.states.find((s) => s.last_node_id && visible.some((t) => t.id === s.track_id));
  const resumeTrack = visible.find((t) => t.id === resume?.track_id);
  const reviews = useReviews();
  const due = reviews.data ? (({ overdue, today }) => overdue.length + today.length)(groupReviews(reviews.data)) : 0;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <PageHeader eyebrow="área de estudos" title={`Olá, ${(user as User).name.split(" ")[0]}`}
        description="Escolha uma trilha, navegue pela estrutura e retome exatamente de onde parou." />
      {resume && resumeTrack && (
        <Link to={`/trilhas/${resumeTrack.id}/n/${resume.last_node_id}`} data-testid="catalog-resume-card"
          className="mb-12 flex items-center justify-between gap-6 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-6 shadow-[0_0_30px_rgba(16,185,129,0.06)] fade-up hover:border-emerald-500/60">
          <div className="flex items-center gap-4">
            <PlayCircle className="h-9 w-9 text-emerald-400" />
            <div>
              <p className="font-mono text-[11px] uppercase tracking-widest text-emerald-400">continuar de onde parou</p>
              <p className="mt-1 text-lg font-semibold text-slate-50">{resume.last_node_title || "Último tópico"}</p>
              <p className="flex items-center gap-1.5 text-xs text-slate-400"><Clock3 className="h-3 w-3" />{resumeTrack.title} · {formatDate(resume.last_at)}</p>
            </div>
          </div>
          <ArrowRight className="h-5 w-5 text-emerald-400" />
        </Link>
      )}
      {due > 0 && (
        <Link to="/estudos" data-testid="catalog-reviews-due" className="-mt-6 mb-12 flex items-center gap-3 rounded-xl border border-cyan-500/25 bg-cyan-500/5 px-6 py-4 text-sm text-cyan-100 hover:border-cyan-500/50 fade-up">
          <CalendarClock className="h-5 w-5 text-cyan-300" />
          {due} revisão(ões) para hoje ou atrasadas<ArrowRight className="ml-auto h-4 w-4" />
        </Link>
      )}
      <div className="mb-5 flex items-center gap-2">
        <Layers3 className="h-4 w-4 text-slate-500" />
        <h2 className="text-lg font-semibold text-slate-200">Trilhas disponíveis</h2>
      </div>
      {tracks.isLoading ? <Loader /> : visible.length === 0 ? (
        <EmptyState icon="Route" title="Nenhuma trilha publicada ainda" description="Quando trilhas forem publicadas pela equipe editorial, elas aparecerão aqui." />
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((t, i) => <TrackCard key={t.id} track={t} index={i} completed={overview.data?.completed[t.id] || 0} />)}
        </div>
      )}
    </div>
  );
}
