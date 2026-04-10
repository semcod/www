import { useState, useEffect } from "react";
import { C } from "../../constants";
import {
  RecentScansBadgeInfo,
  RecentScanCard,
  RecentScansEmptyState,
  RecentScansHeader,
} from "./RecentScansTab.parts.jsx";
import { fetchRecentScans } from "./recentScansHelpers.js";

export function RecentScansTab() {
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [benchmarkOnly, setBenchmarkOnly] = useState(false);

  useEffect(() => {
    fetchRecentScans()
      .then(setScans)
      .catch((error) => {
        console.error("Failed to fetch recent scans:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ maxWidth: 1000, margin: "60px auto", textAlign: "center" }}>
        <div style={{ fontSize: 14, color: C.fg2 }}>Ładowanie ostatnich skanów...</div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1000, margin: "60px auto" }}>
      <RecentScansHeader count={scans.length} />

      {scans.length === 0 ? (
        <RecentScansEmptyState />
      ) : (
        <>
          <div style={{ marginBottom: 10, display: "flex", alignItems: "center", gap: 8 }}>
            <label style={{ fontSize: 12, color: C.fg2, cursor: "pointer", display: "flex", alignItems: "center", gap: 4 }}>
              <input
                type="checkbox"
                checked={benchmarkOnly}
                onChange={(e) => setBenchmarkOnly(e.target.checked)}
              />
              Tylko benchmark
            </label>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {(benchmarkOnly ? scans.filter((s) => s.benchmark_mode) : scans).map((scan, index) => (
            <RecentScanCard key={`${scan.repo}-${index}`} scan={scan} />
          ))}
          </div>
        </>
      )}

      <RecentScansBadgeInfo />
    </div>
  );
}
