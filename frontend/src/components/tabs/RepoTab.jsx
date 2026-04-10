import { useState } from "react";
import { C } from "../../lib/config";

export function RepoTab() {
  const [repoUrl, setRepoUrl] = useState("");

  const handleAnalyze = () => {
    if (!repoUrl.trim()) return;
    window.location.hash = `tab=audit&phase=scanning&repo=${encodeURIComponent(repoUrl)}&sandbox=1`;
    window.location.reload();
  };

  return (
    <div style={{ maxWidth: 600, margin: "60px auto", textAlign: "center" }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>📁</div>
      <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>Analyze any public repo</h2>
      <p style={{ fontSize: 14, color: C.fg2, marginBottom: 32 }}>
        Enter a GitHub, GitLab, or Bitbucket repository URL.
        Works with any public repository — no authentication required.
      </p>

      <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
        <input
          type="text"
          placeholder="https://github.com/owner/repo"
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
          style={{
            flex: 1, background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
            padding: "14px 18px", fontSize: 14, color: C.fg,
            fontFamily: "'JetBrains Mono', monospace",
          }}
        />
        <button onClick={handleAnalyze} style={{
          background: C.cyan, color: C.bg, border: "none", borderRadius: 10,
          padding: "14px 28px", fontSize: 15, fontWeight: 700, cursor: "pointer",
          fontFamily: "inherit",
        }}>
          Analyze →
        </button>
      </div>

      <div style={{ fontSize: 12, color: C.fg3, fontFamily: "'JetBrains Mono', monospace" }}>
        Supports: github.com / gitlab.com / bitbucket.org
      </div>
    </div>
  );
}
