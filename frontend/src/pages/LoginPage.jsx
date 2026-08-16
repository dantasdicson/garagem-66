import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

export default function LoginPage() {
  const { autenticado, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  if (autenticado) return <Navigate to="/" replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setErro("");
    setEnviando(true);
    try {
      const usuario = await login(form.username.trim(), form.password);
      const destino = usuario.deve_alterar_senha ? "/alterar-senha" : location.state?.from?.pathname || "/";
      navigate(destino, { replace: true });
    } catch (error) {
      setErro(error.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="login-title">
        <div className="brand brand-dark"><span className="brand-mark">66</span><span>Garagem 66</span></div>
        <p className="eyebrow">Oficina de motocicletas</p>
        <h1 id="login-title">Acesse sua conta</h1>
        <p className="muted">Entre com seu usuário e senha para acompanhar a oficina.</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Usuário</label>
          <input id="username" autoComplete="username" required value={form.username}
            onChange={(event) => setForm((atual) => ({ ...atual, username: event.target.value }))} />
          <label htmlFor="password">Senha</label>
          <input id="password" type="password" autoComplete="current-password" required value={form.password}
            onChange={(event) => setForm((atual) => ({ ...atual, password: event.target.value }))} />
          {erro ? <p className="form-error" role="alert">{erro}</p> : null}
          <button className="button button-primary" disabled={enviando} type="submit">
            {enviando ? "Entrando..." : "Entrar"}
          </button>
        </form>
        <aside className="demo-access" aria-label="Credenciais para demonstração">
          <strong>Acesso para demonstração</strong>
          <p>Senha para todos: <code>Garagem66@Demo</code></p>
          <dl>
            <div><dt>Administrador</dt><dd>admin.demo</dd></div>
            <div><dt>Atendente</dt><dd>atendente.demo</dd></div>
            <div><dt>Mecânico</dt><dd>mecanico.demo</dd></div>
            <div><dt>Cliente</dt><dd>52998224725</dd></div>
          </dl>
        </aside>
      </section>
    </main>
  );
}
