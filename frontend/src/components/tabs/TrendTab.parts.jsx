import { C } from "../../constants";
import { TrendChart } from "./TrendChart";
import { TrendSummaryCard } from "./TrendSummaryCard";

export const DAYS_OPTIONS = [7, 14, 30, 90];

export function TrendEmptyState() {
  return (
    <div style={{ maxWidth: 1000, margin: "60px auto", textAlign: "center", color: C.fg3 }}>
      Select a repository to view its trend.
    </div>
  );
}

export function TrendHeader({ repoName, days, onDaysChange }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
      <h3 style={{ margin: 0, fontSize: 18, fontWeight: 700 }}>
        Health Trend — <span style={{ color: C.cyan }}>{repoName}</span>
      </h3>
      <DaySelector current={days} onChange={onDaysChange} />
    </div>
  );
}

function DaySelector({ current, onChange }) {
  return (
    <div style={{ display: "flex", gap: 6 }}>
      {DAYS_OPTIONS.map(d => (
        <DayButton key={d} days={d} isActive={current === d} onClick={() => onChange(d)} />
      ))}
    </div>
  );
}

function DayButton({ days, isActive, onClick }) {
  return (
    <button onClick={onClick} style={{
      background: isActive ? C.cyan : C.bg2,
      border: `1px solid ${isActive ? C.cyan : C.border}`,
      color: isActive ? "#fff" : C.fg2,
      padding: "5px 12px", borderRadius: 6, cursor: "pointer",
      fontSize: 12, fontFamily: "inherit",
    }}>{days}d</button>
  );
}

export function TrendLoadingState() {
  return <div style={{ color: C.fg3, fontSize: 13 }}>Loading trend data...</div>;
}

export function TrendErrorState({ message }) {
  return <div style={{ color: "#EF4444", fontSize: 13 }}>Error: {message}</div>;
}

export function TrendContent({ trend, days, history }) {
  const latest = history[history.length - 1];
  const prev = history[history.length - 2];
  const delta = latest && prev ? latest.score - prev.score : undefined;
  const directionColor = getDirectionColor(trend?.trend_direction);

  return (
    <>
      <TrendSummaryCards
        latest={latest}
        delta={delta}
        direction={trend?.trend_direction}
        directionColor={directionColor}
        historyLength={history.length}
        days={days}
      />
      <TrendChartContainer history={history} />
    </>
  );
}

function getDirectionColor(direction) {
  if (direction === "improving") return "#10B981";
  if (direction === "degrading") return "#EF4444";
  return C.fg2;
}

function TrendSummaryCards({ latest, delta, direction, directionColor, historyLength, days }) {
  return (
    <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
      <TrendSummaryCard label="Latest Score" value={latest?.score ?? "—"} delta={delta} color={C.cyan} />
      <TrendSummaryCard label="Scans" value={historyLength} />
      <TrendSummaryCard label="Direction" value={direction || "—"} color={directionColor} />
      <TrendSummaryCard label="Period" value={`${days}d`} />
    </div>
  );
}

function TrendChartContainer({ history }) {
  return (
    <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 20 }}>
      <TrendChart history={history} />
    </div>
  );
}
