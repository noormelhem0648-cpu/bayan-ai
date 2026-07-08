import { Routes, Route, Navigate } from "react-router-dom";

import Layout from "./components/Layout";
import ProtectedRoute from "./components/ProtectedRoute";

import AuthPage from "./pages/AuthPage";
import HomePage from "./pages/HomePage";
import MajorsPage from "./pages/MajorsPage";
import YearsPage from "./pages/YearsPage";
import SubjectsPage from "./pages/SubjectsPage";
import ChatPage from "./pages/ChatPage";
import SettingsPage from "./pages/SettingsPage";
import ProfilePage from "./pages/ProfilePage";
import InstructorPage from "./pages/InstructorPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<AuthPage />} />

      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<HomePage />} />
        <Route path="track/:trackId" element={<MajorsPage />} />
        <Route path="major/:majorId" element={<YearsPage />} />
        <Route path="year/:yearId" element={<SubjectsPage />} />
        <Route path="subject/:subjectId" element={<ChatPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route
          path="instructor"
          element={
            <ProtectedRoute roles={["instructor", "admin"]}>
              <InstructorPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="admin"
          element={
            <ProtectedRoute roles={["admin"]}>
              <AdminPage />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
