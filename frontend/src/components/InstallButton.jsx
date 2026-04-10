import React, { useState } from "react";
import { installApp, uninstallApp, getAppStatus } from "../api.js";

export default function InstallButton({ repo, provider, token, apps = ["audit"] }) {
  const [installed, setInstalled] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  // Check current status on mount
  React.useEffect(() => {
    const checkStatus = async () => {
      try {
        const result = await getAppStatus(repo, provider, token);
        setInstalled(result.installed);
        setStatus(result);
      } catch (err) {
        // Not installed or error - default to not installed
        setInstalled(false);
      }
    };
    checkStatus();
  }, [repo, provider, token]);

  const handleInstall = async () => {
    setLoading(true);
    try {
      await installApp(repo, provider, apps, token);
      setInstalled(true);
      const result = await getAppStatus(repo, provider, token);
      setStatus(result);
    } catch (err) {
      alert("Installation failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUninstall = async () => {
    if (!confirm(`Remove Semcod from ${repo}?`)) return;

    setLoading(true);
    try {
      await uninstallApp(repo, provider, token);
      setInstalled(false);
      setStatus(null);
    } catch (err) {
      alert("Uninstall failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <button style={{ ...styles.button, ...styles.loading }} disabled>
        ⏳ Processing...
      </button>
    );
  }

  if (installed) {
    return (
      <div style={styles.container}>
        <button
          onClick={handleUninstall}
          style={{ ...styles.button, ...styles.installed }}
        >
          ✅ Installed
        </button>
        {status && (
          <div style={styles.status}>
            <div style={styles.statusItem}>
              Last scan: {status.last_scan || "Never"}
            </div>
            {status.score !== undefined && (
              <div style={styles.score(status.score)}>
                Score: {status.score}
              </div>
            )}
          </div>
        )}
      </div>
    );
  }

  return (
    <button
      onClick={handleInstall}
      style={{ ...styles.button, ...styles.install }}
    >
      🚀 Install App
    </button>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  button: {
    padding: "10px 20px",
    borderRadius: 6,
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    border: "none",
    transition: "all 0.2s",
  },
  install: {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "#fff",
    boxShadow: "0 4px 12px rgba(102, 126, 234, 0.4)",
  },
  installed: {
    background: "#28a745",
    color: "#fff",
  },
  loading: {
    background: "#6c757d",
    color: "#fff",
    cursor: "not-allowed",
  },
  status: {
    display: "flex",
    gap: 12,
    fontSize: 12,
    color: "#666",
  },
  statusItem: {
    padding: "4px 8px",
    background: "#f1f3f4",
    borderRadius: 4,
  },
  score: (score) => ({
    padding: "4px 8px",
    borderRadius: 4,
    fontWeight: 600,
    background: score >= 80 ? "#d4edda" : score >= 60 ? "#fff3cd" : "#f8d7da",
    color: score >= 80 ? "#155724" : score >= 60 ? "#856404" : "#721c24",
  }),
};
