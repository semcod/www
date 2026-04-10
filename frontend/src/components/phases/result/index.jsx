import { useState } from "react";
import { DEMO_AUDIT } from "../../../constants";
import { ResultHeader } from "./ResultHeader";
import { ResultMetrics } from "./ResultMetrics";
import { ResultRecommendations } from "./ResultRecommendations";
import { ErrorResult } from "./ErrorResult";
import { ResultTabPanel } from "./ResultTabPanel";
import { useDownloads, getResultTabContent } from "../../../hooks/useDownloads";

export function ResultPhase({ audit, selectedRepo, isSandbox, reset }) {
  const data = audit || DEMO_AUDIT;
  const repoName = selectedRepo?.full_name || selectedRepo?.name || "unknown/repo";
  const [activeTab, setActiveTab] = useState(null);

  const { handleGenericDownload } = useDownloads(data, repoName, isSandbox);

  const activeContent = activeTab ? getResultTabContent(activeTab, data, repoName, isSandbox) : "";

  const handleCopy = () => navigator.clipboard.writeText(activeContent);
  const handleDownload = () => { if (activeTab && activeTab !== "share") handleGenericDownload(activeTab); };

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
        </>
      )}
    </div>
  );
}
