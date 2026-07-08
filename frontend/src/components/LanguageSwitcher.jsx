import { useTranslation } from "react-i18next";
import { LANGUAGES } from "../i18n";
import { useAuthStore } from "../store/authStore";
import { api } from "../api/client";

export default function LanguageSwitcher({ compact = false }) {
  const { i18n } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);

  const change = async (code) => {
    i18n.changeLanguage(code);
    // Persist the choice on the account when logged in.
    if (useAuthStore.getState().accessToken) {
      try {
        const updated = await api.patch("/auth/me", { app_language: code });
        setUser(updated);
      } catch {
        /* non-blocking */
      }
    }
  };

  return (
    <select
      aria-label="Language"
      className={`input ${compact ? "w-auto py-1.5" : ""}`}
      value={i18n.language?.split("-")[0] || "ar"}
      onChange={(e) => change(e.target.value)}
    >
      {LANGUAGES.map((l) => (
        <option key={l.code} value={l.code}>
          {l.native}
        </option>
      ))}
    </select>
  );
}
