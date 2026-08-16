import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

const menusPorPerfil = {
  ADMINISTRADOR: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque", "usuarios"],
  ATENDENTE: ["clientes", "motocicletas", "ordens", "orcamentos", "estoque"],
  MECANICO: ["minhas-ordens", "requisicoes", "estoque"],
  CLIENTE: ["minhas-motos", "minhas-ordens", "orcamentos", "historico"],
};

function nomeMenu(valor) {
  return valor.replaceAll("-", " ").replace(/\b\w/g, (letra) => letra.toUpperCase());
}

export default function AppLayout() {
  const { usuario, logout } = useAuth();
  const menus = menusPorPerfil[usuario.tipo] ?? [];
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" className="brand" aria-label="Ir para o painel">
          <span className="brand-mark">66</span><span>Garagem 66</span>
        </NavLink>
        <nav aria-label="Navegação principal">
          <NavLink to="/" end>Painel</NavLink>
          {menus.map((menu) => <NavLink key={menu} to={`/${menu}`}>{nomeMenu(menu)}</NavLink>)}
        </nav>
        <button className="button button-ghost" type="button" onClick={logout}>Sair</button>
      </aside>
      <main className="content">
        <header className="topbar">
          <div><span className="eyebrow">{usuario.tipo}</span><strong>{usuario.nome}</strong></div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}
