import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";

export default function DashboardPage() {
  const { usuario } = useAuth();
  const cliente = usuario.tipo === "CLIENTE";
  return (
    <section className="page-section">
      <div className="page-title"><span className="page-title-icon">⌁</span><div><h1>{cliente ? "Área do Cliente" : "Dashboard"}</h1><p>{cliente ? "Acompanhe suas motocicletas, ordens de serviço, orçamentos e histórico." : "Visão geral da oficina"}</p></div></div>
      <div className="dashboard-grid">
        <Link className="metric-card metric-link tone-red" to={cliente ? "/minhas-motos" : "/ordens"}><span className="metric-icon">{cliente ? "♞" : "▤"}</span><div><span>{cliente ? "Motocicletas cadastradas" : "Ordens de Serviço"}</span><strong>{cliente ? "2" : "18"}</strong><small>{cliente ? "Ver minhas motocicletas" : "Ver ordens em andamento"}</small></div><span className="metric-arrow">→</span></Link>
        <Link className="metric-card metric-link tone-orange" to={cliente ? "/minhas-ordens" : "/orcamentos"}><span className="metric-icon">▧</span><div><span>{cliente ? "OS em andamento" : "Orçamentos"}</span><strong>{cliente ? "2" : "7"}</strong><small>{cliente ? "Acompanhar minhas ordens" : "Ver aguardando aprovação"}</small></div><span className="metric-arrow">→</span></Link>
        <Link className="metric-card metric-link tone-green" to={cliente ? "/orcamentos" : "/ordens"}><span className="metric-icon">✓</span><div><span>{cliente ? "Orçamentos pendentes" : "Serviços"}</span><strong>{cliente ? "1" : "32"}</strong><small>{cliente ? "Visualizar e decidir agora" : "Ver serviços concluídos"}</small></div><span className="metric-arrow">→</span></Link>
        {!cliente ? <Link className="metric-card metric-link tone-blue" to="/motocicletas"><span className="metric-icon">♞</span><div><span>Motocicletas</span><strong>15</strong><small>Ver motocicletas na oficina</small></div><span className="metric-arrow">→</span></Link> : null}
      </div>
      <article className="dashboard-panel"><div><h2>{cliente ? "Minhas motocicletas" : "Ordens de Serviço recentes"}</h2><p>As informações operacionais aparecerão aqui conforme os registros da oficina.</p></div><Link className="button button-link" to={cliente ? "/minhas-motos" : "/ordens"}>Ver detalhes →</Link></article>
    </section>
  );
}
