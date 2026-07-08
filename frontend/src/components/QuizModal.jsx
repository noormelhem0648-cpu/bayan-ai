import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";
import Spinner from "./Spinner";

export default function QuizModal({ subjectId, onClose }) {
  const { t } = useTranslation();
  const [difficulty, setDifficulty] = useState("beginner");
  const [count, setCount] = useState(5);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [error, setError] = useState("");
  const [revealed, setRevealed] = useState({});

  const generate = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await api.post("/quiz/generate", {
        subject_id: subjectId,
        difficulty,
        question_type: "mcq",
        count: Number(count),
        topic: topic || null,
      });
      setQuiz(data);
      setRevealed({});
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="card max-h-[85vh] w-full max-w-2xl overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-xl font-bold">{t("quiz.title")}</h3>
          <button className="btn-ghost" onClick={onClose}>
            ✕
          </button>
        </div>

        {!quiz && (
          <div className="space-y-4">
            <div>
              <label className="label">{t("quiz.difficulty")}</label>
              <select
                className="input"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="beginner">{t("quiz.beginner")}</option>
                <option value="intermediate">{t("quiz.intermediate")}</option>
                <option value="advanced">{t("quiz.advanced")}</option>
              </select>
            </div>
            <div>
              <label className="label">{t("quiz.count")}</label>
              <input
                type="number"
                min={1}
                max={20}
                className="input"
                value={count}
                onChange={(e) => setCount(e.target.value)}
              />
            </div>
            <div>
              <label className="label">{t("quiz.topic")}</label>
              <input
                className="input"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>
            {error && <div className="text-sm text-red-600">{error}</div>}
            <button className="btn-primary w-full" onClick={generate} disabled={loading}>
              {loading ? t("common.loading") : t("quiz.generate")}
            </button>
          </div>
        )}

        {loading && quiz === null && <Spinner />}

        {quiz && (
          <div className="space-y-4">
            {quiz.questions.map((q, i) => (
              <div key={i} className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                <div className="font-semibold">
                  {i + 1}. {q.text}
                </div>
                {q.options?.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {q.options.map((opt, j) => (
                      <li key={j} className="text-sm">
                        • {opt}
                      </li>
                    ))}
                  </ul>
                )}
                <button
                  className="mt-2 text-sm font-semibold text-brand-600 hover:underline"
                  onClick={() => setRevealed({ ...revealed, [i]: !revealed[i] })}
                >
                  {revealed[i] ? t("quiz.close") : t("quiz.check")}
                </button>
                {revealed[i] && (
                  <div className="mt-2 rounded-lg bg-brand-50 p-3 text-sm dark:bg-brand-900/30">
                    <div className="font-semibold text-brand-700 dark:text-brand-300">
                      ✅ {q.answer}
                    </div>
                    {q.explanation && <div className="mt-1">{q.explanation}</div>}
                  </div>
                )}
              </div>
            ))}
            <button className="btn-ghost w-full" onClick={() => setQuiz(null)}>
              ↺ {t("quiz.generate")}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
