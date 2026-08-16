import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function AlterarSenhaPage() {
  const { alterarSenha, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ atual: "", nova: "", confirmacao: "" });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (form.nova !== form.confirmacao) return setErro("A confirmação não corresponde à nova senha.");
    setErro("");
    setEnviando(true);
    try {
      await alterarSenha(form.atual, form.nova);
      navigate("/", { replace: true });
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="password-title">
        <p className="eyebrow">Primeiro acesso</p>
        <h1 id="password-title">Crie uma nova senha</h1>
        <p className="muted">Por segurança, substitua a senha provisória antes de continuar.</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="current-password">Senha atual</label>
          <input id="current-password" type="password" autoComplete="current-password" required
            onChange={(event) => setForm((atual) => ({ ...atual, atual: event.target.value }))} />
          <label htmlFor="new-password">Nova senha</label>
          <input id="new-password" type="password" autoComplete="new-password" required minLength="8"
            onChange={(event) => setForm((atual) => ({ ...atual, nova: event.target.value }))} />
          <label htmlFor="confirm-password">Confirme a nova senha</label>
          <input id="confirm-password" type="password" autoComplete="new-password" required minLength="8"
            onChange={(event) => setForm((atual) => ({ ...atual, confirmacao: event.target.value }))} />
          {erro ? <p className="form-error" role="alert">{erro}</p> : null}
          <button className="button button-primary" disabled={enviando} type="submit">
            {enviando ? "Salvando..." : "Salvar nova senha"}
          </button>
          <button className="button button-link" type="button" onClick={logout}>Sair da conta</button>
        </form>
      </section>
    </main>
  );
}

