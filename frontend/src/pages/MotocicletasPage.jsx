import { useCallback, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const formularioVazio = { cliente: "", marca: "", modelo: "", ano: "", placa: "", chassi: "", cor: "" };

export default function MotocicletasPage() {
  const { usuario } = useAuth();
  const somenteLeitura = usuario.tipo === "CLIENTE";
  const podeGerenciar = ["ADMINISTRADOR", "ATENDENTE"].includes(usuario.tipo);
  const [motocicletas, setMotocicletas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [form, setForm] = useState(formularioVazio);
  const [editandoId, setEditandoId] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const clientesPorId = useMemo(() => new Map(clientes.map((cliente) => [cliente.id, cliente.nome])), [clientes]);

  const carregar = useCallback(async () => {
    setErro(""); setCarregando(true);
    try {
      const requisicaoMotos = apiRequest("/oficina/motocicletas/");
      const requisicaoClientes = podeGerenciar ? apiRequest("/oficina/clientes/") : Promise.resolve([]);
      const [dadosMotos, dadosClientes] = await Promise.all([requisicaoMotos, requisicaoClientes]);
      setMotocicletas(extrairLista(dadosMotos));
      setClientes(extrairLista(dadosClientes));
    } catch (error) { setErro(error.message); } finally { setCarregando(false); }
  }, [podeGerenciar]);

  useEffect(() => { carregar(); }, [carregar]);

  function editar(moto) {
    setEditandoId(moto.id);
    setForm({ cliente: String(moto.cliente), marca: moto.marca, modelo: moto.modelo, ano: String(moto.ano), placa: moto.placa, chassi: moto.chassi ?? "", cor: moto.cor ?? "" });
  }
  function cancelar() { setEditandoId(null); setForm(formularioVazio); setErro(""); }
  async function salvar(event) {
    event.preventDefault(); setErro(""); setSalvando(true);
    const dados = { ...form, cliente: Number(form.cliente), ano: Number(form.ano), chassi: form.chassi.trim() || null };
    try {
      await apiRequest(editandoId ? `/oficina/motocicletas/${editandoId}/` : "/oficina/motocicletas/", {
        method: editandoId ? "PATCH" : "POST", body: JSON.stringify(dados),
      });
      cancelar(); await carregar();
    } catch (error) { setErro(error.message); } finally { setSalvando(false); }
  }

  return (
    <section className="page-section">
      <div className="page-heading"><div><p className="eyebrow">Veículos</p><h1>{somenteLeitura ? "Minhas motocicletas" : "Motocicletas"}</h1>
        <p className="lead">{somenteLeitura ? "Consulte as motocicletas vinculadas ao seu cadastro." : "Vincule cada motocicleta ao seu proprietário."}</p></div>
        {podeGerenciar ? <button className="button button-secondary" type="button" onClick={cancelar}>Nova motocicleta</button> : null}
      </div>
      {erro ? <p className="form-error" role="alert">{erro}</p> : null}
      <div className={podeGerenciar ? "management-grid" : "management-grid single-column"}>
        <div className="table-card">{carregando ? <p className="muted" role="status">Carregando motocicletas...</p> : (
          <div className="table-scroll"><table><thead><tr><th>Motocicleta</th><th>Placa</th>{podeGerenciar ? <th>Proprietário</th> : null}<th>Ano / Cor</th>{podeGerenciar ? <th><span className="sr-only">Ações</span></th> : null}</tr></thead>
            <tbody>{motocicletas.length ? motocicletas.map((moto) => <tr key={moto.id}><td><strong>{moto.marca} {moto.modelo}</strong><small>{moto.chassi || "Chassi não informado"}</small></td><td>{moto.placa}</td>
              {podeGerenciar ? <td>{clientesPorId.get(moto.cliente) || `Cliente #${moto.cliente}`}</td> : null}<td>{moto.ano}{moto.cor ? ` · ${moto.cor}` : ""}</td>
              {podeGerenciar ? <td><button className="table-action" type="button" onClick={() => editar(moto)}>Editar</button></td> : null}</tr>) : <tr><td colSpan={podeGerenciar ? 5 : 3} className="empty-cell">Nenhuma motocicleta cadastrada.</td></tr>}</tbody></table></div>
        )}</div>
        {podeGerenciar ? <form className="form-card" onSubmit={salvar}><div><p className="eyebrow">{editandoId ? "Edição" : "Novo cadastro"}</p><h2>{editandoId ? "Editar motocicleta" : "Cadastrar motocicleta"}</h2></div>
          <label htmlFor="moto-cliente">Proprietário</label><select id="moto-cliente" required value={form.cliente} onChange={(e) => setForm((v) => ({ ...v, cliente: e.target.value }))}><option value="">Selecione um cliente</option>{clientes.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}</select>
          <div className="field-row"><div><label htmlFor="moto-marca">Marca</label><input id="moto-marca" required value={form.marca} onChange={(e) => setForm((v) => ({ ...v, marca: e.target.value }))} /></div><div><label htmlFor="moto-modelo">Modelo</label><input id="moto-modelo" required value={form.modelo} onChange={(e) => setForm((v) => ({ ...v, modelo: e.target.value }))} /></div></div>
          <div className="field-row"><div><label htmlFor="moto-ano">Ano</label><input id="moto-ano" type="number" min="1900" max="2100" required value={form.ano} onChange={(e) => setForm((v) => ({ ...v, ano: e.target.value }))} /></div><div><label htmlFor="moto-placa">Placa</label><input id="moto-placa" required maxLength="10" value={form.placa} onChange={(e) => setForm((v) => ({ ...v, placa: e.target.value.toUpperCase() }))} /></div></div>
          <label htmlFor="moto-chassi">Chassi</label><input id="moto-chassi" value={form.chassi} onChange={(e) => setForm((v) => ({ ...v, chassi: e.target.value.toUpperCase() }))} />
          <label htmlFor="moto-cor">Cor</label><input id="moto-cor" value={form.cor} onChange={(e) => setForm((v) => ({ ...v, cor: e.target.value }))} />
          <div className="form-actions"><button className="button button-primary" disabled={salvando} type="submit">{salvando ? "Salvando..." : "Salvar motocicleta"}</button>{editandoId ? <button className="button button-link" type="button" onClick={cancelar}>Cancelar</button> : null}</div>
        </form> : null}
      </div>
    </section>
  );
}
