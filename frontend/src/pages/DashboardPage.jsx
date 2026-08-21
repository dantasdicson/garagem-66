import { useCallback, useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";
import { apiRequest } from "../api/client";
import { extrairLista } from "../utils/apiData";

export default function DashboardPage() {
  const { usuario } = useAuth();
  const cliente = usuario.tipo === "CLIENTE";
  const [metricas, setMetricas] = useState({ motos: 0, ativas: 0, pendentes: 0, concluidas: 0 });
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const carregarMetricas = useCallback(async () => {
    setCarregando(true); setErro("");
    try {
      const [dadosMotos, dadosOrdens, dadosOrcamentos] = await Promise.all([
        apiRequest("/oficina/motocicletas/"),
        apiRequest("/oficina/ordens-servico/"),
        apiRequest("/oficina/orcamentos/"),
      ]);
      const motos = extrairLista(dadosMotos);
      const ordens = extrairLista(dadosOrdens);
      const orcamentos = extrairLista(dadosOrcamentos);
      const finalizados = new Set(["CONCLUIDA", "CONCLUIDA_NAO_APROVADA"]);
      setMetricas({
        motos: motos.length,
        ativas: ordens.filter((ordem) => !finalizados.has(ordem.status)).length,
        pendentes: orcamentos.filter((orcamento) => orcamento.status === "AGUARDANDO_APROVACAO").length,
        concluidas: ordens.filter((ordem) => ordem.status === "CONCLUIDA").length,
      });
    } catch (error) { setErro(error.message); }
    finally { setCarregando(false); }
  }, []);

  useEffect(() => { carregarMetricas(); }, [carregarMetricas]);
  const numero = (valor) => carregando ? "—" : valor;
  return (
    <section className="page-section">
      <div className="page-title"><span className="page-title-icon">⌁</span><div><h1>{cliente ? "Área do Cliente" : "Dashboard"}</h1><p>{cliente ? "Acompanhe suas motocicletas, ordens de serviço, orçamentos e histórico." : "Visão geral da oficina"}</p></div></div>
      <div className="dashboard-grid">
        <Link className="metric-card metric-link tone-red" to={cliente ? "/minhas-motos" : "/ordens"}><span className="metric-icon">{cliente ? "♞" : "▤"}</span><div><span>{cliente ? "Motocicletas cadastradas" : "Ordens de Serviço"}</span><strong>{numero(cliente ? metricas.motos : metricas.ativas)}</strong><small>{cliente ? "Ver minhas motocicletas" : "Ver ordens em andamento"}</small></div><span className="metric-arrow">→</span></Link>
        <Link className="metric-card metric-link tone-orange" to={cliente ? "/minhas-ordens" : "/orcamentos"}><span className="metric-icon">▧</span><div><span>{cliente ? "OS em andamento" : "Orçamentos"}</span><strong>{numero(cliente ? metricas.ativas : metricas.pendentes)}</strong><small>{cliente ? "Acompanhar minhas ordens" : "Ver aguardando aprovação"}</small></div><span className="metric-arrow">→</span></Link>
        <Link className="metric-card metric-link tone-green" to={cliente ? "/orcamentos" : "/ordens"}><span className="metric-icon">✓</span><div><span>{cliente ? "Orçamentos pendentes" : "Serviços"}</span><strong>{numero(cliente ? metricas.pendentes : metricas.concluidas)}</strong><small>{cliente ? "Visualizar e decidir agora" : "Ver serviços concluídos"}</small></div><span className="metric-arrow">→</span></Link>
        {!cliente ? <Link className="metric-card metric-link tone-blue" to="/motocicletas"><span className="metric-icon">♞</span><div><span>Motocicletas</span><strong>{numero(metricas.motos)}</strong><small>Ver motocicletas cadastradas</small></div><span className="metric-arrow">→</span></Link> : null}
      </div>
      {erro ? <p className="form-error dashboard-error">Não foi possível atualizar os indicadores: {erro}</p> : null}
      <article className="dashboard-panel"><div><h2>{cliente ? "Minhas motocicletas" : "Ordens de Serviço recentes"}</h2><p>As informações operacionais aparecerão aqui conforme os registros da oficina.</p></div><Link className="button button-link" to={cliente ? "/minhas-motos" : "/ordens"}>Ver detalhes →</Link></article>
    </section>
  );
}
