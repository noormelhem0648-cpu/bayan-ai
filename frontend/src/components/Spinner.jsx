export default function Spinner({ label }) {
  return (
    <div className="flex items-center justify-center gap-3 py-10 text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      {label ? <span>{label}</span> : null}
    </div>
  );
}
