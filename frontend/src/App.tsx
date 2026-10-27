import React, { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "@/context/AuthContext";
import { PendingNoteNavigationGuard } from "@/hooks/useStudy";
import { TopBar } from "@/components/layout/TopBar";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import AuthPage from "@/pages/AuthPage";
import Catalog from "@/pages/student/Catalog";
import ConfirmEmail from "@/pages/ConfirmEmail";
import PasswordRecovery from "@/pages/PasswordRecovery";
import PasswordReset from "@/pages/PasswordReset";

const TrackViewer = lazy(() => import("@/pages/student/TrackViewer"));
const Profile = lazy(() => import("@/pages/Profile"));
const MyStudy = lazy(() => import("@/pages/student/MyStudy"));
const Grading = lazy(() => import("@/pages/admin/Grading"));
const Versions = lazy(() => import("@/pages/admin/Versions"));
const ImportTrack = lazy(() => import("@/pages/admin/ImportTrack"));
const AdminLayout = lazy(() => import("@/pages/admin/AdminLayout"));
const AdminDashboard = lazy(() => import("@/pages/admin/AdminDashboard"));
const AdminTracks = lazy(() => import("@/pages/admin/AdminTracks"));
const TrackEditor = lazy(() => import("@/pages/admin/TrackEditor"));
const Taxonomies = lazy(() => import("@/pages/admin/Taxonomies"));
const Users = lazy(() => import("@/pages/admin/Users"));

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <PendingNoteNavigationGuard />
        <TopBar />
        <Suspense fallback={<div role="status" className="p-6">Carregando…</div>}>
          <Routes>
            <Route path="/login" element={<AuthPage mode="login" />} />
            <Route path="/cadastro" element={<AuthPage mode="register" />} />
            <Route path="/auth/confirm-email" element={<ConfirmEmail />} />
            <Route path="/recuperar-senha" element={<PasswordRecovery />} />
            <Route path="/auth/reset-password" element={<PasswordReset />} />
            <Route path="/" element={<ProtectedRoute><Catalog /></ProtectedRoute>} />
            <Route path="/estudos" element={<ProtectedRoute><MyStudy /></ProtectedRoute>} />
            <Route path="/perfil" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/trilhas/:trackId" element={<ProtectedRoute><TrackViewer /></ProtectedRoute>} />
            <Route path="/trilhas/:trackId/n/:nodeId" element={<ProtectedRoute><TrackViewer /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute perm="content.read"><AdminLayout /></ProtectedRoute>}>
              <Route index element={<AdminDashboard />} />
              <Route path="trilhas" element={<AdminTracks />} />
              <Route path="correcoes" element={<ProtectedRoute perm="submissions.grade"><Grading /></ProtectedRoute>} />
              <Route path="importar" element={<ProtectedRoute perm="content.write"><ImportTrack /></ProtectedRoute>} />
              <Route path="taxonomias" element={<Taxonomies />} />
              <Route path="usuarios" element={<ProtectedRoute perm="users.manage"><Users /></ProtectedRoute>} />
            </Route>
            <Route path="/admin/trilhas/:trackId" element={<ProtectedRoute perm="content.write"><TrackEditor /></ProtectedRoute>} />
            <Route path="/admin/trilhas/:trackId/versoes" element={<ProtectedRoute perm="content.read"><Versions /></ProtectedRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
      <Toaster theme="dark" position="bottom-right" richColors closeButton />
    </AuthProvider>
  );
}
