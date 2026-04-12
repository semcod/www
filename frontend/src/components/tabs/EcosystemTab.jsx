import { useState, useEffect } from "react";
import { fetchEcosystem, fetchProjectHistory } from "../../api";
import { C, gradeColor } from "../../constants";

const trendIcon = (t) => ({ improving: "📈", degrading: "📉", stable: "➡️" }[t] || "➡️");
const trendColor = (t) => ({ improving: C.green, degrading: C.red, stable: C.fg3 }[t] || C.fg3);

function GradeCircle({ grade, size = 36 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: "50%",
      background: `${gradeColor(grade)}22`, border: `2px solid ${gradeColor(grade)}`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: size * 0.4, fontWeight: 700, color: gradeColor(grade),
      fontFamily: "'JetBrains Mono', monospace",
    }}>{grade}</div>
  );
}

function HealthBar({ score }) {
  const color = score >= 80 ? C.green : score >= 60 ? C.amber : C.red;
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 120 }}>
      <div style={{ flex: 1, height: 6, borderRadius: 3, background: C.bg3 }}>
        <div style={{ width: `${score}%`, height: "100%", borderRadius: 3, background: color, transition: "width 0.3s" }} />
      </div>
      <span style={{ fontSize: 12, color: C.fg2, fontFamily: "'JetBrains Mono', monospace", minWidth: 32 }}>{score}%</span>
    </div>
  );
}

function ProjectRow({ project, onSelect }) {
  return (
    <div onClick={() => onSelect(project.name)}
      style={{
        display: "grid", gridTemplateColumns: "44px 1fr 140px 80px 80px",
        alignItems: "center", gap: 12, padding: "12px 16px",
        borderBottom: `1px solid ${C.border}`, cursor: "pointer",
        transition: "background 0.15s",
      }}
      onMouseEnter={e => e.currentTarget.style.background = C.bg3}
      onMouseLeave={e => e.currentTarget.style.background = "transparent"}
    >
      <GradeCircle grade={project.grade} />
      <div>
        <div style={{ fontSize: 14, fontWeight: 600, color: C.fg }}>{project.name}</div>
        <div style={{ fontSize: 11, color: C.fg3, marginTop: 2 }}>
          {project.scan_count} scans · last: {project.last_scan ? new Date(project.last_scan).toLocaleDateString() : "—"}
        </div>
      </div>
      <HealthBar score={project.health_score ?? 0} />
      <span style={{ fontSize: 12, color: trendColor(project.trend), fontWeight: 600, textAlign: "center" }}>
        {trendIcon(project.trend)} {project.trend}
      </span>
      <span style={{
        fontSize: 11, fontWeight: 600, textAlign: "center",
        color: (project.health_score ?? 0) >= 70 ? C.green : C.amber,
      }}>
        {(project.health_score ?? 0) >= 70 ? "OK" : "NEEDS WORK"}
      </span>
    </div>
  );
}

function SummaryCards({ data }) {
  const cards = [
    { label: "Projects", value: data.total_projects, color: C.cyan },
    { label: "Avg Health", value: data.avg_health != null ? `${data.avg_health}%` : "—", color: C.green },
    { label: "Healthy", value: data.projects.filter(p => (p.health_score ?? 0) >= 70).length, color: C.green },
    { label: "Needs Work", value: data.projects.filter(p => (p.health_score ?? 0) < 70).length, color: C.amber },
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
      {cards.map(c => (
        <div key={c.label} style={{
          background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 8,
          padding: "16px 20px", textAlign: "center",
        }}>
          <div style={{ fontSize: 24, fontWeight: 700, color: c.color, fontFamily: "'JetBrains Mono', monospace" }}>{c.value}</div>
          <div style={{ fontSize: 11, color: C.fg3, marginTop: 4 }}>{c.label}</div>
        </div>
      ))}
    </div>
  );
}

function MiniChart({ history }) {
  if (!history || history.length < 2) return <span style={{ color: C.fg3, fontSize: 11 }}>no data</span>;
  const scores = history.map(h => h.score);
  const max = Math.max(...scores, 100);
  const min = Math.min(...scores, 0);
  const w = 200, h = 40;
  const points = scores.map((s, i) => `${(i / (scores.length - 1)) * w},${h - ((s - min) / (max - min || 1)) * h}`).join(" ");
  return (
    <svg width={w} height={h} style={{ display: "block" }}>
      <polyline points={points} fill="none" stroke={C.cyan} strokeWidth="1.5" />
    </svg>
  );
}

function ProjectDetail({ repo, onBack }) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const [owner, name] = repo.includes("/") ? repo.split("/") : [repo, repo];
    setLoading(true);
    fetchProjectHistory(owner, name, 50)
      .then(setHistory)
      .catch(() => setHistory(null))
      .finally(() => setLoading(false));
  }, [repo]);

  return (
    <div>
      <button onClick={onBack} style={{
        background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 4,
        color: C.fg2, padding: "6px 12px", cursor: "pointer", fontSize: 12,
        fontFamily: "'JetBrains Mono', monospace", marginBottom: 16,
      }}>← Back</button>
      <h3 style={{ color: C.fg, margin: "0 0 16px", fontFamily: "'JetBrains Mono', monospace" }}>{repo}</h3>
      {loading && <div style={{ color: C.fg3 }}>Loading history…</div>}
      {!loading && history && (
        <div>
          <div style={{ fontSize: 13, color: C.fg2, marginBottom: 8 }}>
            {history.total_scans} scans recorded
          </div>
          <div style={{
            background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 8,
            padding: 20, marginBottom: 16,
          }}>
            <div style={{ fontSize: 12, color: C.fg3, marginBottom: 8 }}>Health Score Over Time</div>
            {history.history.length >= 2 ? (
              <MiniChart history={history.history} />
            ) : (
              <div style={{ color: C.fg3, fontSize: 12 }}>Not enough data for chart</div>
            )}
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ color: C.fg3, borderBottom: `1px solid ${C.border}` }}>
                <th style={{ textAlign: "left", padding: "8px 12px" }}>Date</th>
                <th style={{ textAlign: "center", padding: "8px 12px" }}>Grade</th>
                <th style={{ textAlign: "right", padding: "8px 12px" }}>Score</th>
              </tr>
            </thead>
            <tbody>
              {history.history.slice().reverse().map((h, i) => (
                <tr key={i} style={{ borderBottom: `1px solid ${C.border}` }}>
                  <td style={{ padding: "8px 12px", color: C.fg2 }}>{h.date ? new Date(h.date).toLocaleString() : "—"}</td>
                  <td style={{ padding: "8px 12px", textAlign: "center", color: gradeColor(h.grade), fontWeight: 600 }}>{h.grade}</td>
                  <td style={{ padding: "8px 12px", textAlign: "right", color: C.fg, fontFamily: "'JetBrains Mono', monospace" }}>{h.score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export function EcosystemTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    fetchEcosystem()
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign: "center", padding: 60, color: C.fg3 }}>Loading ecosystem…</div>;
  if (error) return <div style={{ textAlign: "center", padding: 60, color: C.red }}>Error: {error}</div>;
  if (!data) return null;

  if (selectedProject) {
    return (
      <div style={{ maxWidth: 1000, margin: "60px auto" }}>
        <ProjectDetail repo={selectedProject} onBack={() => setSelectedProject(null)} />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: "60px auto" }}>
      <h2 style={{
        fontFamily: "'JetBrains Mono', monospace", fontWeight: 700,
        fontSize: 20, color: C.fg, marginBottom: 24,
      }}>
        🏗️ Ecosystem Health
      </h2>

      <SummaryCards data={data} />

      <div style={{
        background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden",
      }}>
        <div style={{
          display: "grid", gridTemplateColumns: "44px 1fr 140px 80px 80px",
          gap: 12, padding: "10px 16px", fontSize: 11, color: C.fg3,
          borderBottom: `1px solid ${C.border}`, fontWeight: 600,
        }}>
          <span></span><span>Project</span><span>Health</span><span style={{ textAlign: "center" }}>Trend</span><span style={{ textAlign: "center" }}>Status</span>
        </div>
        {data.projects.map(p => <ProjectRow key={p.name} project={p} onSelect={setSelectedProject} />)}
        {data.projects.length === 0 && (
          <div style={{ padding: 32, textAlign: "center", color: C.fg3 }}>
            No projects scanned yet. Run an audit to see ecosystem health.
          </div>
        )}
      </div>

      {data.priority_ranking.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h3 style={{ fontSize: 14, color: C.fg2, fontFamily: "'JetBrains Mono', monospace", marginBottom: 8 }}>
            Priority Ranking (worst first)
          </h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {data.priority_ranking.map((name, i) => (
              <span key={name} onClick={() => setSelectedProject(name)}
                style={{
                  fontSize: 11, padding: "4px 10px", borderRadius: 4, cursor: "pointer",
                  background: i === 0 ? `${C.red}22` : C.bg3,
                  border: `1px solid ${i === 0 ? C.red : C.border}`,
                  color: i === 0 ? C.red : C.fg2,
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >#{i + 1} {name}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
