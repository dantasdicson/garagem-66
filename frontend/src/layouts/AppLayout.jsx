import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import garagem66Logo from "../assets/garagem-66-logo.png";

const menusPorPerfil = {
  ADMINISTRADOR: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque", "usuarios"],
  ATENDENTE: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque"],
  MECANICO: ["minhas-ordens", "requisicoes", "estoque"],
  CLIENTE: ["minhas-motos", "minhas-ordens", "orcamentos", "historico"],
};
const iconesMenu = { clientes: "♙", motocicletas: "♞", ordens: "▤", orcamentos: "▧", estoque: "◇", usuarios: "♙", "minhas-ordens": "▤", requisicoes: "▱", "minhas-motos": "♞", historico: "◴" };

function nomeMenu(valor) {
  return valor.replaceAll("-", " ").replace(/\b\w/g, (letra) => letra.toUpperCase());
}

export default function AppLayout() {
  const { usuario, logout } = useAuth();
  const menus = menusPorPerfil[usuario.tipo] ?? [];
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
        <header className="topbar"><button className="menu-trigger" aria-label="Abrir menu">☰</button><div className="topbar-actions"><span className="notification">♧<b>3</b></span><span className="avatar">●</span><span><strong>{usuario.nome}</strong><small>{usuario.tipo}</small></span></div></header>
        <Outlet />
      </main>
    </div>
  );
}
