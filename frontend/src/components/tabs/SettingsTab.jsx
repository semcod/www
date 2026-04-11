import { useState, useEffect } from "react";
import { fetchSchedules } from "../../api";
import { SectionHeader, BillingSection, SchedulesSection } from "./SettingsTab.parts";

export function SettingsTab({ sessionToken, billingStatus }) {
  const [schedules, setSchedules] = useState([]);
  const [loadingSchedules, setLoadingSchedules] = useState(true);

  const loadSchedules = () => {
    if (!sessionToken) return;
    setLoadingSchedules(true);
    fetchSchedules(sessionToken)
      .then(setSchedules)
      .catch(() => setSchedules([]))
      .finally(() => setLoadingSchedules(false));
  };

  useEffect(() => { loadSchedules(); }, [sessionToken]);

  return (
    <div style={{ maxWidth: 720, margin: "60px auto" }}>
      <h3 style={{ margin: "0 0 32px 0", fontSize: 20, fontWeight: 700 }}>Settings</h3>
      <BillingSection sessionToken={sessionToken} billingStatus={billingStatus} />
      <SchedulesSection
        sessionToken={sessionToken}
        schedules={schedules}
        loading={loadingSchedules}
        onReload={loadSchedules}
      />
    </div>
  );
}
