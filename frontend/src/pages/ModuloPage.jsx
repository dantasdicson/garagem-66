import { Navigate, useParams } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

const modulosPorPerfil = {
  ADMINISTRADOR: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque", "usuarios"],
  ATENDENTE: ["clientes", "motocicletas", "entradas", "ordens", "orcamentos", "estoque"],
  MECANICO: ["minhas-ordens", "requisicoes", "estoque"],
  CLIENTE: ["minhas-motos", "minhas-ordens", "orcamentos", "historico"],
};

export default function ModuloPage() {
  const { modulo } = useParams();
  const { usuario } = useAuth();
  if (!(modulosPorPerfil[usuario.tipo] ?? []).includes(modulo)) return <Navigate to="/" replace />;
  const titulo = modulo.replaceAll("-", " ").replace(/\b\w/g, (letra) => letra.toUpperCase());
  return (
    <section className="page-section">
      <p className="eyebrow">Módulo</p><h1>{titulo}</h1>
      <div className="empty-state"><strong>Estrutura preparada</strong><p>Esta tela será conectada aos endpoints do backend na próxima etapa.</p></div>
    </section>
  );
}

