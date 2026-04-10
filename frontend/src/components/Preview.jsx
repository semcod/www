import React, { useState } from "react";
import { getPreview } from "../api.js";

export default function Preview({ repo, provider, token }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadPreview = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getPreview(repo, provider, token);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={styles.loading}>Analyzing...</div>;
  }

  return (
    <div style={styles.container}>
      <button
        onClick={loadPreview}
        disabled={loading}
        style={styles.previewButton}
      >
        👁️ Preview PR Comment
      </button>

      {error && (
        <div style={styles.error}>Error: {error}</div>
      )}

      {data && (
        <div style={styles.previewCard}>
          <div style={styles.previewHeader}>
            <span style={styles.previewTitle}>🔮 PR Preview</span>
            <span style={styles.score(data.score)}>
              Score: {data.score}/100
            </span>
          </div>

          <div
            style={styles.comment}
            dangerouslySetInnerHTML={{ __html: formatComment(data.comment) }}
          />

          {data.issues && data.issues.length > 0 && (
            <div style={styles.issues}>
              <h4 style={styles.issuesTitle}>Issues ({data.issues.length})</h4>
              <ul style={styles.issuesList}>
                {data.issues.map((issue, i) => (
                  <li key={i} style={styles.issue(issue.severity)}>
                    {getSeverityIcon(issue.severity)} {issue.message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {data.suggested_patch && (
            <div style={styles.patchSection}>
              <h4 style={styles.patchTitle}>🛠️ Suggested Fix (Pro)</h4>
              <pre style={styles.patch}>{data.suggested_patch}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function formatComment(comment) {
  // Simple markdown-like formatting
  return comment
    .replace(/## (.*)/g, '<h3 style="margin:0 0 12px 0;font-size:18px;">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br/>');
}

function getSeverityIcon(severity) {
  const icons = {
    critical: "🔴",
    high: "🟠",
    medium: "🟡",
    low: "🔵",
  };
  return icons[severity] || "⚪";
}

const styles = {
  container: {
    marginTop: 16,
  },
  loading: {
    color: "#666",
    fontSize: 14,
    padding: 12,
  },
  previewButton: {
    background: "#6c5ce7",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "10px 16px",
    fontSize: 13,
    fontWeight: 600,
    cursor: "pointer",
    transition: "background 0.2s",
  },
  error: {
    color: "#e74c3c",
    fontSize: 13,
    marginTop: 8,
  },
  previewCard: {
    marginTop: 16,
    border: "1px solid #e1e4e8",
    borderRadius: 8,
    background: "#fff",
    overflow: "hidden",
  },
  previewHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 16px",
    background: "#f6f8fa",
    borderBottom: "1px solid #e1e4e8",
  },
  previewTitle: {
    fontSize: 14,
    fontWeight: 600,
    color: "#24292e",
  },
  score: (score) => ({
    fontSize: 14,
    fontWeight: 700,
    color: score >= 80 ? "#28a745" : score >= 60 ? "#f0ad4e" : "#dc3545",
  }),
  comment: {
    padding: 16,
    fontSize: 14,
    lineHeight: 1.6,
    color: "#24292e",
    background: "#fff",
  },
  issues: {
    padding: "0 16px 16px",
    borderTop: "1px solid #e1e4e8",
  },
  issuesTitle: {
    fontSize: 13,
    fontWeight: 600,
    margin: "12px 0 8px 0",
    color: "#586069",
  },
  issuesList: {
    margin: 0,
    paddingLeft: 20,
    fontSize: 13,
  },
  issue: (severity) => ({
    marginBottom: 4,
    color: severity === "critical" || severity === "high" ? "#dc3545" : "#666",
  }),
  patchSection: {
    padding: 16,
    borderTop: "1px solid #e1e4e8",
    background: "#f6f8fa",
  },
  patchTitle: {
    fontSize: 13,
    fontWeight: 600,
    margin: "0 0 8px 0",
    color: "#586069",
  },
  patch: {
    margin: 0,
    padding: 12,
    background: "#fff",
    border: "1px solid #e1e4e8",
    borderRadius: 6,
    fontSize: 12,
    fontFamily: "monospace",
    overflow: "auto",
    maxHeight: 200,
  },
};
