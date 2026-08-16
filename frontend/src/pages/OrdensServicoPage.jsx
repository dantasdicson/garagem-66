import { useCallback, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";

const formularioVazio = {
  motocicleta: "", mecanico: "", tipo_manutencao: "CORRETIVA", descricao_problema: "",
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
  const podeCadastrar = ["ADMINISTRADOR", "ATENDENTE"].includes(usuario.tipo);
  const [ordens, setOrdens] = useState([]);
  const [motocicletas, setMotocicletas] = useState([]);
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
      const requisicaoUsuarios = usuario.tipo === "ADMINISTRADOR"
        ? apiRequest("/usuarios/")
        : Promise.resolve([]);
      const [dadosOrdens, dadosMotos, dadosUsuarios] = await Promise.all([
        requisicaoOrdens, requisicaoMotos, requisicaoUsuarios,
      ]);
      setOrdens(extrairLista(dadosOrdens));
      setMotocicletas(extrairLista(dadosMotos));
      setMecanicos(extrairLista(dadosUsuarios).filter((item) => item.tipo === "MECANICO" && item.is_active));
    } catch (error) {
      setErro(error.message);
    } finally {
      setCarregando(false);
    }
  }, [usuario.tipo]);

  useEffect(() => { carregar(); }, [carregar]);

  async function salvar(event) {
    event.preventDefault();
    const moto = motosPorId.get(Number(form.motocicleta));
    if (!moto) return;
    setErro("");
    setSalvando(true);
    const dados = {
      motocicleta: moto.id,
      cliente: moto.cliente,
      mecanico: form.mecanico ? Number(form.mecanico) : null,
      tipo_manutencao: form.tipo_manutencao,
      descricao_problema: form.descricao_problema.trim(),
    };
    try {
      await apiRequest("/oficina/ordens-servico/", { method: "POST", body: JSON.stringify(dados) });
      setForm(formularioVazio);
      await carregar();
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
        <p className="lead">Acompanhe o atendimento da abertura até a conclusão.</p></div></div>
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
          <label htmlFor="os-moto">Motocicleta</label><select id="os-moto" required value={form.motocicleta} onChange={(e) => setForm((valor) => ({ ...valor, motocicleta: e.target.value }))}><option value="">Selecione</option>{motocicletas.map((moto) => <option key={moto.id} value={moto.id}>{moto.placa} — {moto.marca} {moto.modelo}</option>)}</select>
          {usuario.tipo === "ADMINISTRADOR" ? <><label htmlFor="os-mecanico">Mecânico</label><select id="os-mecanico" value={form.mecanico} onChange={(e) => setForm((valor) => ({ ...valor, mecanico: e.target.value }))}><option value="">Atribuir depois</option>{mecanicos.map((mecanico) => <option key={mecanico.id} value={mecanico.id}>{mecanico.first_name} {mecanico.last_name}</option>)}</select></> : null}
          <label htmlFor="os-tipo">Tipo de manutenção</label><select id="os-tipo" value={form.tipo_manutencao} onChange={(e) => setForm((valor) => ({ ...valor, tipo_manutencao: e.target.value }))}><option value="CORRETIVA">Corretiva</option><option value="PREVENTIVA">Preventiva</option></select>
          <label htmlFor="os-descricao">Problema relatado</label><textarea id="os-descricao" required rows="5" value={form.descricao_problema} onChange={(e) => setForm((valor) => ({ ...valor, descricao_problema: e.target.value }))} />
          <button className="button button-primary" disabled={salvando} type="submit">{salvando ? "Abrindo..." : "Abrir ordem de serviço"}</button>
        </form> : null}
      </div>
    </section>
  );
}
