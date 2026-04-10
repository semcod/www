import { useState } from "react";
import { C, DEMO_AUDIT } from "../../../constants";
import { ResultHeader } from "./ResultHeader";
import { ResultMetrics } from "./ResultMetrics";
import { ResultRecommendations } from "./ResultRecommendations";
import { ShareButtons } from "../../ShareButtons";
import { useDownloads, getResultTabContent, TAB_TITLES } from "../../../hooks/useDownloads";

export function ResultPhase({ audit, selectedRepo, isSandbox, reset }) {
  const data = audit || DEMO_AUDIT;
  const repoName = selectedRepo?.full_name || selectedRepo?.name || "unknown/repo";
  const [activeTab, setActiveTab] = useState(null);

  const { handleGenericDownload } = useDownloads(data, repoName, isSandbox);

  const activeContent = activeTab ? getResultTabContent(activeTab, data, repoName, isSandbox) : "";

  const handleCopy = () => {
    navigator.clipboard.writeText(activeContent);
  };

  const handleDownload = () => {
    if (!activeTab || activeTab === "share") {
      return;
    }
    handleGenericDownload(activeTab);
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

      {activeTab && (
        <div style={{
          background: C.bg2,
          border: `1px solid ${C.border}`,
          borderRadius: 8,
          padding: 16,
          marginBottom: 28,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <h4 style={{ margin: 0, fontSize: 14, fontWeight: 600, color: C.fg2 }}>
              {TAB_TITLES[activeTab] || ""}
            </h4>
            <div style={{ display: "flex", gap: 8 }}>
              {activeTab !== 'share' && (
                <button
                  onClick={handleDownload}
                  style={{
                    background: C.cyan, border: "none", color: "#fff",
                    cursor: "pointer", fontSize: 12, padding: "6px 12px", borderRadius: 6,
                    fontFamily: "inherit", fontWeight: 500,
                  }}
                >Download</button>
              )}
              {activeTab === 'share' && (
                <ShareButtons scan={data} repo={repoName} size="small" onClick={() => {}} />
              )}
              <button
                onClick={handleCopy}
                style={{
                  background: C.fg3, border: "none", color: "#fff",
                  cursor: "pointer", fontSize: 12, padding: "6px 12px", borderRadius: 6,
                  fontFamily: "inherit", fontWeight: 500,
                }}
              >Copy</button>
              <button
                onClick={() => setActiveTab(null)}
                style={{
                  background: "transparent", border: `1px solid ${C.border}`, color: C.fg2,
                  cursor: "pointer", fontSize: 12, padding: "6px 12px", borderRadius: 6,
                  fontFamily: "inherit",
                }}
              >Close</button>
            </div>
          </div>
          <div style={{
            background: C.bg1,
            border: `1px solid ${C.border}`,
            borderRadius: 6,
            padding: 12,
            maxHeight: 400,
            overflow: "auto",
            fontSize: 12,
            fontFamily: "monospace",
            whiteSpace: "pre-wrap",
            wordBreak: "break-word",
            color: C.fg1,
          }}>
            {activeContent}
          </div>
        </div>
      )}

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
          <ResultMetrics data={data} />
          <ResultRecommendations recommendations={data.recommendations} />
        </>
      )}
    </div>
  );
}
