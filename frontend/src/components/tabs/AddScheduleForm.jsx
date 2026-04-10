import { useState } from "react";
import { C } from "../../constants";
import { createSchedule } from "../../api";

const inputStyle = {
  background: C.bg2, border: `1px solid ${C.border}`, color: C.fg1,
  padding: "7px 10px", borderRadius: 6, fontSize: 13, fontFamily: "inherit", width: "100%",
};

export function AddScheduleForm({ sessionToken, onAdded }) {
  const [repo, setRepo] = useState("");
  const [hours, setHours] = useState(24);
  const [webhook, setWebhook] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await createSchedule({ repo, interval_hours: hours, webhook_url: webhook || null }, sessionToken);
      setRepo("");
      setWebhook("");
      onAdded();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10, padding: "14px", background: C.bg2, borderRadius: 8, border: `1px solid ${C.border}` }}>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <input value={repo} onChange={e => setRepo(e.target.value)} placeholder="owner/repo" required style={{ ...inputStyle, flex: 2, minWidth: 160 }} />
        <input type="number" value={hours} onChange={e => setHours(Number(e.target.value))} min={0.1} max={168} step={0.5} style={{ ...inputStyle, flex: 1, minWidth: 80 }} />
        <span style={{ lineHeight: "34px", fontSize: 12, color: C.fg3, whiteSpace: "nowrap" }}>hours</span>
      </div>
      <input value={webhook} onChange={e => setWebhook(e.target.value)} placeholder="Slack/Discord webhook URL (optional)" style={inputStyle} />
      {error && <div style={{ fontSize: 12, color: "#EF4444" }}>{error}</div>}
      <button type="submit" disabled={loading || !repo} style={{
        background: C.cyan, border: "none", color: "#fff",
        padding: "8px 16px", borderRadius: 6, cursor: "pointer", fontSize: 13,
        fontFamily: "inherit", fontWeight: 600, alignSelf: "flex-start",
      }}>{loading ? "Adding…" : "Add Schedule"}</button>
    </form>
  );
}
