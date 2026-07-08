import { useTranslation } from "react-i18next";
import { useThemeStore } from "../store/themeStore";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function SettingsPage() {
  const { t } = useTranslation();
  const theme = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-bold">{t("settings.title")}</h1>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold">{t("settings.appearance")}</h2>
        <label className="label">{t("settings.theme")}</label>
        <div className="flex gap-2">
          {["light", "dark"].map((mode) => (
            <button
              key={mode}
              className={theme === mode ? "btn-primary" : "btn-ghost border border-slate-300 dark:border-slate-600"}
              onClick={() => setTheme(mode)}
            >
              {mode === "dark" ? `🌙 ${t("settings.dark")}` : `☀️ ${t("settings.light")}`}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <h2 className="mb-4 text-lg font-semibold">{t("settings.language")}</h2>
        <LanguageSwitcher />
      </div>
    </div>
  );
}
