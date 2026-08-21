import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

import { apiRequest } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import { extrairLista } from "../utils/apiData";
import garagem66Logo from "../assets/garagem-66-logo.png";

const menusPorPerfil = {
  ADMINISTRADOR: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque", "requisicoes", "usuarios"],
  ATENDENTE: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque", "requisicoes"],
  MECANICO: ["minhas-ordens", "requisicoes", "estoque"],
  CLIENTE: ["minhas-motos", "minhas-ordens", "orcamentos", "historico"],
};
const iconesMenu = { clientes: "♙", motocicletas: "♞", ordens: "▤", orcamentos: "▧", estoque: "◇", usuarios: "♙", "minhas-ordens": "▤", requisicoes: "▱", "minhas-motos": "♞", historico: "◴" };

function nomeMenu(valor) {
  if (valor === "usuarios") return "Colaboradores";
  return valor.replaceAll("-", " ").replace(/\b\w/g, (letra) => letra.toUpperCase());
}

export default function AppLayout() {
  const { usuario, logout } = useAuth();
  const menus = menusPorPerfil[usuario.tipo] ?? [];
  const recebeNotificacoes = ["ADMINISTRADOR", "MECANICO"].includes(usuario.tipo);
  const chaveLidas = `garagem66.notificacoes.lidas.${usuario.id}`;
  const [notificacoes, setNotificacoes] = useState([]);
  const [lidas, setLidas] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem(chaveLidas)) || []; } catch { return []; }
  });
  const [notificacoesAbertas, setNotificacoesAbertas] = useState(false);

  const carregarNotificacoes = useCallback(async () => {
    if (!recebeNotificacoes) return;
    try {
      const [historico, ordens] = await Promise.all([
        apiRequest("/oficina/historico-status-ordens/"),
        apiRequest("/oficina/ordens-servico/"),
      ]);
      const ordensPorId = new Map(extrairLista(ordens).map((ordem) => [ordem.id, ordem]));
      const eventos = extrairLista(historico)
        .filter((evento) => evento.novo_status === "EM_EXECUCAO" && evento.status_anterior === "AGUARDANDO_APROVACAO")
        .slice(0, 8)
        .map((evento) => ({
          ...evento,
          numeroOrdem: ordensPorId.get(evento.ordem_servico)?.numero || `OS #${evento.ordem_servico}`,
        }));
      setNotificacoes(eventos);
    } catch {
      // O cabeçalho continua funcional caso o servidor esteja temporariamente indisponível.
    }
  }, [recebeNotificacoes]);

  useEffect(() => {
    carregarNotificacoes();
    const atualizacao = setInterval(carregarNotificacoes, 30000);
    return () => clearInterval(atualizacao);
  }, [carregarNotificacoes]);

  const naoLidas = useMemo(() => notificacoes.filter((item) => !lidas.includes(item.id)), [notificacoes, lidas]);

  function alternarNotificacoes() {
    const abrir = !notificacoesAbertas;
    setNotificacoesAbertas(abrir);
    if (abrir && naoLidas.length) {
      const ids = [...new Set([...lidas, ...notificacoes.map((item) => item.id)])];
      setLidas(ids);
      sessionStorage.setItem(chaveLidas, JSON.stringify(ids));
    }
  }
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" className="brand" aria-label="Ir para o painel"><img className="garage-logo-image" src={garagem66Logo} alt="Garagem 66" /></NavLink>
        <p className="brand-slogan">Sua moto.<br />Seu histórico.<br /><em>Tudo sob controle.</em></p>
        <nav aria-label="Navegação principal">
          <NavLink to="/" end><span className="menu-icon">⌁</span>{usuario.tipo === "CLIENTE" ? "Início" : "Dashboard"}</NavLink>
          {menus.map((menu) => <NavLink key={menu} to={`/${menu}`}><span className="menu-icon">{iconesMenu[menu] ?? "○"}</span>{nomeMenu(menu)}</NavLink>)}
        </nav>
        <div className="sidebar-profile"><span className="avatar">●</span><span><strong>{usuario.nome}</strong><small>{usuario.tipo}</small></span></div>
        <button className="button button-ghost" type="button" onClick={logout}>↪ Sair</button>
      </aside>
      <main className="content">
        <header className="topbar"><button className="menu-trigger" aria-label="Abrir menu">☰</button><div className="topbar-actions">
          {recebeNotificacoes ? <div className="notification-wrap"><button className="notification" type="button" aria-label={`${naoLidas.length} notificações não lidas`} aria-expanded={notificacoesAbertas} onClick={alternarNotificacoes}>♧{naoLidas.length ? <b>{naoLidas.length}</b> : null}</button>
            {notificacoesAbertas ? <div className="notification-panel"><div className="notification-heading"><strong>Atualizações da oficina</strong><small>{naoLidas.length ? `${naoLidas.length} nova(s)` : "Tudo lido"}</small></div>
              {notificacoes.length ? notificacoes.map((item) => <Link key={item.id} to={usuario.tipo === "MECANICO" ? "/minhas-ordens" : "/ordens"} onClick={() => setNotificacoesAbertas(false)}><span className="notification-dot">✓</span><span><strong>Orçamento aprovado</strong><small>{item.numeroOrdem} foi liberada para execução por {item.responsavel_nome || "cliente"}.</small></span></Link>) : <p>Nenhuma aprovação recente.</p>}
            </div> : null}
          </div> : null}
          <span className="avatar">●</span><span><strong>{usuario.nome}</strong><small>{usuario.tipo}</small></span></div></header>
        <Outlet />
      </main>
    </div>
  );
}
