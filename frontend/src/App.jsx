import { useState, useEffect, useCallback } from "react";

// ─── Config ──────────────────────────────────────────────────────────────────
const API = import.meta.env.VITE_API_URL || "";

// ─── Color tokens ────────────────────────────────────────────────────────────
const C = {
  bg: "#05080f", bg2: "#0c1220", bg3: "#131d30", bg4: "#1a2740",
  fg: "#e4eaf4", fg2: "#8899b4", fg3: "#556680",
  cyan: "#00e5ff", green: "#00e676", amber: "#ffab00", red: "#ff5252",
  violet: "#b388ff",
  border: "rgba(0,229,255,0.08)",
  glow: "rgba(0,229,255,0.12)",
};

const gradeColor = (g) => ({
  "A+": C.green, A: C.green, "B+": "#c6ff00", B: C.amber,
  C: "#ff9100", D: C.red, F: C.red, "?": C.fg3,
}[g] || C.fg3);

// ─── Demo data (used when API unavailable) ───────────────────────────────────
const DEMO_REPOS = [
  { full_name: "acme/backend-api", name: "backend-api", language: "Python", stars: 42, size_kb: 3200, private: false },
  { full_name: "acme/frontend-app", name: "frontend-app", language: "TypeScript", stars: 18, size_kb: 8400, private: false },
  { full_name: "acme/data-pipeline", name: "data-pipeline", language: "Python", stars: 7, size_kb: 1800, private: true },
  { full_name: "acme/ml-service", name: "ml-service", language: "Python", stars: 3, size_kb: 5100, private: true },
  { full_name: "acme/infra", name: "infra", language: "Shell", stars: 1, size_kb: 420, private: true },
];

const DEMO_AUDIT = {
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
      title: "God module: formatters.py (CC=28, 614 linii)",
      description: "Podziel na mniejsze moduły odpowiedzialne za poszczególne formaty. ReDSL zrobi to automatycznie — split z zachowaniem testów i importów.",
      tool: "redsl", action: "redsl refactor ./src/formatters.py --strategy split --max-cc 10",
    },
    {
      priority: "high", category: "complexity",
      title: "Fan-out: register() 29 zależności → cel: 10",
      description: "Funkcja register() zależy od 29 modułów — złam to przez dependency injection lub registry pattern.",
      tool: "redsl", action: "redsl refactor --target register --strategy reduce-fanout",
    },
    {
      priority: "medium", category: "duplication",
      title: "17 grup duplikacji (218 linii do odzyskania)",
      description: "Ekstrakcja wspólnych wzorców do shared/utils. redup wygeneruje plan, ReDSL go wykona.",
      tool: "redup", action: "redup plan --top 10 --output dedup-plan.json",
    },
    {
      priority: "medium", category: "quality",
      title: "4 błędy typów + 6 ostrzeżeń (mypy + bandit)",
      description: "Brakujące type hints w publicznych API i 2 potencjalne issues bezpieczeństwa (bandit B101, B608).",
      tool: "pyqual", action: "pyqual fix --auto --tools mypy,bandit",
    },
    {
      priority: "low", category: "maintenance",
      title: "4 relative import errors",
      description: "Popraw importy relatywne, które się nie rozwiązują po przeniesieniu plików.",
      tool: "redsl", action: "redsl fix-imports ./src",
    },
  ],
};

// ═══════════════════════════════════════════════════════════════════════════════
// COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════════

function GradeCircle({ grade, score, size = 130 }) {
  const [animatedOffset, setAnimatedOffset] = useState(999);
  const color = gradeColor(grade);
  const r = size / 2 - 10;
  const circ = 2 * Math.PI * r;
  const targetOffset = circ * (1 - (score || 0) / 100);

  useEffect(() => {
    const t = setTimeout(() => setAnimatedOffset(targetOffset), 100);
    return () => clearTimeout(t);
  }, [targetOffset]);

  return (
    <div style={{ position: "relative", width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={C.bg3} strokeWidth="5" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth="5"
          strokeDasharray={circ} strokeDashoffset={animatedOffset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 1.8s cubic-bezier(0.4, 0, 0.2, 1)" }} />
      </svg>
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <span style={{ fontSize: size * 0.3, fontWeight: 800, color, lineHeight: 1 }}>{grade}</span>
        <span style={{ fontSize: size * 0.13, color: C.fg2, marginTop: 3, fontFamily: "'JetBrains Mono', monospace" }}>{score}/100</span>
      </div>
    </div>
  );
}

function MetricCard({ label, value, sub, icon }) {
  return (
    <div style={{
      background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
      padding: "16px 20px", flex: "1 1 140px", minWidth: 140,
    }}>
      <div style={{ fontSize: 12, color: C.fg3, marginBottom: 6, fontFamily: "'JetBrains Mono', monospace" }}>{icon} {label}</div>
      <div style={{ fontSize: 24, fontWeight: 700, color: C.fg, letterSpacing: -0.5 }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: C.fg3, marginTop: 3 }}>{sub}</div>}
    </div>
  );
}

function RecommendationCard({ rec, index }) {
  const [expanded, setExpanded] = useState(false);
  const prioColor = { high: C.red, medium: C.amber, low: C.green }[rec.priority] || C.fg3;
  const prioLabel = { high: "KRYTYCZNY", medium: "WAŻNY", low: "NISKI" }[rec.priority] || rec.priority;

  return (
    <div
      style={{
        background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
        padding: 20, borderLeft: `3px solid ${prioColor}`, cursor: "pointer",
        animation: `fadeUp 0.4s ease-out ${index * 0.08}s both`,
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <span style={{ fontSize: 14, fontWeight: 600, color: C.fg, lineHeight: 1.4 }}>{rec.title}</span>
        <span style={{
          fontSize: 10, fontWeight: 700, color: prioColor, textTransform: "uppercase",
          background: `${prioColor}15`, padding: "3px 8px", borderRadius: 4,
          fontFamily: "'JetBrains Mono', monospace", whiteSpace: "nowrap", flexShrink: 0,
        }}>{prioLabel}</span>
      </div>
      {expanded && (
        <div style={{ marginTop: 12 }}>
          <p style={{ fontSize: 13, color: C.fg2, margin: "0 0 14px", lineHeight: 1.6 }}>{rec.description}</p>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{
              fontSize: 10, color: C.violet, background: `${C.violet}15`, padding: "2px 6px",
              borderRadius: 4, fontFamily: "'JetBrains Mono', monospace", fontWeight: 600,
            }}>{rec.tool}</span>
            <code style={{
              flex: 1, fontSize: 12, color: C.cyan, background: C.bg,
              padding: "8px 12px", borderRadius: 6, fontFamily: "'JetBrains Mono', monospace",
            }}>$ {rec.action}</code>
          </div>
        </div>
      )}
      {!expanded && (
        <div style={{ fontSize: 11, color: C.fg3, marginTop: 8, fontFamily: "'JetBrains Mono', monospace" }}>
          ↳ {rec.tool}: kliknij aby zobaczyć komendę
        </div>
      )}
    </div>
  );
}

function LanguageBar({ languages }) {
  const total = Object.values(languages).reduce((a, b) => a + b, 0);
  const colors = [C.cyan, C.green, C.violet, C.amber, C.red];
  const entries = Object.entries(languages);

  return (
    <div style={{ marginBottom: 32 }}>
      <div style={{ fontSize: 11, color: C.fg3, marginBottom: 8, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>Języki</div>
      <div style={{ display: "flex", gap: 2, height: 8, borderRadius: 4, overflow: "hidden" }}>
        {entries.map(([, lines], i) => (
          <div key={i} style={{ width: `${(lines / total) * 100}%`, background: colors[i % colors.length], transition: "width 1s ease-out" }} />
        ))}
      </div>
      <div style={{ display: "flex", gap: 16, marginTop: 8, flexWrap: "wrap" }}>
        {entries.map(([lang, lines], i) => (
          <span key={lang} style={{ fontSize: 12, color: C.fg2, display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 8, height: 8, borderRadius: "50%", background: colors[i % colors.length] }} />
            {lang} <span style={{ color: C.fg3 }}>({(lines / 1000).toFixed(1)}k)</span>
          </span>
        ))}
      </div>
    </div>
  );
}

function PRCommentPreview() {
  return (
    <div style={{
      background: "#0d1117", border: "1px solid #30363d", borderRadius: 8,
      padding: 24, fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
      fontSize: 14, color: "#e6edf3", maxWidth: 720,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, paddingBottom: 14, borderBottom: "1px solid #21262d" }}>
        <div style={{
          width: 36, height: 36, borderRadius: "50%", background: "linear-gradient(135deg, #00e5ff, #00e676)",
          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 800, color: "#000",
        }}>S</div>
        <div>
          <span style={{ fontWeight: 600, fontSize: 14 }}>semcod-bot</span>
          <span style={{ color: "#7d8590", fontSize: 12, marginLeft: 8 }}>commented 2 minutes ago</span>
        </div>
      </div>

      <h2 style={{ fontSize: 20, margin: "0 0 18px", color: "#e6edf3", fontWeight: 600 }}>
        🟡 Semcod Code Health: <strong>B+</strong> (72/100)
      </h2>

      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 20 }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #21262d" }}>
            <th style={{ textAlign: "left", padding: "10px 0", color: "#7d8590", fontWeight: 500, fontSize: 12 }}>Metryka</th>
            <th style={{ textAlign: "left", padding: "10px 0", color: "#7d8590", fontWeight: 500, fontSize: 12 }}>Wartość</th>
          </tr>
        </thead>
        <tbody>
          {[
            ["Pliki zmienione", "12"],
            ["Dodane linie", "+347"],
            ["Usunięte linie", "-89"],
            ["Złożoność (CC̄)", "4.2 → 4.8 ⚠️"],
            ["Nowe duplikacje", "+2 grupy"],
            ["Testy w PR", "⚠️ Brak"],
          ].map(([k, v]) => (
            <tr key={k} style={{ borderBottom: "1px solid #21262d" }}>
              <td style={{ padding: "10px 0", color: "#e6edf3" }}>{k}</td>
              <td style={{ padding: "10px 0", color: "#e6edf3", fontFamily: "'JetBrains Mono', monospace", fontSize: 13 }}>{v}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={{ fontSize: 15, margin: "20px 0 10px", color: "#e6edf3" }}>⚠️ Duże pliki (&gt;300 zmian)</h3>
      <ul style={{ margin: "0 0 16px", paddingLeft: 20, color: "#e6edf3", lineHeight: 1.8 }}>
        <li><code style={{ background: "#161b22", padding: "2px 8px", borderRadius: 4, fontSize: 13 }}>src/formatters.py</code> — 412 zmian</li>
      </ul>

      <h3 style={{ fontSize: 15, margin: "20px 0 10px", color: "#e6edf3" }}>🎯 Sugerowane poprawki</h3>
      <ul style={{ margin: "0 0 16px", paddingLeft: 20, color: "#e6edf3", lineHeight: 1.8 }}>
        <li>Podziel <code style={{ background: "#161b22", padding: "2px 8px", borderRadius: 4, fontSize: 13 }}>formatters.py</code> — CC=28 (cel: ≤10)</li>
        <li>Dodaj testy dla nowych endpointów</li>
        <li>2 nowe duplikacje z <code style={{ background: "#161b22", padding: "2px 8px", borderRadius: 4, fontSize: 13 }}>utils/parse.py</code></li>
      </ul>

      <blockquote style={{
        borderLeft: "3px solid #1f6feb", padding: "10px 16px", margin: "16px 0",
        color: "#7d8590", background: "#161b22", borderRadius: "0 6px 6px 0", fontSize: 13,
      }}>
        💡 <strong style={{ color: "#e6edf3" }}>Auto-fix dostępny:</strong> <code style={{ background: "#21262d", padding: "2px 6px", borderRadius: 3 }}>redsl refactor --pr 47 --auto</code> naprawi 3 z 5 problemów automatycznie.
      </blockquote>

      <hr style={{ border: "none", borderTop: "1px solid #21262d", margin: "18px 0" }} />
      <sub style={{ color: "#7d8590" }}>
        🔬 <a href="#" style={{ color: "#58a6ff" }}>Semcod</a> · audyt: <code style={{ background: "#161b22", padding: "1px 4px", borderRadius: 3 }}>a3f7b2c</code> · <a href="#" style={{ color: "#58a6ff" }}>pełny raport</a> · <a href="#" style={{ color: "#58a6ff" }}>dashboard</a>
      </sub>
    </div>
  );
}

function BadgeSVG({ grade, score, width = 152 }) {
  const color = gradeColor(grade);
  const labelW = 82;
  const valueText = score != null ? `${grade} · ${score}%` : grade;
  const valueW = width - labelW;

  return (
    <svg width={width} height="20" role="img" style={{ display: "block" }}>
      <defs>
        <linearGradient id="bg" x2="0" y2="100%">
          <stop offset="0" stopColor="#bbb" stopOpacity=".1" />
          <stop offset="1" stopOpacity=".1" />
        </linearGradient>
        <clipPath id="cr"><rect width={width} height="20" rx="3" /></clipPath>
      </defs>
      <g clipPath="url(#cr)">
        <rect width={labelW} height="20" fill="#555" />
        <rect x={labelW} width={valueW} height="20" fill={color} />
        <rect width={width} height="20" fill="url(#bg)" />
      </g>
      <g fill="#fff" textAnchor="middle" fontFamily="Verdana,Geneva,sans-serif" fontSize="11">
        <text x={labelW / 2} y="15" fillOpacity=".3" fill="#010101">code health</text>
        <text x={labelW / 2} y="14">code health</text>
        <text x={labelW + valueW / 2} y="15" fillOpacity=".3" fill="#010101">{valueText}</text>
        <text x={labelW + valueW / 2} y="14">{valueText}</text>
      </g>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════════════════════

export default function App() {
  const [tab, setTab] = useState("audit");
  const [phase, setPhase] = useState("landing"); // landing → repos → scanning → result
  const [repos, setRepos] = useState([]);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [scanLabel, setScanLabel] = useState("");
  const [audit, setAudit] = useState(null);
  const [badgeRepo, setBadgeRepo] = useState("acme/backend-api");
  const [token, setToken] = useState(null);

  // Check for OAuth token in URL
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get("token");
    if (t) {
      setToken(t);
      setPhase("repos");
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, []);

  // Fetch repos when token available
  useEffect(() => {
    if (!token || phase !== "repos") return;
    fetch(`${API}/api/repos?token=${token}`)
      .then((r) => r.json())
      .then(setRepos)
      .catch(() => setRepos(DEMO_REPOS));
  }, [token, phase]);

  // Scan animation
  useEffect(() => {
    if (phase !== "scanning") return;
    setScanProgress(0);
    const steps = [
      { p: 8, t: 300, l: "⏳ Klonowanie repozytorium..." },
      { p: 20, t: 700, l: "🔬 code2llm: analiza CFG, DFG, call graphs..." },
      { p: 35, t: 1300, l: "🔁 redup: detekcja duplikacji (AST)..." },
      { p: 50, t: 1900, l: "🧹 pyqual: quality gates (ruff + mypy + bandit)..." },
      { p: 65, t: 2500, l: "📉 regix: indeks regresji..." },
      { p: 80, t: 3100, l: "✅ vallm: walidacja wyników..." },
      { p: 92, t: 3600, l: "📊 Generowanie raportu i badge..." },
      { p: 100, t: 4000, l: "✅ Gotowe!" },
    ];
    const timers = steps.map(({ p, t, l }) =>
      setTimeout(() => { setScanProgress(p); setScanLabel(l); }, t)
    );
    const done = setTimeout(() => { setAudit(DEMO_AUDIT); setPhase("result"); }, 4500);
    return () => { timers.forEach(clearTimeout); clearTimeout(done); };
  }, [phase]);

  const startOAuth = () => {
    // In production: redirect to API OAuth endpoint
    // window.location.href = `${API}/auth/github`;
    // Demo mode: skip OAuth, show demo repos
    setRepos(DEMO_REPOS);
    setPhase("repos");
  };

  const startAudit = useCallback((repo) => {
    setSelectedRepo(repo);
    setPhase("scanning");

    // In production: POST to API
    if (token) {
      fetch(`${API}/api/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo: repo.full_name, token }),
      }).catch(() => {});
    }
  }, [token]);

  const reset = () => { setPhase("landing"); setSelectedRepo(null); setAudit(null); };

  const tabBtn = (id, label) => (
    <button
      onClick={() => { setTab(id); if (id === "audit") reset(); }}
      style={{
        padding: "12px 20px", cursor: "pointer", fontSize: 13, fontWeight: 600,
        color: tab === id ? C.cyan : C.fg3, background: "transparent", border: "none",
        borderBottom: `2px solid ${tab === id ? C.cyan : "transparent"}`,
        fontFamily: "'JetBrains Mono', monospace", transition: "all 0.2s",
      }}
    >{label}</button>
  );

  return (
    <div style={{ minHeight: "100vh" }}>
      {/* ─── Header ─── */}
      <header style={{
        borderBottom: `1px solid ${C.border}`, padding: "0 24px",
        background: "rgba(5,8,15,0.92)", backdropFilter: "blur(24px)",
        position: "sticky", top: 0, zIndex: 50,
      }}>
        <div style={{ maxWidth: 1000, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 58 }}>
          <span onClick={reset} style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: 18, color: C.cyan, cursor: "pointer" }}>
            semcod<span style={{ color: C.fg3 }}>.dev</span>
          </span>
          <nav style={{ display: "flex" }}>
            {tabBtn("audit", "Audit")}
            {tabBtn("prbot", "PR Bot")}
            {tabBtn("badge", "Badge")}
          </nav>
        </div>
      </header>

      <main style={{ maxWidth: 1000, margin: "0 auto", padding: "32px 24px 80px" }}>

        {/* ═══════ AUDIT TAB ═══════ */}
        {tab === "audit" && (
          <>
            {phase === "landing" && (
              <div style={{ textAlign: "center", padding: "80px 0 60px" }}>
                <div style={{
                  display: "inline-flex", alignItems: "center", gap: 8,
                  background: C.glow, border: `1px solid ${C.border}`,
                  padding: "6px 16px", borderRadius: 99, fontSize: 12,
                  fontFamily: "'JetBrains Mono', monospace", color: C.cyan, marginBottom: 28,
                }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.green, animation: "pulse 2s infinite" }} />
                  8 narzędzi · 468 testów · free for public repos
                </div>

                <h1 style={{ fontSize: "clamp(2rem, 5vw, 3.2rem)", fontWeight: 800, letterSpacing: -1.5, lineHeight: 1.1, marginBottom: 20 }}>
                  Sprawdź{" "}
                  <span style={{ background: `linear-gradient(135deg, ${C.cyan}, ${C.green})`, WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                    zdrowie kodu
                  </span>
                  <br />jednym kliknięciem
                </h1>

                <p style={{ fontSize: 17, color: C.fg2, maxWidth: 520, margin: "0 auto 36px", lineHeight: 1.65 }}>
                  Podłącz GitHub → wybierz repo → 60 sekund → raport z metrykami,
                  rekomendacjami i komendami ReDSL do naprawy. Plus badge do README.
                </p>

                <button onClick={startOAuth} style={{
                  display: "inline-flex", alignItems: "center", gap: 10,
                  background: C.fg, color: C.bg, border: "none", borderRadius: 10,
                  padding: "16px 36px", fontSize: 16, fontWeight: 700, cursor: "pointer",
                  fontFamily: "inherit", transition: "all 0.2s",
                }}
                  onMouseOver={(e) => e.currentTarget.style.transform = "translateY(-2px)"}
                  onMouseOut={(e) => e.currentTarget.style.transform = "none"}
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/></svg>
                  Połącz z GitHub
                </button>

                <p style={{ fontSize: 12, color: C.fg3, marginTop: 20, fontFamily: "'JetBrains Mono', monospace" }}>
                  read-only access · dane nie są przechowywane · open-source pipeline
                </p>
              </div>
            )}

            {phase === "repos" && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
                  <h2 style={{ fontSize: 22, fontWeight: 700 }}>Wybierz repozytorium</h2>
                  <button onClick={reset} style={{ background: "none", border: "none", color: C.fg3, cursor: "pointer", fontSize: 13 }}>← Wróć</button>
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {(repos.length ? repos : DEMO_REPOS).map((repo) => (
                    <button key={repo.full_name} onClick={() => startAudit(repo)} style={{
                      display: "flex", alignItems: "center", justifyContent: "space-between",
                      background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10,
                      padding: "18px 22px", cursor: "pointer", color: C.fg, fontFamily: "inherit",
                      transition: "all 0.15s", textAlign: "left", width: "100%",
                    }}
                      onMouseOver={(e) => { e.currentTarget.style.borderColor = `${C.cyan}40`; e.currentTarget.style.background = C.bg3; }}
                      onMouseOut={(e) => { e.currentTarget.style.borderColor = C.border; e.currentTarget.style.background = C.bg2; }}
                    >
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 15 }}>{repo.full_name}</div>
                        <div style={{ fontSize: 12, color: C.fg3, marginTop: 5, fontFamily: "'JetBrains Mono', monospace" }}>
                          {repo.language || "—"} · {(repo.size_kb / 1024).toFixed(1)} MB · ⭐ {repo.stars}
                          {repo.private && <span style={{ marginLeft: 8, color: C.amber }}>🔒 private</span>}
                        </div>
                      </div>
                      <span style={{ color: C.cyan, fontSize: 13, fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>Skanuj →</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {phase === "scanning" && (
              <div style={{ textAlign: "center", padding: "100px 0" }}>
                <div style={{ fontSize: 15, color: C.fg2, marginBottom: 28, fontFamily: "'JetBrains Mono', monospace" }}>
                  Analizuję <span style={{ color: C.cyan, fontWeight: 600 }}>{selectedRepo?.full_name}</span>
                </div>
                <div style={{ width: 360, maxWidth: "100%", height: 6, background: C.bg3, borderRadius: 3, margin: "0 auto 16px", overflow: "hidden" }}>
                  <div style={{
                    width: `${scanProgress}%`, height: "100%", borderRadius: 3,
                    background: `linear-gradient(90deg, ${C.cyan}, ${C.green})`,
                    transition: "width 0.4s ease-out",
                    boxShadow: `0 0 12px ${C.cyan}40`,
                  }} />
                </div>
                <div style={{ fontSize: 12, color: C.fg3, fontFamily: "'JetBrains Mono', monospace", height: 20 }}>
                  {scanLabel}
                </div>
              </div>
            )}

            {phase === "result" && audit && (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
                  <h2 style={{ fontSize: 22, fontWeight: 700 }}>
                    <span style={{ color: C.fg3 }}>Raport:</span> {selectedRepo?.full_name}
                  </h2>
                  <button onClick={reset} style={{
                    background: C.bg3, border: `1px solid ${C.border}`, color: C.fg2,
                    cursor: "pointer", fontSize: 13, padding: "8px 16px", borderRadius: 8,
                    fontFamily: "inherit",
                  }}>Nowy audyt</button>
                </div>

                {/* Score + metrics */}
                <div style={{ display: "flex", gap: 20, alignItems: "center", flexWrap: "wrap", marginBottom: 32 }}>
                  <GradeCircle grade={audit.grade} score={audit.health_score} />
                  <div style={{ display: "flex", gap: 10, flexWrap: "wrap", flex: 1 }}>
                    <MetricCard icon="📁" label="PLIKI" value={audit.stats.total_files} sub={`${(audit.stats.total_lines / 1000).toFixed(1)}k linii`} />
                    <MetricCard icon="🔬" label="CC̄" value={audit.metrics.complexity.cc_avg.toFixed(1)} sub={`${audit.metrics.complexity.functions} funkcji`} />
                    <MetricCard icon="🔁" label="DUPLIKACJE" value={audit.metrics.duplication.duplication_groups} sub={`${audit.metrics.duplication.recoverable_lines} linii do odzysk.`} />
                    <MetricCard icon="✅" label="QUALITY" value={`${audit.metrics.quality.passed}/${audit.metrics.quality.passed + audit.metrics.quality.errors}`} sub={`${audit.metrics.quality.warnings} ostrzeżeń`} />
                  </div>
                </div>

                <LanguageBar languages={audit.stats.languages} />

                {/* Target metrics */}
                <div style={{
                  background: C.glow, border: `1px solid ${C.border}`, borderRadius: 10,
                  padding: "16px 20px", marginBottom: 24, display: "flex", gap: 24, flexWrap: "wrap",
                  fontFamily: "'JetBrains Mono', monospace", fontSize: 13,
                }}>
                  <span style={{ color: C.fg2 }}>📈 Po ReDSL:</span>
                  <span>CC̄ <span style={{ color: C.fg3 }}>4.2</span><span style={{ color: C.green }}> → 2.8</span></span>
                  <span>duplikacje <span style={{ color: C.fg3 }}>17</span><span style={{ color: C.green }}> → 0</span></span>
                  <span>god modules <span style={{ color: C.fg3 }}>1</span><span style={{ color: C.green }}> → 0</span></span>
                  <span style={{ color: C.amber }}>est. koszt LLM: $0.41</span>
                </div>

                {/* Recommendations */}
                <div style={{ marginBottom: 32 }}>
                  <div style={{ fontSize: 11, color: C.fg3, marginBottom: 14, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>
                    Rekomendacje ({audit.recommendations.length})
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {audit.recommendations.map((rec, i) => <RecommendationCard key={i} rec={rec} index={i} />)}
                  </div>
                </div>

                {/* Badge */}
                <div style={{
                  background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 22,
                }}>
                  <div style={{ fontSize: 11, color: C.fg3, marginBottom: 12, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>Badge do README</div>
                  <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
                    <BadgeSVG grade={audit.grade} score={audit.health_score} />
                    <code style={{
                      flex: 1, fontSize: 11, color: C.fg2, background: C.bg, padding: "10px 14px",
                      borderRadius: 8, fontFamily: "'JetBrains Mono', monospace", lineHeight: 1.5,
                      wordBreak: "break-all", minWidth: 200,
                    }}>
                      {`[![Code Health](https://semcod.dev/badge/${selectedRepo?.full_name.replace("/", "-")}.svg)](https://semcod.dev/report/${selectedRepo?.full_name})`}
                    </code>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

        {/* ═══════ PR BOT TAB ═══════ */}
        {tab === "prbot" && (
          <div>
            <div style={{ marginBottom: 32 }}>
              <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 10 }}>PR Comment Bot</h2>
              <p style={{ color: C.fg2, fontSize: 15, lineHeight: 1.65, maxWidth: 640 }}>
                Automatyczny komentarz przy każdym Pull Request z metrykami jakości, flagami ryzyka,
                sugestiami ReDSL i jednolinijkową komendą do auto-fix.
                Instalacja: GitHub App → wybierz repozytoria → gotowe.
              </p>
            </div>

            <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginBottom: 36 }}>
              {[
                { icon: "⚡", title: "Automatyczny", desc: "Komentuje każdy PR w <30 sekund po otwarciu lub push" },
                { icon: "🎯", title: "Precyzyjny", desc: "CC delta, nowe duplikacje, brak testów, ryzykowne pliki" },
                { icon: "🔧", title: "Actionable", desc: "Konkretne komendy ReDSL/redup/pyqual do naprawy" },
                { icon: "🔒", title: "Read-only", desc: "Nie modyfikuje kodu — tylko komentuje i ustawia status" },
              ].map(({ icon, title, desc }) => (
                <div key={title} style={{
                  flex: "1 1 200px", background: C.bg2, border: `1px solid ${C.border}`,
                  borderRadius: 10, padding: 20,
                }}>
                  <div style={{ fontSize: 24, marginBottom: 8 }}>{icon}</div>
                  <div style={{ fontWeight: 600, marginBottom: 4, fontSize: 14 }}>{title}</div>
                  <div style={{ fontSize: 13, color: C.fg3, lineHeight: 1.5 }}>{desc}</div>
                </div>
              ))}
            </div>

            <div style={{ fontSize: 11, color: C.fg3, marginBottom: 14, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>
              Przykład komentarza w PR
            </div>
            <PRCommentPreview />

            <div style={{
              marginTop: 24, background: C.glow, border: `1px solid ${C.border}`, borderRadius: 10,
              padding: "16px 20px", fontSize: 13, color: C.fg2, lineHeight: 1.6,
            }}>
              <strong style={{ color: C.cyan }}>Webhook events:</strong> pull_request.opened, pull_request.synchronize →
              analiza diff → komentarz + commit status (success/pending/failure).
            </div>
          </div>
        )}

        {/* ═══════ BADGE TAB ═══════ */}
        {tab === "badge" && (
          <div>
            <div style={{ marginBottom: 32 }}>
              <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 10 }}>Code Health Badge</h2>
              <p style={{ color: C.fg2, fontSize: 15, lineHeight: 1.65, maxWidth: 640 }}>
                Dynamiczny badge do README. Aktualizuje się automatycznie przy każdym push.
                Każdy kto widzi badge → klika → sprawdza swoje repo → instaluje app.
              </p>
            </div>

            <div style={{ background: C.bg2, border: `1px solid ${C.border}`, borderRadius: 10, padding: 24 }}>
              <div style={{ fontSize: 13, color: C.fg3, marginBottom: 10 }}>Wpisz owner/repo:</div>
              <input
                value={badgeRepo}
                onChange={(e) => setBadgeRepo(e.target.value)}
                style={{
                  width: "100%", maxWidth: 420, background: C.bg, border: `1px solid ${C.border}`,
                  borderRadius: 8, padding: "12px 16px", color: C.fg, fontSize: 14,
                  fontFamily: "'JetBrains Mono', monospace", outline: "none", transition: "border-color 0.2s",
                }}
                onFocus={(e) => e.target.style.borderColor = C.cyan}
                onBlur={(e) => e.target.style.borderColor = C.border}
                placeholder="owner/repo"
              />

              <div style={{ marginTop: 28, display: "flex", flexDirection: "column", gap: 24 }}>
                <div>
                  <div style={{ fontSize: 11, color: C.fg3, marginBottom: 10, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>Preview</div>
                  <div style={{ display: "flex", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
                    {[
                      { g: "A+", s: 95 }, { g: "A", s: 82 }, { g: "B+", s: 72 },
                      { g: "B", s: 63 }, { g: "C", s: 48 }, { g: "F", s: 22 },
                    ].map(({ g, s }) => <BadgeSVG key={g} grade={g} score={s} />)}
                  </div>
                </div>

                {[
                  { label: "MARKDOWN", color: C.cyan, code: `[![Code Health](https://semcod.dev/badge/${badgeRepo.replace("/", "-")}.svg)](https://semcod.dev/report/${badgeRepo})` },
                  { label: "HTML", color: C.green, code: `<a href="https://semcod.dev/report/${badgeRepo}"><img src="https://semcod.dev/badge/${badgeRepo.replace("/", "-")}.svg" alt="Code Health" /></a>` },
                  { label: "ENDPOINT", color: C.violet, code: `GET https://semcod.dev/badge/${badgeRepo.replace("/", "-")}.svg` },
                ].map(({ label, color, code }) => (
                  <div key={label}>
                    <div style={{ fontSize: 11, color: C.fg3, marginBottom: 8, fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: 1.5 }}>{label}</div>
                    <code style={{
                      display: "block", fontSize: 12, color, background: C.bg,
                      padding: "12px 16px", borderRadius: 8, fontFamily: "'JetBrains Mono', monospace",
                      lineHeight: 1.6, wordBreak: "break-all",
                    }}>{code}</code>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
