import { C } from "../../../constants";
import { TAB_TITLES } from "../../../hooks/useDownloads";
import { ShareButtons } from "../../ShareButtons";

export function ResultTabPanel({ activeTab, activeContent, repoName, scan, onDownload, onCopy, onClose }) {
  if (!activeTab) return null;

  return (
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
          {activeTab !== "share" && (
            <button
              onClick={onDownload}
              style={{
                background: C.cyan, border: "none", color: "#fff",
                cursor: "pointer", fontSize: 12, padding: "6px 12px", borderRadius: 6,
                fontFamily: "inherit", fontWeight: 500,
              }}
            >Download</button>
          )}
          {activeTab === "share" && (
            <ShareButtons scan={scan} repo={repoName} size="small" onClick={() => {}} />
          )}
          <button
            onClick={onCopy}
            style={{
              background: C.fg3, border: "none", color: "#fff",
              cursor: "pointer", fontSize: 12, padding: "6px 12px", borderRadius: 6,
              fontFamily: "inherit", fontWeight: 500,
            }}
          >Copy</button>
          <button
            onClick={onClose}
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
  );
}
