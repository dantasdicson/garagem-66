import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const etapas = [
  ["ABERTA", "Aberta"],
  ["AGUARDANDO_ORCAMENTO", "Aguardando orçamento"],
  ["AGUARDANDO_APROVACAO", "Aguardando aprovação"],
  ["EM_EXECUCAO", "Em execução"],
  ["AGUARDANDO_PECAS", "Aguardando peças"],
  ["CONCLUIDA", "Concluída"],
];
const nomesStatus = Object.fromEntries(etapas);
nomesStatus.CONCLUIDA_NAO_APROVADA = "Concluída — não aprovada";

export default function OrdemServicoDetalhePage() {
  const { ordemId } = useParams();
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [ordem, setOrdem] = useState(null);
  const [orcamento, setOrcamento] = useState(null);
  const [historico, setHistorico] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      setCarregando(true); setErro("");
      try {
        const ordemAtual = await apiRequest(`/oficina/ordens-servico/${ordemId}/`);
        const [orcamentos, eventos] = await Promise.all([
          apiRequest("/oficina/orcamentos/"),
          apiRequest(`/oficina/historico-status-ordens/?ordem_servico=${ordemId}`),
        ]);
        if (!ativo) return;
        setOrdem(ordemAtual);
        setOrcamento(extrairLista(orcamentos).find((item) => item.ordem_servico === ordemAtual.id) || null);
        setHistorico(extrairLista(eventos));
      } catch (error) { if (ativo) setErro(error.message); }
      finally { if (ativo) setCarregando(false); }
    }
    carregar();
    return () => { ativo = false; };
  }, [ordemId]);

  const etapaAtual = useMemo(() => {
    if (!ordem) return 0;
    if (ordem.status === "CONCLUIDA_NAO_APROVADA") return 2;
    return Math.max(0, etapas.findIndex(([status]) => status === ordem.status));
  }, [ordem]);

  const voltar = usuario.tipo === "CLIENTE" ? "/minhas-ordens" : "/ordens";
  if (carregando) return <section className="page-section"><p className="muted">Carregando ordem de serviço...</p></section>;
  if (erro || !ordem) return <section className="page-section"><p className="form-error">{erro || "Ordem não encontrada."}</p><button className="button button-link" onClick={() => navigate(voltar)}>← Voltar</button></section>;

  return <section className="page-section order-page">
    <div className="order-page-header"><button className="back-link" type="button" onClick={() => navigate(voltar)}>← Voltar para ordens</button><div><p className="eyebrow">Ordem de serviço</p><h1>{ordem.numero}</h1><p>Acompanhe todas as informações e a evolução deste atendimento.</p></div><span className={`status-badge status-${ordem.status.toLowerCase()}`}>{nomesStatus[ordem.status] || ordem.status}</span></div>

    <article className="order-progress-card"><h2>Andamento do serviço</h2><div className="order-progress">{etapas.map(([status, nome], indice) => <div className={indice <= etapaAtual ? "progress-step completed" : "progress-step"} key={status}><span>{indice < etapaAtual ? "✓" : indice + 1}</span><small>{nome}</small></div>)}</div></article>

    <div className="order-page-grid">
      <article className="order-info-card"><h2>Dados da ordem</h2><dl className="detail-list"><div><dt>Cliente</dt><dd>{ordem.cliente_nome || `Cliente #${ordem.cliente}`}</dd></div><div><dt>Motocicleta</dt><dd>{ordem.motocicleta_descricao || `Motocicleta #${ordem.motocicleta}`}</dd></div><div><dt>Mecânico responsável</dt><dd>{ordem.mecanico_nome || (ordem.mecanico ? `Usuário #${ordem.mecanico}` : "Não atribuído")}</dd></div><div><dt>Tipo de manutenção</dt><dd>{ordem.tipo_manutencao === "PREVENTIVA" ? "Preventiva" : "Corretiva"}</dd></div><div><dt>Aberta em</dt><dd>{new Date(ordem.aberta_em).toLocaleString("pt-BR")}</dd></div><div><dt>Atualizada em</dt><dd>{new Date(ordem.atualizada_em).toLocaleString("pt-BR")}</dd></div></dl><div className="order-problem"><small>Problema relatado / serviço solicitado</small><p>{ordem.descricao_problema}</p></div></article>

      <aside className="order-side-column"><article className="order-info-card"><div className="card-title-row"><h2>Orçamento</h2><Link to="/orcamentos">Ver orçamento →</Link></div>{orcamento ? <><strong className="order-budget-total">{Number(orcamento.valor_total).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</strong><p><span className={`status-badge status-${orcamento.status.toLowerCase()}`}>{orcamento.status.replaceAll("_", " ")}</span></p><small>Validade: {orcamento.validade ? new Date(`${orcamento.validade}T12:00:00`).toLocaleDateString("pt-BR") : "Não informada"}</small></> : <p className="muted">Ainda não há orçamento emitido.</p>}</article>
      <article className="order-info-card"><h2>Histórico</h2><ol className="order-history">{historico.map((evento) => <li key={evento.id}><span /><div><strong>{evento.novo_status_descricao}</strong><small>{new Date(evento.criado_em).toLocaleString("pt-BR")} · {evento.responsavel_nome || "Sistema"}</small><p>{evento.observacao}</p></div></li>)}{!historico.length ? <li className="muted">Nenhuma atualização registrada.</li> : null}</ol></article></aside>
    </div>
  </section>;
}
