// ─── Config ──────────────────────────────────────────────────────────────────
export const API = import.meta.env.VITE_API_URL || "";

// ─── Color tokens ────────────────────────────────────────────────────────────
export const C = {
  bg: "#05080f", bg2: "#0c1220", bg3: "#131d30", bg4: "#1a2740",
  fg: "#e4eaf4", fg2: "#8899b4", fg3: "#556680",
  cyan: "#00e5ff", green: "#00e676", amber: "#ffab00", red: "#ff5252",
  violet: "#b388ff",
  border: "rgba(0,229,255,0.08)",
  glow: "rgba(0,229,255,0.12)",
};

// ─── Grade colors ───────────────────────────────────────────────────────────
export const gradeColor = (g) => ({
  "A+": C.green, A: C.green, "B+": "#c6ff00", B: C.amber,
  C: "#ff9100", D: C.red, F: C.red, "?": C.fg3,
}[g] || C.fg3);

