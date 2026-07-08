import { create } from "zustand";
import { persist } from "zustand/middleware";

function apply(theme) {
  const root = document.documentElement;
  if (theme === "dark") root.classList.add("dark");
  else root.classList.remove("dark");
}

export const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: "light",
      setTheme: (theme) => {
        apply(theme);
        set({ theme });
      },
      toggle: () => {
        const next = get().theme === "dark" ? "light" : "dark";
        apply(next);
        set({ theme: next });
      },
      init: () => apply(get().theme),
    }),
    { name: "bayan.theme" }
  )
);
