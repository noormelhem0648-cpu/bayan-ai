import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { api } from "../api/client";
import { localized } from "../lib/i18nContent";
import ChoiceGrid from "../components/ChoiceGrid";
import Spinner from "../components/Spinner";
import BackBar from "../components/BackBar";

export default function MajorsPage() {
  const { trackId } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const lang = i18n.language?.split("-")[0] || "ar";
  const [majors, setMajors] = useState(null);

  useEffect(() => {
    api
      .get(`/catalog/majors?track_id=${trackId}`)
      .then((data) => {
        // One program per track → skip this step and go straight to years/levels.
        if (data.length === 1) {
          navigate(`/major/${data[0].id}`, { replace: true });
          return;
        }
        setMajors(data);
      })
      .catch(() => setMajors([]));
  }, [trackId, navigate]);

  if (!majors) return <Spinner label={t("common.loading")} />;

  const items = majors.map((m) => ({
    key: m.id,
    to: `/major/${m.id}`,
    label: localized(m.name_i18n, lang),
    icon: "🎓",
  }));

  return (
    <>
      <BackBar />
      <ChoiceGrid title={t("flow.chooseMajor")} items={items} />
    </>
  );
}
