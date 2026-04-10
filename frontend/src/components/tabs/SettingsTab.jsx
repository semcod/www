import { useState, useEffect } from "react";
import { C } from "../../constants";
import { fetchSchedules, deleteSchedule, fetchBillingPortal } from "../../api";
import { ScheduleRow } from "./ScheduleRow";
import { AddScheduleForm } from "./AddScheduleForm";

function SectionHeader({ title }) {
  return (
    <h4 style={{ fontSize: 15, fontWeight: 700, color: C.fg1, margin: "0 0 16px 0", borderBottom: `1px solid ${C.border}`, paddingBottom: 10 }}>
      {title}
    </h4>
  );
}

export function SettingsTab({ sessionToken, billingStatus }) {
  const [schedules, setSchedules] = useState([]);
  const [loadingSchedules, setLoadingSchedules] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const loadSchedules = () => {
    if (!sessionToken) return;
    setLoadingSchedules(true);
    fetchSchedules(sessionToken)
      .then(setSchedules)
      .catch(() => setSchedules([]))
      .finally(() => setLoadingSchedules(false));
  };

  useEffect(() => { loadSchedules(); }, [sessionToken]);

  const handleDelete = async (owner, repo) => {
    await deleteSchedule(owner, repo, sessionToken);
    loadSchedules();
  };

  const handleBillingPortal = async () => {
    setPortalLoading(true);
    try {
      const { url } = await fetchBillingPortal(sessionToken);
      window.open(url, "_blank");
    } catch (e) {
      alert("Billing portal unavailable: " + e.message);
    } finally {
      setPortalLoading(false);
    }
  };

  const plan = billingStatus?.plan || "free";
  const planColor = plan === "pro" ? C.cyan : plan === "team" ? "#8B5CF6" : C.fg3;

  return (
    <div style={{ maxWidth: 720, margin: "60px auto" }}>
      <h3 style={{ margin: "0 0 32px 0", fontSize: 20, fontWeight: 700 }}>Settings</h3>

      <div style={{ marginBottom: 32 }}>
        <SectionHeader title="Billing" />
        <div style={{ display: "flex", alignItems: "center", gap: 16, padding: "14px 16px", background: C.bg2, borderRadius: 8, border: `1px solid ${C.border}` }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, color: C.fg3 }}>Current plan</div>
            <div style={{ fontSize: 18, fontWeight: 700, color: planColor, textTransform: "capitalize" }}>{plan}</div>
            {billingStatus && (
              <div style={{ fontSize: 11, color: C.fg3, marginTop: 2 }}>
                {billingStatus.scans_used ?? 0} / {billingStatus.scans_limit ?? "∞"} scans used
              </div>
            )}
          </div>
          {sessionToken && (
            <button onClick={handleBillingPortal} disabled={portalLoading} style={{
              background: C.bg3, border: `1px solid ${C.border}`, color: C.fg1,
              padding: "8px 16px", borderRadius: 6, cursor: "pointer", fontSize: 13, fontFamily: "inherit",
            }}>{portalLoading ? "Opening…" : "Manage Subscription →"}</button>
          )}
        </div>
      </div>

      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <SectionHeader title="Scheduled Scans" />
          <button onClick={() => setShowAddForm(v => !v)} style={{
            background: showAddForm ? C.bg3 : C.cyan, border: "none", color: "#fff",
            padding: "6px 14px", borderRadius: 6, cursor: "pointer", fontSize: 12,
            fontFamily: "inherit", fontWeight: 600, marginTop: -16,
          }}>{showAddForm ? "Cancel" : "+ Add"}</button>
        </div>

        {showAddForm && (
          <div style={{ marginBottom: 12 }}>
            <AddScheduleForm sessionToken={sessionToken} onAdded={() => { setShowAddForm(false); loadSchedules(); }} />
          </div>
        )}

        {loadingSchedules ? (
          <div style={{ fontSize: 13, color: C.fg3 }}>Loading schedules…</div>
        ) : schedules.length === 0 ? (
          <div style={{ fontSize: 13, color: C.fg3, padding: "20px 0" }}>No scheduled scans yet. Add one above.</div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {schedules.map(s => (
              <ScheduleRow key={s.repo} schedule={s} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
