import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import { ClipboardCheck, FileUp, Gauge, Route, Shapes, Users } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";

const linkCls = ({ isActive }: { isActive: boolean }) =>
  cn("flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-emerald-500/10 text-emerald-300" : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-100");

export default function AdminLayout() {
  const { can } = useAuth();
  return (
    <div className="grid min-h-[calc(100vh-3.5rem)] md:grid-cols-[220px_1fr]">
      <aside className="border-r border-slate-800 bg-sidebar p-4">
        <p className="mb-3 px-3 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-500">painel editorial</p>
        <nav className="space-y-1">
          <NavLink end to="/admin" className={linkCls} data-testid="admin-nav-dashboard"><Gauge className="h-4 w-4" />Visão geral</NavLink>
          <NavLink to="/admin/trilhas" className={linkCls} data-testid="admin-nav-tracks"><Route className="h-4 w-4" />Trilhas</NavLink>
          {can("content.write") && <NavLink to="/admin/importar" className={linkCls} data-testid="admin-nav-import"><FileUp className="h-4 w-4" />Importar estrutura</NavLink>}
          {can("submissions.grade") && <NavLink to="/admin/correcoes" className={linkCls} data-testid="admin-nav-grading"><ClipboardCheck className="h-4 w-4" />Correções</NavLink>}
          <NavLink to="/admin/taxonomias" className={linkCls} data-testid="admin-nav-taxonomies"><Shapes className="h-4 w-4" />Taxonomias & blocos</NavLink>
          {can("users.manage") && <NavLink to="/admin/usuarios" className={linkCls} data-testid="admin-nav-users"><Users className="h-4 w-4" />Usuários</NavLink>}
        </nav>
      </aside>
      <main className="min-w-0 px-6 py-10 lg:px-12"><Outlet /></main>
    </div>
  );
}
