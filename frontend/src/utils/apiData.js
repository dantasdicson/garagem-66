export function extrairLista(dados) {
  if (Array.isArray(dados)) return dados;
  return Array.isArray(dados?.results) ? dados.results : [];
}

