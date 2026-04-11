import { useState, useEffect } from "react";
import { C, gradeColor, API } from "../../constants";
import { getShareUrls } from "../../utils/share";
import { ShareButtons } from "../ShareButtons";

export function LandingPhase({ startOAuth, repoUrl, setRepoUrl, startSandbox }) {
  const [recentScans, setRecentScans] = useState([]);

  useEffect(() => {
    fetchRecentScans();
  }, []);

  const fetchRecentScans = async () => {
    try {
      const response = await fetch(`${API}/api/scans/recent?limit=5`);
      const data = await response.json();
      setRecentScans(data.scans || []);
    } catch (error) {
      console.error("Failed to fetch recent scans:", error);
    }
  };



  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("pl-PL", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  };

  return (
    <div style={{ textAlign: "center", padding: "80px 0 60px" }}>
      <div style={{
        display: "inline-flex", alignItems: "center", gap: 8,
        background: C.glow, border: `1px solid ${C.border}`,
        padding: "6px 16px", borderRadius: 99, fontSize: 12,
        fontFamily: "'JetBrains Mono', monospace", color: C.cyan, marginBottom: 28,
      }}>
        <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.green }} />
        AI-powered code reviews
      </div>

      <h1 style={{ fontSize: 48, fontWeight: 800, marginBottom: 16, letterSpacing: -1 }}>
        One-click <span style={{ color: C.cyan }}>code audit</span>
      </h1>
      <p style={{ fontSize: 18, color: C.fg2, maxWidth: 520, margin: "0 auto 40px", lineHeight: 1.6 }}>
        Detect complexity, duplication, and security issues in seconds. <br/>
        Get a health score badge for your README.
      </p>

      <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap", marginBottom: 60 }}>
        <button onClick={startOAuth} style={{
          background: C.cyan, color: C.bg, border: "none", borderRadius: 10,
          padding: "16px 32px", fontSize: 16, fontWeight: 700, cursor: "pointer",
          fontFamily: "inherit",
        }}>
          Connect GitHub →
        </button>
        <span style={{ color: C.fg3, padding: "16px 8px" }}>or</span>
        <div style={{ maxWidth: 600, margin: "0 auto", textAlign: "center" }}>
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
              onKeyDown={(e) => e.key === "Enter" && startSandbox()}
              style={{
                flex: 1, background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
                padding: "14px 18px", fontSize: 14, color: C.fg,
                fontFamily: "'JetBrains Mono', monospace",
              }}
            />
            <button onClick={startSandbox} style={{
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
      </div>

      <div style={{ display: "flex", gap: 40, justifyContent: "center", flexWrap: "wrap" }}>
        {[
          { icon: "🔬", label: "Static Analysis", desc: "code2llm TOON metrics" },
          { icon: "🔁", label: "Duplication", desc: "redup AST scanning" },
          { icon: "🧹", label: "Quality Gates", desc: "ruff + mypy + bandit" },
          { icon: "📊", label: "Health Badge", desc: "shields.io style" },
        ].map(({ icon, label, desc }) => (
          <div key={label} style={{ textAlign: "center" }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>{icon}</div>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 12, color: C.fg3, fontFamily: "'JetBrains Mono', monospace" }}>{desc}</div>
          </div>
        ))}
      </div>

      {recentScans.length > 0 && (
        <div style={{ marginTop: 80, maxWidth: 800, margin: "80px auto 0" }}>
          <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 24, textAlign: "center" }}>
            Ostatnio skanowane projekty
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {recentScans.map((scan, index) => (
              <div
                key={`${scan.repo}-${index}`}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 16,
                  padding: 16,
                  background: C.bg2,
                  borderRadius: 10,
                  border: `1px solid ${C.border}`,
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onClick={() => {
                  window.open(`https://github.com/${scan.repo}`, "_blank");
                }}
              >
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: "50%",
                    background: gradeColor(scan.grade),
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: 700,
                    color: C.bg,
                    fontSize: 14,
                    flexShrink: 0,
                  }}
                >
                  {scan.grade}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: C.fg,
                      marginBottom: 4,
                      fontFamily: "'JetBrains Mono', monospace",
                    }}
                  >
                    {scan.repo}
                  </div>
                  <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                    <span style={{ fontSize: 11, color: C.fg3 }}>
                      {formatDate(scan.completed)}
                    </span>
                    <span style={{ fontSize: 11, color: C.fg3 }}>
                      {scan.health_score}% zdrowie kodu
                    </span>
                  </div>
                </div>
                <ShareButtons scan={scan} repo={scan.repo} size="small" />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
