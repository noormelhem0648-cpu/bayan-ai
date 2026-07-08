# Bayan AI — Frontend (React + Vite)

Multilingual (9 languages), RTL/LTR, dark/light SPA.

## Run
```bash
npm install
cp .env.example .env         # set VITE_API_BASE_URL if backend isn't on :8000
npm run dev                  # http://localhost:5173
npm run build                # production build → dist/
```

## Structure
```
src/
├── i18n/            i18next config + locales/<code>/common.json (9 languages)
├── store/           Zustand: auth, theme
├── api/             fetch client + SSE streaming
├── lib/             localized() helper for DB-driven name_i18n
├── components/      Navbar, Layout, ChoiceGrid, QuizModal, LanguageSwitcher…
└── pages/           Auth, Home(tracks) → Majors → Years → Subjects → Chat,
                     Settings, Profile, Instructor, Admin
```

## i18n rules
- No hard-coded UI strings — everything goes through `t()` / locale JSON.
- Direction (`rtl`/`ltr`) is derived from the language and applied to `<html dir>`.
- DB-driven catalog names use `name_i18n` maps resolved by `localized()`.
- The AI answers in the user's chosen application language (enforced server-side).

## Deploy (Vercel)
Import the `frontend/` directory; `vercel.json` sets the build + SPA rewrite.
Set `VITE_API_BASE_URL` to your Render backend URL.
