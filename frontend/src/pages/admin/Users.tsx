import React from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, apiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { User } from "@/types";
import { Loader, PageHeader } from "@/components/common";
import { formatDate, ROLE_LABELS } from "@/lib/utils";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function Users() {
  const qc = useQueryClient();
  const { user: me } = useAuth();
  const { data, isLoading } = useQuery({ queryKey: ["users"], queryFn: () => api.get<User[]>("/users").then((r) => r.data) });
  const setRole = async (id: string, role: string) => {
    try { await api.put(`/users/${id}/role`, { role }); qc.invalidateQueries({ queryKey: ["users"] }); toast.success("Papel atualizado"); }
    catch (e) { toast.error(apiError(e)); }
  };
  return (
    <div className="max-w-5xl">
      <PageHeader eyebrow="acesso" title="Usuários e papéis" description="Admin gerencia tudo; editor cria e publica conteúdo; estudante consome trilhas." />
      {isLoading ? <Loader /> : (
        <div className="overflow-hidden rounded-xl border border-slate-800">
          {(data || []).map((u) => (
            <div key={u.id} data-testid={`user-row-${u.email}`} className="flex items-center gap-4 border-b border-slate-800 bg-slate-900/40 px-5 py-3 last:border-0">
              <span className="grid h-8 w-8 place-items-center rounded-full bg-slate-800 font-heading text-xs font-bold text-slate-300">{u.name.slice(0, 2).toUpperCase()}</span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-slate-100">{u.name}</p>
                <p className="truncate text-xs text-slate-500">{u.email} · desde {formatDate(u.created_at)}</p>
              </div>
              <Select value={u.role} onValueChange={(v) => setRole(u.id, v)} disabled={!!me && u.id === me.id}>
                <SelectTrigger data-testid={`user-role-select-${u.email}`} className="w-36"><SelectValue /></SelectTrigger>
                <SelectContent>{Object.entries(ROLE_LABELS).map(([k, l]) => <SelectItem key={k} value={k}>{l}</SelectItem>)}</SelectContent>
              </Select>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
