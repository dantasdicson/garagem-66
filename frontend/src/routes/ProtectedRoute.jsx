import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function ProtectedRoute() {
  const { autenticado, carregando, usuario } = useAuth();
  const location = useLocation();
  if (carregando) return <div className="page-state" role="status">Validando sua sessão...</div>;
  if (!autenticado) return <Navigate to="/login" replace state={{ from: location }} />;
  if (usuario.deve_alterar_senha && location.pathname !== "/alterar-senha") {
    return <Navigate to="/alterar-senha" replace />;
  }
  if (!usuario.deve_alterar_senha && location.pathname === "/alterar-senha") {
    return <Navigate to="/" replace />;
  }
  return <Outlet />;
}

