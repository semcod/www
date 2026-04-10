import { useState } from "react";
import { C } from "../../constants";

export function ScheduleRow({ schedule, onDelete }) {
  const [deleting, setDeleting] = useState(false);
  const [owner, repo] = schedule.repo.includes("/") ? schedule.repo.split("/") : [schedule.repo, schedule.repo];

  const handleDelete = async () => {
    setDeleting(true);
    try { await onDelete(owner, repo); }
    finally { setDeleting(false); }
  };

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px", background: C.bg2, borderRadius: 8, border: `1px solid ${C.border}` }}>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: C.fg1 }}>{schedule.repo}</div>
        <div style={{ fontSize: 11, color: C.fg3, marginTop: 2 }}>
          Every {schedule.interval_hours}h · Next: {schedule.next_run ? new Date(schedule.next_run).toLocaleString() : "—"}
          {schedule.webhook_url && <span style={{ marginLeft: 8 }}>🔔 webhook</span>}
        </div>
      </div>
      <button onClick={handleDelete} disabled={deleting} style={{
        background: "#EF444420", border: "1px solid #EF4444", color: "#EF4444",
        padding: "5px 12px", borderRadius: 6, cursor: "pointer", fontSize: 12, fontFamily: "inherit",
      }}>{deleting ? "…" : "Delete"}</button>
    </div>
  );
}
