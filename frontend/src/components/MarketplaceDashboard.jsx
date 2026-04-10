import React, { useState, useEffect } from "react";
import { getApps, fetchRepos, getInstallations } from "../api.js";
import AppCard from "./AppCard.jsx";
import Preview from "./Preview.jsx";
import InstallButton from "./InstallButton.jsx";

export default function MarketplaceDashboard({ token, provider }) {
  const [apps, setApps] = useState([]);
  const [repos, setRepos] = useState([]);
  const [installations, setInstallations] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [selectedApps, setSelectedApps] = useState(["audit"]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [step, setStep] = useState("select-repo"); // select-repo, preview, install

  useEffect(() => {
    const loadData = async () => {
      try {
        const [appsData, reposData, installsData] = await Promise.all([
          getApps(),
          fetchRepos(token),
          getInstallations(token),
        ]);
        setApps(appsData);
        setRepos(reposData);
        setInstallations(installsData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [token]);

  const toggleApp = (appName) => {
    setSelectedApps((prev) =>
      prev.includes(appName)
        ? prev.filter((a) => a !== appName)
        : [...prev, appName]
    );
  };

  const handleRepoSelect = (repo) => {
    setSelectedRepo(repo);
    setStep("preview");
  };

  const isRepoInstalled = (repo) => {
    return installations.some(
      (i) => i.repo === repo.full_name && i.provider === provider
    );
  };

  if (loading) {
    return <div style={styles.loading}>Loading...</div>;
  }

  if (error) {
    return <div style={styles.error}>Error: {error}</div>;
  }

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>🔧 Semcod Marketplace</h1>
        <p style={styles.subtitle}>Install apps to analyze your repositories</p>
      </header>

      {step === "select-repo" && (
        <div style={styles.step}>
          <h2 style={styles.stepTitle}>Step 1: Select Repository</h2>
          <div style={styles.repoList}>
            {repos.map((repo) => (
              <div
                key={repo.id}
                style={{
                  ...styles.repoCard,
                  ...(isRepoInstalled(repo) && styles.repoInstalled),
                }}
                onClick={() => handleRepoSelect(repo)}
              >
                <div style={styles.repoInfo}>
                  <h3 style={styles.repoName}>{repo.name}</h3>
                  <p style={styles.repoFull}>{repo.full_name}</p>
                </div>
                {isRepoInstalled(repo) ? (
                  <span style={styles.installedBadge}>✅ Installed</span>
                ) : (
                  <button style={styles.selectButton}>Select</button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {step === "preview" && selectedRepo && (
        <div style={styles.step}>
          <h2 style={styles.stepTitle}>Step 2: Preview & Configure</h2>

          <div style={styles.selectedRepo}>
            <h3 style={styles.selectedRepoName}>{selectedRepo.full_name}</h3>
            <button style={styles.backButton} onClick={() => setStep("select-repo")}>
              ← Change repo
            </button>
          </div>

          <div style={styles.appSelection}>
            <h4 style={styles.sectionTitle}>Select Apps to Install</h4>
            <div style={styles.appGrid}>
              {apps.map((app) => (
                <AppCard
                  key={app.name}
                  app={app}
                  selected={selectedApps.includes(app.name)}
                  onToggle={toggleApp}
                  disabled={app.pricing === "pro"} // Disable pro apps for now
                />
              ))}
            </div>
          </div>

          <div style={styles.previewSection}>
            <h4 style={styles.sectionTitle}>Preview</h4>
            <Preview
              repo={selectedRepo.full_name}
              provider={provider}
              token={token}
            />
          </div>

          <div style={styles.installSection}>
            <h4 style={styles.sectionTitle}>Ready to Install</h4>
            <InstallButton
              repo={selectedRepo.full_name}
              provider={provider}
              token={token}
              apps={selectedApps}
            />
          </div>
        </div>
      )}

      <footer style={styles.footer}>
        <p>Logged in via {provider}</p>
      </footer>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "24px 16px",
  },
  loading: {
    textAlign: "center",
    padding: 40,
    color: "#666",
  },
  error: {
    textAlign: "center",
    padding: 40,
    color: "#e74c3c",
  },
  header: {
    textAlign: "center",
    marginBottom: 32,
  },
  title: {
    fontSize: 32,
    fontWeight: 700,
    margin: "0 0 8px 0",
  },
  subtitle: {
    fontSize: 16,
    color: "#666",
    margin: 0,
  },
  step: {
    marginBottom: 32,
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: 600,
    marginBottom: 16,
    color: "#24292e",
  },
  repoList: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
    gap: 12,
  },
  repoCard: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    border: "1px solid #e1e4e8",
    borderRadius: 8,
    cursor: "pointer",
    transition: "all 0.2s",
    hover: {
      borderColor: "#0366d6",
      boxShadow: "0 2px 8px rgba(3, 102, 214, 0.1)",
    },
  },
  repoInstalled: {
    borderColor: "#28a745",
    background: "#f0fff4",
  },
  repoInfo: {
    flex: 1,
  },
  repoName: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600,
  },
  repoFull: {
    margin: "4px 0 0 0",
    fontSize: 13,
    color: "#666",
  },
  selectButton: {
    padding: "6px 12px",
    background: "#0366d6",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
  },
  installedBadge: {
    fontSize: 13,
    color: "#28a745",
    fontWeight: 600,
  },
  selectedRepo: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    background: "#f6f8fa",
    borderRadius: 8,
    marginBottom: 24,
  },
  selectedRepoName: {
    margin: 0,
    fontSize: 18,
    fontWeight: 600,
  },
  backButton: {
    padding: "6px 12px",
    background: "transparent",
    color: "#666",
    border: "1px solid #e1e4e8",
    borderRadius: 6,
    fontSize: 13,
    cursor: "pointer",
  },
  appSelection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 600,
    marginBottom: 12,
    color: "#24292e",
  },
  appGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
    gap: 16,
  },
  previewSection: {
    marginBottom: 24,
    padding: 16,
    background: "#fff",
    border: "1px solid #e1e4e8",
    borderRadius: 8,
  },
  installSection: {
    padding: 24,
    background: "#fff",
    border: "1px solid #e1e4e8",
    borderRadius: 8,
    textAlign: "center",
  },
  footer: {
    textAlign: "center",
    padding: 24,
    color: "#666",
    fontSize: 13,
    borderTop: "1px solid #e1e4e8",
  },
};
