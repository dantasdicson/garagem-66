import { useAuth } from "../contexts/AuthContext";

export default function DashboardPage() {
  const { usuario } = useAuth();
  const cliente = usuario.tipo === "CLIENTE";
  return (
    <section className="page-section">
      <div className="page-title"><span className="page-title-icon">⌁</span><div><h1>{cliente ? "Área do Cliente" : "Dashboard"}</h1><p>{cliente ? "Acompanhe suas motocicletas, ordens de serviço, orçamentos e histórico." : "Visão geral da oficina"}</p></div></div>
      <div className="dashboard-grid">
        <article className="metric-card tone-red"><span className="metric-icon">{cliente ? "♞" : "▤"}</span><div><span>{cliente ? "Motocicletas cadastradas" : "Ordens de Serviço"}</span><strong>{cliente ? "2" : "18"}</strong><small>{cliente ? "Total de motocicletas" : "em andamento"}</small></div></article>
        <article className="metric-card tone-orange"><span className="metric-icon">▧</span><div><span>{cliente ? "OS em andamento" : "Orçamentos"}</span><strong>{cliente ? "2" : "7"}</strong><small>{cliente ? "Ordens de serviço ativas" : "aguardando aprovação"}</small></div></article>
        <article className="metric-card tone-green"><span className="metric-icon">✓</span><div><span>{cliente ? "Orçamentos pendentes" : "Serviços"}</span><strong>{cliente ? "1" : "32"}</strong><small>{cliente ? "Aguardando sua decisão" : "concluídos no mês"}</small></div></article>
        {!cliente ? <article className="metric-card tone-blue"><span className="metric-icon">♞</span><div><span>Motocicletas</span><strong>15</strong><small>na oficina</small></div></article> : null}
      </div>
      <article className="dashboard-panel"><div><h2>{cliente ? "Minhas motocicletas" : "Ordens de Serviço recentes"}</h2><p>As informações operacionais aparecerão aqui conforme os registros da oficina.</p></div><button className="button button-link">Ver detalhes →</button></article>
    </section>
  );
}

