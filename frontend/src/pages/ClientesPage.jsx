import { useCallback, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const formularioVazio = {
  nome: "", cpf: "", data_nascimento: "", email: "", telefone: "", endereco: "",
};

export default function ClientesPage() {
  const { usuario } = useAuth();
  const [clientes, setClientes] = useState([]);
  const [form, setForm] = useState(formularioVazio);
  const [editandoId, setEditandoId] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const autorizado = ["ADMINISTRADOR", "ATENDENTE"].includes(usuario.tipo);

  const carregar = useCallback(async () => {
    setErro("");
    setCarregando(true);
    try {
      setClientes(extrairLista(await apiRequest("/oficina/clientes/")));
    } catch (error) {
      setErro(error.message);
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => { if (autorizado) carregar(); }, [autorizado, carregar]);
  if (!autorizado) return <Navigate to="/" replace />;

  function editar(cliente) {
    setEditandoId(cliente.id);
    setForm({
      nome: cliente.nome, cpf: cliente.cpf ?? "", data_nascimento: cliente.data_nascimento ?? "",
      email: cliente.email, telefone: cliente.telefone ?? "", endereco: cliente.endereco ?? "",
    });
    setErro("");
  }

  function cancelar() {
    setEditandoId(null);
    setForm(formularioVazio);
    setErro("");
  }

  async function salvar(event) {
    event.preventDefault();
    setErro("");
    setSalvando(true);
    try {
      const caminho = editandoId ? `/oficina/clientes/${editandoId}/` : "/oficina/clientes/";
      await apiRequest(caminho, { method: editandoId ? "PATCH" : "POST", body: JSON.stringify(form) });
      cancelar();
      await carregar();
    } catch (error) {
      setErro(error.message);
    } finally {
      setSalvando(false);
    }
  }

  return (
    <section className="page-section">
      <div className="page-heading"><div><p className="eyebrow">Atendimento</p><h1>Clientes</h1>
        <p className="lead">Cadastre proprietários e mantenha os dados de contato atualizados.</p></div>
        <button className="button button-secondary" type="button" onClick={cancelar}>Novo cliente</button>
      </div>
      {erro ? <p className="form-error" role="alert">{erro}</p> : null}
      <div className="management-grid">
        <div className="table-card">
          {carregando ? <p className="muted" role="status">Carregando clientes...</p> : (
            <div className="table-scroll"><table><thead><tr><th>Nome</th><th>CPF</th><th>Contato</th><th><span className="sr-only">Ações</span></th></tr></thead>
              <tbody>{clientes.length ? clientes.map((cliente) => (
                <tr key={cliente.id}><td><strong>{cliente.nome}</strong><small>{cliente.email}</small></td>
                  <td>{cliente.cpf}</td><td>{cliente.telefone || "Não informado"}</td>
                  <td><button className="table-action" type="button" onClick={() => editar(cliente)}>Editar</button></td></tr>
              )) : <tr><td colSpan="4" className="empty-cell">Nenhum cliente cadastrado.</td></tr>}</tbody></table></div>
          )}
        </div>
        <form className="form-card" onSubmit={salvar}>
          <div><p className="eyebrow">{editandoId ? "Edição" : "Novo cadastro"}</p><h2>{editandoId ? "Editar cliente" : "Cadastrar cliente"}</h2></div>
          <label htmlFor="cliente-nome">Nome completo</label><input id="cliente-nome" required value={form.nome} onChange={(e) => setForm((v) => ({ ...v, nome: e.target.value }))} />
          <div className="field-row"><div><label htmlFor="cliente-cpf">CPF</label><input id="cliente-cpf" required disabled={Boolean(editandoId)} value={form.cpf} onChange={(e) => setForm((v) => ({ ...v, cpf: e.target.value }))} /></div>
            <div><label htmlFor="cliente-nascimento">Nascimento</label><input id="cliente-nascimento" type="date" required disabled={Boolean(editandoId)} value={form.data_nascimento} onChange={(e) => setForm((v) => ({ ...v, data_nascimento: e.target.value }))} /></div></div>
          <label htmlFor="cliente-email">E-mail</label><input id="cliente-email" type="email" required value={form.email} onChange={(e) => setForm((v) => ({ ...v, email: e.target.value }))} />
          <label htmlFor="cliente-telefone">Telefone</label><input id="cliente-telefone" placeholder="(11) 99999-9999" value={form.telefone} onChange={(e) => setForm((v) => ({ ...v, telefone: e.target.value }))} />
          <label htmlFor="cliente-endereco">Endereço</label><textarea id="cliente-endereco" rows="3" value={form.endereco} onChange={(e) => setForm((v) => ({ ...v, endereco: e.target.value }))} />
          <div className="form-actions"><button className="button button-primary" disabled={salvando} type="submit">{salvando ? "Salvando..." : "Salvar cliente"}</button>
            {editandoId ? <button className="button button-link" type="button" onClick={cancelar}>Cancelar</button> : null}</div>
        </form>
      </div>
    </section>
  );
}

