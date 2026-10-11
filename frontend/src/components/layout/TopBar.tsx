import React from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { BookMarked, LayoutDashboard, LogOut, NotebookTabs, UserRound } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn, ROLE_LABELS } from "@/lib/utils";

export function Logo() {
  return (
    <Link to="/" data-testid="app-logo" className="flex items-center gap-2.5">
      <span className="grid h-8 w-8 place-items-center rounded-lg border border-emerald-500/40 bg-emerald-500/10 font-mono text-sm font-bold text-emerald-400">
        {"{t}"}
      </span>
      <span className="font-heading text-lg font-bold tracking-tight text-slate-50">
        Trilha<span className="text-emerald-400">Code</span>
      </span>
    </Link>
  );
}

const navCls = ({ isActive }: { isActive: boolean }) =>
  cn("flex items-center gap-2 rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors",
    isActive ? "bg-slate-800 text-slate-50" : "text-slate-400 hover:text-slate-100");

export function TopBar() {
  const { user, logout, can } = useAuth();
  const navigate = useNavigate();
  if (!user) return null;
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#090D16]/80 backdrop-blur-xl">
      <div className="flex h-14 items-center justify-between px-4 sm:px-6">
        <div className="flex items-center gap-8">
          <Logo />
          <nav className="flex items-center gap-1">
            <NavLink to="/" end className={navCls} data-testid="nav-study">
              <BookMarked className="h-4 w-4" /> Estudar
            </NavLink>
            <NavLink to="/estudos" className={navCls} data-testid="nav-my-study">
              <NotebookTabs className="h-4 w-4" /> Meu estudo
            </NavLink>
            {can("content.read") && (
              <NavLink to="/admin" className={navCls} data-testid="nav-admin">
                <LayoutDashboard className="h-4 w-4" /> Admin
              </NavLink>
            )}
          </nav>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger data-testid="user-menu-trigger"
            className="flex items-center gap-2.5 rounded-full border border-slate-800 bg-slate-900/60 py-1 pl-1 pr-3 text-sm hover:border-slate-700">
            <span className="grid h-7 w-7 place-items-center rounded-full bg-emerald-500/15 font-heading text-xs font-bold text-emerald-300">
              {user.name.slice(0, 2).toUpperCase()}
            </span>
            <span className="hidden text-slate-200 sm:inline">{user.name}</span>
            <span className="hidden font-mono text-[10px] uppercase text-slate-500 sm:inline">{ROLE_LABELS[user.role]}</span>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-52 border-slate-800 bg-slate-900">
            <DropdownMenuLabel className="text-xs text-slate-400">{user.email}</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem data-testid="user-menu-profile" onClick={() => navigate("/perfil")}>
              <UserRound className="mr-2 h-4 w-4" /> Perfil
            </DropdownMenuItem>
            <DropdownMenuItem data-testid="user-menu-logout" onClick={async () => { await logout(); navigate("/login"); }}>
              <LogOut className="mr-2 h-4 w-4" /> Sair
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
