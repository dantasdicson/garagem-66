import { useCallback, useEffect, useMemo, useState } from "react";
import { Navigate } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const vazio = { username: "", first_name: "", last_name: "", email: "", tipo: "ATENDENTE", is_active: true, password: "" };
const nomesTipo = { ADMINISTRADOR: "Administrador", ATENDENTE: "Atendente", MECANICO: "Mecânico", CLIENTE: "Cliente" };

export default function UsuariosPage() {
  const { usuario } = useAuth();
  const [usuarios, setUsuarios] = useState([]);
  const [form, setForm] = useState(vazio);
  const [editando, setEditando] = useState(null);
  const [filtro, setFiltro] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  const carregar = useCallback(async () => {
    setCarregando(true); setErro("");
    try { setUsuarios(extrairLista(await apiRequest("/usuarios/"))); }
    catch (error) { setErro(error.message); }
    finally { setCarregando(false); }
  }, []);
  useEffect(() => { if (usuario.tipo === "ADMINISTRADOR") carregar(); }, [usuario.tipo, carregar]);

  const equipe = useMemo(() => usuarios.filter((item) => item.tipo !== "CLIENTE" && (!filtro || item.tipo === filtro)), [usuarios, filtro]);
  const totais = useMemo(() => Object.fromEntries(["ADMINISTRADOR", "ATENDENTE", "MECANICO"].map((tipo) => [tipo, usuarios.filter((u) => u.tipo === tipo && u.is_active).length])), [usuarios]);

  if (usuario.tipo !== "ADMINISTRADOR") return <Navigate to="/" replace />;

  function editar(item) {
    setEditando(item.id);
    setForm({ username: item.username, first_name: item.first_name, last_name: item.last_name, email: item.email, tipo: item.tipo, is_active: item.is_active, password: "" });
    setErro("");
  }
  function limpar() { setEditando(null); setForm(vazio); setErro(""); }
  async function salvar(event) {
    event.preventDefault(); setSalvando(true); setErro("");
    try {
      const payload = { ...form };
      if (!payload.password) delete payload.password;
      await apiRequest(editando ? `/usuarios/${editando}/` : "/usuarios/", { method: editando ? "PATCH" : "POST", body: JSON.stringify(payload) });
      limpar(); await carregar();
    } catch (error) { setErro(error.message); } finally { setSalvando(false); }
  }

  return <section className="page-section">
    <div className="page-heading"><div><p className="eyebrow">Administração</p><h1>Usuários e Equipe</h1><p className="lead">Gerencie administradores, atendentes e mecânicos da Garagem 66.</p></div><button className="button button-primary" onClick={limpar}>+ Novo usuário</button></div>
    <div className="summary-grid"><article className="summary-card tone-red"><span>♙</span><div><small>Administradores</small><strong>{totais.ADMINISTRADOR || 0}</strong></div></article><article className="summary-card tone-orange"><span>◎</span><div><small>Atendentes</small><strong>{totais.ATENDENTE || 0}</strong></div></article><article className="summary-card tone-green"><span>⚒</span><div><small>Mecânicos</small><strong>{totais.MECANICO || 0}</strong></div></article></div>
    {erro ? <p className="form-error">{erro}</p> : null}
    <div className="management-grid"><div className="table-card"><div className="table-toolbar"><select value={filtro} onChange={(e) => setFiltro(e.target.value)}><option value="">Toda a equipe</option><option value="ADMINISTRADOR">Administradores</option><option value="ATENDENTE">Atendentes</option><option value="MECANICO">Mecânicos</option></select></div>{carregando ? <p className="muted">Carregando equipe...</p> : <div className="table-scroll"><table><thead><tr><th>Nome</th><th>Usuário</th><th>Perfil</th><th>Situação</th><th>Ações</th></tr></thead><tbody>{equipe.map((item) => <tr key={item.id}><td><strong>{[item.first_name, item.last_name].filter(Boolean).join(" ") || item.username}</strong><small>{item.email}</small></td><td>{item.username}</td><td><span className={`role-badge role-${item.tipo.toLowerCase()}`}>{nomesTipo[item.tipo]}</span></td><td><span className={`status-badge ${item.is_active ? "request-aprovada" : "request-recusada"}`}>{item.is_active ? "Ativo" : "Inativo"}</span></td><td><button className="table-action" onClick={() => editar(item)}>Editar</button></td></tr>)}{!equipe.length ? <tr><td colSpan="5" className="empty-cell">Nenhum usuário encontrado.</td></tr> : null}</tbody></table></div>}</div>
      <form className="form-card" onSubmit={salvar}><div><p className="eyebrow">{editando ? "Edição" : "Cadastro"}</p><h2>{editando ? "Editar usuário" : "Novo usuário"}</h2></div><div className="field-row"><div><label htmlFor="user-nome">Nome</label><input id="user-nome" required value={form.first_name} onChange={(e) => setForm((v) => ({...v, first_name:e.target.value}))} /></div><div><label htmlFor="user-sobrenome">Sobrenome</label><input id="user-sobrenome" required value={form.last_name} onChange={(e) => setForm((v) => ({...v, last_name:e.target.value}))} /></div></div><label htmlFor="user-login">Usuário</label><input id="user-login" required value={form.username} onChange={(e) => setForm((v) => ({...v, username:e.target.value.toLowerCase().replaceAll(" ", ".")}))} /><label htmlFor="user-email">E-mail</label><input id="user-email" type="email" required value={form.email} onChange={(e) => setForm((v) => ({...v, email:e.target.value}))} /><label htmlFor="user-tipo">Perfil</label><select id="user-tipo" value={form.tipo} onChange={(e) => setForm((v) => ({...v, tipo:e.target.value}))}><option value="ATENDENTE">Atendente</option><option value="MECANICO">Mecânico</option><option value="ADMINISTRADOR">Administrador</option></select><label htmlFor="user-senha">{editando ? "Nova senha (opcional)" : "Senha inicial"}</label><input id="user-senha" type="password" required={!editando} minLength="8" value={form.password} onChange={(e) => setForm((v) => ({...v, password:e.target.value}))} /><label className="option-toggle"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm((v) => ({...v, is_active:e.target.checked}))} /> Usuário ativo</label><div className="form-actions"><button className="button button-primary" disabled={salvando}>{salvando ? "Salvando..." : "Salvar usuário"}</button>{editando ? <button className="button button-link" type="button" onClick={limpar}>Cancelar</button> : null}</div></form>
    </div>
  </section>;
}

