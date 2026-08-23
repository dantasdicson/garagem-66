import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import garagem66Logo from "../assets/garagem-66-logo.png";

export default function LoginPage() {
  const { autenticado, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  if (autenticado) return <Navigate to="/" replace />;

  async function handleSubmit(event) {
    event.preventDefault(); setErro(""); setEnviando(true);
    try {
      const usuario = await login(form.username.trim(), form.password);
      navigate(usuario.deve_alterar_senha ? "/alterar-senha" : location.state?.from?.pathname || "/", { replace: true });
    } catch (error) { setErro(error.message); } finally { setEnviando(false); }
  }

  return (
    <main className="auth-page">
      <section className="auth-showcase" aria-label="Garagem 66">
        <img className="garage-logo-image garage-logo-image-large" src={garagem66Logo} alt="Garagem 66" />
        <h2>Sua moto.<br />Seu histórico.<br /><em>Tudo sob controle.</em></h2>
        <p>Sistema de gerenciamento completo para oficinas de motos.</p>
      </section>
      <section className="auth-card" aria-labelledby="login-title">
        <h1 id="login-title">Acesse sua conta</h1><p className="auth-subtitle">Garagem 66</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Usuário ou e-mail</label>
          <input id="username" placeholder="Digite seu usuário ou e-mail" autoComplete="username" required value={form.username} onChange={(event) => setForm((atual) => ({ ...atual, username: event.target.value }))} />
          <label htmlFor="password">Senha</label>
          <input id="password" placeholder="Digite sua senha" type="password" autoComplete="current-password" required value={form.password} onChange={(event) => setForm((atual) => ({ ...atual, password: event.target.value }))} />
          {erro ? <p className="form-error" role="alert">{erro}</p> : null}
          <button className="button button-primary" disabled={enviando} type="submit">{enviando ? "Entrando..." : "Entrar"}</button>
        </form>
        <aside className="demo-access"><strong>ⓘ Primeiro acesso</strong><p>Sua senha inicial é sua data de nascimento no formato DDMMAAAA.</p>
          <details><summary>Acessos para demonstração</summary><p>Senha: <code>Garagem66@Demo</code></p>
            <dl className="demo-users"><div><dt>Administrador — Renato Almeida</dt><dd>renato.almeida</dd></div><div><dt>Atendente — Camila Rocha</dt><dd>camila.rocha</dd></div><div><dt>Mecânico — Bruno Martins</dt><dd>bruno.martins</dd></div><div><dt>Cliente — Mariana Costa</dt><dd>11144477735</dd></div></dl>
          </details>
        </aside>
      </section>
    </main>
  );
}
