import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";
import { useAuthStore } from "../store/authStore";

export default function ProfilePage() {
  const { t } = useTranslation();
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);

  const [name, setName] = useState(user?.name || "");
  const [pwd, setPwd] = useState({ current_password: "", new_password: "" });
  const [msg, setMsg] = useState("");

  const saveProfile = async () => {
    const updated = await api.patch("/auth/me", { name });
    setUser(updated);
    setMsg(t("settings.saved"));
  };

  const changePassword = async () => {
    setMsg("");
    try {
      await api.post("/auth/me/change-password", pwd);
      setPwd({ current_password: "", new_password: "" });
      setMsg(t("settings.saved"));
    } catch (e) {
      setMsg(e.message);
    }
  };

  return (
    <div className="mx-auto max-w-xl space-y-6">
      <h1 className="text-2xl font-bold">{t("profile.title")}</h1>

      <div className="card space-y-4">
        <div>
          <label className="label">{t("profile.name")}</label>
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label className="label">{t("profile.email")}</label>
          <input className="input" value={user?.email || ""} disabled />
        </div>
        <button className="btn-primary" onClick={saveProfile}>
          {t("common.save")}
        </button>
      </div>

      <div className="card space-y-4">
        <h2 className="text-lg font-semibold">{t("profile.changePassword")}</h2>
        <div>
          <label className="label">{t("profile.current")}</label>
          <input
            type="password"
            className="input"
            value={pwd.current_password}
            onChange={(e) => setPwd({ ...pwd, current_password: e.target.value })}
          />
        </div>
        <div>
          <label className="label">{t("profile.new")}</label>
          <input
            type="password"
            className="input"
            value={pwd.new_password}
            onChange={(e) => setPwd({ ...pwd, new_password: e.target.value })}
          />
        </div>
        <button className="btn-primary" onClick={changePassword}>
          {t("profile.update")}
        </button>
      </div>

      {msg && <div className="text-center text-sm text-brand-600">{msg}</div>}
    </div>
  );
}
