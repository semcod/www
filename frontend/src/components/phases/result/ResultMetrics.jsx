import { GradeCircle, MetricCard, LanguageBar } from "../../ui";

export function ResultMetrics({ data }) {
  return (
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
    </>
  );
}
