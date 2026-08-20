import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const rotulos = { PENDENTE: "Pendente", APROVADA: "Aprovada", RECUSADA: "Recusada" };

export default function RequisicoesPecasPage() {
  const { usuario } = useAuth();
  const autorizado = ["ADMINISTRADOR", "ATENDENTE", "MECANICO"].includes(usuario.tipo);
  const [requisicoes, setRequisicoes] = useState([]);
  const [pecas, setPecas] = useState([]);
  const [ordens, setOrdens] = useState([]);
  const [form, setForm] = useState({ peca: "", ordem_servico: "", quantidade: 1, observacoes: "" });
  const [status, setStatus] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [processando, setProcessando] = useState("");
  const [erro, setErro] = useState("");

  const carregar = useCallback(async () => {
    setCarregando(true); setErro("");
    try {
      const [r, p, o] = await Promise.all([apiRequest("/estoque/requisicoes-peca/"), apiRequest("/estoque/pecas/"), apiRequest("/oficina/ordens-servico/")]);
      setRequisicoes(extrairLista(r)); setPecas(extrairLista(p)); setOrdens(extrairLista(o));
    } catch (error) { setErro(error.message); } finally { setCarregando(false); }
  }, []);
  useEffect(() => { if (autorizado) carregar(); }, [autorizado, carregar]);

  const pecasPorId = useMemo(() => new Map(pecas.map((p) => [p.id, p])), [pecas]);
  const ordensPorId = useMemo(() => new Map(ordens.map((o) => [o.id, o])), [ordens]);
  const exibidas = status ? requisicoes.filter((r) => r.status === status) : requisicoes;
  const totais = Object.fromEntries(Object.keys(rotulos).map((s) => [s, requisicoes.filter((r) => r.status === s).length]));

  if (!autorizado) return <Navigate to="/" replace />;

  async function criar(event) {
    event.preventDefault(); setProcessando("nova"); setErro("");
    try {
      await apiRequest("/estoque/requisicoes-peca/", { method: "POST", body: JSON.stringify({ ...form, peca: Number(form.peca), ordem_servico: Number(form.ordem_servico), quantidade: Number(form.quantidade) }) });
      setForm({ peca: "", ordem_servico: "", quantidade: 1, observacoes: "" }); await carregar();
    } catch (error) { setErro(error.message); } finally { setProcessando(""); }
  }
  async function decidir(id, acao) {
    setProcessando(`${id}-${acao}`); setErro("");
    try { await apiRequest(`/estoque/requisicoes-peca/${id}/${acao}/`, { method: "POST", body: "{}" }); await carregar(); }
    catch (error) { setErro(error.message); } finally { setProcessando(""); }
  }

  return <section className="page-section">
    <div className="page-heading"><div><p className="eyebrow">Oficina</p><h1>Requisições de Peças</h1><p className="lead">Registre e acompanhe solicitações de peças para as ordens de serviço.</p></div></div>
    <div className="summary-grid"><article className="summary-card tone-orange"><span>◷</span><div><small>Pendentes</small><strong>{totais.PENDENTE || 0}</strong></div></article><article className="summary-card tone-green"><span>✓</span><div><small>Aprovadas</small><strong>{totais.APROVADA || 0}</strong></div></article><article className="summary-card tone-red"><span>×</span><div><small>Recusadas</small><strong>{totais.RECUSADA || 0}</strong></div></article></div>
    {erro ? <p className="form-error" role="alert">{erro}</p> : null}
    <div className={usuario.tipo === "MECANICO" ? "management-grid" : "management-grid single-column"}>
      <div className="table-card"><div className="table-toolbar"><select aria-label="Filtrar requisições" value={status} onChange={(e) => setStatus(e.target.value)}><option value="">Todos os status</option>{Object.entries(rotulos).map(([valor, nome]) => <option key={valor} value={valor}>{nome}</option>)}</select></div>{carregando ? <p className="muted">Carregando requisições...</p> : <div className="table-scroll"><table><thead><tr><th>Peça</th><th>Quantidade</th><th>OS</th><th>Status</th><th>Observação</th><th>Ações</th></tr></thead><tbody>{exibidas.map((item) => <tr key={item.id}><td><strong>{pecasPorId.get(item.peca)?.nome || `Peça #${item.peca}`}</strong></td><td>{item.quantidade}</td><td>{ordensPorId.get(item.ordem_servico)?.numero || `OS #${item.ordem_servico}`}</td><td><span className={`status-badge request-${item.status.toLowerCase()}`}>{rotulos[item.status]}</span></td><td>{item.observacoes || "—"}</td><td><div className="table-actions">{usuario.tipo === "ADMINISTRADOR" && item.status === "PENDENTE" ? <><button className="table-action action-approve" disabled={Boolean(processando)} onClick={() => decidir(item.id, "aprovar")}>Aprovar</button><button className="table-action action-reject" disabled={Boolean(processando)} onClick={() => decidir(item.id, "recusar")}>Recusar</button></> : <span className="muted">Visualização</span>}</div></td></tr>)}{!exibidas.length ? <tr><td className="empty-cell" colSpan="6">Nenhuma requisição encontrada.</td></tr> : null}</tbody></table></div>}</div>
      {usuario.tipo === "MECANICO" ? <form className="form-card" onSubmit={criar}><div><p className="eyebrow">Solicitação</p><h2>Nova requisição</h2></div><label htmlFor="req-os">Ordem de serviço</label><select id="req-os" required value={form.ordem_servico} onChange={(e) => setForm((v) => ({...v, ordem_servico:e.target.value}))}><option value="">Selecione</option>{ordens.filter((o) => ["EM_EXECUCAO", "AGUARDANDO_PECAS"].includes(o.status)).map((o) => <option key={o.id} value={o.id}>{o.numero}</option>)}</select><label htmlFor="req-peca">Peça</label><select id="req-peca" required value={form.peca} onChange={(e) => setForm((v) => ({...v, peca:e.target.value}))}><option value="">Selecione</option>{pecas.map((p) => <option key={p.id} value={p.id}>{p.codigo} — {p.nome}</option>)}</select><label htmlFor="req-qtd">Quantidade</label><input id="req-qtd" type="number" min="1" required value={form.quantidade} onChange={(e) => setForm((v) => ({...v, quantidade:e.target.value}))} /><label htmlFor="req-obs">Observações</label><textarea id="req-obs" rows="4" value={form.observacoes} onChange={(e) => setForm((v) => ({...v, observacoes:e.target.value}))} /><button className="button button-primary" disabled={Boolean(processando)}>{processando === "nova" ? "Enviando..." : "Solicitar peça"}</button></form> : null}
    </div>
  </section>;
}

