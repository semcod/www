import { C } from "../../constants";

export function TrendChart({ history }) {
  if (!history || history.length < 2) {
    return <div style={{ color: C.fg3, fontSize: 13, padding: "24px 0" }}>Not enough data to show chart.</div>;
  }

  const W = 600, H = 120, PAD = 16;
  const scores = history.map(h => h.score);
  const minS = Math.max(0, Math.min(...scores) - 5);
  const maxS = Math.min(100, Math.max(...scores) + 5);
  const range = maxS - minS || 1;

  const x = i => PAD + (i / (history.length - 1)) * (W - PAD * 2);
  const y = s => H - PAD - ((s - minS) / range) * (H - PAD * 2);

  const points = history.map((h, i) => `${x(i)},${y(h.score)}`).join(" ");
  const fillPoints = `${x(0)},${H} ${points} ${x(history.length - 1)},${H}`;

  return (
    <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: "block" }}>
      <defs>
        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={C.cyan} stopOpacity="0.3" />
          <stop offset="100%" stopColor={C.cyan} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <polygon points={fillPoints} fill="url(#trendFill)" />
      <polyline points={points} fill="none" stroke={C.cyan} strokeWidth="2" strokeLinejoin="round" />
      {history.map((h, i) => (
        <g key={i}>
          <circle cx={x(i)} cy={y(h.score)} r="4" fill={C.cyan} />
          <text x={x(i)} y={H - 2} fontSize="9" fill={C.fg3} textAnchor="middle">
            {new Date(h.completed).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
          </text>
          <text x={x(i)} y={y(h.score) - 7} fontSize="10" fill={C.fg1} textAnchor="middle" fontWeight="600">
            {h.score}
          </text>
        </g>
      ))}
    </svg>
  );
}
