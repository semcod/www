import { useState } from "react";
import { C } from "../../constants";
import { fetchBillingPortal, deleteSchedule } from "../../api";
import { ScheduleRow } from "./ScheduleRow";
import { AddScheduleForm } from "./AddScheduleForm";

export function SectionHeader({ title }) {
  return (
    <h4 style={{ fontSize: 15, fontWeight: 700, color: C.fg1, margin: "0 0 16px 0", borderBottom: `1px solid ${C.border}`, paddingBottom: 10 }}>
      {title}
    </h4>
  );
}

export function BillingSection({ sessionToken, billingStatus }) {
  const [portalLoading, setPortalLoading] = useState(false);

  const plan = billingStatus?.plan || "free";
  const planColor = getPlanColor(plan);

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

  return (
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
          <BillingPortalButton onClick={handleBillingPortal} loading={portalLoading} />
        )}
      </div>
    </div>
  );
}

function getPlanColor(plan) {
  if (plan === "pro") return C.cyan;
  if (plan === "team") return "#8B5CF6";
  return C.fg3;
}

function BillingPortalButton({ onClick, loading }) {
  return (
    <button onClick={onClick} disabled={loading} style={{
      background: C.bg3, border: `1px solid ${C.border}`, color: C.fg1,
      padding: "8px 16px", borderRadius: 6, cursor: "pointer", fontSize: 13, fontFamily: "inherit",
    }}>{loading ? "Opening…" : "Manage Subscription →"}</button>
  );
}

export function SchedulesSection({ sessionToken, schedules, loading, onReload }) {
  const [showAddForm, setShowAddForm] = useState(false);

  const handleDelete = async (owner, repo) => {
    await deleteSchedule(owner, repo, sessionToken);
    onReload();
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <SectionHeader title="Scheduled Scans" />
        <AddScheduleButton show={showAddForm} onToggle={() => setShowAddForm(v => !v)} />
      </div>

      {showAddForm && (
        <div style={{ marginBottom: 12 }}>
          <AddScheduleForm sessionToken={sessionToken} onAdded={() => { setShowAddForm(false); onReload(); }} />
        </div>
      )}

      <SchedulesList schedules={schedules} loading={loading} onDelete={handleDelete} />
    </div>
  );
}

function AddScheduleButton({ show, onToggle }) {
  return (
    <button onClick={onToggle} style={{
      background: show ? C.bg3 : C.cyan, border: "none", color: "#fff",
      padding: "6px 14px", borderRadius: 6, cursor: "pointer", fontSize: 12,
      fontFamily: "inherit", fontWeight: 600, marginTop: -16,
    }}>{show ? "Cancel" : "+ Add"}</button>
  );
}

function SchedulesList({ schedules, loading, onDelete }) {
  if (loading) {
    return <div style={{ fontSize: 13, color: C.fg3 }}>Loading schedules…</div>;
  }

  if (schedules.length === 0) {
    return <div style={{ fontSize: 13, color: C.fg3, padding: "20px 0" }}>No scheduled scans yet. Add one above.</div>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {schedules.map(s => (
        <ScheduleRow key={s.repo} schedule={s} onDelete={onDelete} />
      ))}
    </div>
  );
}
