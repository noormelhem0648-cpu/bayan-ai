import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";
import { localized } from "../lib/i18nContent";

export default function InstructorPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language?.split("-")[0] || "ar";

  const [stats, setStats] = useState(null);
  const [restrictions, setRestrictions] = useState([]);

  // Cascading subject picker.
  const [tracks, setTracks] = useState([]);
  const [majors, setMajors] = useState([]);
  const [years, setYears] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [sel, setSel] = useState({ track: "", major: "", year: "", subject: "" });

  const [books, setBooks] = useState([]);
  const [bookForm, setBookForm] = useState({ title: "", author: "", file: null });
  const [note, setNote] = useState("");
  const [restForm, setRestForm] = useState({ reason: "", starts_at: "", ends_at: "" });

  const refresh = () => {
    api.get("/instructor/stats").then(setStats).catch(() => {});
    api.get("/restrictions").then(setRestrictions).catch(() => {});
  };

  useEffect(() => {
    refresh();
    api.get("/catalog/tracks").then(setTracks).catch(() => {});
  }, []);

  const onTrack = (id) => {
    setSel({ track: id, major: "", year: "", subject: "" });
    setMajors([]); setYears([]); setSubjects([]);
    if (id) api.get(`/catalog/majors?track_id=${id}`).then(setMajors);
  };
  const onMajor = (id) => {
    setSel((s) => ({ ...s, major: id, year: "", subject: "" }));
    setYears([]); setSubjects([]);
    if (id) api.get(`/catalog/years?major_id=${id}`).then(setYears);
  };
  const onYear = (id) => {
    setSel((s) => ({ ...s, year: id, subject: "" }));
    setSubjects([]);
    if (id) api.get(`/catalog/subjects?year_id=${id}`).then(setSubjects);
  };
  const onSubject = (id) => {
    setSel((s) => ({ ...s, subject: id }));
    if (id) api.get(`/instructor/subjects/${id}/books`).then(setBooks);
  };

  const uploadBook = async (e) => {
    e.preventDefault();
    if (!sel.subject || !bookForm.file) return;
    const fd = new FormData();
    fd.append("title", bookForm.title);
    if (bookForm.author) fd.append("author", bookForm.author);
    fd.append("file", bookForm.file);
    await api.upload(`/instructor/subjects/${sel.subject}/books`, fd);
    setBookForm({ title: "", author: "", file: null });
    setNote("✅ Uploaded");
    api.get(`/instructor/subjects/${sel.subject}/books`).then(setBooks);
  };

  const reindex = async () => {
    setNote("⏳ Indexing…");
    try {
      const r = await api.post(`/instructor/subjects/${sel.subject}/reindex`);
      setNote(`✅ Indexed ${r.chunk_count} chunks`);
    } catch (e) {
      setNote(`⚠️ ${e.message}`);
    }
  };

  const deleteBook = async (id) => {
    await api.del(`/instructor/books/${id}`);
    api.get(`/instructor/subjects/${sel.subject}/books`).then(setBooks);
  };

  const createRestriction = async (e) => {
    e.preventDefault();
    if (!sel.subject) return;
    await api.post("/restrictions", {
      subject_id: Number(sel.subject),
      reason: restForm.reason || null,
      starts_at: restForm.starts_at || null,
      ends_at: restForm.ends_at || null,
      is_active: true,
    });
    setRestForm({ reason: "", starts_at: "", ends_at: "" });
    refresh();
  };

  const deleteRestriction = async (id) => {
    await api.del(`/restrictions/${id}`);
    refresh();
  };

  const Dropdown = ({ value, onChange, options, placeholder, labelKey }) => (
    <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">{placeholder}</option>
      {options.map((o) => (
        <option key={o.id} value={o.id}>
          {labelKey ? localized(o[labelKey], lang) || o.code : o.code}
        </option>
      ))}
    </select>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{t("nav.instructor")}</h1>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Object.entries(stats).map(([k, v]) => (
            <div key={k} className="card text-center">
              <div className="text-2xl font-bold text-brand-600">{v}</div>
              <div className="text-sm capitalize text-slate-500">{k}</div>
            </div>
          ))}
        </div>
      )}

      {/* Subject picker */}
      <div className="card space-y-3">
        <h2 className="text-lg font-semibold">{t("flow.chooseSubject")}</h2>
        <div className="grid gap-3 sm:grid-cols-4">
          <Dropdown value={sel.track} onChange={onTrack} options={tracks} placeholder="—" labelKey="name_i18n" />
          <Dropdown value={sel.major} onChange={onMajor} options={majors} placeholder="—" labelKey="name_i18n" />
          <Dropdown value={sel.year} onChange={onYear} options={years} placeholder="—" labelKey="name_i18n" />
          <Dropdown value={sel.subject} onChange={onSubject} options={subjects} placeholder="—" labelKey="name_i18n" />
        </div>
      </div>

      {sel.subject && (
        <>
          {/* Books */}
          <div className="card space-y-4">
            <h2 className="text-lg font-semibold">📚 Books</h2>
            <form onSubmit={uploadBook} className="grid gap-3 sm:grid-cols-4 sm:items-end">
              <input
                className="input" placeholder="Title" required
                value={bookForm.title}
                onChange={(e) => setBookForm({ ...bookForm, title: e.target.value })}
              />
              <input
                className="input" placeholder="Author"
                value={bookForm.author}
                onChange={(e) => setBookForm({ ...bookForm, author: e.target.value })}
              />
              <input
                type="file" accept="application/pdf" required
                className="input"
                onChange={(e) => setBookForm({ ...bookForm, file: e.target.files[0] })}
              />
              <button className="btn-primary">{t("common.create")}</button>
            </form>

            <ul className="divide-y divide-slate-200 dark:divide-slate-700">
              {books.map((b) => (
                <li key={b.id} className="flex items-center justify-between py-2">
                  <span>{b.title}{b.author ? ` — ${b.author}` : ""}</span>
                  <button className="text-red-600 hover:underline" onClick={() => deleteBook(b.id)}>
                    {t("common.delete")}
                  </button>
                </li>
              ))}
            </ul>

            <div className="flex items-center gap-3">
              <button className="btn-primary" onClick={reindex} disabled={books.length === 0}>
                🧠 Build / rebuild index
              </button>
              {note && <span className="text-sm text-slate-500">{note}</span>}
            </div>
          </div>

          {/* Restriction */}
          <div className="card space-y-4">
            <h2 className="text-lg font-semibold">🔒 Exam-time block</h2>
            <form onSubmit={createRestriction} className="grid gap-3 sm:grid-cols-4 sm:items-end">
              <input
                className="input" placeholder="Reason"
                value={restForm.reason}
                onChange={(e) => setRestForm({ ...restForm, reason: e.target.value })}
              />
              <div>
                <label className="label text-xs">Start (optional)</label>
                <input
                  type="datetime-local" className="input"
                  value={restForm.starts_at}
                  onChange={(e) => setRestForm({ ...restForm, starts_at: e.target.value })}
                />
              </div>
              <div>
                <label className="label text-xs">End (optional)</label>
                <input
                  type="datetime-local" className="input"
                  value={restForm.ends_at}
                  onChange={(e) => setRestForm({ ...restForm, ends_at: e.target.value })}
                />
              </div>
              <button className="btn-primary">Block</button>
            </form>
          </div>
        </>
      )}

      {/* All restrictions */}
      <div className="card">
        <h2 className="mb-3 text-lg font-semibold">Active & scheduled blocks</h2>
        <ul className="divide-y divide-slate-200 dark:divide-slate-700">
          {restrictions.length === 0 && (
            <li className="py-2 text-sm text-slate-400">—</li>
          )}
          {restrictions.map((r) => (
            <li key={r.id} className="flex items-center justify-between py-2 text-sm">
              <span>
                #{r.subject_id} · {r.reason || "—"}{" "}
                <span className="text-slate-400">
                  {r.starts_at ? `from ${new Date(r.starts_at).toLocaleString()} ` : ""}
                  {r.ends_at ? `to ${new Date(r.ends_at).toLocaleString()}` : ""}
                </span>
              </span>
              <button className="text-red-600 hover:underline" onClick={() => deleteRestriction(r.id)}>
                {t("common.delete")}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
