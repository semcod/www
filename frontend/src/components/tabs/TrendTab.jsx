import { useState, useEffect } from "react";
import { fetchTrend } from "../../api";
import {
  TrendEmptyState,
  TrendHeader,
  TrendLoadingState,
  TrendErrorState,
  TrendContent
} from "./TrendTab.parts";

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
    return <TrendEmptyState />;
  }

  const history = trend?.history || [];

  return (
    <div style={{ maxWidth: 1000, margin: "60px auto" }}>
      <TrendHeader repoName={repoName} days={days} onDaysChange={setDays} />
      {loading && <TrendLoadingState />}
      {error && <TrendErrorState message={error} />}
      {!loading && !error && <TrendContent trend={trend} days={days} history={history} />}
    </div>
  );
}
