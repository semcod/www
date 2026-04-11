import { useState } from "react";
import { ResultHeader } from "./ResultHeader";
import { ResultMetrics } from "./ResultMetrics";
import { ResultRecommendations } from "./ResultRecommendations";
import { ErrorResult } from "./ErrorResult";
import { ResultTabPanel } from "./ResultTabPanel";
import { useDownloads, getResultTabContent } from "../../../hooks/useDownloads";
import { useBenchmarkTracking } from "../../../hooks/useBenchmarkTracking";
import BenchmarkReviewPanel from "../../benchmark/BenchmarkReviewPanel";

export function ResultPhase({ audit, selectedRepo, isSandbox, reset, benchmarkCaseId, setBenchmarkCaseId }) {
  const data = audit || { error: "No audit data available" };
  const repoName = selectedRepo?.full_name || selectedRepo?.name || "unknown/repo";
  const [activeTab, setActiveTab] = useState(null);

  const { handleGenericDownload } = useDownloads(data, repoName, isSandbox);
  const { trackExport, trackRecommendationOpened, trackDecision } = useBenchmarkTracking({
    phase: "result",
    auditId: data.audit_id,
    caseId: benchmarkCaseId,
    repo: repoName,
  });

  const activeContent = activeTab ? getResultTabContent(activeTab, data, repoName, isSandbox) : "";

  const handleCopy = () => navigator.clipboard.writeText(activeContent);
  const handleDownload = () => {
    if (activeTab && activeTab !== "share") {
      trackExport(activeTab);
      handleGenericDownload(activeTab);
    }
  };

  return (
    <div>
      <ResultHeader
        selectedRepo={selectedRepo}
        isSandbox={isSandbox}
        data={data}
        reset={reset}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <ResultTabPanel
        activeTab={activeTab}
        activeContent={activeContent}
        repoName={repoName}
        scan={data}
        onDownload={handleDownload}
        onCopy={handleCopy}
        onClose={() => setActiveTab(null)}
      />

      {data.error && <ErrorResult error={data.error} isSandbox={isSandbox} />}

      {!data.error && (
        <>
          <ResultMetrics data={data} />
          <ResultRecommendations recommendations={data.recommendations} />
          <BenchmarkReviewPanel auditId={data.audit_id} repo={repoName} recommendations={data.recommendations || []} benchmarkCaseId={benchmarkCaseId} setBenchmarkCaseId={setBenchmarkCaseId} trackRecommendationOpened={trackRecommendationOpened} trackDecision={trackDecision} />
        </>
      )}
    </div>
  );
}
