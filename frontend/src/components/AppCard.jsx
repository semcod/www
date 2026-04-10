import React from "react";

export default function AppCard({ app, selected, onToggle, disabled }) {
  const isPro = app.pricing === "pro" || app.pricing === "team";

  return (
    <div
      style={{
        ...styles.card,
        ...(selected && styles.selected),
        ...(disabled && styles.disabled),
      }}
      onClick={() => !disabled && onToggle(app.name)}
    >
      <div style={styles.header}>
        <div style={styles.icon}>{getAppIcon(app.name)}</div>
        <div style={styles.info}>
          <h3 style={styles.name}>
            {app.name}
            {isPro && <span style={styles.proBadge}>PRO</span>}
          </h3>
          <p style={styles.version}>v{app.version}</p>
        </div>
        <div style={styles.checkbox}>
          {selected ? "☑️" : "⬜️"}
        </div>
      </div>

      <p style={styles.description}>{app.description}</p>

      <div style={styles.footer}>
        <div style={styles.triggers}>
          {app.triggers?.map((t) => (
            <span key={t} style={styles.trigger}>
              {getTriggerIcon(t)} {t.replace("_", " ")}
            </span>
          ))}
        </div>
        <div style={styles.actions}>
          {app.actions?.slice(0, 3).map((a) => (
            <span key={a} style={styles.action}>{a}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

function getAppIcon(name) {
  const icons = {
    audit: "🔍",
    security: "🔒",
    performance: "⚡",
    default: "📦",
  };
  return icons[name] || icons.default;
}

function getTriggerIcon(trigger) {
  const icons = {
    pull_request: "🔀",
    push: "⬆️",
    pull_request_comment: "💬",
    issue: "🐛",
  };
  return icons[trigger] || "⚡";
}

const styles = {
  card: {
    border: "2px solid #e1e4e8",
    borderRadius: 10,
    padding: 16,
    background: "#fff",
    cursor: "pointer",
    transition: "all 0.2s",
    hover: {
      borderColor: "#0366d6",
    },
  },
  selected: {
    borderColor: "#28a745",
    background: "#f0fff4",
  },
  disabled: {
    opacity: 0.6,
    cursor: "not-allowed",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    marginBottom: 8,
  },
  icon: {
    fontSize: 28,
  },
  info: {
    flex: 1,
  },
  name: {
    margin: 0,
    fontSize: 16,
    fontWeight: 600,
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  proBadge: {
    fontSize: 10,
    fontWeight: 700,
    padding: "2px 6px",
    background: "#ffd700",
    color: "#000",
    borderRadius: 4,
  },
  version: {
    margin: "4px 0 0 0",
    fontSize: 12,
    color: "#666",
  },
  checkbox: {
    fontSize: 20,
  },
  description: {
    margin: "0 0 12px 0",
    fontSize: 13,
    color: "#586069",
    lineHeight: 1.5,
  },
  footer: {
    display: "flex",
    flexDirection: "column",
    gap: 8,
  },
  triggers: {
    display: "flex",
    gap: 8,
    flexWrap: "wrap",
  },
  trigger: {
    fontSize: 11,
    padding: "3px 8px",
    background: "#f1f8ff",
    color: "#0366d6",
    borderRadius: 12,
    textTransform: "capitalize",
  },
  actions: {
    display: "flex",
    gap: 6,
  },
  action: {
    fontSize: 10,
    padding: "2px 6px",
    background: "#e1e4e8",
    color: "#24292e",
    borderRadius: 4,
  },
};
