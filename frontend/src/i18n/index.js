import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";

import ar from "./locales/ar/common.json";
import en from "./locales/en/common.json";
import ms from "./locales/ms/common.json";
import id from "./locales/id/common.json";
import zh from "./locales/zh/common.json";
import am from "./locales/am/common.json";
import th from "./locales/th/common.json";
import ko from "./locales/ko/common.json";
import ru from "./locales/ru/common.json";

// Central language registry — direction drives RTL/LTR everywhere.
export const LANGUAGES = [
  { code: "ar", native: "العربية", dir: "rtl" },
  { code: "en", native: "English", dir: "ltr" },
  { code: "ms", native: "Bahasa Melayu", dir: "ltr" },
  { code: "id", native: "Bahasa Indonesia", dir: "ltr" },
  { code: "zh", native: "中文", dir: "ltr" },
  { code: "am", native: "አማርኛ", dir: "rtl" },
  { code: "th", native: "ภาษาไทย", dir: "ltr" },
  { code: "ko", native: "한국어", dir: "ltr" },
  { code: "ru", native: "Русский", dir: "ltr" },
];

export const dirOf = (code) =>
  LANGUAGES.find((l) => l.code === code)?.dir || "ltr";

const resources = {
  ar: { common: ar },
  en: { common: en },
  ms: { common: ms },
  id: { common: id },
  zh: { common: zh },
  am: { common: am },
  th: { common: th },
  ko: { common: ko },
  ru: { common: ru },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    defaultNS: "common",
    supportedLngs: LANGUAGES.map((l) => l.code),
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
      lookupLocalStorage: "bayan.lang",
    },
  });

/** Apply <html lang/dir> whenever the language changes. */
export function applyDocumentDirection(code) {
  const dir = dirOf(code);
  document.documentElement.setAttribute("lang", code);
  document.documentElement.setAttribute("dir", dir);
}

i18n.on("languageChanged", applyDocumentDirection);
applyDocumentDirection(i18n.language);

export default i18n;
