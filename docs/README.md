<!-- code2docs:start --># www

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.8-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-245-green)
> **245** functions | **4** classes | **73** files | CC̄ = 3.0

> Auto-generated project documentation from source code analysis.

**Author:** Tom Softreck <tom@sapletta.com>  
**License:** Not specified  
**Repository:** [https://github.com/semcod/www](https://github.com/semcod/www)

## Installation

### From PyPI

```bash
pip install www
```

### From Source

```bash
git clone https://github.com/semcod/www
cd www
pip install -e .
```

### Optional Extras

```bash
pip install www[dev]    # development tools
```

## Quick Start

### CLI Usage

```bash
# Generate full documentation for your project
www ./my-project

# Only regenerate README
www ./my-project --readme-only

# Preview what would be generated (no file writes)
www ./my-project --dry-run

# Check documentation health
www check ./my-project

# Sync — regenerate only changed modules
www sync ./my-project
```

### Python API

```python
from www import generate_readme, generate_docs, Code2DocsConfig

# Quick: generate README
generate_readme("./my-project")

# Full: generate all documentation
config = Code2DocsConfig(project_name="mylib", verbose=True)
docs = generate_docs("./my-project", config=config)
```

## Generated Output

When you run `www`, the following files are produced:

```
<project>/
├── README.md                 # Main project README (auto-generated sections)
├── docs/
│   ├── api.md               # Consolidated API reference
│   ├── modules.md           # Module documentation with metrics
│   ├── architecture.md      # Architecture overview with diagrams
│   ├── dependency-graph.md  # Module dependency graphs
│   ├── coverage.md          # Docstring coverage report
│   ├── getting-started.md   # Getting started guide
│   ├── configuration.md    # Configuration reference
│   └── api-changelog.md    # API change tracking
├── examples/
│   ├── quickstart.py       # Basic usage examples
│   └── advanced_usage.py   # Advanced usage examples
├── CONTRIBUTING.md         # Contribution guidelines
└── mkdocs.yml             # MkDocs site configuration
```

## Configuration

Create `www.yaml` in your project root (or run `www init`):

```yaml
project:
  name: my-project
  source: ./
  output: ./docs/

readme:
  sections:
    - overview
    - install
    - quickstart
    - api
    - structure
  badges:
    - version
    - python
    - coverage
  sync_markers: true

docs:
  api_reference: true
  module_docs: true
  architecture: true
  changelog: true

examples:
  auto_generate: true
  from_entry_points: true

sync:
  strategy: markers    # markers | full | git-diff
  watch: false
  ignore:
    - "tests/"
    - "__pycache__"
```

## Sync Markers

www can update only specific sections of an existing README using HTML comment markers:

```markdown
<!-- www:start -->
# Project Title
... auto-generated content ...
<!-- www:end -->
```

Content outside the markers is preserved when regenerating. Enable this with `sync_markers: true` in your configuration.

## Architecture

```
www/
├── project    ├── generate-certs    ├── config    ├── database    ├── sample_projects    ├── server_new        ├── scoring        ├── analyzer    ├── services/    ├── store        ├── github_client        ├── system        ├── scan_samples    ├── server    ├── routers/        ├── metrics        ├── auth        ├── report        ├── badge        ├── config        ├── config        ├── constants        ├── config        ├── api        ├── App        ├── webhook        ├── main            ├── Header            ├── LanguageBar            ├── ProgressSteps            ├── MetricCard            ├── RecommendationCard            ├── PRCommentPreview            ├── GradeCircle        ├── components/            ├── useAppState                ├── AuthPhase            ├── phases/                ├── ScanningPhase        ├── audit                ├── LandingPhase                ├── LanguageBar                ├── MetricCard                ├── RecommendationCard                ├── GradeCircle            ├── ui/                ├── ReposPhase                ├── RepoTab                ├── PRBotTab            ├── tabs/                ├── BadgeTab        ├── screens/            ├── share            ├── spec            ├── spec                ├── RecentScansTab                ├── ResultPhase            ├── spec            ├── spec            ├── spec            ├── spec        ├── config            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec        ├── mcp```

## API Overview

### Classes

- **`MCPResource`** — MCP Resource definition.
- **`MCPTool`** — MCP Tool definition.
- **`MCPResourceResponse`** — MCP resource content response.
- **`MCPToolRequest`** — MCP tool invocation request.

### Functions

- `init_db()` — Initialize the database and create tables.
- `save_scan(scan_data)` — Save a scan to the database.
- `get_recent_scans(limit)` — Get recent scans from the database.
- `get_total_scan_count()` — Get total number of scans in the database.
- `upsert_user(github_id, login, name, avatar_url)` — Create or update a user. Returns the user dict.
- `get_user_by_github_id(github_id)` — Get user by GitHub ID.
- `get_user_by_id(user_id)` — Get user by internal ID.
- `get_sample_projects()` — Return list of sample projects for scanning.
- `calculate_health_score(stats, complexity, duplication, quality)` — Calculate 0-100 health score from metrics.
- `score_to_grade(score)` — Convert score to letter grade.
- `generate_recommendations(complexity, duplication, quality)` — Generate actionable recommendations based on metrics.
- `count_code_stats(repo_path)` — Count source files and lines.
- `run_tool(name, args, fallback)` — Run a semcod tool, return JSON result or fallback.
- `get_installation_token(installation_id)` — Get GitHub App installation access token using JWT.
- `health_check()` — Health check endpoint with cache stats.
- `get_domain_config()` — Return the configured domain from environment.
- `scan_sample_projects()` — Scan all sample projects and save to database.
- `get_standard_metrics(limit)` — Get standardized metrics for recent scans.
- `get_metrics_summary()` — Get summary statistics of all scans.
- `get_repository_metrics(repo_path)` — Get metrics for a specific repository.
- `download_project_prompt()` — Download the project prompt.txt file for LLM analysis.
- `download_project_prompt_markdown()` — Download the project prompt as markdown format.
- `create_session_token(user_id)` — —
- `decode_session_token(token)` — —
- `get_current_user(credentials)` — —
- `github_oauth_start()` — Step 1: Redirect user to GitHub OAuth.
- `github_oauth_callback(code)` — Step 2: Exchange code for token, fetch profile, create user, issue JWT.
- `demo_login()` — Demo login: create a demo user and return JWT session token.
- `get_me(user)` — —
- `logout()` — —
- `list_repos(user)` — List user's repos for audit selection.
- `report_page(owner, repo)` — Redirect to frontend report page.
- `health_badge(repo_slug, style)` — Generate SVG badge with code health score.
- `scan_count_badge()` — Generate SVG badge showing total number of scans performed.
- `API()` — —
- `gradeColor()` — —
- `PUBLIC_URL()` — —
- `authHeaders()` — —
- `fetchMe()` — —
- `res()` — —
- `logout()` — —
- `fetchRepos()` — —
- `startAudit()` — —
- `fetchAudit()` — —
- `demoLogin()` — —
- `analyzePublicRepo()` — —
- `github_webhook(request)` — Handle GitHub webhook events.
- `Header()` — —
- `tabBtn()` — —
- `LanguageBar()` — —
- `total()` — —
- `entries()` — —
- `ProgressSteps()` — —
- `currentIdx()` — —
- `stepIdx()` — —
- `done()` — —
- `active()` — —
- `MetricCard()` — —
- `RecommendationCard()` — —
- `GradeCircle()` — —
- `color()` — —
- `r()` — —
- `circ()` — —
- `targetOffset()` — —
- `t()` — —
- `useAppState()` — —
- `searchParams()` — —
- `session()` — —
- `hash()` — —
- `params()` — —
- `tabParam()` — —
- `phaseParam()` — —
- `repoParam()` — —
- `parts()` — —
- `owner()` — —
- `repo()` — —
- `auditParam()` — —
- `timers()` — —
- `done()` — —
- `pollCount()` — —
- `maxPolls()` — —
- `poll()` — —
- `data()` — —
- `interval()` — —
- `shouldStop()` — —
- `reset()` — —
- `startOAuth()` — —
- `confirmAuth()` — —
- `startAudit()` — —
- `startSandbox()` — —
- `url()` — —
- `match()` — —
- `sshMatch()` — —
- `startDemoLogin()` — —
- `doLogout()` — —
- `AuthPhase()` — —
- `handleLogin()` — —
- `handleDemoLogin()` — —
- `data()` — —
- `ScanningPhase()` — —
- `run_audit(request, user)` — Run one-click audit on a repo. Requires authentication.
- `get_audit_result(audit_id)` — Poll audit status and results.
- `get_recent_scans_api(limit)` — Get list of recent scans with metrics.
- `analyze_repo(request)` — Analyze any public repository by URL (sandbox mode).
- `LandingPhase()` — —
- `fetchRecentScans()` — —
- `response()` — —
- `data()` — —
- `handleShare()` — —
- `shareUrls()` — —
- `formatDate()` — —
- `date()` — —
- `ReposPhase()` — —
- `RepoTab()` — —
- `handleAnalyze()` — —
- `PRBotTab()` — —
- `BadgeSVG()` — —
- `color()` — —
- `labelW()` — —
- `valueText()` — —
- `valueW()` — —
- `BadgeTab()` — —
- `badgeUrl()` — —
- `generateShareText()` — —
- `grade()` — —
- `score()` — —
- `files()` — —
- `lines()` — —
- `getShareUrls()` — —
- `text()` — —
- `url()` — —
- `input()` — —
- `RecentScansTab()` — —
- `fetchRecentScans()` — —
- `response()` — —
- `data()` — —
- `formatDate()` — —
- `date()` — —
- `getLanguageBadge()` — —
- `topLang()` — —
- `handleShare()` — —
- `shareUrls()` — —
- `ResultPhase()` — —
- `data()` — —
- `repoName()` — —
- `shareUrls()` — —
- `handleShare()` — —
- `handleDownloadMetrics()` — —
- `blob()` — —
- `url()` — —
- `a()` — —
- `handleDownloadPrompt()` — —
- `filesContent()` — —
- `handleDownloadMarkdown()` — —
- `handleDownloadToon()` — —
- `getTabContent()` — —
- `content()` — —
- `recentSection()` — —
- `isVisible()` — —
- `scanCards()` — —
- `count()` — —
- `scanCard()` — —
- `viewButton()` — —
- `response()` — —
- `data()` — —
- `scan()` — —
- `listResponse()` — —
- `listData()` — —
- `repo()` — —
- `input()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `blueskyButton()` — —
- `anyVisible()` — —
- `shareButtons()` — —
- `count()` — —
- `recentSection()` — —
- `isVisible()` — —
- `input()` — —
- `currentUrl()` — —
- `recentScansSection()` — —
- `isVisible()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `recentTab()` — —
- `isTabVisible()` — —
- `skipInCI()` — —
- `recentSection()` — —
- `isVisible()` — —
- `scanCards()` — —
- `count()` — —
- `scanCard()` — —
- `viewButton()` — —
- `repoButtons()` — —
- `count()` — —
- `input()` — —
- `reportVisible()` — —
- `noScansMessage()` — —
- `hasNoScans()` — —
- `scanCard()` — —
- `shareTab()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `blueskyButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `blueskyVisible()` — —
- `recentSection()` — —
- `isVisible()` — —
- `hasScan()` — —
- `currentUrl()` — —
- `recentScansSection()` — —
- `isVisible()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `recentTab()` — —
- `isTabVisible()` — —
- `skipInCI()` — —
- `response()` — —
- `data()` — —
- `scan()` — —
- `listResponse()` — —
- `listData()` — —
- `repo()` — —
- `mcp_list_resources()` — List all available MCP resources.
- `mcp_get_resource(uri)` — Get content of a specific MCP resource by URI.
- `mcp_list_tools()` — List all available MCP tools.
- `mcp_invoke_tool(request)` — Invoke an MCP tool with the provided arguments.
- `mcp_server_info()` — Get MCP server information.


## Project Structure

📄 `backend.config`
📄 `backend.database` (7 functions)
📦 `backend.routers`
📄 `backend.routers.audit` (8 functions)
📄 `backend.routers.auth` (9 functions)
📄 `backend.routers.badge` (4 functions)
📄 `backend.routers.mcp` (6 functions, 4 classes)
📄 `backend.routers.metrics` (6 functions)
📄 `backend.routers.report` (1 functions)
📄 `backend.routers.system` (2 functions)
📄 `backend.routers.webhook` (5 functions)
📄 `backend.sample_projects` (1 functions)
📄 `backend.scripts.scan_samples` (1 functions)
📄 `backend.server`
📄 `backend.server_new`
📦 `backend.services`
📄 `backend.services.analyzer` (2 functions)
📄 `backend.services.github_client` (1 functions)
📄 `backend.services.scoring` (3 functions)
📄 `backend.store`
📄 `e2e.playwright.config`
📄 `e2e.specs.audit.spec` (1 functions)
📄 `e2e.specs.badge.spec` (1 functions)
📄 `e2e.specs.demo-login.spec`
📄 `e2e.specs.demo-mode.spec` (2 functions)
📄 `e2e.specs.metrics.spec` (14 functions)
📄 `e2e.specs.recent-scans.spec` (8 functions)
📄 `e2e.specs.scan-workflow.spec` (9 functions)
📄 `e2e.specs.smoke.spec` (2 functions)
📄 `e2e.specs.social-sharing.spec` (31 functions)
📄 `frontend.e2e.audit.spec`
📄 `frontend.e2e.badge.spec` (1 functions)
📄 `frontend.e2e.metrics.spec` (13 functions)
📄 `frontend.e2e.recent-scans.spec` (8 functions)
📄 `frontend.e2e.scan-workflow.spec` (9 functions)
📄 `frontend.e2e.smoke.spec` (1 functions)
📄 `frontend.e2e.social-sharing.spec` (10 functions)
📄 `frontend.playwright.config`
📄 `frontend.src.App`
📄 `frontend.src.api` (15 functions)
📦 `frontend.src.components`
📄 `frontend.src.components.GradeCircle` (6 functions)
📄 `frontend.src.components.Header` (2 functions)
📄 `frontend.src.components.LanguageBar` (3 functions)
📄 `frontend.src.components.MetricCard` (1 functions)
📄 `frontend.src.components.PRCommentPreview`
📄 `frontend.src.components.ProgressSteps` (5 functions)
📄 `frontend.src.components.RecommendationCard` (1 functions)
📦 `frontend.src.components.phases`
📄 `frontend.src.components.phases.AuthPhase` (4 functions)
📄 `frontend.src.components.phases.LandingPhase` (8 functions)
📄 `frontend.src.components.phases.ReposPhase` (1 functions)
📄 `frontend.src.components.phases.ResultPhase` (29 functions)
📄 `frontend.src.components.phases.ScanningPhase` (1 functions)
📦 `frontend.src.components.tabs`
📄 `frontend.src.components.tabs.BadgeTab` (7 functions)
📄 `frontend.src.components.tabs.PRBotTab` (1 functions)
📄 `frontend.src.components.tabs.RecentScansTab` (10 functions)
📄 `frontend.src.components.tabs.RepoTab` (2 functions)
📦 `frontend.src.components.ui`
📄 `frontend.src.components.ui.GradeCircle`
📄 `frontend.src.components.ui.LanguageBar`
📄 `frontend.src.components.ui.MetricCard`
📄 `frontend.src.components.ui.RecommendationCard`
📄 `frontend.src.config` (1 functions)
📄 `frontend.src.constants` (2 functions)
📄 `frontend.src.hooks.useAppState` (31 functions)
📄 `frontend.src.main`
📦 `frontend.src.screens`
📄 `frontend.src.utils.share` (8 functions)
📄 `frontend.vite.config`
📄 `project`
📄 `traefik.generate-certs`

## Requirements

- Python >= >=3.8
- fastapi >=0.110.0- httpx >=0.27.0- PyJWT >=2.8.0- goal >=2.1.0- costs >=0.1.20- pfix >=0.1.60

## Contributing

**Contributors:**
- Tom Softreck <tom@sapletta.com>
- Tom Sapletta <tom-sapletta-com@users.noreply.github.com>

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/semcod/www
cd www

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Documentation

- 📖 [Full Documentation](https://github.com/semcod/www/tree/main/docs) — API reference, module docs, architecture
- 🚀 [Getting Started](https://github.com/semcod/www/blob/main/docs/getting-started.md) — Quick start guide
- 📚 [API Reference](https://github.com/semcod/www/blob/main/docs/api.md) — Complete API documentation
- 🔧 [Configuration](https://github.com/semcod/www/blob/main/docs/configuration.md) — Configuration options
- 💡 [Examples](./examples) — Usage examples and code samples

### Generated Files

| Output | Description | Link |
|--------|-------------|------|
| `README.md` | Project overview (this file) | — |
| `docs/api.md` | Consolidated API reference | [View](./docs/api.md) |
| `docs/modules.md` | Module reference with metrics | [View](./docs/modules.md) |
| `docs/architecture.md` | Architecture with diagrams | [View](./docs/architecture.md) |
| `docs/dependency-graph.md` | Dependency graphs | [View](./docs/dependency-graph.md) |
| `docs/coverage.md` | Docstring coverage report | [View](./docs/coverage.md) |
| `docs/getting-started.md` | Getting started guide | [View](./docs/getting-started.md) |
| `docs/configuration.md` | Configuration reference | [View](./docs/configuration.md) |
| `docs/api-changelog.md` | API change tracking | [View](./docs/api-changelog.md) |
| `CONTRIBUTING.md` | Contribution guidelines | [View](./CONTRIBUTING.md) |
| `examples/` | Usage examples | [Browse](./examples) |
| `mkdocs.yml` | MkDocs configuration | — |

<!-- code2docs:end -->