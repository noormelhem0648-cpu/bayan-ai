import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { api } from "../api/client";
import { useAuthStore } from "../store/authStore";
import { LANGUAGES } from "../i18n";
import LanguageSwitcher from "../components/LanguageSwitcher";
import ThemeToggle from "../components/ThemeToggle";

export default function AuthPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  const [mode, setMode] = useState("login"); // login | register
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    app_language: i18n.language?.split("-")[0] || "ar",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await api.post("/auth/register", form);
        i18n.changeLanguage(form.app_language);
      }
      const tokens = await api.post("/auth/login", {
        email: form.email,
        password: form.password,
      });
      setTokens(tokens);
      const me = await api.get("/auth/me");
      setUser(me);
      if (me.app_language) i18n.changeLanguage(me.app_language);
      navigate("/");
    } catch (err) {
      setError(err.message || t("errors.generic"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Brand panel */}
      <div className="hidden flex-col justify-between bg-brand-700 p-10 text-white lg:flex">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-white/15 text-2xl font-bold">
            ب
          </span>
          <span className="text-xl font-bold">{t("app.name")}</span>
        </div>
        <div>
          <h1 className="text-4xl font-extrabold leading-tight">
            {t("auth.welcome")}
          </h1>
          <p className="mt-4 max-w-md text-brand-100">{t("auth.subtitle")}</p>
        </div>
        <div className="text-sm text-brand-200">© Bayan AI</div>
      </div>

      {/* Form panel */}
      <div className="flex flex-col items-center justify-center p-6">
        <div className="mb-4 flex w-full max-w-md items-center justify-end gap-2">
          <LanguageSwitcher compact />
          <ThemeToggle />
        </div>
        <form onSubmit={submit} className="card w-full max-w-md">
          <h2 className="mb-1 text-2xl font-bold">
            {mode === "login" ? t("auth.login") : t("auth.register")}
          </h2>
          <p className="mb-6 text-sm text-slate-500">{t("app.tagline")}</p>

          {mode === "register" && (
            <div className="mb-4">
              <label className="label">{t("auth.name")}</label>
              <input className="input" value={form.name} onChange={update("name")} required />
            </div>
          )}

          <div className="mb-4">
            <label className="label">{t("auth.email")}</label>
            <input
              type="email"
              className="input"
              value={form.email}
              onChange={update("email")}
              required
            />
          </div>

          <div className="mb-4">
            <label className="label">{t("auth.password")}</label>
            <input
              type="password"
              className="input"
              value={form.password}
              onChange={update("password")}
              minLength={8}
              required
            />
          </div>

          {mode === "register" && (
            <div className="mb-4">
              <label className="label">{t("auth.appLanguage")}</label>
              <select
                className="input"
                value={form.app_language}
                onChange={update("app_language")}
              >
                {LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.native}
                  </option>
                ))}
              </select>
            </div>
          )}

          {error && (
            <div className="mb-4 rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-600 dark:bg-red-900/30 dark:text-red-300">
              {error}
            </div>
          )}

          <button className="btn-primary w-full" disabled={busy}>
            {busy ? t("common.loading") : mode === "login" ? t("auth.signIn") : t("auth.signUp")}
          </button>

          <div className="mt-5 text-center text-sm text-slate-500">
            {mode === "login" ? t("auth.noAccount") : t("auth.haveAccount")}{" "}
            <button
              type="button"
              className="font-semibold text-brand-600 hover:underline"
              onClick={() => {
                setMode(mode === "login" ? "register" : "login");
                setError("");
              }}
            >
              {mode === "login" ? t("auth.signUp") : t("auth.signIn")}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
