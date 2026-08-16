import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { apiRequest } from "../api/client";
import { extrairLista } from "../utils/apiData";

const itensChecklist = [
  ["PNEU_DIANTEIRO", "Pneu dianteiro", true], ["PNEU_TRASEIRO", "Pneu traseiro", true],
  ["RODAS", "Rodas", false], ["FREIOS", "Freios", false], ["ILUMINACAO", "Faróis e lanternas", false],
  ["RETROVISORES", "Retrovisores", false], ["CARENAGENS", "Carenagens", false],
  ["SUSPENSAO", "Suspensão", false], ["PAINEL", "Painel", false],
];
const formularioVazio = {
  cliente: "", motocicleta: "", nova_motocicleta: true, modelo_catalogo: "", marca: "", modelo: "",
  ano: "", placa: "", chassi: "", cor: "", tipo_manutencao: "CORRETIVA", descricao_problema: "",
  quilometragem: "", nivel_combustivel: "", motivo_entrada: "", observacoes: "",
};
function checklistInicial() {
  return Object.fromEntries(itensChecklist.map(([item, , pneu]) => [item, { estado: pneu ? "" : "NORMAL", percentual: pneu ? "100" : "", observacao: "" }]));
}

export default function EntradasVeiculoPage() {
  const navigate = useNavigate();
  const [parametros] = useSearchParams();
  const [clientes, setClientes] = useState([]);
  const [motocicletas, setMotocicletas] = useState([]);
  const [catalogo, setCatalogo] = useState([]);
  const [form, setForm] = useState(formularioVazio);
  const [checklist, setChecklist] = useState(checklistInicial);
  const [avarias, setAvarias] = useState([]);
  const [acessorios, setAcessorios] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const motosDoCliente = useMemo(() => motocicletas.filter((moto) => moto.cliente === Number(form.cliente)), [form.cliente, motocicletas]);

  const carregar = useCallback(async () => {
    setCarregando(true);
    try {
      const [dadosClientes, dadosMotos, dadosCatalogo] = await Promise.all([
        apiRequest("/oficina/clientes/"), apiRequest("/oficina/motocicletas/"), apiRequest("/oficina/modelos-motocicleta/"),
      ]);
      setClientes(extrairLista(dadosClientes)); setMotocicletas(extrairLista(dadosMotos)); setCatalogo(extrairLista(dadosCatalogo));
    } catch (error) { setErro(error.message); } finally { setCarregando(false); }
  }, []);
  useEffect(() => { carregar(); }, [carregar]);
  useEffect(() => {
    const cliente = parametros.get("cliente");
    if (cliente) setForm((atual) => ({ ...atual, cliente, nova_motocicleta: parametros.get("nova_moto") === "1" }));
  }, [parametros]);

  function atualizarChecklist(item, campo, valor) {
    setChecklist((atual) => ({ ...atual, [item]: { ...atual[item], [campo]: valor } }));
  }
  function atualizarLista(definir, indice, campo, valor) {
    definir((atual) => atual.map((item, posicao) => posicao === indice ? { ...item, [campo]: valor } : item));
  }

  async function salvar(event) {
    event.preventDefault(); setErro(""); setSalvando(true);
    const itens = itensChecklist.map(([item, , pneu]) => ({
      item, estado: pneu ? "" : checklist[item].estado, percentual: pneu ? Number(checklist[item].percentual) : null,
      observacao: checklist[item].observacao.trim(),
    }));
    const dados = {
      cliente: Number(form.cliente), motocicleta: form.nova_motocicleta ? null : Number(form.motocicleta),
      tipo_manutencao: form.tipo_manutencao, descricao_problema: form.descricao_problema.trim(),
      quilometragem: form.quilometragem ? Number(form.quilometragem) : null, nivel_combustivel: form.nivel_combustivel,
      motivo_entrada: form.motivo_entrada.trim(), observacoes: form.observacoes.trim(), itens_checklist: itens,
      avarias: avarias.filter((item) => item.descricao.trim()), acessorios: acessorios.filter((item) => item.descricao.trim()),
    };
    if (form.nova_motocicleta) Object.assign(dados, {
      marca: form.marca.trim(), modelo: form.modelo.trim(), ano: Number(form.ano), placa: form.placa.trim().toUpperCase(),
      chassi: form.chassi.trim().toUpperCase() || null, cor: form.cor.trim(),
    });
    try {
      await apiRequest("/oficina/ordens-servico/abrir-atendimento/", { method: "POST", body: JSON.stringify(dados) });
      navigate("/orcamentos");
    } catch (error) { setErro(error.message); } finally { setSalvando(false); }
  }

  return <section className="page-section">
    <div className="page-heading"><div><p className="eyebrow">Recepção</p><h1>Novo atendimento</h1><p className="lead">Registre cliente, motocicleta e vistoria. A ordem de serviço será gerada automaticamente.</p></div></div>
    {erro ? <p className="form-error" role="alert">{erro}</p> : null}
    <form className="intake-form" onSubmit={salvar}>
      <section><h2>1. Cliente e motocicleta</h2><label htmlFor="at-cliente">Cliente</label><select id="at-cliente" required disabled={carregando} value={form.cliente} onChange={(e) => setForm((v) => ({ ...v, cliente: e.target.value, motocicleta: "" }))}><option value="">Selecione</option>{clientes.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome} — {cliente.cpf}</option>)}</select>
        <label className="option-toggle"><input type="checkbox" checked={form.nova_motocicleta} onChange={(e) => setForm((v) => ({ ...v, nova_motocicleta: e.target.checked }))} /> Cadastrar nova motocicleta</label>
        {form.nova_motocicleta ? <div className="inline-vehicle-form"><label htmlFor="at-catalogo">Catálogo</label><select id="at-catalogo" value={form.modelo_catalogo} onChange={(e) => { const item = catalogo.find((modelo) => modelo.id === Number(e.target.value)); setForm((v) => ({ ...v, modelo_catalogo: e.target.value, marca: item?.marca || "", modelo: item?.modelo || "" })); }}><option value="">Selecione ou preencha manualmente</option>{catalogo.map((item) => <option key={item.id} value={item.id}>{item.marca} — {item.modelo}</option>)}</select><div className="field-row"><div><label htmlFor="at-marca">Marca</label><input id="at-marca" required value={form.marca} onChange={(e) => setForm((v) => ({ ...v, marca: e.target.value }))} /></div><div><label htmlFor="at-modelo">Modelo</label><input id="at-modelo" required value={form.modelo} onChange={(e) => setForm((v) => ({ ...v, modelo: e.target.value }))} /></div></div><div className="field-row"><div><label htmlFor="at-placa">Placa</label><input id="at-placa" required value={form.placa} onChange={(e) => setForm((v) => ({ ...v, placa: e.target.value.toUpperCase() }))} /></div><div><label htmlFor="at-chassi">Chassi</label><input id="at-chassi" value={form.chassi} onChange={(e) => setForm((v) => ({ ...v, chassi: e.target.value.toUpperCase() }))} /></div></div><div className="field-row"><div><label htmlFor="at-ano">Ano</label><input id="at-ano" type="number" min="1900" max="2100" required value={form.ano} onChange={(e) => setForm((v) => ({ ...v, ano: e.target.value }))} /></div><div><label htmlFor="at-cor">Cor</label><input id="at-cor" value={form.cor} onChange={(e) => setForm((v) => ({ ...v, cor: e.target.value }))} /></div></div></div> : <><label htmlFor="at-moto">Motocicleta cadastrada</label><select id="at-moto" required value={form.motocicleta} onChange={(e) => setForm((v) => ({ ...v, motocicleta: e.target.value }))}><option value="">Selecione</option>{motosDoCliente.map((moto) => <option key={moto.id} value={moto.id}>{moto.placa} — {moto.marca} {moto.modelo}</option>)}</select></>}
      </section>
      <section><h2>2. Solicitação e recepção</h2><label htmlFor="at-tipo">Tipo de manutenção</label><select id="at-tipo" value={form.tipo_manutencao} onChange={(e) => setForm((v) => ({ ...v, tipo_manutencao: e.target.value }))}><option value="CORRETIVA">Corretiva</option><option value="PREVENTIVA">Preventiva</option></select><label htmlFor="at-problema">Problema relatado</label><textarea id="at-problema" required rows="3" value={form.descricao_problema} onChange={(e) => setForm((v) => ({ ...v, descricao_problema: e.target.value }))} /><div className="field-row"><div><label htmlFor="at-km">Quilometragem</label><input id="at-km" type="number" min="0" value={form.quilometragem} onChange={(e) => setForm((v) => ({ ...v, quilometragem: e.target.value }))} /></div><div><label htmlFor="at-combustivel">Combustível</label><select id="at-combustivel" value={form.nivel_combustivel} onChange={(e) => setForm((v) => ({ ...v, nivel_combustivel: e.target.value }))}><option value="">Não informado</option><option>Reserva</option><option>1/4 do tanque</option><option>Meio tanque</option><option>3/4 do tanque</option><option>Tanque cheio</option></select></div></div><label htmlFor="at-motivo">Motivo da entrada</label><textarea id="at-motivo" required rows="3" value={form.motivo_entrada} onChange={(e) => setForm((v) => ({ ...v, motivo_entrada: e.target.value }))} /></section>
      <section className="intake-wide"><h2>3. Checklist da motocicleta</h2><fieldset className="checklist-fieldset"><legend>Condições no recebimento</legend>{itensChecklist.map(([item, nome, pneu]) => <div className="checklist-row" key={item}><label htmlFor={`at-${item}`}>{nome}</label>{pneu ? <div className="percentage-input"><input id={`at-${item}`} type="number" min="0" max="100" required value={checklist[item].percentual} onChange={(e) => atualizarChecklist(item, "percentual", e.target.value)} /><span>%</span></div> : <select id={`at-${item}`} value={checklist[item].estado} onChange={(e) => atualizarChecklist(item, "estado", e.target.value)}><option value="NORMAL">Normal</option><option value="COM_AVARIA">Com avaria</option><option value="NAO_VERIFICADO">Não verificado</option></select>}<input aria-label={`Observação sobre ${nome}`} placeholder="Observação opcional" value={checklist[item].observacao} onChange={(e) => atualizarChecklist(item, "observacao", e.target.value)} /></div>)}</fieldset></section>
      <section><div className="section-action"><h2>4. Avarias</h2><button className="table-action" type="button" onClick={() => setAvarias((v) => [...v, { descricao: "", localizacao: "" }])}>Adicionar</button></div>{avarias.map((item, i) => <div className="dynamic-row" key={i}><input required placeholder="Local" value={item.localizacao} onChange={(e) => atualizarLista(setAvarias, i, "localizacao", e.target.value)} /><input required placeholder="Descrição" value={item.descricao} onChange={(e) => atualizarLista(setAvarias, i, "descricao", e.target.value)} /><button className="remove-action" type="button" onClick={() => setAvarias((v) => v.filter((_, p) => p !== i))}>Remover</button></div>)}</section>
      <section><div className="section-action"><h2>5. Acessórios</h2><button className="table-action" type="button" onClick={() => setAcessorios((v) => [...v, { descricao: "" }])}>Adicionar</button></div>{acessorios.map((item, i) => <div className="dynamic-row accessory-row" key={i}><input required placeholder="Acessório entregue" value={item.descricao} onChange={(e) => atualizarLista(setAcessorios, i, "descricao", e.target.value)} /><button className="remove-action" type="button" onClick={() => setAcessorios((v) => v.filter((_, p) => p !== i))}>Remover</button></div>)}<label htmlFor="at-obs">Observações gerais</label><textarea id="at-obs" rows="3" value={form.observacoes} onChange={(e) => setForm((v) => ({ ...v, observacoes: e.target.value }))} /></section>
      <div className="intake-submit"><p><strong>Ao confirmar:</strong> a entrada será registrada e a OS será gerada em “Aguardando orçamento”.</p><button className="button button-primary" disabled={salvando || carregando} type="submit">{salvando ? "Gerando atendimento..." : "Confirmar entrada e gerar OS"}</button></div>
    </form>
  </section>;
}
