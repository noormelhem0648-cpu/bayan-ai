import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { api } from "../api/client";
import { localized } from "../lib/i18nContent";
import { toRoman } from "../lib/roman";
import ChoiceGrid from "../components/ChoiceGrid";
import Spinner from "../components/Spinner";
import BackBar from "../components/BackBar";

export default function YearsPage() {
  const { majorId } = useParams();
  const { t, i18n } = useTranslation();
  const lang = i18n.language?.split("-")[0] || "ar";
  const [years, setYears] = useState(null);

  useEffect(() => {
    api.get(`/catalog/years?major_id=${majorId}`).then(setYears).catch(() => setYears([]));
  }, [majorId]);

  if (!years) return <Spinner label={t("common.loading")} />;

  const items = years.map((y) => ({
    key: y.id,
    to: `/year/${y.id}`,
    numeral: toRoman(y.number),
    label: localized(y.name_i18n, lang) || `${t("flow.year")} ${y.number}`,
    subtitle: lang === "en" ? "" : y.name_i18n?.en,
  }));

  return (
    <>
      <BackBar />
      <ChoiceGrid title={t("flow.chooseYear")} items={items} />
    </>
  );
}
