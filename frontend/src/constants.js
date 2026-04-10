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

// ─── Demo data (used when API unavailable) ───────────────────────────────────
export const DEMO_REPOS = [
  { full_name: "acme/backend-api", name: "backend-api", language: "Python", stars: 42, size_kb: 3200, private: false },
  { full_name: "acme/frontend-app", name: "frontend-app", language: "TypeScript", stars: 18, size_kb: 8400, private: false },
  { full_name: "acme/data-pipeline", name: "data-pipeline", language: "Python", stars: 7, size_kb: 1800, private: true },
  { full_name: "acme/ml-service", name: "ml-service", language: "Python", stars: 3, size_kb: 5100, private: true },
  { full_name: "acme/infra", name: "infra", language: "Shell", stars: 1, size_kb: 420, private: true },
];

export const DEMO_AUDIT = {
  status: "complete",
  health_score: 72,
  grade: "B+",
  stats: { total_files: 114, total_lines: 19151, languages: { Python: 16200, Shell: 1800, JavaScript: 1151 } },
  metrics: {
    complexity: { cc_avg: 4.2, functions: 395, classes: 56, modules: 12 },
    duplication: { duplication_groups: 17, duplicated_lines: 418, recoverable_lines: 218 },
    quality: { passed: 135, warnings: 6, errors: 4, score: 82 },
  },
  recommendations: [
    {
      priority: "high", category: "complexity",
      title: "God module: formatters.py (CC=28, 614 lines)",
      description: "Split into smaller modules responsible for specific formats. ReDSL will do this automatically — split while preserving tests and imports.",
      tool: "redsl", action: "redsl refactor ./src/formatters.py --strategy split --max-cc 10",
    },
    {
      priority: "high", category: "complexity",
      title: "Fan-out: register() 29 dependencies → target: 10",
      description: "The register() function depends on 29 modules — break this with dependency injection or registry pattern.",
      tool: "redsl", action: "redsl refactor --target register --strategy reduce-fanout",
    },
    {
      priority: "medium", category: "duplication",
      title: "17 duplication groups (218 lines recoverable)",
      description: "Extract common patterns to shared/utils. redup generates plan, ReDSL executes it.",
      tool: "redup", action: "redup plan --top 10 --output dedup-plan.json",
    },
    {
      priority: "medium", category: "quality",
      title: "4 type errors + 6 warnings (mypy + bandit)",
      description: "Missing type hints in public APIs and 2 potential security issues (bandit B101, B608).",
      tool: "pyqual", action: "pyqual fix --auto --tools mypy,bandit",
    },
    {
      priority: "low", category: "maintenance",
      title: "4 relative import errors",
      description: "Fix relative imports that don't resolve after moving files.",
      tool: "redsl", action: "redsl fix-imports ./src",
    },
  ],
};
