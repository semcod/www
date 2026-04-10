import { useState, useEffect } from "react";
import { C } from "../../constants";
import { fetchTrend } from "../../api";
import { TrendChart } from "./TrendChart";
import { TrendSummaryCard } from "./TrendSummaryCard";

const DAYS_OPTIONS = [7, 14, 30, 90];

export function TrendTab({ selectedRepo, sessionToken }) {
  const [days, setDays] = useState(30);
  const [trend, setTrend] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const repoName = selectedRepo?.full_name || selectedRepo?.name;

  useEffect(() => {
    if (!repoName) return;
    const [owner, repo] = repoName.includes("/") ? repoName.split("/") : [repoName, repoName];
    setLoading(true);
    setError(null);
    fetchTrend(owner, repo, days)
      .then(setTrend)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [repoName, days]);

  if (!repoName) {
    return (
      <div style={{ maxWidth: 1000, margin: "60px auto", textAlign: "center", color: C.fg3 }}>
        Select a repository to view its trend.
      </div>
    );
  }

  const history = trend?.history || [];
  const latest = history[history.length - 1];
  const prev = history[history.length - 2];
  const delta = latest && prev ? latest.score - prev.score : undefined;
  const directionColor = trend?.trend_direction === "improving" ? "#10B981"
    : trend?.trend_direction === "degrading" ? "#EF4444" : C.fg2;

  return (
    <div style={{ maxWidth: 1000, margin: "60px auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
          Health Trend — <span style={{ color: C.cyan }}>{repoName}</span>
        </h3>
        <div style={{ display: "flex", gap: 6 }}>
          {DAYS_OPTIONS.map(d => (
            <button key={d} onClick={() => setDays(d)} style={{
              background: days === d ? C.cyan : C.bg2,
              border: `1px solid ${days === d ? C.cyan : C.border}`,
              color: days === d ? "#fff" : C.fg2,
              padding: "5px 12px", borderRadius: 6, cursor: "pointer",
              fontSize: 12, fontFamily: "inherit",
            }}>{d}d</button>
          ))}
        </div>
      </div>

      {loading && <div style={{ color: C.fg3, fontSize: 13 }}>Loading trend data...</div>}
      {error && <div style={{ color: "#EF4444", fontSize: 13 }}>Error: {error}</div>}

      {!loading && !error && (
        <>
          <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
            <TrendSummaryCard label="Latest Score" value={latest?.score ?? "—"} delta={delta} color={C.cyan} />
            <TrendSummaryCard label="Scans" value={history.length} />
            <TrendSummaryCard label="Direction" value={trend?.trend_direction || "—"} color={directionColor} />
            <TrendSummaryCard label="Period" value={`${days}d`} />
          </div>

          <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
            <TrendChart history={history} />
          </div>
        </>
      )}
    </div>
  );
}
