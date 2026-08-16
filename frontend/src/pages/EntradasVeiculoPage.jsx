import { useCallback, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../api/client";
import { extrairLista } from "../utils/apiData";

const itensChecklist = [
  ["PNEU_DIANTEIRO", "Pneu dianteiro", true], ["PNEU_TRASEIRO", "Pneu traseiro", true],
  ["RODAS", "Rodas", false], ["FREIOS", "Freios", false],
  ["ILUMINACAO", "Faróis e lanternas", false], ["RETROVISORES", "Retrovisores", false],
  ["CARENAGENS", "Carenagens", false], ["SUSPENSAO", "Suspensão", false], ["PAINEL", "Painel", false],
];
const estados = { NORMAL: "Normal", COM_AVARIA: "Com avaria", NAO_VERIFICADO: "Não verificado" };
const formularioVazio = { ordem_servico: "", quilometragem: "", nivel_combustivel: "", motivo_entrada: "", observacoes: "" };

function checklistInicial() {
  return Object.fromEntries(itensChecklist.map(([item, , percentual]) => [item, {
    estado: percentual ? "" : "NORMAL", percentual: percentual ? "100" : "", observacao: "",
  }]));
}

export default function EntradasVeiculoPage() {
  const [entradas, setEntradas] = useState([]);
  const [ordens, setOrdens] = useState([]);
  const [motocicletas, setMotocicletas] = useState([]);
  const [selecionadaId, setSelecionadaId] = useState(null);
  const [form, setForm] = useState(formularioVazio);
  const [checklist, setChecklist] = useState(checklistInicial);
  const [avarias, setAvarias] = useState([]);
  const [acessorios, setAcessorios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");

  const ordensPorId = useMemo(() => new Map(ordens.map((ordem) => [ordem.id, ordem])), [ordens]);
  const motosPorId = useMemo(() => new Map(motocicletas.map((moto) => [moto.id, moto])), [motocicletas]);
  const ordensComEntrada = useMemo(() => new Set(entradas.map((entrada) => entrada.ordem_servico)), [entradas]);
  const ordensElegiveis = useMemo(() => ordens.filter(
    (ordem) => ordem.status === "ABERTA" && !ordensComEntrada.has(ordem.id),
  ), [ordens, ordensComEntrada]);
  const selecionada = entradas.find((entrada) => entrada.id === selecionadaId) || null;

  const carregar = useCallback(async (manterSelecao = true) => {
    setErro(""); setCarregando(true);
    try {
      const [dadosEntradas, dadosOrdens, dadosMotos] = await Promise.all([
        apiRequest("/oficina/entradas-veiculo/"), apiRequest("/oficina/ordens-servico/"), apiRequest("/oficina/motocicletas/"),
      ]);
      const lista = extrairLista(dadosEntradas);
      setEntradas(lista); setOrdens(extrairLista(dadosOrdens)); setMotocicletas(extrairLista(dadosMotos));
      setSelecionadaId((atual) => manterSelecao && lista.some((entrada) => entrada.id === atual) ? atual : lista[0]?.id ?? null);
    } catch (error) { setErro(error.message); } finally { setCarregando(false); }
  }, []);

  useEffect(() => { carregar(false); }, [carregar]);

  function atualizarChecklist(item, campo, valor) {
    setChecklist((atual) => ({ ...atual, [item]: { ...atual[item], [campo]: valor } }));
  }
  function atualizarLista(definir, indice, campo, valor) {
    definir((atual) => atual.map((item, posicao) => posicao === indice ? { ...item, [campo]: valor } : item));
  }

  async function registrar(event) {
    event.preventDefault(); setErro(""); setSalvando(true);
    const dadosChecklist = itensChecklist.map(([item, , usaPercentual]) => ({
      item, estado: usaPercentual ? "" : checklist[item].estado,
      percentual: usaPercentual ? Number(checklist[item].percentual) : null,
      observacao: checklist[item].observacao.trim(),
    }));
    try {
      const criada = await apiRequest("/oficina/entradas-veiculo/", { method: "POST", body: JSON.stringify({
        ordem_servico: Number(form.ordem_servico), quilometragem: form.quilometragem ? Number(form.quilometragem) : null,
        nivel_combustivel: form.nivel_combustivel, motivo_entrada: form.motivo_entrada.trim(), observacoes: form.observacoes.trim(),
        itens_checklist: dadosChecklist,
        avarias: avarias.filter((item) => item.descricao.trim()).map((item) => ({ descricao: item.descricao.trim(), localizacao: item.localizacao.trim() })),
        acessorios: acessorios.filter((item) => item.descricao.trim()).map((item) => ({ descricao: item.descricao.trim() })),
      }) });
      setForm(formularioVazio); setChecklist(checklistInicial()); setAvarias([]); setAcessorios([]);
      await carregar(); setSelecionadaId(criada.id);
    } catch (error) { setErro(error.message); } finally { setSalvando(false); }
  }

  function referencias(entrada) {
    const ordem = ordensPorId.get(entrada.ordem_servico);
    return { ordem, moto: motosPorId.get(ordem?.motocicleta) };
  }

  return <section className="page-section">
    <div className="page-heading"><div><p className="eyebrow">Recepção técnica</p><h1>Entrada da motocicleta</h1><p className="lead">Registre as condições do veículo recebidas junto com a ordem de serviço.</p></div></div>
    {erro ? <p className="form-error" role="alert">{erro}</p> : null}
    <div className="entry-layout"><div className="entry-records"><div className="table-card">{carregando ? <p className="muted" role="status">Carregando entradas...</p> : <div className="table-scroll"><table><thead><tr><th>Ordem</th><th>Motocicleta</th><th>Quilometragem</th><th><span className="sr-only">Ações</span></th></tr></thead><tbody>{entradas.length ? entradas.map((entrada) => { const { ordem, moto } = referencias(entrada); return <tr key={entrada.id} className={entrada.id === selecionadaId ? "selected-row" : ""}><td><strong>{ordem?.numero || `OS #${entrada.ordem_servico}`}</strong><small>{entrada.motivo_entrada}</small></td><td>{moto ? `${moto.marca} ${moto.modelo}` : "Motocicleta"}<small>{moto?.placa}</small></td><td>{entrada.quilometragem ? `${entrada.quilometragem.toLocaleString("pt-BR")} km` : "Não informada"}</td><td><button className="table-action" type="button" onClick={() => setSelecionadaId(entrada.id)}>Ver vistoria</button></td></tr>; }) : <tr><td colSpan="4" className="empty-cell">Nenhuma entrada registrada.</td></tr>}</tbody></table></div>}</div>
      {selecionada ? <article className="inspection-detail"><div><p className="eyebrow">Vistoria registrada</p><h2>{ordensPorId.get(selecionada.ordem_servico)?.numero}</h2><p>{selecionada.motivo_entrada}</p></div><dl className="budget-summary"><div><dt>Combustível</dt><dd>{selecionada.nivel_combustivel || "Não informado"}</dd></div><div><dt>Quilometragem</dt><dd>{selecionada.quilometragem ? `${selecionada.quilometragem.toLocaleString("pt-BR")} km` : "Não informada"}</dd></div><div><dt>Registro</dt><dd>{new Date(selecionada.registrada_em).toLocaleString("pt-BR")}</dd></div></dl><div className="inspection-columns"><section><h3>Checklist</h3><ul className="inspection-list">{selecionada.itens_checklist.map((item) => <li key={item.id}><strong>{itensChecklist.find(([codigo]) => codigo === item.item)?.[1] || item.item}</strong><span>{item.percentual !== null ? `${item.percentual}%` : estados[item.estado]}{item.observacao ? ` — ${item.observacao}` : ""}</span></li>)}</ul></section><section><h3>Avarias</h3>{selecionada.avarias.length ? <ul className="inspection-list">{selecionada.avarias.map((item) => <li key={item.id}><strong>{item.localizacao || "Local não informado"}</strong><span>{item.descricao}</span></li>)}</ul> : <p className="muted">Nenhuma avaria registrada.</p>}<h3>Acessórios</h3>{selecionada.acessorios.length ? <ul className="inspection-list">{selecionada.acessorios.map((item) => <li key={item.id}>{item.descricao}</li>)}</ul> : <p className="muted">Nenhum acessório registrado.</p>}</section></div>{selecionada.observacoes ? <p className="budget-note"><strong>Observações:</strong> {selecionada.observacoes}</p> : null}</article> : null}</div>
      <form className="entry-form" onSubmit={registrar}><div><p className="eyebrow">Nova entrada</p><h2>Dados da recepção</h2></div><label htmlFor="entrada-os">OS e motocicleta</label><select id="entrada-os" required value={form.ordem_servico} onChange={(e) => setForm((atual) => ({ ...atual, ordem_servico: e.target.value }))}><option value="">Selecione</option>{ordensElegiveis.map((ordem) => { const moto = motosPorId.get(ordem.motocicleta); return <option key={ordem.id} value={ordem.id}>{ordem.numero} — {moto ? `${moto.placa} · ${moto.marca} ${moto.modelo}` : "Motocicleta"}</option>; })}</select>{!ordensElegiveis.length ? <small className="muted">A motocicleta precisa ter uma OS aberta e ainda não pode possuir entrada registrada.</small> : null}<div className="field-row"><div><label htmlFor="entrada-km">Quilometragem</label><input id="entrada-km" type="number" min="0" value={form.quilometragem} onChange={(e) => setForm((atual) => ({ ...atual, quilometragem: e.target.value }))} /></div><div><label htmlFor="entrada-combustivel">Combustível</label><select id="entrada-combustivel" value={form.nivel_combustivel} onChange={(e) => setForm((atual) => ({ ...atual, nivel_combustivel: e.target.value }))}><option value="">Não informado</option><option>Reserva</option><option>1/4 do tanque</option><option>Meio tanque</option><option>3/4 do tanque</option><option>Tanque cheio</option></select></div></div><label htmlFor="entrada-motivo">Motivo da entrada</label><textarea id="entrada-motivo" required rows="3" value={form.motivo_entrada} onChange={(e) => setForm((atual) => ({ ...atual, motivo_entrada: e.target.value }))} />
        <fieldset className="checklist-fieldset"><legend>Checklist obrigatório</legend>{itensChecklist.map(([item, nome, usaPercentual]) => <div className="checklist-row" key={item}><label htmlFor={`check-${item}`}>{nome}</label>{usaPercentual ? <div className="percentage-input"><input id={`check-${item}`} type="number" required min="0" max="100" value={checklist[item].percentual} onChange={(e) => atualizarChecklist(item, "percentual", e.target.value)} /><span>%</span></div> : <select id={`check-${item}`} value={checklist[item].estado} onChange={(e) => atualizarChecklist(item, "estado", e.target.value)}><option value="NORMAL">Normal</option><option value="COM_AVARIA">Com avaria</option><option value="NAO_VERIFICADO">Não verificado</option></select>}<input aria-label={`Observação sobre ${nome}`} placeholder="Observação opcional" value={checklist[item].observacao} onChange={(e) => atualizarChecklist(item, "observacao", e.target.value)} /></div>)}</fieldset>
        <section className="dynamic-section"><div><h3>Avarias</h3><button className="table-action" type="button" onClick={() => setAvarias((atual) => [...atual, { descricao: "", localizacao: "" }])}>Adicionar</button></div>{avarias.map((avaria, indice) => <div className="dynamic-row" key={indice}><input aria-label={`Local da avaria ${indice + 1}`} placeholder="Local" value={avaria.localizacao} onChange={(e) => atualizarLista(setAvarias, indice, "localizacao", e.target.value)} /><input aria-label={`Descrição da avaria ${indice + 1}`} required placeholder="Descrição da avaria" value={avaria.descricao} onChange={(e) => atualizarLista(setAvarias, indice, "descricao", e.target.value)} /><button className="remove-action" type="button" onClick={() => setAvarias((atual) => atual.filter((_, posicao) => posicao !== indice))}>Remover</button></div>)}</section>
        <section className="dynamic-section"><div><h3>Acessórios entregues</h3><button className="table-action" type="button" onClick={() => setAcessorios((atual) => [...atual, { descricao: "" }])}>Adicionar</button></div>{acessorios.map((acessorio, indice) => <div className="dynamic-row accessory-row" key={indice}><input aria-label={`Acessório ${indice + 1}`} required placeholder="Ex.: baú traseiro" value={acessorio.descricao} onChange={(e) => atualizarLista(setAcessorios, indice, "descricao", e.target.value)} /><button className="remove-action" type="button" onClick={() => setAcessorios((atual) => atual.filter((_, posicao) => posicao !== indice))}>Remover</button></div>)}</section><label htmlFor="entrada-observacoes">Observações gerais</label><textarea id="entrada-observacoes" rows="3" value={form.observacoes} onChange={(e) => setForm((atual) => ({ ...atual, observacoes: e.target.value }))} /><button className="button button-primary" disabled={salvando || !ordensElegiveis.length} type="submit">{salvando ? "Registrando..." : "Registrar entrada e checklist"}</button></form></div>
  </section>;
}
