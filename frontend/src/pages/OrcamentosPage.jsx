import {useCallback, useEffect, useMemo, useState} from "react";

import {apiRequest} from "../api/client";
import {useAuth} from "../contexts/AuthContext";
import {extrairLista} from "../utils/apiData";

const orcamentoVazio = {ordem_servico: "", valor_mao_obra: "", valor_pecas: "", validade: "", observacoes: ""};
const servicoVazio = {descricao: "", quantidade: "1", valor_unitario: ""};
const pecaVazia = {peca: "", quantidade: "1", valor_unitario: ""};

const nomesStatus = {
    RASCUNHO: "Aguardando publicação",
    AGUARDANDO_APROVACAO: "Aguardando aprovação",
    APROVADO: "Aprovado",
    RECUSADO: "Recusado",
};

const formatadorMoeda = new Intl.NumberFormat("pt-BR", {style: "currency", currency: "BRL"});

function moeda(valor) {
    return formatadorMoeda.format(Number(valor || 0));
}

function dataBrasileira(valor) {
    if (!valor) return "Não informada";
    return new Intl.DateTimeFormat("pt-BR", {timeZone: "UTC"}).format(new Date(`${valor}T00:00:00Z`));
}

export default function OrcamentosPage() {
    const {usuario} = useAuth();
    const podeEditar = ["ADMINISTRADOR", "ATENDENTE", "MECANICO"].includes(usuario.tipo);
    const ehAdministrador = usuario.tipo === "ADMINISTRADOR";
    const ehCliente = usuario.tipo === "CLIENTE";
    const [orcamentos, setOrcamentos] = useState([]);
    const [ordens, setOrdens] = useState([]);
    const [pecas, setPecas] = useState([]);
    const [selecionadoId, setSelecionadoId] = useState(null);
    const [formOrcamento, setFormOrcamento] = useState(orcamentoVazio);
    const [formServico, setFormServico] = useState(servicoVazio);
    const [formPeca, setFormPeca] = useState(pecaVazia);
    const [carregando, setCarregando] = useState(true);
    const [processando, setProcessando] = useState("");
    const [erro, setErro] = useState("");

    const ordensPorId = useMemo(() => new Map(ordens.map((ordem) => [ordem.id, ordem])), [ordens]);
    const pecasPorId = useMemo(() => new Map(pecas.map((peca) => [peca.id, peca])), [pecas]);
    const idsComOrcamento = useMemo(() => new Set(orcamentos.map((item) => item.ordem_servico)), [orcamentos]);
    const ordensElegiveis = useMemo(
        () => ordens.filter((ordem) => ["ABERTA", "AGUARDANDO_ORCAMENTO"].includes(ordem.status) && !idsComOrcamento.has(ordem.id)),
        [idsComOrcamento, ordens],
    );
    const selecionado = orcamentos.find((item) => item.id === selecionadoId) || null;
    const totalNovoOrcamento = Number(formOrcamento.valor_mao_obra || 0) + Number(formOrcamento.valor_pecas || 0);

    const carregar = useCallback(async (manterSelecionado = true) => {
        setErro("");
        setCarregando(true);
        try {
            const requisicaoOrcamentos = apiRequest("/oficina/orcamentos/");
            const requisicaoOrdens = apiRequest("/oficina/ordens-servico/");
            const requisicaoPecas = podeEditar ? apiRequest("/estoque/pecas/") : Promise.resolve([]);
            const [dadosOrcamentos, dadosOrdens, dadosPecas] = await Promise.all([
                requisicaoOrcamentos, requisicaoOrdens, requisicaoPecas,
            ]);
            const listaOrcamentos = extrairLista(dadosOrcamentos);
            setOrcamentos(listaOrcamentos);
            setOrdens(extrairLista(dadosOrdens));
            setPecas(extrairLista(dadosPecas));
            setSelecionadoId((atual) => manterSelecionado && listaOrcamentos.some((item) => item.id === atual)
                ? atual
                : listaOrcamentos[0]?.id ?? null);
        } catch (error) {
            setErro(error.message);
        } finally {
            setCarregando(false);
        }
    }, [podeEditar]);

    useEffect(() => {
        carregar(false);
    }, [carregar]);

    async function emitir(event) {
        event.preventDefault();
        setErro("");
        setProcessando("emitir");
        try {
            const criado = await apiRequest("/oficina/orcamentos/", {
                method: "POST",
                body: JSON.stringify({
                    ordem_servico: Number(formOrcamento.ordem_servico),
                    valor_mao_obra: formOrcamento.valor_mao_obra,
                    valor_pecas: formOrcamento.valor_pecas,
                    validade: formOrcamento.validade || null,
                    observacoes: formOrcamento.observacoes.trim(),
                }),
            });
            setFormOrcamento(orcamentoVazio);
            await carregar();
            setSelecionadoId(criado.id);
        } catch (error) {
            setErro(error.message);
        } finally {
            setProcessando("");
        }
    }

    async function adicionarServico(event) {
        event.preventDefault();
        if (!selecionado) return;
        setErro("");
        setProcessando("servico");
        try {
            await apiRequest("/oficina/orcamento-servicos/", {
                method: "POST",
                body: JSON.stringify({
                    orcamento: selecionado.id,
                    descricao: formServico.descricao.trim(),
                    quantidade: Number(formServico.quantidade),
                    valor_unitario: formServico.valor_unitario,
                }),
            });
            setFormServico(servicoVazio);
            await carregar();
        } catch (error) {
            setErro(error.message);
        } finally {
            setProcessando("");
        }
    }

    async function adicionarPeca(event) {
        event.preventDefault();
        if (!selecionado) return;
        setErro("");
        setProcessando("peca");
        try {
            await apiRequest("/oficina/orcamento-pecas/", {
                method: "POST",
                body: JSON.stringify({
                    orcamento: selecionado.id,
                    peca: Number(formPeca.peca),
                    quantidade: Number(formPeca.quantidade),
                    valor_unitario: formPeca.valor_unitario,
                }),
            });
            setFormPeca(pecaVazia);
            await carregar();
        } catch (error) {
            setErro(error.message);
        } finally {
            setProcessando("");
        }
    }

    async function removerItem(tipo, id) {
        if (!window.confirm("Remover este item do orçamento?")) return;
        setErro("");
        setProcessando(`${tipo}-${id}`);
        try {
            await apiRequest(`/oficina/orcamento-${tipo}/${id}/`, {method: "DELETE"});
            await carregar();
        } catch (error) {
            setErro(error.message);
        } finally {
            setProcessando("");
        }
    }

    async function decidir(decisao) {
        if (!selecionado) return;
        const texto = decisao === "aprovar" ? "aprovar" : "recusar";
        if (!window.confirm(`Deseja realmente ${texto} este orçamento? Essa decisão não poderá ser alterada.`)) return;
        setErro("");
        setProcessando(decisao);
        try {
            await apiRequest(`/oficina/orcamentos/${selecionado.id}/${decisao}/`, {method: "POST", body: "{}"});
            await carregar();
        } catch (error) {
            setErro(error.message);
        } finally {
            setProcessando("");
        }
    }

    async function publicar() {
        if (!selecionado) return;
        if (!window.confirm("Publicar este orçamento para o cliente? Após a publicação, os valores e itens não poderão ser alterados.")) return;
        setErro("");
        setProcessando("publicar");
        try {
            await apiRequest(`/oficina/orcamentos/${selecionado.id}/publicar/`, {method: "POST", body: "{}"});
            await carregar();
        } catch (error) {
            setErro(error.message);
        } finally {
            setProcessando("");
        }
    }

    return (
        <section className="page-section">
            <div className="page-heading">
                <div><p className="eyebrow">Atendimento</p><h1>Orçamentos</h1>
                    <p className="lead">Prepare o orçamento em rascunho, envie para revisão administrativa e acompanhe a decisão do cliente.</p>
                </div>
            </div>
            {erro ? <p className="form-error" role="alert">{erro}</p> : null}
            <div className={podeEditar ? "management-grid" : "management-grid single-column"}>
                <div className="budget-workspace">
                    <div className="table-card">{carregando ?
                        <p className="muted" role="status">Carregando orçamentos...</p> : (
                            <div className="table-scroll">
                                <table>
                                    <thead>
                                    <tr>
                                        <th>Ordem</th>
                                        <th>Status</th>
                                        <th>Validade</th>
                                        <th>Total</th>
                                        <th><span className="sr-only">Ações</span></th>
                                    </tr>
                                    </thead>
                                    <tbody>{orcamentos.length ? orcamentos.map((orcamento) => {
                                        const ordem = ordensPorId.get(orcamento.ordem_servico);
                                        const classeSelecionada = orcamento.id === selecionadoId ? `selected-row selected-${orcamento.status.toLowerCase()}` : "";
                                        return <tr key={orcamento.id} className={classeSelecionada}>
                                            <td>
                                                <strong>{ordem?.numero || `OS #${orcamento.ordem_servico}`}</strong><small>{ordem?.descricao_problema}</small>
                                            </td>
                                            <td><span
                                                className={`status-badge status-${orcamento.status.toLowerCase()}`}>{nomesStatus[orcamento.status]}</span>
                                            </td>
                                            <td>{dataBrasileira(orcamento.validade)}</td>
                                            <td><strong>{moeda(orcamento.valor_total)}</strong></td>
                                            <td>
                                                <button className="table-action" type="button"
                                                        onClick={() => setSelecionadoId(orcamento.id)}>Ver detalhes
                                                </button>
                                            </td>
                                        </tr>;
                                    }) : <tr>
                                        <td colSpan="5" className="empty-cell">Nenhum orçamento encontrado.</td>
                                    </tr>}</tbody>
                                </table>
                            </div>
                        )}</div>
                    {selecionado ?
                        <article className={`budget-detail budget-detail-${selecionado.status.toLowerCase()}`}
                                 aria-labelledby="orcamento-detalhes">
                            <div className="budget-detail-heading">
                                <div><p className="eyebrow">Detalhamento</p><h2
                                    id="orcamento-detalhes">{ordensPorId.get(selecionado.ordem_servico)?.numero || `Orçamento #${selecionado.id}`}</h2>
                                </div>
                                <strong className="budget-total">{moeda(selecionado.valor_total)}</strong></div>
                            <dl className="budget-summary">
                                <div>
                                    <dt>Mão de obra</dt>
                                    <dd>{moeda(selecionado.valor_mao_obra)}</dd>
                                </div>
                                <div>
                                    <dt>Peças</dt>
                                    <dd>{moeda(selecionado.valor_pecas)}</dd>
                                </div>
                                <div>
                                    <dt>Validade</dt>
                                    <dd>{dataBrasileira(selecionado.validade)}</dd>
                                </div>
                            </dl>
                            {selecionado.observacoes ?
                                <p className="budget-note"><strong>Observações:</strong> {selecionado.observacoes}
                                </p> : null}
                            <div className="budget-items">
                                <section><h3>Serviços previstos</h3>{selecionado.servicos_previstos.length ?
                                    <ul>{selecionado.servicos_previstos.map((item) => <li key={item.id}>
                                        <span><strong>{item.descricao}</strong><small>{item.quantidade} × {moeda(item.valor_unitario)}</small></span><span><strong>{moeda(item.valor_total)}</strong>{podeEditar && selecionado.status === "RASCUNHO" ?
                                        <button className="remove-action" type="button" disabled={Boolean(processando)}
                                                onClick={() => removerItem("servicos", item.id)}>Remover</button> : null}</span>
                                    </li>)}</ul> : <p className="muted">Nenhum serviço previsto.</p>}</section>
                                <section><h3>Peças previstas</h3>{selecionado.pecas_previstas.length ?
                                    <ul>{selecionado.pecas_previstas.map((item) => <li key={item.id}>
                                        <span><strong>{item.peca_nome || `Peça #${item.peca}`}</strong><small>{item.peca_codigo ? `${item.peca_codigo} · ` : ""}{item.quantidade} × {moeda(item.valor_unitario)}</small></span><span><strong>{moeda(item.valor_total)}</strong>{podeEditar && selecionado.status === "RASCUNHO" ?
                                        <button className="remove-action" type="button" disabled={Boolean(processando)}
                                                onClick={() => removerItem("pecas", item.id)}>Remover</button> : null}</span>
                                    </li>)}</ul> : <p className="muted">Nenhuma peça prevista.</p>}</section>
                            </div>
                            {podeEditar && selecionado.status === "RASCUNHO" ? <div className="budget-editor">
                                <form onSubmit={adicionarServico}><h3>Adicionar serviço</h3><label
                                    htmlFor="servico-descricao">Descrição</label><input id="servico-descricao" required
                                                                                        value={formServico.descricao}
                                                                                        onChange={(e) => setFormServico((valor) => ({
                                                                                            ...valor,
                                                                                            descricao: e.target.value
                                                                                        }))}/>
                                    <div className="field-row">
                                        <div><label htmlFor="servico-quantidade">Quantidade</label><input
                                            id="servico-quantidade" type="number" min="1" required
                                            value={formServico.quantidade} onChange={(e) => setFormServico((valor) => ({
                                            ...valor,
                                            quantidade: e.target.value
                                        }))}/></div>
                                        <div><label htmlFor="servico-valor">Valor unitário</label><input
                                            id="servico-valor" type="number" min="0" step="0.01" required
                                            value={formServico.valor_unitario}
                                            onChange={(e) => setFormServico((valor) => ({
                                                ...valor,
                                                valor_unitario: e.target.value
                                            }))}/></div>
                                    </div>
                                    <button className="button button-secondary" disabled={Boolean(processando)}
                                            type="submit">{processando === "servico" ? "Adicionando..." : "Adicionar serviço"}</button>
                                </form>
                                <form onSubmit={adicionarPeca}><h3>Adicionar peça</h3><label
                                    htmlFor="orcamento-peca">Peça</label><select id="orcamento-peca" required
                                                                                 value={formPeca.peca}
                                                                                 onChange={(e) => {
                                                                                     const id = e.target.value;
                                                                                     const peca = pecasPorId.get(Number(id));
                                                                                     setFormPeca((valor) => ({
                                                                                         ...valor,
                                                                                         peca: id,
                                                                                         valor_unitario: peca?.valor_unitario || valor.valor_unitario
                                                                                     }));
                                                                                 }}>
                                    <option value="">Selecione</option>
                                    {pecas.map((peca) => <option key={peca.id}
                                                                 value={peca.id}>{peca.codigo} — {peca.nome}</option>)}
                                </select>
                                    <div className="field-row">
                                        <div><label htmlFor="peca-quantidade">Quantidade</label><input
                                            id="peca-quantidade" type="number" min="1" required
                                            value={formPeca.quantidade} onChange={(e) => setFormPeca((valor) => ({
                                            ...valor,
                                            quantidade: e.target.value
                                        }))}/></div>
                                        <div><label htmlFor="peca-valor">Valor unitário</label><input id="peca-valor"
                                                                                                      type="number"
                                                                                                      min="0"
                                                                                                      step="0.01"
                                                                                                      required
                                                                                                      value={formPeca.valor_unitario}
                                                                                                      onChange={(e) => setFormPeca((valor) => ({
                                                                                                          ...valor,
                                                                                                          valor_unitario: e.target.value
                                                                                                      }))}/></div>
                                    </div>
                                    <button className="button button-secondary" disabled={Boolean(processando)}
                                            type="submit">{processando === "peca" ? "Adicionando..." : "Adicionar peça"}</button>
                                </form>
                            </div> : null}
                            {selecionado.status === "RASCUNHO" ? <div className="decision-panel">
                                <div><strong>Este orçamento ainda não foi publicado.</strong>
                                    <p>{ehAdministrador ? "Revise os valores e itens antes de enviar ao cliente." : "Após o preenchimento, o Administrador deverá revisar e publicar."}</p>
                                </div>
                                {ehAdministrador ? <div>
                                    <button className="button button-primary" disabled={Boolean(processando)}
                                            type="button"
                                            onClick={publicar}>{processando === "publicar" ? "Publicando..." : "Publicar para o cliente"}</button>
                                </div> : null}</div> : null}
                            {ehCliente && selecionado.status === "AGUARDANDO_APROVACAO" ?
                                <div className="decision-panel">
                                    <div><strong>Este orçamento aguarda sua decisão.</strong><p>Confira todos os itens e
                                        valores antes de continuar.</p></div>
                                    <div>
                                        <button className="button button-secondary" disabled={Boolean(processando)}
                                                type="button" onClick={() => decidir("aprovar")}>Aprovar orçamento
                                        </button>
                                        <button className="button button-danger" disabled={Boolean(processando)}
                                                type="button" onClick={() => decidir("recusar")}>Recusar
                                        </button>
                                    </div>
                                </div> : null}
                        </article> : null}
                </div>
                {podeEditar ? <form className="form-card" onSubmit={emitir}>
                    <div><p className="eyebrow">Nova proposta</p><h2>Criar rascunho</h2></div>
                    <label htmlFor="orcamento-os">Ordem de serviço</label><select id="orcamento-os" required
                                                                                  value={formOrcamento.ordem_servico}
                                                                                  onChange={(e) => setFormOrcamento((valor) => ({
                                                                                      ...valor,
                                                                                      ordem_servico: e.target.value
                                                                                  }))}>
                    <option value="">Selecione</option>
                    {ordensElegiveis.map((ordem) => <option key={ordem.id}
                                                            value={ordem.id}>{ordem.numero} — {ordem.descricao_problema}</option>)}
                </select>{!ordensElegiveis.length ?
                    <small className="muted">Não há OS disponível para um novo rascunho.</small> : null}
                    <div className="field-row">
                        <div><label htmlFor="orcamento-mao-obra">Valor da mão de obra</label><input
                            id="orcamento-mao-obra" type="number" min="0" step="0.01" placeholder="0,00" required
                            value={formOrcamento.valor_mao_obra} onChange={(e) => setFormOrcamento((valor) => ({
                            ...valor,
                            valor_mao_obra: e.target.value
                        }))}/></div>
                        <div><label htmlFor="orcamento-pecas">Valor estimado das peças</label><input
                            id="orcamento-pecas" type="number" min="0" step="0.01" placeholder="0,00" required
                            value={formOrcamento.valor_pecas}
                            onChange={(e) => setFormOrcamento((valor) => ({...valor, valor_pecas: e.target.value}))}/>
                        </div>
                    </div>
                    <div className="budget-issue-total">
                        <span>Valor total do orçamento</span><strong>{moeda(totalNovoOrcamento)}</strong></div>
                    <label htmlFor="orcamento-validade">Validade</label><input id="orcamento-validade" type="date"
                                                                               value={formOrcamento.validade}
                                                                               onChange={(e) => setFormOrcamento((valor) => ({
                                                                                   ...valor,
                                                                                   validade: e.target.value
                                                                               }))}/><label
                    htmlFor="orcamento-observacoes">Observações</label><textarea id="orcamento-observacoes" rows="4"
                                                                                 value={formOrcamento.observacoes}
                                                                                 onChange={(e) => setFormOrcamento((valor) => ({
                                                                                     ...valor,
                                                                                     observacoes: e.target.value
                                                                                 }))}/>
                    <button className="button button-primary"
                            disabled={processando === "emitir" || !ordensElegiveis.length || totalNovoOrcamento <= 0}
                            type="submit">{processando === "emitir" ? "Salvando..." : "Salvar rascunho"}</button>
                </form> : null}
            </div>
        </section>
    );
}
