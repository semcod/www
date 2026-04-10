import { C, gradeColor } from "../../constants";
import { ShareButtons } from "../ShareButtons";
import {
  formatRecentScanDate,
  getPrimaryLanguage,
  openRecentScanAudit,
  openRecentScanRepository,
} from "./recentScansHelpers.js";

function LanguageBadge({ languages }) {
  const language = getPrimaryLanguage(languages);
  if (!language) {
    return null;
  }

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
      {language}
    </span>
  );
}

function ScanMetrics({ scan }) {
  return (
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
  );
}

export function RecentScanCard({ scan }) {
  return (
    <div
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
        openRecentScanRepository(scan.repo);
      }}
    >
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
            {formatRecentScanDate(scan.completed)}
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
          <LanguageBadge languages={scan.stats?.languages} />
        </div>
      </div>

      <ScanMetrics scan={scan} />

      <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
        <ShareButtons scan={scan} repo={scan.repo} size="small" />
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
            openRecentScanAudit(scan.repo);
          }}
        >
          Zobacz →
        </button>
      </div>
    </div>
  );
}

export function RecentScansEmptyState() {
  return (
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
  );
}

export function RecentScansHeader({ count }) {
  return (
    <div style={{ textAlign: "center", marginBottom: 40 }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🔍</div>
      <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>
        Ostatnio skanowane projekty
      </h2>
      <p style={{ fontSize: 14, color: C.fg2, marginBottom: 8 }}>
        Lista 100 ostatnich skanowanych repozytoriów z ich metrykami jakości kodu.
      </p>
      <p style={{ fontSize: 12, color: C.fg3 }}>
        Liczba skanów: {count}
      </p>
    </div>
  );
}

export function RecentScansBadgeInfo() {
  return (
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
  );
}
