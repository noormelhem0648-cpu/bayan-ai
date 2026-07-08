import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { api } from "../api/client";
import { localized } from "../lib/i18nContent";
import ChoiceGrid from "../components/ChoiceGrid";
import Spinner from "../components/Spinner";

const ICONS = { arabic: "📖", "applied-arabic": "🗣️", "non-natives": "🌍" };

export default function HomePage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language?.split("-")[0] || "ar";
  const [tracks, setTracks] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/catalog/tracks")
      .then(setTracks)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="card text-red-600">{error}</div>;
  if (!tracks) return <Spinner label={t("common.loading")} />;

  const items = tracks.map((tr) => ({
    key: tr.id,
    to: `/track/${tr.id}`,
    label: localized(tr.name_i18n, lang),
    subtitle: lang === "en" ? "" : tr.name_i18n?.en,
    icon: ICONS[tr.slug] || "📚",
  }));

  return (
    <ChoiceGrid
      pill={t("app.tagline")}
      title={t("flow.chooseTrack")}
      items={items}
    />
  );
}
