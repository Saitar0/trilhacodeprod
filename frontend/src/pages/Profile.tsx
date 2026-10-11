import React, { useState } from "react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";
import { api, apiError } from "@/lib/api";
import { User } from "@/types";
import { PageHeader } from "@/components/common";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ROLE_LABELS } from "@/lib/utils";

export default function Profile() {
  const { user, setUser } = useAuth();
  const u = user as User;
  const [name, setName] = useState(u.name);
  const [bio, setBio] = useState(u.profile?.bio || "");
  const [goals, setGoals] = useState(u.profile?.goals || "");

  const save = async () => {
    try {
      const { data } = await api.put<User>("/profile", { name, profile: { ...u.profile, bio, goals } });
      setUser(data);
      toast.success("Perfil atualizado");
    } catch (e) {
      toast.error(apiError(e));
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <PageHeader eyebrow={ROLE_LABELS[u.role]} title="Seu perfil" description={u.email} />
      <div className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="space-y-2"><Label>Nome</Label>
          <Input data-testid="profile-name-input" value={name} onChange={(e) => setName(e.target.value)} /></div>
        <div className="space-y-2"><Label>Bio</Label>
          <Textarea data-testid="profile-bio-input" value={bio} onChange={(e) => setBio(e.target.value)} /></div>
        <div className="space-y-2"><Label>Objetivos de estudo</Label>
          <Textarea data-testid="profile-goals-input" value={goals} onChange={(e) => setGoals(e.target.value)} /></div>
        <Button data-testid="profile-save-button" className="rounded-full" onClick={save}>Salvar perfil</Button>
      </div>
    </div>
  );
}
