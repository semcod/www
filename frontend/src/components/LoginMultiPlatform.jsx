import React from "react";
import { loginWithProvider } from "../api.js";

export default function LoginMultiPlatform() {
  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Semcod</h1>
        <p style={styles.subtitle}>AI-powered code health analysis for your repositories</p>

        <div style={styles.buttons}>
          <button
            onClick={() => loginWithProvider("github")}
            style={{ ...styles.button, ...styles.github }}
          >
            <GitHubIcon /> Login with GitHub
          </button>

          <button
            onClick={() => loginWithProvider("gitlab")}
            style={{ ...styles.button, ...styles.gitlab }}
          >
            <GitLabIcon /> Login with GitLab
          </button>

          <button
            onClick={() => loginWithProvider("gitea")}
            style={{ ...styles.button, ...styles.gitea }}
          >
            <GiteaIcon /> Login with Gitea
          </button>
        </div>

        <p style={styles.hint}>
          Supports GitHub, GitLab, and self-hosted Gitea
        </p>
      </div>
    </div>
  );
}

// Icons (inline SVG for simplicity)
function GitHubIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={styles.icon}>
      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
    </svg>
  );
}

function GitLabIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={styles.icon}>
      <path d="M12 0L8.35 8.35 0 9.27l6.06 5.23L4.18 24 12 20.45 19.82 24l-1.88-9.5L24 9.27l-8.35-.92L12 0z"/>
    </svg>
  );
}

function GiteaIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={styles.icon}>
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" fill="none"/>
      <text x="12" y="16" textAnchor="middle" fontSize="10" fill="currentColor">G</text>
    </svg>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
  },
  card: {
    background: "#fff",
    borderRadius: 12,
    padding: "48px 40px",
    textAlign: "center",
    boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
    maxWidth: 400,
    width: "100%",
  },
  title: {
    fontSize: 32,
    fontWeight: 700,
    margin: "0 0 8px 0",
    color: "#1a1a2e",
  },
  subtitle: {
    fontSize: 14,
    color: "#666",
    margin: "0 0 32px 0",
  },
  buttons: {
    display: "flex",
    flexDirection: "column",
    gap: 12,
    marginBottom: 24,
  },
  button: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    padding: "12px 24px",
    border: "none",
    borderRadius: 8,
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    transition: "opacity 0.2s",
  },
  github: {
    background: "#24292e",
    color: "#fff",
  },
  gitlab: {
    background: "#fc6d26",
    color: "#fff",
  },
  gitea: {
    background: "#609926",
    color: "#fff",
  },
  icon: {
    flexShrink: 0,
  },
  hint: {
    fontSize: 12,
    color: "#999",
    margin: 0,
  },
};
