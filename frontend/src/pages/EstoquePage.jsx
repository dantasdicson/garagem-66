import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const vazio = { codigo: "", nome: "", descricao: "", quantidade_estoque: "", quantidade_minima: "", valor_unitario: "" };
const rotulos = { DISPONIVEL: "Disponível", ESTOQUE_BAIXO: "Estoque baixo", INDISPONIVEL: "Indisponível" };

export default function EstoquePage() {
  const { usuario } = useAuth();
  const autorizado = ["ADMINISTRADOR", "ATENDENTE", "MECANICO"].includes(usuario.tipo);
  const podeEditar = ["ADMINISTRADOR", "ATENDENTE"].includes(usuario.tipo);
  const [pecas, setPecas] = useState([]);
  const [form, setForm] = useState(vazio);
  const [editando, setEditando] = useState(null);
  const [busca, setBusca] = useState("");
  const [status, setStatus] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  const carregar = useCallback(async () => {
    setCarregando(true); setErro("");
    try { setPecas(extrairLista(await apiRequest("/estoque/pecas/"))); }
    catch (error) { setErro(error.message); }
    finally { setCarregando(false); }
  }, []);

  useEffect(() => { if (autorizado) carregar(); }, [autorizado, carregar]);

  const filtradas = useMemo(() => pecas.filter((peca) => {
    const termo = busca.trim().toLowerCase();
    return (!termo || `${peca.nome} ${peca.codigo}`.toLowerCase().includes(termo)) && (!status || peca.status_estoque === status);
  }), [pecas, busca, status]);

  const totais = useMemo(() => ({
    cadastradas: pecas.length,
    baixas: pecas.filter((item) => item.status_estoque === "ESTOQUE_BAIXO").length,
    indisponiveis: pecas.filter((item) => item.status_estoque === "INDISPONIVEL").length,
  }), [pecas]);

  if (!autorizado) return <Navigate to="/" replace />;

  function editar(peca) {
    setEditando(peca.id);
    setForm({ codigo: peca.codigo, nome: peca.nome, descricao: peca.descricao || "", quantidade_estoque: peca.quantidade_estoque, quantidade_minima: peca.quantidade_minima, valor_unitario: peca.valor_unitario });
  }
  function limpar() { setEditando(null); setForm(vazio); setErro(""); }
  async function salvar(event) {
    event.preventDefault(); setSalvando(true); setErro("");
    try {
      const payload = { ...form, quantidade_estoque: Number(form.quantidade_estoque), quantidade_minima: Number(form.quantidade_minima), valor_unitario: Number(form.valor_unitario) };
      await apiRequest(editando ? `/estoque/pecas/${editando}/` : "/estoque/pecas/", { method: editando ? "PATCH" : "POST", body: JSON.stringify(payload) });
      limpar(); await carregar();
    } catch (error) { setErro(error.message); } finally { setSalvando(false); }
  }

  return <section className="page-section">
    <div className="page-heading"><div><p className="eyebrow">Peças</p><h1>Controle de Estoque</h1><p className="lead">Consulte e controle as peças disponíveis na oficina.</p></div>{podeEditar ? <button className="button button-primary" onClick={limpar}>+ Nova peça</button> : null}</div>
    <div className="summary-grid"><article className="summary-card tone-green"><span>◇</span><div><small>Peças cadastradas</small><strong>{totais.cadastradas}</strong></div></article><article className="summary-card tone-orange"><span>△</span><div><small>Estoque baixo</small><strong>{totais.baixas}</strong></div></article><article className="summary-card tone-red"><span>⊘</span><div><small>Indisponíveis</small><strong>{totais.indisponiveis}</strong></div></article></div>
    {erro ? <p className="form-error" role="alert">{erro}</p> : null}
    <div className={podeEditar ? "management-grid" : "management-grid single-column"}>
      <div className="table-card"><div className="table-toolbar"><input aria-label="Buscar peça" placeholder="Buscar peça ou código" value={busca} onChange={(e) => setBusca(e.target.value)} /><select aria-label="Filtrar por status" value={status} onChange={(e) => setStatus(e.target.value)}><option value="">Todos os status</option>{Object.entries(rotulos).map(([valor, nome]) => <option key={valor} value={valor}>{nome}</option>)}</select></div>
        {carregando ? <p className="muted">Carregando estoque...</p> : <div className="table-scroll"><table><thead><tr><th>Peça</th><th>Código</th><th>Disponível</th><th>Mínima</th><th>Valor unitário</th><th>Status</th>{podeEditar ? <th>Ações</th> : null}</tr></thead><tbody>{filtradas.map((peca) => <tr key={peca.id}><td><strong>{peca.nome}</strong><small>{peca.descricao}</small></td><td>{peca.codigo}</td><td>{peca.quantidade_estoque}</td><td>{peca.quantidade_minima}</td><td>{Number(peca.valor_unitario).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}</td><td><span className={`status-badge stock-${peca.status_estoque.toLowerCase()}`}>{rotulos[peca.status_estoque]}</span></td>{podeEditar ? <td><button className="table-action" onClick={() => editar(peca)}>Editar</button></td> : null}</tr>)}{!filtradas.length ? <tr><td className="empty-cell" colSpan={podeEditar ? 7 : 6}>Nenhuma peça encontrada.</td></tr> : null}</tbody></table></div>}
      </div>
      {podeEditar ? <form className="form-card" onSubmit={salvar}><div><p className="eyebrow">{editando ? "Edição" : "Cadastro"}</p><h2>{editando ? "Editar peça" : "Nova peça"}</h2></div><label htmlFor="peca-codigo">Código</label><input id="peca-codigo" required value={form.codigo} onChange={(e) => setForm((v) => ({...v, codigo:e.target.value.toUpperCase()}))} /><label htmlFor="peca-nome">Nome</label><input id="peca-nome" required value={form.nome} onChange={(e) => setForm((v) => ({...v, nome:e.target.value}))} /><label htmlFor="peca-descricao">Descrição</label><textarea id="peca-descricao" rows="3" value={form.descricao} onChange={(e) => setForm((v) => ({...v, descricao:e.target.value}))} /><div className="field-row"><div><label htmlFor="peca-quantidade">Quantidade</label><input id="peca-quantidade" type="number" min="0" required value={form.quantidade_estoque} onChange={(e) => setForm((v) => ({...v, quantidade_estoque:e.target.value}))} /></div><div><label htmlFor="peca-minima">Estoque mínimo</label><input id="peca-minima" type="number" min="0" required value={form.quantidade_minima} onChange={(e) => setForm((v) => ({...v, quantidade_minima:e.target.value}))} /></div></div><label htmlFor="peca-valor">Valor unitário</label><input id="peca-valor" type="number" min="0" step="0.01" required value={form.valor_unitario} onChange={(e) => setForm((v) => ({...v, valor_unitario:e.target.value}))} /><div className="form-actions"><button className="button button-primary" disabled={salvando}>{salvando ? "Salvando..." : "Salvar peça"}</button>{editando ? <button className="button button-link" type="button" onClick={limpar}>Cancelar</button> : null}</div></form> : null}
    </div>
  </section>;
}

