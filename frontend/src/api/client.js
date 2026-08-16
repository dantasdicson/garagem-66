import { carregarSessao, limparSessao, salvarSessao } from "../services/tokenStorage";

const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api").replace(/\/$/, "");
let renovacaoEmAndamento = null;

async function extrairErro(response) {
  const dados = await response.json().catch(() => null);
  if (dados?.detail) return dados.detail;
  if (dados && typeof dados === "object") {
    const primeiraChave = Object.keys(dados)[0];
    const mensagem = dados[primeiraChave];
    return Array.isArray(mensagem) ? mensagem[0] : String(mensagem);
  }
  return "Não foi possível concluir a operação.";
}

async function renovarToken() {
  const sessao = carregarSessao();
  if (!sessao?.refresh) return null;
  const response = await fetch(`${API_URL}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh: sessao.refresh }),
  });
  if (!response.ok) {
    limparSessao();
    return null;
  }
  const tokens = await response.json();
  const novaSessao = { ...sessao, access: tokens.access, refresh: tokens.refresh || sessao.refresh };
  salvarSessao(novaSessao);
  return novaSessao.access;
}

async function obterNovoToken() {
  if (!renovacaoEmAndamento) {
    renovacaoEmAndamento = renovarToken().finally(() => {
      renovacaoEmAndamento = null;
    });
  }
  return renovacaoEmAndamento;
}

export async function apiRequest(caminho, opcoes = {}, repetir = true) {
  const sessao = carregarSessao();
  const headers = new Headers(opcoes.headers);
  if (!(opcoes.body instanceof FormData)) headers.set("Content-Type", "application/json");
  if (sessao?.access) headers.set("Authorization", `Bearer ${sessao.access}`);

  const response = await fetch(`${API_URL}${caminho}`, { cache: "no-store", ...opcoes, headers });
  if (response.status === 401 && repetir && sessao?.refresh) {
    const novoToken = await obterNovoToken();
    if (novoToken) return apiRequest(caminho, opcoes, false);
  }
  if (!response.ok) throw new Error(await extrairErro(response));
  if (response.status === 204) return null;
  return response.json();
}

export { API_URL };
