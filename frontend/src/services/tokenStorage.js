const STORAGE_KEY = "garagem66.auth.v1";

export function carregarSessao() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) ?? null;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function salvarSessao(sessao) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessao));
}

export function limparSessao() {
  localStorage.removeItem(STORAGE_KEY);
}

