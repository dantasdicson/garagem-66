import { useAuth } from "../contexts/AuthContext";

const descricoes = {
  ADMINISTRADOR: "Acompanhe toda a operação, usuários e estoque da oficina.",
  ATENDENTE: "Cadastre clientes, registre entradas e acompanhe os orçamentos.",
  MECANICO: "Consulte suas ordens e registre os serviços em execução.",
  CLIENTE: "Acompanhe suas motocicletas, ordens de serviço e orçamentos.",
};

export default function DashboardPage() {
  const { usuario } = useAuth();
  return (
    <section className="page-section">
      <p className="eyebrow">Visão geral</p>
      <h1>Olá, {usuario.nome.split(" ")[0]}</h1>
      <p className="lead">{descricoes[usuario.tipo]}</p>
      <div className="dashboard-grid">
        <article className="metric-card"><span>Ambiente</span><strong>Conectado</strong><small>API Garagem 66</small></article>
        <article className="metric-card"><span>Perfil</span><strong>{usuario.tipo}</strong><small>Acessos ajustados ao seu perfil</small></article>
        <article className="metric-card"><span>Sessão</span><strong>Protegida</strong><small>Renovação automática do token</small></article>
      </div>
    </section>
  );
}

