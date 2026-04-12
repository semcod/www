# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   React     │  │   Vite      │  │    React Hooks          │  │
│  │   Components│  │   Build     │  │    (useAppState)        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                            │
│              │   REST API Calls    │                            │
│              └─────────────────────┘                            │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND                                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Server                        │   │
│  │  ┌──────────┬──────────┬──────────┬──────────┬─────────┐ │   │
│  │  │  Auth    │  Audit   │  Badge   │ Metrics  │ Webhook │ │   │
│  │  │  Router  │  Router  │  Router  │  Router  │  Router │ │   │
│  │  └──────────┴──────────┴──────────┴──────────┴─────────┘ │   │
│  │  ┌──────────┬──────────┬──────────┬────────────────────┐ │   │
│  │  │   MCP    │  Report  │  Health  │    API Router      │ │   │
│  │  │  Router  │  Router  │  Router  │    (Consolidated)  │ │   │
│  │  └──────────┴──────────┴──────────┴────────────────────┘ │   │
│  │  ┌──────────────────┬──────────────────────────────────┐ │   │
│  │  │  Benchmark       │  ReDSL                           │ │   │
│  │  │  Router          │  Router                          │ │   │
│  │  └──────────────────┴──────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │    Services         │  │           Database              │   │
│  │  ┌───────────────┐  │  │  ┌───────────────────────────┐  │   │
│  │  │  Analyzer     │  │  │  │    SQLite (scans.db)      │  │   │
│  │  │  (code2llm)   │  │  │  │  - scans table            │  │   │
│  │  ├───────────────┤  │  │  │  - badges cache           │  │   │
│  │  │  Scoring      │  │  │  │  - benchmark_cases        │  │   │
│  │  │  (health)     │  │  │  │  - benchmark_events       │  │   │
│  │  ├───────────────┤  │  │  │  - recommendation_feedback│  │   │
│  │  │  GitHub Client│  │  │  └───────────────────────────┘  │   │
│  │  ├───────────────┤  │  └─────────────────────────────────┘   │
│  │  │  RedslClient  │  │                                        │
│  │  │  (reDSL HTTP) │  │                                        │
│  │  └───────────────┘  │  ┌─────────────────────────────────┐   │
│  └─────────────────────┘  │        In-Memory Store          │   │
│                           │    - audit_results (dict)       │   │
│                           │    - badge_cache (dict)         │   │
│                           │    - scan_history (list)        │   │
│                           └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                           │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   GitHub     │  │   GitLab     │  │   Bitbucket          │   │
│  │   API        │  │   API        │  │   API                │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 Analysis Tools                             │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │ │
│  │  │ code2llm   │  │   redup    │  │     pyqual         │    │ │
│  │  │(complexity)│  │(duplication│  │  (quality check)   │    │ │
│  │  └────────────┘  └────────────┘  └────────────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 ReDSL Engine (separate service)            │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │ │
│  │  │  analyze   │  │  refactor  │  │  health_score      │    │ │
│  │  │            │  │(15 actions)│  │  (grade + metrics) │    │ │
│  │  └────────────┘  └────────────┘  └────────────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React + Vite)

**Structure:**
```
frontend/src/
├── App.jsx              # Main application component
├── api.js               # API client functions
├── constants.js         # App constants
├── components/
│   ├── Header.jsx       # Navigation header
│   ├── LanguageBar.jsx  # Language distribution bar
│   ├── MetricCard.jsx   # Metric display card
│   ├── GradeCircle.jsx  # Grade visualization
│   ├── ProgressSteps.jsx # Progress indicator
│   ├── RecommendationCard.jsx
│   ├── phases/          # Application phases
│   │   ├── AuthPhase.jsx
│   │   ├── LandingPhase.jsx
│   │   ├── ReposPhase.jsx
│   │   ├── ScanningPhase.jsx
│   │   └── ResultPhase.jsx
│   ├── benchmark/       # Benchmark KPI components
│   │   ├── BenchmarkReviewPanel.jsx
│   │   ├── RecommendationFeedbackForm.jsx
│   │   └── BenchmarkDecisionPanel.jsx
│   └── tabs/            # Result tabs
│       ├── BadgeTab.jsx
│       ├── PRBotTab.jsx
│       ├── RecentScansTab.jsx
│       └── RepoTab.jsx
├── hooks/
│   └── useAppState.js    # Main state management hook
└── screens/             # Page screens
```

**State Management:**
- Single `useAppState` hook manages entire app state
- URL-based routing with hash parameters
- No external state library (React hooks only)

---

### Backend (FastAPI)

**Router Structure:**

| Router | File | Purpose |
|--------|------|---------|
| Auth | `routers/auth.py` | GitHub OAuth flow |
| Audit | `routers/audit.py` | Repository analysis pipeline |
| Badge | `routers/badge.py` | SVG badge generation |
| Metrics | `routers/metrics.py` | Standardized metrics API |
| MCP | `routers/mcp.py` | AI assistant integration |
| Report | `routers/report.py` | Report redirects |
| Webhook | `routers/webhook.py` | GitHub webhooks |
| Benchmark | `routers/benchmark.py` | KPI benchmark (cases, feedback, decisions, events, export) |
| ReDSL | `routers/redsl.py` | reDSL engine (analyze, refactor, health, decide, badge) |

**Services:**

| Service | File | Purpose |
|---------|------|---------|
| Analyzer | `services/analyzer.py` | Code statistics collection |
| Scoring | `services/scoring.py` | Health score calculation + recommendation_id |
| GitHub Client | `services/github_client.py` | GitHub API integration |
| RedslClient | `services/redsl_client.py` | ReDSL engine HTTP client |

---

## Data Flow

### 1. Audit Flow

```
User → Frontend → POST /api/audit → Backend
                                      │
                                      ▼
                              ┌──────────────┐
                              │ Generate     │
                              │ audit_id     │
                              └──────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │ Schedule     │
                              │ Background   │
                              │ Task         │
                              └──────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────┐
│                    BACKGROUND PIPELINE                       │
│  1. Clone repo → 2. Count stats → 3. Run tools → 4. Score    │
│                                                              │
│  Tools: code2llm (complexity)                                │
│         redup (duplication)                                  │
│         pyqual (quality)                                     │
└──────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │ Save Results │
                              │ - SQLite     │
                              │ - Memory     │
                              └──────────────┘
```

### 2. Badge Flow

```
Request: GET /badge/{repo}.svg
                │
                ▼
        ┌───────────────┐
        │ Check Cache   │
        │ (badge_cache) │
        └───────────────┘
                │
        ┌───────┴───────┐
        │               │
    Cache Hit        Cache Miss
        │               │
        ▼               ▼
   Return SVG    Generate Default
   from Cache    SVG Badge
```

### 3. Metrics Flow

```
Request: GET /api/metrics/standard
                │
                ▼
        ┌───────────────┐
        │ Query SQLite  │
        │ (scans table) │
        └───────────────┘
                │
                ▼
        ┌───────────────┐
        │ Format Data   │
        │ - Platform    │
        │ - Metrics     │
        │ - Grades      │
        └───────────────┘
                │
                ▼
        Return JSON
```

---

## Database Schema

### SQLite (`scans.db`)

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_id TEXT UNIQUE,
    repo TEXT NOT NULL,
    health_score INTEGER,
    grade TEXT,
    stats TEXT,           -- JSON
    completed TEXT,       -- ISO timestamp
    badge_url TEXT
);

CREATE TABLE badges (
    repo TEXT PRIMARY KEY,
    score INTEGER,
    grade TEXT,
    weekly_issues INTEGER,
    updated TEXT          -- ISO timestamp
);

CREATE TABLE benchmark_cases (
    case_id TEXT PRIMARY KEY,
    audit_id TEXT,
    repo TEXT NOT NULL,
    source_type TEXT DEFAULT 'repo',
    change_type TEXT,
    baseline_tools TEXT,      -- JSON
    baseline_findings TEXT,
    baseline_detected BOOLEAN,
    reviewer_verdict TEXT,
    recommendation_accepted BOOLEAN,
    pr_candidate BOOLEAN,
    deployment_candidate BOOLEAN,
    deployment_model_selected TEXT,
    time_to_first_result_seconds INTEGER,
    time_to_first_useful_recommendation_seconds INTEGER,
    next_action TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE benchmark_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT REFERENCES benchmark_cases(case_id),
    audit_id TEXT,
    event_name TEXT NOT NULL,
    event_value TEXT,
    metadata_json TEXT,       -- JSON
    created_at TEXT
);

CREATE TABLE recommendation_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT REFERENCES benchmark_cases(case_id),
    audit_id TEXT,
    recommendation_id TEXT NOT NULL,
    accepted BOOLEAN,
    novelty_score INTEGER,         -- 0-3
    usefulness_score INTEGER,     -- 0-3
    accuracy_score INTEGER,       -- 0-3
    actionability_score INTEGER,  -- 0-3
    business_value_score INTEGER, -- 0-3
    notes TEXT,
    created_at TEXT
);
```

### In-Memory Store

```python
audit_results: dict[str, dict]  # Running/completed audits
badge_cache: dict[str, dict]    # Cached badge data
scan_history: list[dict]         # Recent scans (last 100)
```

---

## MCP Integration

MCP (Model Context Protocol) allows AI assistants to interact with Semcod:

```
AI Assistant (Claude/Cascade)
            │
            │ MCP Protocol
            ▼
    ┌───────────────┐
    │ /mcp endpoints│
    │ - /resources  │
    │ - /tools      │
    │ - /invoke     │
    └───────────────┘
            │
            ▼
    Backend Services
```

**Resources:**
- `scans://list` - JSON list of scans
- `scan://{id}` - Single scan details
- `metrics://summary` - Aggregated stats
- `badge://{repo}` - Badge status

**Tools:**
- `start_audit` - Begin new audit
- `get_scan_status` - Check progress
- `get_repository_metrics` - Get repo data
- `analyze_public_repo` - Sandbox analysis

---

## Deployment

### Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///data/scans.db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

### Production Setup

1. **Backend** - FastAPI + Uvicorn
2. **Frontend** - Static files served by Nginx
3. **Database** - SQLite (migratable to PostgreSQL)
4. **Cache** - In-memory with Redis option

---

## Security Considerations

- **OAuth Tokens** - Stored client-side only
- **Webhook Signatures** - Verified with GitHub secret
- **CORS** - Configured for specific origins
- **Rate Limiting** - Applied per IP/token
- **Sandbox Mode** - Public repos only, no token needed
