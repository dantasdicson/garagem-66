import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { apiRequest } from "../api/client";
import { carregarSessao, limparSessao, salvarSessao } from "../services/tokenStorage";

const AuthContext = createContext(null);

function normalizarUsuario(usuario) {
  const nomeCompleto = [usuario.first_name, usuario.last_name].filter(Boolean).join(" ");
  return { ...usuario, nome: usuario.nome || nomeCompleto || usuario.username };
}

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(() => carregarSessao()?.usuario ?? null);
  const [carregando, setCarregando] = useState(() => Boolean(carregarSessao()?.access));

  const logout = useCallback(() => {
    limparSessao();
    setUsuario(null);
  }, []);

  useEffect(() => {
    if (!carregarSessao()?.access) return;
    apiRequest("/usuarios/me/")
      .then((perfil) => {
        const usuarioAtualizado = normalizarUsuario(perfil);
        const sessao = carregarSessao();
        if (sessao) salvarSessao({ ...sessao, usuario: usuarioAtualizado });
        setUsuario(usuarioAtualizado);
      })
      .catch(logout)
      .finally(() => setCarregando(false));
  }, [logout]);

  const login = useCallback(async (username, password) => {
    const dados = await apiRequest("/auth/token/", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    const usuarioAutenticado = normalizarUsuario(dados.usuario);
    salvarSessao({ access: dados.access, refresh: dados.refresh, usuario: usuarioAutenticado });
    setUsuario(usuarioAutenticado);
    return usuarioAutenticado;
  }, []);

  const alterarSenha = useCallback(async (senhaAtual, novaSenha) => {
    await apiRequest("/usuarios/alterar-senha/", {
      method: "POST",
      body: JSON.stringify({ senha_atual: senhaAtual, nova_senha: novaSenha }),
    });
    setUsuario((atual) => {
      const atualizado = { ...atual, deve_alterar_senha: false };
      const sessao = carregarSessao();
      if (sessao) salvarSessao({ ...sessao, usuario: atualizado });
      return atualizado;
    });
  }, []);

  const valor = useMemo(
    () => ({ usuario, autenticado: Boolean(usuario), carregando, login, logout, alterarSenha }),
    [usuario, carregando, login, logout, alterarSenha],
  );
  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error("useAuth deve ser usado dentro de AuthProvider.");
  return contexto;
}

