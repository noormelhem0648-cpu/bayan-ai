import { useNavigate } from "react-router-dom";

// Reusable elegant grid used across the catalog flow.
// Each item: { key, to, label, subtitle?, numeral?, icon?, description? }
export default function ChoiceGrid({ title, subtitle, pill, items }) {
  const navigate = useNavigate();
  return (
    <section>
      <div className="mb-8 text-center">
        {pill && <div className="page-pill">{pill}</div>}
        {title && <h1 className="page-title">{title}</h1>}
        {subtitle && (
          <p className="mx-auto mt-3 max-w-xl text-ink/60 dark:text-slate-400">
            {subtitle}
          </p>
        )}
      </div>

      <div className="mx-auto grid max-w-3xl gap-5 sm:grid-cols-2">
        {items.map((it) => (
          <button
            key={it.key}
            onClick={() => navigate(it.to)}
            className="card flex flex-col items-center justify-center py-8 text-center
                       transition hover:-translate-y-1 hover:border-brand-400
                       hover:shadow-lg"
          >
            <div className="numeral">{it.numeral || it.icon || "•"}</div>
            <div className="text-lg font-bold text-ink dark:text-cream-100">
              {it.label}
            </div>
            {it.subtitle && (
              <div className="mt-1 text-sm text-ink/50 dark:text-slate-400">
                {it.subtitle}
              </div>
            )}
            {it.description && (
              <div className="mt-1 text-sm text-ink/50 dark:text-slate-400">
                {it.description}
              </div>
            )}
          </button>
        ))}
      </div>
    </section>
  );
}
