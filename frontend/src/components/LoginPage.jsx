import React, { useState } from "react";
import { Flame, LogIn, UserPlus, RefreshCw } from "lucide-react";
import { api, apiError, setToken } from "../api";

export default function LoginPage({ onLoggedIn, registrationOpen = true }) {
  const [mode, setMode] = useState("login"); // login | register
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res =
        mode === "login"
          ? await api.post("/auth/login", { email, password })
          : await api.post("/auth/register", { name, email, password });
      setToken(res.data.token);
      onLoggedIn(res.data.user);
    } catch (err) {
      setError(apiError(err, mode === "login" ? "Login failed." : "Registration failed."));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-screen">
      <form className="studio-card auth-card" onSubmit={submit}>
        <div className="auth-brand">
          <div className="brand-icon-box">
            <Flame size={22} className="text-purple-400" />
          </div>
          <div className="brand-main-title">
            Ad<span>spire</span>
          </div>
        </div>
        <h2>{mode === "login" ? "Welcome back" : "Create your account"}</h2>
        <p className="hint-text">
          {mode === "login" ? "Log in to generate and save campaigns." : "Your campaigns and brands are private to your account."}
        </p>

        {mode === "register" && (
          <div className="custom-form-group">
            <label>NAME</label>
            <input className="modern-input" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" required minLength={2} />
          </div>
        )}
        <div className="custom-form-group">
          <label>EMAIL</label>
          <input className="modern-input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" required />
        </div>
        <div className="custom-form-group">
          <label>PASSWORD</label>
          <input
            className="modern-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            required
            minLength={mode === "register" ? 8 : 1}
          />
          {mode === "register" && <span className="hint-text">At least 8 characters.</span>}
        </div>

        {error && <div className="warning-banner">{error}</div>}

        <button className="action-btn-glow" type="submit" disabled={busy}>
          {busy ? <RefreshCw size={18} className="spin-animation" /> : mode === "login" ? <LogIn size={18} /> : <UserPlus size={18} />}
          <span>{mode === "login" ? "Log In" : "Create Account"}</span>
        </button>

        {(registrationOpen || mode === "register") && <p className="auth-switch">
          {mode === "login" ? "New here?" : "Already have an account?"}{" "}
          <button type="button" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); }}>
            {mode === "login" ? "Create an account" : "Log in"}
          </button>
        </p>}
        {!registrationOpen && mode === "login" && <p className="hint-text center">New sign-ups are closed. Ask an administrator for an account.</p>}
      </form>
    </div>
  );
}
