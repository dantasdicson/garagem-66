const STORAGE_KEY = "garagem66.auth.v1";

function removerSessaoPersistenteAntiga() {
  localStorage.removeItem(STORAGE_KEY);
}

export function carregarSessao() {
  removerSessaoPersistenteAntiga();
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY)) ?? null;
  } catch {
    sessionStorage.removeItem(STORAGE_KEY);
    return null;
  }
}

export function salvarSessao(sessao) {
  removerSessaoPersistenteAntiga();
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(sessao));
}

export function limparSessao() {
  sessionStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem(STORAGE_KEY);
}
