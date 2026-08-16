import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const formularioVazio = {
  cliente: "", motocicleta: "", nova_motocicleta: false, modelo_catalogo: "", marca: "", modelo: "",
  ano: "", placa: "", chassi: "", cor: "", mecanico: "", tipo_manutencao: "CORRETIVA", descricao_problema: "",
};

const nomesStatus = {
  ABERTA: "Aberta",
  AGUARDANDO_ORCAMENTO: "Aguardando orçamento",
  AGUARDANDO_APROVACAO: "Aguardando aprovação",
  EM_EXECUCAO: "Em execução",
  AGUARDANDO_PECAS: "Aguardando peças",
  CONCLUIDA: "Concluída",
  CONCLUIDA_NAO_APROVADA: "Concluída — não aprovada",
};

function acoesDisponiveis(ordem, tipoUsuario) {
  const equipe = ["ADMINISTRADOR", "ATENDENTE", "MECANICO"].includes(tipoUsuario);
  const acoes = [];
  if (equipe && ordem.status === "EM_EXECUCAO") {
    acoes.push(["aguardar_pecas", "Aguardar peças"], ["concluir", "Concluir"]);
  }
  if (equipe && ordem.status === "AGUARDANDO_PECAS") acoes.push(["retomar_execucao", "Retomar"]);
  if (tipoUsuario === "ADMINISTRADOR" && ordem.status === "CONCLUIDA") acoes.push(["reabrir", "Reabrir"]);
  return acoes;
}

export default function OrdensServicoPage() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [parametros] = useSearchParams();
  const podeIniciar = ["ADMINISTRADOR", "ATENDENTE"].includes(usuario.tipo);
  const podeCadastrar = false;
  const [ordens, setOrdens] = useState([]);
  const [motocicletas, setMotocicletas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [catalogo, setCatalogo] = useState([]);
  const [mecanicos, setMecanicos] = useState([]);
  const [form, setForm] = useState(formularioVazio);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [acaoEmAndamento, setAcaoEmAndamento] = useState("");
  const [erro, setErro] = useState("");

  const motosPorId = useMemo(
    () => new Map(motocicletas.map((moto) => [moto.id, moto])),
    [motocicletas],
  );
  const mecanicosPorId = useMemo(
    () => new Map(mecanicos.map((mecanico) => [mecanico.id, mecanico])),
    [mecanicos],
  );

  const carregar = useCallback(async () => {
    setErro("");
    setCarregando(true);
    try {
      const requisicaoOrdens = apiRequest("/oficina/ordens-servico/");
      const requisicaoMotos = apiRequest("/oficina/motocicletas/");
      const requisicaoClientes = podeCadastrar ? apiRequest("/oficina/clientes/") : Promise.resolve([]);
      const requisicaoCatalogo = podeCadastrar ? apiRequest("/oficina/modelos-motocicleta/") : Promise.resolve([]);
      const requisicaoUsuarios = usuario.tipo === "ADMINISTRADOR"
        ? apiRequest("/usuarios/")
        : Promise.resolve([]);
      const [dadosOrdens, dadosMotos, dadosClientes, dadosCatalogo, dadosUsuarios] = await Promise.all([
        requisicaoOrdens, requisicaoMotos, requisicaoClientes, requisicaoCatalogo, requisicaoUsuarios,
      ]);
      setOrdens(extrairLista(dadosOrdens));
      setMotocicletas(extrairLista(dadosMotos));
      setClientes(extrairLista(dadosClientes));
      setCatalogo(extrairLista(dadosCatalogo));
      setMecanicos(extrairLista(dadosUsuarios).filter((item) => item.tipo === "MECANICO" && item.is_active));
    } catch (error) {
      setErro(error.message);
    } finally {
      setCarregando(false);
    }
  }, [podeCadastrar, usuario.tipo]);

  useEffect(() => { carregar(); }, [carregar]);

  useEffect(() => {
    const cliente = parametros.get("cliente");
    if (cliente) setForm((atual) => ({ ...atual, cliente, nova_motocicleta: parametros.get("nova_moto") === "1" }));
  }, [parametros]);

  async function salvar(event) {
    event.preventDefault();
    setErro("");
    setSalvando(true);
    const dadosOrdem = {
      mecanico: form.mecanico ? Number(form.mecanico) : null,
      tipo_manutencao: form.tipo_manutencao,
      descricao_problema: form.descricao_problema.trim(),
    };
    try {
      if (form.nova_motocicleta) {
        await apiRequest("/oficina/ordens-servico/abrir-atendimento/", { method: "POST", body: JSON.stringify({
          ...dadosOrdem, cliente: Number(form.cliente), marca: form.marca.trim(), modelo: form.modelo.trim(),
          ano: Number(form.ano), placa: form.placa.trim().toUpperCase(), chassi: form.chassi.trim().toUpperCase() || null,
          cor: form.cor.trim(),
        }) });
      } else {
        const moto = motosPorId.get(Number(form.motocicleta));
        if (!moto) throw new Error("Selecione uma motocicleta.");
        await apiRequest("/oficina/ordens-servico/", { method: "POST", body: JSON.stringify({
          ...dadosOrdem, motocicleta: moto.id, cliente: moto.cliente,
        }) });
      }
      setForm(formularioVazio);
      await carregar();
      navigate("/entradas");
    } catch (error) {
      setErro(error.message);
    } finally {
      setSalvando(false);
    }
  }

  async function executarAcao(ordem, acao) {
    const observacao = acao === "reabrir" ? window.prompt("Informe o motivo da reabertura:") : "";
    if (acao === "reabrir" && !observacao?.trim()) return;
    const chave = `${ordem.id}-${acao}`;
    setErro("");
    setAcaoEmAndamento(chave);
    try {
      await apiRequest(`/oficina/ordens-servico/${ordem.id}/${acao}/`, {
        method: "POST", body: JSON.stringify({ observacao: observacao || "" }),
      });
      await carregar();
    } catch (error) {
      setErro(error.message);
    } finally {
      setAcaoEmAndamento("");
    }
  }

  return (
    <section className="page-section">
      <div className="page-heading"><div><p className="eyebrow">Oficina</p><h1>{usuario.tipo === "CLIENTE" ? "Minhas ordens" : "Ordens de serviço"}</h1>
        <p className="lead">Acompanhe o atendimento da abertura até a conclusão.</p></div>{podeIniciar ? <button className="button button-primary" type="button" onClick={() => navigate("/novo-atendimento")}>Novo atendimento</button> : null}</div>
      {erro ? <p className="form-error" role="alert">{erro}</p> : null}
      <div className={podeCadastrar ? "management-grid" : "management-grid single-column"}>
        <div className="table-card">{carregando ? <p className="muted" role="status">Carregando ordens...</p> : (
          <div className="table-scroll"><table><thead><tr><th>Ordem</th><th>Motocicleta</th><th>Status</th><th>Responsável</th><th><span className="sr-only">Ações</span></th></tr></thead>
            <tbody>{ordens.length ? ordens.map((ordem) => {
              const moto = motosPorId.get(ordem.motocicleta);
              const mecanico = mecanicosPorId.get(ordem.mecanico);
              return <tr key={ordem.id}><td><strong>{ordem.numero}</strong><small>{ordem.tipo_manutencao === "PREVENTIVA" ? "Preventiva" : "Corretiva"}</small></td>
                <td>{moto ? `${moto.marca} ${moto.modelo}` : `Motocicleta #${ordem.motocicleta}`}<small>{moto?.placa}</small></td>
                <td><span className={`status-badge status-${ordem.status.toLowerCase()}`}>{nomesStatus[ordem.status] || ordem.status}</span></td>
                <td>{mecanico ? `${mecanico.first_name} ${mecanico.last_name}` : ordem.mecanico ? `Usuário #${ordem.mecanico}` : "Não atribuído"}</td>
                <td><div className="table-actions">{acoesDisponiveis(ordem, usuario.tipo).map(([acao, rotulo]) => <button key={acao} className="table-action" type="button" disabled={Boolean(acaoEmAndamento)} onClick={() => executarAcao(ordem, acao)}>{acaoEmAndamento === `${ordem.id}-${acao}` ? "Aguarde..." : rotulo}</button>)}</div></td></tr>;
            }) : <tr><td colSpan="5" className="empty-cell">Nenhuma ordem de serviço encontrada.</td></tr>}</tbody></table></div>
        )}</div>
        {podeCadastrar ? <form className="form-card" onSubmit={salvar}><div><p className="eyebrow">Novo atendimento</p><h2>Abrir ordem</h2></div>
          <p className="generated-field"><span>Número da OS</span><strong>Gerado automaticamente ao salvar</strong></p>
          <label htmlFor="os-cliente">Cliente</label><select id="os-cliente" required value={form.cliente} onChange={(e) => setForm((valor) => ({ ...valor, cliente: e.target.value, motocicleta: "" }))}><option value="">Selecione</option>{clientes.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome} — {cliente.cpf}</option>)}</select>
          <label className="option-toggle"><input type="checkbox" checked={form.nova_motocicleta} onChange={(e) => setForm((valor) => ({ ...valor, nova_motocicleta: e.target.checked, motocicleta: "" }))} /> Cadastrar nova motocicleta neste atendimento</label>
          {form.nova_motocicleta ? <div className="inline-vehicle-form"><label htmlFor="os-catalogo">Modelo do catálogo</label><select id="os-catalogo" value={form.modelo_catalogo} onChange={(e) => { const id = e.target.value; const item = catalogo.find((modelo) => modelo.id === Number(id)); setForm((valor) => ({ ...valor, modelo_catalogo: id, marca: item?.marca || valor.marca, modelo: item?.modelo || valor.modelo })); }}><option value="">Selecione ou preencha manualmente</option>{catalogo.map((item) => <option key={item.id} value={item.id}>{item.marca} — {item.modelo}</option>)}</select><div className="field-row"><div><label htmlFor="os-marca">Marca</label><input id="os-marca" required value={form.marca} onChange={(e) => setForm((valor) => ({ ...valor, marca: e.target.value }))} /></div><div><label htmlFor="os-modelo">Modelo</label><input id="os-modelo" required value={form.modelo} onChange={(e) => setForm((valor) => ({ ...valor, modelo: e.target.value }))} /></div></div><div className="field-row"><div><label htmlFor="os-placa">Placa</label><input id="os-placa" required maxLength="10" value={form.placa} onChange={(e) => setForm((valor) => ({ ...valor, placa: e.target.value.toUpperCase() }))} /></div><div><label htmlFor="os-chassi">Chassi</label><input id="os-chassi" maxLength="30" value={form.chassi} onChange={(e) => setForm((valor) => ({ ...valor, chassi: e.target.value.toUpperCase() }))} /></div></div><div className="field-row"><div><label htmlFor="os-ano">Ano</label><input id="os-ano" required type="number" min="1900" max="2100" value={form.ano} onChange={(e) => setForm((valor) => ({ ...valor, ano: e.target.value }))} /></div><div><label htmlFor="os-cor">Cor</label><input id="os-cor" value={form.cor} onChange={(e) => setForm((valor) => ({ ...valor, cor: e.target.value }))} /></div></div></div> : <><label htmlFor="os-moto">Motocicleta cadastrada</label><select id="os-moto" required value={form.motocicleta} onChange={(e) => setForm((valor) => ({ ...valor, motocicleta: e.target.value }))}><option value="">Selecione</option>{motocicletas.filter((moto) => !form.cliente || moto.cliente === Number(form.cliente)).map((moto) => <option key={moto.id} value={moto.id}>{moto.placa} — {moto.marca} {moto.modelo}</option>)}</select></>}
          {usuario.tipo === "ADMINISTRADOR" ? <><label htmlFor="os-mecanico">Mecânico</label><select id="os-mecanico" value={form.mecanico} onChange={(e) => setForm((valor) => ({ ...valor, mecanico: e.target.value }))}><option value="">Atribuir depois</option>{mecanicos.map((mecanico) => <option key={mecanico.id} value={mecanico.id}>{mecanico.first_name} {mecanico.last_name}</option>)}</select></> : null}
          <label htmlFor="os-tipo">Tipo de manutenção</label><select id="os-tipo" value={form.tipo_manutencao} onChange={(e) => setForm((valor) => ({ ...valor, tipo_manutencao: e.target.value }))}><option value="CORRETIVA">Corretiva</option><option value="PREVENTIVA">Preventiva</option></select>
          <label htmlFor="os-descricao">Problema relatado</label><textarea id="os-descricao" required rows="5" value={form.descricao_problema} onChange={(e) => setForm((valor) => ({ ...valor, descricao_problema: e.target.value }))} />
          <button className="button button-primary" disabled={salvando} type="submit">{salvando ? "Abrindo..." : "Abrir ordem de serviço"}</button>
        </form> : null}
      </div>
    </section>
  );
}
