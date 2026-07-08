// Resolve a per-language name_i18n / description_i18n map to the active language,
// falling back gracefully so no label is ever empty.
export function localized(map, lang, fallback = "") {
  if (!map || typeof map !== "object") return fallback;
  return map[lang] || map.ar || map.en || Object.values(map)[0] || fallback;
}
