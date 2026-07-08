import { useNavigate } from "react-router-dom";

// Reusable responsive grid of clickable cards used across the catalog flow.
export default function ChoiceGrid({ title, subtitle, items }) {
  const navigate = useNavigate();
  return (
    <section>
      {title && <h1 className="mb-1 text-2xl font-bold sm:text-3xl">{title}</h1>}
      {subtitle && <p className="mb-6 text-slate-500">{subtitle}</p>}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((it) => (
          <button
            key={it.key}
            onClick={() => navigate(it.to)}
            className="card group text-start transition hover:-translate-y-0.5 hover:border-brand-400 hover:shadow-md"
          >
            <div className="mb-3 grid h-12 w-12 place-items-center rounded-xl bg-brand-100 text-2xl dark:bg-brand-900/40">
              {it.icon || "📘"}
            </div>
            <div className="text-lg font-semibold">{it.label}</div>
            {it.description && (
              <div className="mt-1 text-sm text-slate-500">{it.description}</div>
            )}
          </button>
        ))}
      </div>
    </section>
  );
}
