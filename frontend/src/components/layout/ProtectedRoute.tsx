import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Loader } from "@/components/common";

export function ProtectedRoute({ perm, children }: { perm?: string; children: React.ReactElement }) {
  const { user, can } = useAuth();
  const location = useLocation();
  if (user === null) return <Loader label="Verificando sessão..." />;
  if (user === false) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (perm && !can(perm)) return <Navigate to="/" replace />;
  return children;
}
