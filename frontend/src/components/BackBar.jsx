import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function BackBar() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  return (
    <button className="btn-ghost mb-4 -ms-2" onClick={() => navigate(-1)}>
      <span className="rtl:rotate-180">←</span> {t("flow.back")}
    </button>
  );
}
