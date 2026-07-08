import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { api } from "../api/client";
import { localized } from "../lib/i18nContent";
import ChoiceGrid from "../components/ChoiceGrid";
import Spinner from "../components/Spinner";
import BackBar from "../components/BackBar";

export default function SubjectsPage() {
  const { yearId } = useParams();
  const { t, i18n } = useTranslation();
  const lang = i18n.language?.split("-")[0] || "ar";
  const [subjects, setSubjects] = useState(null);

  useEffect(() => {
    api
      .get(`/catalog/subjects?year_id=${yearId}`)
      .then(setSubjects)
      .catch(() => setSubjects([]));
  }, [yearId]);

  if (!subjects) return <Spinner label={t("common.loading")} />;

  const items = subjects.map((s) => ({
    key: s.id,
    to: `/subject/${s.id}`,
    label: localized(s.name_i18n, lang),
    description: localized(s.description_i18n, lang, ""),
    icon: "📗",
  }));

  return (
    <>
      <BackBar />
      <ChoiceGrid title={t("flow.chooseSubject")} items={items} />
    </>
  );
}
