import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";

const ROLES = ["student", "instructor", "admin"];

export default function AdminPage() {
  const { t } = useTranslation();
  const [users, setUsers] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [usage, setUsage] = useState(null);

  const load = () => {
    api.get("/admin/users").then(setUsers).catch(() => {});
    api.get("/admin/languages").then(setLanguages).catch(() => {});
    api.get("/admin/ai-usage").then(setUsage).catch(() => {});
  };

  useEffect(load, []);

  const setRole = async (id, role) => {
    await api.patch(`/admin/users/${id}/role?role=${role}`);
    load();
  };
  const setActive = async (id, isActive) => {
    await api.patch(`/admin/users/${id}/active?is_active=${isActive}`);
    load();
  };
  const toggleLanguage = async (lang) => {
    await api.post("/admin/languages", { ...lang, is_active: !lang.is_active });
    load();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t("nav.admin")}</h1>

      {usage && (
        <div className="grid grid-cols-2 gap-4">
          <div className="card text-center">
            <div className="text-2xl font-bold text-brand-600">{usage.total_tokens}</div>
            <div className="text-sm text-slate-500">AI tokens</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-bold text-brand-600">{usage.events}</div>
            <div className="text-sm text-slate-500">AI events</div>
          </div>
        </div>
      )}

      {/* Users */}
      <div className="card overflow-x-auto">
        <h2 className="mb-3 text-lg font-semibold">Users</h2>
        <table className="w-full text-sm">
          <thead className="text-start text-slate-500">
            <tr>
              <th className="p-2 text-start">Name</th>
              <th className="p-2 text-start">Email</th>
              <th className="p-2 text-start">Role</th>
              <th className="p-2 text-start">Active</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t border-slate-200 dark:border-slate-700">
                <td className="p-2">{u.name}</td>
                <td className="p-2">{u.email}</td>
                <td className="p-2">
                  <select
                    className="input py-1"
                    value={u.role}
                    onChange={(e) => setRole(u.id, e.target.value)}
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </td>
                <td className="p-2">
                  <button
                    className={u.is_verified ? "text-brand-600" : "text-slate-400"}
                    onClick={() => setActive(u.id, true)}
                    title="Toggle active"
                  >
                    ●
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Languages */}
      <div className="card">
        <h2 className="mb-3 text-lg font-semibold">Languages</h2>
        <div className="flex flex-wrap gap-2">
          {languages.map((l) => (
            <button
              key={l.code}
              onClick={() => toggleLanguage(l)}
              className={`rounded-full px-3 py-1.5 text-sm ${
                l.is_active
                  ? "bg-brand-600 text-white"
                  : "bg-slate-200 text-slate-500 dark:bg-slate-700"
              }`}
            >
              {l.native_name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
