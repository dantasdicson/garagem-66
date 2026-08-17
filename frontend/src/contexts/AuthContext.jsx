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
  const [mensagemCarregamento, setMensagemCarregamento] = useState("Validando sua sessão...");

  const logout = useCallback(() => {
    limparSessao();
    setUsuario(null);
  }, []);

  useEffect(() => {
    if (!carregarSessao()?.access) return;

    let ativo = true;
    let controller;
    const pausas = [0, 2000, 4000, 6000];
    const aguardar = (tempo) => new Promise((resolve) => setTimeout(resolve, tempo));
    const erroDeConexao = (erro) => erro?.name === "AbortError" || erro instanceof TypeError;

    async function validarSessao() {
      try {
        for (let tentativa = 0; tentativa < pausas.length; tentativa += 1) {
          if (pausas[tentativa]) await aguardar(pausas[tentativa]);
          if (!ativo) return;

          if (tentativa > 0) setMensagemCarregamento("Servidor iniciando... tentando novamente.");
          controller = new AbortController();
          const limite = setTimeout(() => controller.abort(), 20000);

          try {
            const perfil = await apiRequest("/usuarios/me/", { signal: controller.signal });
            const usuarioAtualizado = normalizarUsuario(perfil);
            const sessao = carregarSessao();
            if (sessao) salvarSessao({ ...sessao, usuario: usuarioAtualizado });
            if (ativo) setUsuario(usuarioAtualizado);
            return;
          } catch (erro) {
            const ultimaTentativa = tentativa === pausas.length - 1;
            if (!erroDeConexao(erro) || ultimaTentativa) throw erro;
            if (ativo) setMensagemCarregamento("Servidor iniciando... tentando novamente.");
          } finally {
            clearTimeout(limite);
          }
        }
      } catch {
        if (ativo) logout();
      } finally {
        if (ativo) setCarregando(false);
      }
    }

    const avisoServidor = setTimeout(() => {
      if (ativo) setMensagemCarregamento("Servidor iniciando... aguarde um momento.");
    }, 1500);

    validarSessao();
    return () => {
      ativo = false;
      clearTimeout(avisoServidor);
      controller?.abort();
    };
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
    () => ({ usuario, autenticado: Boolean(usuario), carregando, mensagemCarregamento, login, logout, alterarSenha }),
    [usuario, carregando, mensagemCarregamento, login, logout, alterarSenha],
  );
  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) throw new Error("useAuth deve ser usado dentro de AuthProvider.");
  return contexto;
}
