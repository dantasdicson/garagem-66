import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./routes/ProtectedRoute";
import AppLayout from "./layouts/AppLayout";
import AlterarSenhaPage from "./pages/AlterarSenhaPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import ModuloPage from "./pages/ModuloPage";
import ClientesPage from "./pages/ClientesPage";
import MotocicletasPage from "./pages/MotocicletasPage";
import OrdensServicoPage from "./pages/OrdensServicoPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/alterar-senha" element={<AlterarSenhaPage />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/clientes" element={<ClientesPage />} />
          <Route path="/motocicletas" element={<MotocicletasPage />} />
          <Route path="/minhas-motos" element={<MotocicletasPage />} />
          <Route path="/ordens" element={<OrdensServicoPage />} />
          <Route path="/minhas-ordens" element={<OrdensServicoPage />} />
          <Route path="/:modulo" element={<ModuloPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
