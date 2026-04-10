import { useState, useEffect } from "react";
import { C, gradeColor } from "../../constants";
import { getShareUrls } from "../../utils/share";
import { config } from "../../config";

export function RecentScansTab() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentScans();
  }, []);

  const fetchRecentScans = async () => {
    try {
      const response = await fetch("/api/scans/recent?limit=100");
      const data = await response.json();
      setScans(data.scans || []);
    } catch (error) {
      console.error("Failed to fetch recent scans:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("pl-PL", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getLanguageBadge = (languages) => {
    if (!languages || Object.keys(languages).length === 0) return null;
    const topLang = Object.entries(languages)[0];
    return (
      <span
        style={{
          fontSize: 11,
          padding: "2px 8px",
          borderRadius: 4,
          background: C.bg2,
          color: C.fg2,
          fontFamily: "'JetBrains Mono', monospace",
        }}
      >
        {topLang[0]}
      </span>
    );
  };

  const handleShare = (scan, platform) => {
    const shareUrls = getShareUrls(scan, scan.repo);
    window.open(shareUrls[platform], '_blank', 'width=600,height=400');
  };

  if (loading) {
    return (
      <div style={{ maxWidth: 1000, margin: "60px auto", textAlign: "center" }}>
        <div style={{ fontSize: 14, color: C.fg2 }}>Ładowanie ostatnich skanów...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: "60px auto" }}>
      <div style={{ textAlign: "center", marginBottom: 40 }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
        <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>
          Ostatnio skanowane projekty
        </h2>
        <p style={{ fontSize: 14, color: C.fg2, marginBottom: 8 }}>
          Lista 100 ostatnich skanowanych repozytoriów z ich metrykami jakości kodu.
        </p>
        <p style={{ fontSize: 12, color: C.fg3 }}>
          Liczba skanów: {scans.length}
        </p>
      </div>

      {scans.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: 60,
            background: C.bg2,
            borderRadius: 12,
            border: `1px solid ${C.border}`,
          }}
        >
          <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
          <p style={{ fontSize: 14, color: C.fg2 }}>
            Brak zapisanych skanów. Zeskanuj pierwszy projekt!
          </p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {scans.map((scan, index) => (
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
                transition: "all 0.2s",
                cursor: "pointer",
              }}
              onClick={() => {
                window.open(`https://github.com/${scan.repo}`, "_blank");
              }}
            >
              {/* Grade Badge */}
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: "50%",
                  background: gradeColor(scan.grade),
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  color: C.bg,
                  fontSize: 16,
                  flexShrink: 0,
                }}
              >
                {scan.grade}
              </div>

              {/* Repo Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: 15,
                    fontWeight: 600,
                    color: C.fg,
                    marginBottom: 4,
                    fontFamily: "'JetBrains Mono', monospace",
                  }}
                >
                  {scan.repo}
                </div>
                <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
                  <span style={{ fontSize: 12, color: C.fg3 }}>
                    {formatDate(scan.completed)}
                  </span>
                  {scan.sandbox && (
                    <span
                      style={{
                        fontSize: 11,
                        padding: "2px 6px",
                        borderRadius: 4,
                        background: "#7c3aed",
                        color: "#fff",
                      }}
                    >
                      Sandbox
                    </span>
                  )}
                  {getLanguageBadge(scan.stats?.languages)}
                </div>
              </div>

              {/* Metrics */}
              <div
                style={{
                  display: "flex",
                  gap: 24,
                  textAlign: "center",
                  flexShrink: 0,
                }}
              >
                <div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: C.fg }}>
                    {scan.health_score}%
                  </div>
                  <div style={{ fontSize: 11, color: C.fg3 }}>Wynik</div>
                </div>
                <div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: C.fg }}>
                    {scan.stats?.total_files || 0}
                  </div>
                  <div style={{ fontSize: 11, color: C.fg3 }}>Pliki</div>
                </div>
                <div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: C.fg }}>
                    {(scan.stats?.total_lines || 0) / 1000}k
                  </div>
                  <div style={{ fontSize: 11, color: C.fg3 }}>Linii</div>
                </div>
              </div>

              {/* View Button */}
              <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                <button
                  style={{
                    padding: "8px 12px",
                    background: "#1DA1F2",
                    color: "#fff",
                    border: "none",
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleShare(scan, 'twitter');
                  }}
                  title="Share on X (Twitter)"
                >
                  𝕏
                </button>
                <button
                  style={{
                    padding: "8px 12px",
                    background: "#0077B5",
                    color: "#fff",
                    border: "none",
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleShare(scan, 'linkedin');
                  }}
                  title="Share on LinkedIn"
                >
                  in
                </button>
                <button
                  style={{
                    padding: "8px 12px",
                    background: "#0085FF",
                    color: "#fff",
                    border: "none",
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleShare(scan, 'bluesky');
                  }}
                  title="Share on Bluesky"
                >
                  🦋
                </button>
                <button
                  style={{
                    padding: "8px 16px",
                    background: C.cyan,
                    color: C.bg,
                    border: "none",
                    borderRadius: 6,
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: "pointer",
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    window.location.hash = `tab=audit&phase=scanning&repo=${encodeURIComponent(
                      `https://github.com/${scan.repo}`
                    )}&sandbox=1`;
                    window.location.reload();
                  }}
                >
                  Zobacz →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Badge Info */}
      <div
        style={{
          marginTop: 40,
          padding: 24,
          background: C.bg2,
          borderRadius: 10,
          border: `1px solid ${C.border}`,
        }}
      >
        <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12, color: C.fg }}>
          🏆 Dodaj badge do swojego projektu
        </h3>
        <p style={{ fontSize: 13, color: C.fg2, marginBottom: 16 }}>
          Pokaż wynik skanu w README swojego repozytorium. Badge aktualizuje się automatycznie po każdym skanie.
        </p>
        <code
          style={{
            display: "block",
            background: C.bg,
            padding: 12,
            borderRadius: 6,
            fontSize: 12,
            color: C.cyan,
            fontFamily: "'JetBrains Mono', monospace",
            overflowX: "auto",
          }}
        >
          ![Code Health](https://semcod.com/badge/owner-repo.svg)
        </code>
      </div>
    </div>
  );
}
