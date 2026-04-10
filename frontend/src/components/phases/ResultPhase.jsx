import { C, DEMO_AUDIT } from "../../lib/config";
import { GradeCircle, MetricCard, RecommendationCard, LanguageBar } from "../ui";

export function ResultPhase({ audit, selectedRepo, isSandbox, reset }) {
  const data = audit || DEMO_AUDIT;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
        <div>
          <h2 style={{ fontSize: 22, fontWeight: 700 }}>
            <span style={{ color: C.fg3 }}>Report:</span> {selectedRepo?.full_name}
            {isSandbox && (
              <span style={{
                display: "inline-block",
                marginLeft: 12,
                fontSize: 11,
                color: C.amber,
                background: `${C.amber}15`,
                padding: "2px 8px",
                borderRadius: 4,
                fontWeight: 500,
              }}>🔒 Sandbox</span>
            )}
          </h2>
          {isSandbox && !data.error && (
            <p style={{ fontSize: 13, color: C.fg3, marginTop: 4 }}>
              Public repository analyzed without authentication.
              <a href="#" onClick={(e) => { e.preventDefault(); reset(); }} style={{ color: C.cyan, marginLeft: 8 }}>Install GitHub App for PR reviews →</a>
            </p>
          )}
        </div>
        <button onClick={reset} style={{
          background: C.bg3, border: `1px solid ${C.border}`, color: C.fg2,
          cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
          fontFamily: "inherit",
        }}>New audit</button>
      </div>

      {data.error && (
        <div style={{
          background: `${C.red}15`, border: `1px solid ${C.red}`, borderRadius: 10,
          padding: "20px 24px", marginBottom: 28,
        }}>
          <div style={{ fontSize: 16, fontWeight: 600, color: C.red, marginBottom: 8 }}>
            ⚠️ Analysis failed
          </div>
          <p style={{ fontSize: 14, color: C.fg2, margin: 0 }}>{data.error}</p>
          {isSandbox && (
            <p style={{ fontSize: 13, color: C.fg3, marginTop: 12 }}>
              Make sure the repository is public and accessible.
              Private repositories require GitHub authentication.
            </p>
          )}
        </div>
      )}

      {!data.error && (
        <>
          <div style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap", marginBottom: 32 }}>
            <GradeCircle grade={data.grade} score={data.health_score} />
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", flex: 1 }}>
              <MetricCard icon="📁" label="FILES" value={data.stats.total_files} sub={`${(data.stats.total_lines / 1000).toFixed(1)}k lines`} />
              <MetricCard icon="🔬" label="CC̄" value={data.metrics.complexity.cc_avg.toFixed(1)} sub={`${data.metrics.complexity.functions} functions`} />
              <MetricCard icon="🔁" label="DUPLICATES" value={data.metrics.duplication.duplication_groups} sub={`${data.metrics.duplication.recoverable_lines} lines recoverable`} />
              <MetricCard icon="✅" label="QUALITY" value={`${data.metrics.quality.passed}/${data.metrics.quality.passed + data.metrics.quality.errors}`} sub={`${data.metrics.quality.warnings} warnings`} />
            </div>
          </div>

          <LanguageBar languages={data.stats.languages} />

          <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Recommendations</h3>
          <div style={{ display: "grid", gap: 12 }}>
            {data.recommendations.map((rec, i) => (
              <RecommendationCard key={i} rec={rec} index={i} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
