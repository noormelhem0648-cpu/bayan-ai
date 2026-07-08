import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../store/authStore";
import LanguageSwitcher from "./LanguageSwitcher";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const doLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-700 dark:bg-slate-900/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
        <Link to="/" className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-brand-600 text-lg font-bold text-white">
            ب
          </span>
          <div className="leading-tight">
            <div className="font-bold text-brand-700 dark:text-brand-300">
              {t("app.name")}
            </div>
            <div className="hidden text-xs text-slate-500 sm:block">
              {t("app.tagline")}
            </div>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-2">
          {user?.role === "instructor" || user?.role === "admin" ? (
            <Link className="btn-ghost hidden sm:inline-flex" to="/instructor">
              {t("nav.instructor")}
            </Link>
          ) : null}
          {user?.role === "admin" ? (
            <Link className="btn-ghost hidden sm:inline-flex" to="/admin">
              {t("nav.admin")}
            </Link>
          ) : null}
          <Link className="btn-ghost hidden sm:inline-flex" to="/settings">
            {t("nav.settings")}
          </Link>
          <LanguageSwitcher compact />
          <ThemeToggle />
          {user ? (
            <button className="btn-primary" onClick={doLogout}>
              {t("nav.logout")}
            </button>
          ) : (
            <Link className="btn-primary" to="/login">
              {t("auth.signIn")}
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
