import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import { AuthProvider } from "@/context/AuthContext";
import { TopBar } from "@/components/layout/TopBar";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import AuthPage from "@/pages/AuthPage";
import Catalog from "@/pages/student/Catalog";
import TrackViewer from "@/pages/student/TrackViewer";
import Profile from "@/pages/Profile";
import MyStudy from "@/pages/student/MyStudy";
import Grading from "@/pages/admin/Grading";
import Versions from "@/pages/admin/Versions";
import ImportTrack from "@/pages/admin/ImportTrack";
import AdminLayout from "@/pages/admin/AdminLayout";
import AdminDashboard from "@/pages/admin/AdminDashboard";
import AdminTracks from "@/pages/admin/AdminTracks";
import TrackEditor from "@/pages/admin/TrackEditor";
import Taxonomies from "@/pages/admin/Taxonomies";
import Users from "@/pages/admin/Users";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <TopBar />
        <Routes>
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/cadastro" element={<AuthPage mode="register" />} />
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
      </BrowserRouter>
      <Toaster theme="dark" position="bottom-right" richColors closeButton />
    </AuthProvider>
  );
}
