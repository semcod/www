<!-- code2docs:start --># www

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.8-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-809-green)
> **809** functions | **62** classes | **167** files | CC̄ = 2.7

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
├── project    ├── generate-certs    ├── config    ├── server    ├── store    ├── database    ├── sample_projects    ├── db_session    ├── worker/    ├── db_models        ├── scan_job        ├── webhook_service        ├── mirror        ├── autofix    ├── quality_gate        ├── analyzer        ├── stripe_connect        ├── scan_service        ├── scoring        ├── mirror_models        ├── tenants_orm        ├── users        ├── schema        ├── github_client        ├── tenants        ├── events    ├── db_module/        ├── users_orm        ├── installations        ├── repositories_orm        ├── billing        ├── installations_orm        ├── scans        ├── repositories        ├── scans_orm        ├── events_orm        ├── env        ├── wrappers        ├── _celery_stub            ├── maintenance            ├── marketplace        ├── tasks/            ├── autopr            ├── 0001_initial_schema    ├── events/        ├── scan_samples            ├── scan        ├── loader        ├── registry    ├── apps/            ├── pipeline        ├── base            ├── hooks            ├── pipeline            ├── pipeline    ├── adapters/        ├── base        ├── gitea_events        ├── gitlab        ├── gitea        ├── gitlab_events        ├── system        ├── models        ├── webhook        ├── github        ├── auth        ├── trend        ├── metrics        ├── badge        ├── webhook_v2        ├── report        ├── audit        ├── cron        ├── marketplace/            ├── deploy            ├── publish            ├── models            ├── browse            ├── connect            ├── billing            ├── resources            ├── tools        ├── mcp/            ├── models        ├── config        ├── config        ├── constants        ├── config        ├── api        ├── App        ├── main            ├── usePolling            ├── useAuth            ├── useUrlState            ├── useAppState            ├── useAuditActions            ├── useDownloads            ├── useBilling            ├── MarketplaceDashboard            ├── Header            ├── LanguageBar            ├── ProgressSteps            ├── MetricCard            ├── RecommendationCard            ├── PaywallModal            ├── GradeCircle            ├── Preview            ├── LoginMultiPlatform        ├── components/            ├── ShareButtons            ├── AppCard            ├── InstallButton                ├── AuthPhase                ├── LandingPhase            ├── phases/                ├── ScanningPhase                ├── ReposPhase                    ├── ErrorResult                    ├── ResultMetrics                    ├── ResultRecommendations                    ├── index/                    ├── DownloadButtons                    ├── ResultHeader                    ├── ResultTabPanel                ├── LanguageBar                ├── MetricCard                ├── RecommendationCard                ├── GradeCircle            ├── ui/                ├── TrendTab                ├── PRBotTab                ├── recentScansHelpers                ├── RepoTab                    ├── parts                ├── TrendSummaryCard                ├── BadgeTab            ├── tabs/                ├── AddScheduleForm                ├── SettingsTab                ├── MarketplaceTab                ├── RecentScansTab                ├── ScheduleRow                ├── TrendChart            ├── share            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec        ├── config            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec        ├── autopr        ├── mirror        ├── billing```

## API Overview

### Classes

- **`Base`** — —
- **`Scan`** — —
- **`Subscription`** — —
- **`User`** — —
- **`Tenant`** — —
- **`Repository`** — —
- **`Installation`** — —
- **`Event`** — —
- **`AuditResult`** — —
- **`BadgeCache`** — —
- **`MirrorService`** — Service for mirroring repos to local Gitea.
- **`Patch`** — Represents a single file patch.
- **`FixResult`** — Result of applying auto-fix.
- **`PatchGenerator`** — Generates patches for common code issues.
- **`AutoFixService`** — Service for creating auto-fix PRs.
- **`FunctionResult`** — —
- **`FileResult`** — —
- **`Violation`** — —
- **`MirrorConfig`** — Configuration for repo mirror.
- **`MirrorStatus`** — Status of mirror operation.
- **`BillingEventType`** — —
- **`UsageTracker`** — Tracks usage per tenant for billing purposes.
- **`StripeBilling`** — Stripe integration for usage-based billing.
- **`AppRegistry`** — Central registry for all marketplace apps.
- **`SecurityApp`** — Security vulnerability scanner.
- **`AppResult`** — Standard result format for all apps.
- **`AppContext`** — Context passed to apps during execution.
- **`AppBase`** — Base class for all marketplace apps.
- **`AuditApp`** — Main code quality audit app.
- **`PerformanceApp`** — Performance bottleneck analyzer.
- **`GitProvider`** — Abstract base class for git platform integrations.
- **`GitLabAdapter`** — GitLab API implementation of GitProvider.
- **`GiteaAdapter`** — Gitea API implementation of GitProvider.
- **`EventType`** — Supported event types across all platforms.
- **`ProviderType`** — Supported git providers.
- **`Event`** — Unified event representation across all git platforms.
- **`GitHubAdapter`** — GitHub API implementation of GitProvider.
- **`ScheduleCreate`** — —
- **`ScheduleOut`** — —
- **`PreviewRequest`** — —
- **`PreviewResponse`** — —
- **`InstallRequest`** — —
- **`InstallResponse`** — —
- **`AppStatusResponse`** — —
- **`AutoFixRequest`** — —
- **`AutoFixResponse`** — —
- **`ConnectRegisterRequest`** — —
- **`PayoutRequest`** — —
- **`MCPResource`** — MCP Resource definition.
- **`MCPTool`** — MCP Tool definition.
- **`MCPResourceResponse`** — MCP resource content response.
- **`MCPToolRequest`** — MCP tool invocation request.
- **`PatchFile`** — —
- **`AutoPRRequest`** — —
- **`AutoPRResult`** — —
- **`CreateMirrorRequest`** — —
- **`SyncMirrorRequest`** — —
- **`MirrorResponse`** — —
- **`MirrorInfo`** — —
- **`CheckoutRequest`** — —
- **`BillingStatus`** — —

### Functions

- `lifespan(app)` — —
- `get_sample_projects()` — Return list of sample projects for scanning.
- `get_db()` — Get database session for dependency injection.
- `init_db()` — Initialize database with all tables.
- `get_celery_app()` — Get configured Celery application instance.
- `run_scheduled_scan(repo, token, webhook_url)` — Execute a full audit pipeline for *repo* (scheduled, no HTTP context).
- `get_adapter_for_event(event, token)` — Factory function - get appropriate adapter for event provider.
- `process_pr_event(event, provider)` — Process pull request event - audit repo and comment results.
- `process_push_event(event, provider)` — Process push event - trigger analysis if main branch.
- `parse_github_webhook(payload)` — Parse GitHub webhook payload into Event.
- `parse_gitlab_webhook(payload)` — Parse GitLab webhook payload into Event.
- `parse_gitea_webhook(payload)` — Parse Gitea webhook payload into Event.
- `verify_github_signature(body, signature, secret)` — Verify GitHub webhook signature.
- `verify_gitea_signature(body, signature, secret)` — Verify Gitea webhook signature.
- `analyze_file(path)` — —
- `collect_results(dirs)` — —
- `check_file_lines(results, baseline)` — —
- `check_function_cc(results)` — —
- `check_cc_mean_delta(results, baseline)` — —
- `check_critical_delta(results, baseline)` — —
- `build_snapshot(results)` — —
- `main()` — —
- `count_code_stats(repo_path)` — Count source files and lines.
- `analyze_complexity(repo_path)` — Analyze code complexity using Python (no external tools).
- `analyze_duplication(repo_path)` — Analyze code duplication using Python (no external tools).
- `analyze_quality(repo_path)` — Analyze code quality using Python (no external tools).
- `analyze_repo(repo, commit_sha, config)` — Analyze a repository and return health metrics.
- `run_tool(name, args, fallback)` — Run a semcod tool, return JSON result or fallback.
- `create_connect_account(email, country)` — Create a Stripe Express Connect account for a publisher.
- `create_onboarding_link(account_id)` — Return onboarding URL for publisher to complete KYC.
- `get_account_status(account_id)` — Return payouts_enabled, charges_enabled, requirements.
- `transfer_revenue(amount_cents, account_id, metadata)` — Transfer publisher share (70%) to their Connect account.
- `calculate_health_score(stats, complexity, duplication, quality)` — Calculate 0-100 health score from metrics.
- `score_to_grade(score)` — Convert score to letter grade.
- `generate_recommendations(complexity, duplication, quality)` — Generate actionable recommendations based on metrics.
- `get_or_create_tenant(db, provider, provider_user_id, login)` — Get existing tenant or create new one.
- `get_tenant_by_id(db, tenant_id)` — Get tenant by ID.
- `update_tenant_plan(db, tenant_id, plan, billing_customer_id)` — Update tenant's billing plan.
- `get_connection()` — Get database connection based on DB_TYPE.
- `convert_query(query)` — Convert query placeholders based on DB_TYPE.
- `execute_query(cursor, query, params)` — Execute query with automatic placeholder conversion.
- `upsert_user(github_id, login, name, avatar_url)` — Create or update a user. Returns the user dict.
- `get_user_by_github_id(github_id)` — Get user by GitHub ID.
- `get_user_by_id(user_id)` — Get user by internal ID.
- `get_subscription(user_id)` — Get active subscription for a user. Returns None if not found (treat as free).
- `upsert_subscription(user_id, plan, stripe_customer_id, stripe_subscription_id)` — Create or update subscription for a user.
- `increment_scan_count(user_id)` — Increment scans_this_week counter. Resets if a new week has started. Returns new count.
- `get_connection()` — Get database connection based on DB_TYPE.
- `init_db()` — Initialize the database and create tables.
- `get_installation_token(installation_id)` — Get GitHub App installation access token using JWT.
- `get_connection()` — Get database connection based on DB_TYPE.
- `get_or_create_tenant(provider, provider_user_id, login, name)` — Get existing tenant or create new one.
- `get_tenant_by_id(tenant_id)` — Get tenant by ID.
- `update_tenant_plan(tenant_id, plan, billing_customer_id, billing_subscription_id)` — Update tenant's billing plan.
- `get_connection()` — Get database connection based on DB_TYPE.
- `queue_event(event_id, event_type, provider, repo_full_name)` — Queue a new event for processing.
- `get_pending_events(limit)` — Get pending events for processing.
- `update_event_status(event_id, status, error_message)` — Update event processing status.
- `upsert_user(db, github_id, login, name)` — Create or update a user. Returns the user dict.
- `get_user_by_github_id(db, github_id)` — Get user by GitHub ID.
- `get_user_by_id(db, user_id)` — Get user by internal ID.
- `get_subscription(db, user_id)` — Get active subscription for a user. Returns None if not found (treat as free).
- `upsert_subscription(db, user_id, plan, stripe_customer_id)` — Create or update subscription for a user.
- `increment_scan_count(db, user_id)` — Increment scans_this_week counter. Resets if a new week has started. Returns new count.
- `get_connection()` — Get database connection based on DB_TYPE.
- `create_installation(tenant_id, repository_id, apps, webhook_id)` — Create app installation for a repository.
- `get_installation(tenant_id, repository_id)` — Get installation by tenant and repository.
- `get_tenant_installations(tenant_id)` — Get all installations for a tenant.
- `delete_installation(tenant_id, repository_id)` — Delete installation (soft delete - set inactive).
- `update_installation_scan(tenant_id, repository_id, score)` — Update last scan info for installation.
- `get_or_create_repository(db, tenant_id, provider, repo_provider_id)` — Get existing repository or create new one for tenant.
- `get_tenant_repositories(db, tenant_id)` — Get all repositories for a tenant.
- `get_repository_by_full_name(db, tenant_id, provider, full_name)` — Get repository by tenant + provider + full_name.
- `get_usage_tracker()` — Get singleton usage tracker.
- `get_stripe_billing()` — Get singleton Stripe billing.
- `create_installation(db, tenant_id, repository_id, apps)` — Create app installation for a repository.
- `get_installation(db, tenant_id, repository_id)` — Get installation by tenant and repository.
- `get_tenant_installations(db, tenant_id)` — Get all installations for a tenant.
- `delete_installation(db, tenant_id, repository_id)` — Delete installation (soft delete - set inactive).
- `update_installation_scan(db, tenant_id, repository_id, score)` — Update last scan info for installation.
- `get_connection()` — Get database connection based on DB_TYPE.
- `save_scan(scan_data)` — Save a scan to the database.
- `get_recent_scans(limit)` — Get recent scans from the database.
- `get_repo_scans(repo, limit)` — Get scans for a specific repository ordered by date ascending.
- `get_total_scan_count()` — Get total number of scans in the database.
- `save_audit_result(audit_id, audit_data)` — Save audit result to database.
- `get_audit_result(audit_id)` — Get audit result from database.
- `save_badge_cache(repo, badge_data)` — Save badge cache to database.
- `get_badge_cache(repo)` — Get badge cache from database.
- `get_connection()` — Get database connection based on DB_TYPE.
- `get_or_create_repository(tenant_id, provider, repo_provider_id, name)` — Get existing repository or create new one for tenant.
- `get_tenant_repositories(tenant_id)` — Get all repositories for a tenant.
- `get_repository_by_full_name(tenant_id, provider, full_name)` — Get repository by tenant + provider + full_name.
- `save_scan(db, scan_data)` — Save a scan to the database.
- `get_recent_scans(db, limit)` — Get recent scans from the database.
- `get_repo_scans(db, repo, limit)` — Get scans for a specific repository ordered by date ascending.
- `get_total_scan_count(db)` — Get total number of scans in the database.
- `save_audit_result(db, audit_id, audit_data)` — Save audit result to database.
- `get_audit_result(db, audit_id)` — Get audit result from database.
- `save_badge_cache(db, repo, badge_data)` — Save badge cache to database.
- `get_badge_cache(db, repo)` — Get badge cache from database.
- `queue_event(db, event_id, event_type, provider)` — Queue a new event for processing.
- `get_pending_events(db, limit)` — Get pending events for processing.
- `update_event_status(db, event_id, status, error_message)` — Update event processing status.
- `get_url()` — Get DB URL from env, fallback to alembic.ini.
- `run_migrations_offline()` — Run migrations in 'offline' mode (generates SQL without a connection).
- `run_migrations_online()` — Run migrations in 'online' mode (requires live DB connection).
- `save_scan(scan_data)` — —
- `get_recent_scans(limit)` — —
- `get_repo_scans(repo, limit)` — —
- `get_total_scan_count()` — —
- `save_audit_result(audit_id, audit_data)` — —
- `get_audit_result(audit_id)` — —
- `save_badge_cache(repo, badge_data)` — —
- `get_badge_cache(repo)` — —
- `upsert_user(github_id, login, name, avatar_url)` — —
- `get_user_by_github_id(github_id)` — —
- `get_user_by_id(user_id)` — —
- `get_subscription(user_id)` — —
- `upsert_subscription(user_id, plan, stripe_customer_id, stripe_subscription_id)` — —
- `increment_scan_count(user_id)` — —
- `get_or_create_tenant(provider, provider_user_id, login, name)` — —
- `get_tenant_by_id(tenant_id)` — —
- `update_tenant_plan(tenant_id, plan, billing_customer_id, billing_subscription_id)` — —
- `get_or_create_repository(tenant_id, provider, repo_provider_id, name)` — —
- `get_tenant_repositories(tenant_id)` — —
- `get_repository_by_full_name(tenant_id, provider, full_name)` — —
- `create_installation(tenant_id, repository_id, apps, webhook_id)` — —
- `get_installation(tenant_id, repository_id)` — —
- `get_tenant_installations(tenant_id)` — —
- `delete_installation(tenant_id, repository_id)` — —
- `update_installation_scan(tenant_id, repository_id, score)` — —
- `queue_event(event_id, event_type, provider, repo_full_name)` — —
- `get_pending_events(limit)` — —
- `update_event_status(event_id, status, error_message)` — —
- `shared_task(fn)` — Drop-in replacement for celery.shared_task with no broker dependency.
- `check_health_regression(repo, previous_score, new_score, threshold)` — Check if health score regressed and create issue if needed.
- `check_score_and_notify(repo, previous_score, new_score, tenant_id)` — Check if score improved after auto-fix and send notifications.
- `sync_mirror_task(self, mirror_id, source_repo, source_provider)` — Sync mirror from source to Gitea asynchronously.
- `schedule_periodic_mirrors()` — Schedule periodic sync for all active mirrors.
- `create_auto_pr(self, repo, base_branch, patches)` — Create automated PR with fixes asynchronously.
- `create_auto_fix_pr(self, repo, base_branch, files)` — Create automated PR with fixes asynchronously.
- `upgrade()` — —
- `downgrade()` — —
- `scan_sample_projects()` — Scan all sample projects and save to database.
- `run_audit(self, repo, commit_sha, config)` — Run code audit on a repository asynchronously.
- `process_pr_event(self, event_dict)` — Process pull request event asynchronously.
- `process_push_event(event_dict)` — Process push event - trigger analysis for default branch.
- `analyze_diff(self, repo, diff, config)` — Analyze a diff asynchronously using actual analysis.
- `load_manifest(app_name)` — Load manifest.yaml for an app.
- `load_pricing(app_name)` — Load pricing.json for an app.
- `load_app(app_name)` — Load a single app by name.
- `load_apps()` — Load all available apps.
- `get_app_by_trigger(trigger)` — Get all apps that respond to a specific trigger.
- `validate_manifest(manifest)` — Validate manifest structure. Returns list of errors.
- `get_registry()` — Get singleton registry instance.
- `on_pr_comment(event, context)` — Handle PR comment commands.
- `get_adapter_for_event(event, token)` — Factory function - get appropriate adapter for event provider.
- `parse_gitea_event(payload)` — Parse Gitea webhook payload into unified Event.
- `parse_gitlab_event(payload)` — Parse GitLab webhook payload into unified Event.
- `health_check()` — Health check endpoint with cache stats.
- `get_domain_config()` — Return the configured domain from environment.
- `github_webhook(request)` — Handle GitHub webhook events.
- `parse_github_event(payload)` — Parse GitHub webhook payload into unified Event.
- `create_session_token(user_id)` — —
- `decode_session_token(token)` — —
- `get_current_user(credentials)` — —
- `github_oauth_start()` — Step 1: Redirect user to GitHub OAuth.
- `github_oauth_callback(code)` — Step 2: Exchange code for token, fetch profile, create user, issue JWT.
- `demo_login()` — Demo login: create a demo user and return JWT session token.
- `get_me(user)` — —
- `logout()` — —
- `list_repos(user)` — List user's repos for audit selection.
- `get_repo_trend(owner, repo, days)` — Get historical health scores for a repository.
- `compare_repo_trend(owner, repo, days)` — Compare the latest scan against the scan from {days} ago.
- `get_scan_diff(owner, repo)` — Compare the latest scan against the previous one for a repository.
- `get_standard_metrics(limit)` — Get standardized metrics for recent scans.
- `get_metrics_summary()` — Get summary statistics of all scans.
- `get_repository_metrics(repo_path)` — Get metrics for a specific repository.
- `download_project_prompt()` — Download the project prompt.txt file for LLM analysis.
- `download_project_prompt_markdown()` — Download the project prompt as markdown format.
- `health_badge(repo_slug, style)` — Generate SVG badge with code health score.
- `scan_count_badge()` — Generate SVG badge showing total number of scans performed.
- `github_webhook(request)` — Handle GitHub webhook events using unified adapter system.
- `gitlab_webhook(request)` — Handle GitLab webhook events.
- `gitea_webhook(request)` — Handle Gitea webhook events.
- `report_page(owner, repo)` — Redirect to frontend report page.
- `run_audit(request, user)` — Run one-click audit on a repo. Requires authentication.
- `get_audit_result_endpoint(audit_id)` — Poll audit status and results.
- `get_recent_scans_api(limit)` — Get list of recent scans with metrics.
- `analyze_repo(request)` — Analyze any public repository by URL (sandbox mode).
- `get_scheduler()` — —
- `start_scheduler()` — —
- `stop_scheduler()` — —
- `create_schedule(body)` — Register a new periodic scan for a repository.
- `list_schedules()` — List all active scan schedules.
- `get_schedule(owner, repo)` — Get schedule details for a specific repository.
- `update_schedule(owner, repo, body)` — Update interval or webhook for an existing schedule.
- `delete_schedule(owner, repo)` — Remove a scheduled scan.
- `trigger_auto_fix(request, user)` — Trigger auto-fix PR generation for a repository.
- `install_app(request, user)` — Install Semcod app on a repository.
- `uninstall_app(repo, provider, user)` — Remove Semcod app from a repository.
- `list_installations(user)` — List all installations for the current user.
- `get_app_status(repo, provider, user)` — Get installation status and last scan results for a repo.
- `preview_pr_comment(request, user)` — Generate preview of PR comment for a repository.
- `list_apps()` — List all available marketplace apps.
- `register_publisher(request, user)` — Create a Stripe Express Connect account for this publisher.
- `connect_status(account_id, user)` — Return Connect account status (payouts_enabled, requirements).
- `trigger_payout(request, user)` — Transfer revenue share to a publisher's Connect account.
- `get_billing_status(user)` — Get current billing status and usage.
- `list_billing_plans()` — List available billing plans.
- `mcp_list_resources()` — List all available MCP resources.
- `mcp_get_resource(uri)` — Get content of a specific MCP resource by URI.
- `mcp_list_tools()` — List all available MCP tools.
- `mcp_invoke_tool(request)` — Invoke an MCP tool with the provided arguments.
- `mcp_server_info()` — Get MCP server information.
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
- `fetchBillingStatus()` — —
- `createCheckoutSession()` — —
- `analyzePublicRepo()` — —
- `loginWithProvider()` — —
- `getPreview()` — —
- `installApp()` — —
- `getInstallations()` — —
- `uninstallApp()` — —
- `fetchTrend()` — —
- `fetchSchedules()` — —
- `createSchedule()` — —
- `deleteSchedule()` — —
- `fetchBillingPortal()` — —
- `getApps()` — —
- `getAppStatus()` — —
- `useScanAnimation()` — —
- `timers()` — —
- `done()` — —
- `useAuditPolling()` — —
- `pollCount()` — —
- `MAX_POLLS()` — —
- `poll()` — —
- `data()` — —
- `interval()` — —
- `shouldStop()` — —
- `useSessionCallbackBootstrap()` — —
- `searchParams()` — —
- `session()` — —
- `useSessionProfile()` — —
- `getOAuthStartUrl()` — —
- `confirmAuthFlow()` — —
- `startDemoSession()` — —
- `data()` — —
- `logoutSession()` — —
- `VALID_TABS()` — —
- `VALID_PHASES()` — —
- `parseRepositoryReference()` — —
- `trimmed()` — —
- `urlMatch()` — —
- `parts()` — —
- `createSelectedRepo()` — —
- `parsed()` — —
- `useHashBootstrap()` — —
- `hash()` — —
- `params()` — —
- `tabParam()` — —
- `phaseParam()` — —
- `repoParam()` — —
- `sandboxMode()` — —
- `repoData()` — —
- `auditParam()` — —
- `useHashSync()` — —
- `useAppState()` — —
- `demoUser()` — —
- `reset()` — —
- `startOAuth()` — —
- `confirmAuth()` — —
- `startDemoLogin()` — —
- `doLogout()` — —
- `useAuditActions()` — —
- `startAudit()` — —
- `data()` — —
- `startSandbox()` — —
- `url()` — —
- `repoData()` — —
- `resetAudit()` — —
- `recommendationLabel()` — —
- `recommendationLine()` — —
- `markdownRecommendationLine()` — —
- `toonRecommendationLine()` — —
- `filesContent()` — —
- `buildMetricsExportData()` — —
- `buildPromptText()` — —
- `buildMarkdownText()` — —
- `buildToonText()` — —
- `buildShareText()` — —
- `getResultTabContent()` — —
- `downloadContent()` — —
- `blob()` — —
- `url()` — —
- `link()` — —
- `useDownloads()` — —
- `handleDownloadMetrics()` — —
- `handleDownloadPrompt()` — —
- `handleDownloadMarkdown()` — —
- `handleDownloadToon()` — —
- `handleGenericDownload()` — —
- `useBilling()` — —
- `refreshBilling()` — —
- `checkScanAllowed()` — —
- `openCheckout()` — —
- `dismissPaywall()` — —
- `loadData()` — —
- `toggleApp()` — —
- `handleRepoSelect()` — —
- `isRepoInstalled()` — —
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
- `PlanCard()` — —
- `PaywallModal()` — —
- `GradeCircle()` — —
- `color()` — —
- `r()` — —
- `circ()` — —
- `targetOffset()` — —
- `t()` — —
- `loadPreview()` — —
- `result()` — —
- `formatComment()` — —
- `getSeverityIcon()` — —
- `GitHubIcon()` — —
- `GitLabIcon()` — —
- `GiteaIcon()` — —
- `ShareButtons()` — —
- `handleShare()` — —
- `shareUrls()` — —
- `isPro()` — —
- `getAppIcon()` — —
- `getTriggerIcon()` — —
- `checkStatus()` — —
- `result()` — —
- `handleInstall()` — —
- `handleUninstall()` — —
- `AuthPhase()` — —
- `handleLogin()` — —
- `handleDemoLogin()` — —
- `data()` — —
- `LandingPhase()` — —
- `fetchRecentScans()` — —
- `response()` — —
- `data()` — —
- `formatDate()` — —
- `date()` — —
- `ScanningPhase()` — —
- `ReposPhase()` — —
- `ErrorResult()` — —
- `ResultMetrics()` — —
- `ResultRecommendations()` — —
- `ResultPhase()` — —
- `data()` — —
- `repoName()` — —
- `activeContent()` — —
- `handleCopy()` — —
- `handleDownload()` — —
- `DownloadButtons()` — —
- `active()` — —
- `ResultHeader()` — —
- `ResultTabPanel()` — —
- `TrendTab()` — —
- `repoName()` — —
- `history()` — —
- `latest()` — —
- `prev()` — —
- `delta()` — —
- `directionColor()` — —
- `PRBotTab()` — —
- `fetchRecentScans()` — —
- `response()` — —
- `data()` — —
- `formatRecentScanDate()` — —
- `date()` — —
- `getPrimaryLanguage()` — —
- `openRecentScanRepository()` — —
- `openRecentScanAudit()` — —
- `RepoTab()` — —
- `LanguageBadge()` — —
- `language()` — —
- `ScanMetrics()` — —
- `RecentScanCard()` — —
- `RecentScansEmptyState()` — —
- `RecentScansHeader()` — —
- `RecentScansBadgeInfo()` — —
- `TrendSummaryCard()` — —
- `sign()` — —
- `deltaColor()` — —
- `BadgeSVG()` — —
- `color()` — —
- `labelW()` — —
- `valueText()` — —
- `valueW()` — —
- `BadgeTab()` — —
- `badgeUrl()` — —
- `AddScheduleForm()` — —
- `handleSubmit()` — —
- `SectionHeader()` — —
- `SettingsTab()` — —
- `loadSchedules()` — —
- `handleDelete()` — —
- `handleBillingPortal()` — —
- `plan()` — —
- `planColor()` — —
- `MarketplaceTab()` — —
- `provider()` — —
- `RecentScansTab()` — —
- `ScheduleRow()` — —
- `handleDelete()` — —
- `TrendChart()` — —
- `W()` — —
- `scores()` — —
- `minS()` — —
- `maxS()` — —
- `range()` — —
- `x()` — —
- `y()` — —
- `points()` — —
- `generateShareText()` — —
- `grade()` — —
- `score()` — —
- `files()` — —
- `lines()` — —
- `getShareUrls()` — —
- `text()` — —
- `url()` — —
- `input()` — —
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
- `input()` — —
- `skipInCI()` — —
- `recentSection()` — —
- `isVisible()` — —
- `scanCards()` — —
- `count()` — —
- `scanCard()` — —
- `viewButton()` — —
- `skipInCI()` — —
- `response()` — —
- `data()` — —
- `scan()` — —
- `listResponse()` — —
- `listData()` — —
- `repo()` — —
- `repoButtons()` — —
- `count()` — —
- `demoButton()` — —
- `isVisible()` — —
- `noScansMessage()` — —
- `hasNoScans()` — —
- `scanCard()` — —
- `hasScan()` — —
- `shareTab()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `blueskyButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `blueskyVisible()` — —
- `recentSection()` — —
- `isVisible()` — —
- `input()` — —
- `sandboxBadge()` — —
- `hasSandbox()` — —
- `baseUrl()` — —
- `response()` — —
- `data()` — —
- `scan()` — —
- `heading()` — —
- `isVisible()` — —
- `recentTab()` — —
- `input()` — —
- `reportVisible()` — —
- `tabButton()` — —
- `element()` — —
- `isVisible()` — —
- `recentSection()` — —
- `badgeTab()` — —
- `anyVisible()` — —
- `el()` — —
- `avatar()` — —
- `avatarVisible()` — —
- `demoIndicator()` — —
- `demoVisible()` — —
- `currentUrl()` — —
- `recentScansSection()` — —
- `isVisible()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `recentTab()` — —
- `isTabVisible()` — —
- `create_auto_pr(body, user)` — Apply LLM-generated patches to a repository and create a GitHub PR.
- `create_mirror(request, user)` — Create new mirror from GitHub/GitLab to local Gitea.
- `sync_mirror(request, user)` — Sync existing mirror with latest changes from source.
- `list_mirrors(user)` — List all mirrors for current user.
- `get_mirror(mirror_id, user)` — Get mirror by ID.
- `delete_mirror(mirror_id, user)` — Delete mirror.
- `list_plans()` — Return available plans and pricing (no auth required).
- `billing_status(user)` — Return current plan, limits, and scan usage for the authenticated user.
- `create_checkout(body, user)` — Create a Stripe Checkout session.
- `billing_portal(user)` — Create a Stripe Customer Portal session.
- `stripe_webhook(request)` — Handle Stripe webhook events.
- `check_scan_allowed(user_id)` — Raise HTTP 402 if the user has hit their weekly scan limit.


## Project Structure

📦 `backend.adapters` (1 functions)
📄 `backend.adapters.base` (19 functions, 1 classes)
📄 `backend.adapters.gitea` (21 functions, 1 classes)
📄 `backend.adapters.gitea_events` (2 functions)
📄 `backend.adapters.github` (22 functions, 1 classes)
📄 `backend.adapters.gitlab` (21 functions, 1 classes)
📄 `backend.adapters.gitlab_events` (2 functions)
📄 `backend.alembic.env` (3 functions)
📄 `backend.alembic.versions.0001_initial_schema` (2 functions)
📦 `backend.apps`
📄 `backend.apps.audit.hooks` (1 functions)
📄 `backend.apps.audit.pipeline` (8 functions, 1 classes)
📄 `backend.apps.base` (13 functions, 3 classes)
📄 `backend.apps.loader` (6 functions)
📄 `backend.apps.performance.pipeline` (7 functions, 1 classes)
📄 `backend.apps.registry` (9 functions, 1 classes)
📄 `backend.apps.security.pipeline` (5 functions, 1 classes)
📄 `backend.config`
📄 `backend.database`
📄 `backend.db_models` (1 functions, 10 classes)
📦 `backend.db_module`
📄 `backend.db_module.events` (4 functions)
📄 `backend.db_module.events_orm` (3 functions)
📄 `backend.db_module.installations` (6 functions)
📄 `backend.db_module.installations_orm` (5 functions)
📄 `backend.db_module.repositories` (4 functions)
📄 `backend.db_module.repositories_orm` (3 functions)
📄 `backend.db_module.scans` (9 functions)
📄 `backend.db_module.scans_orm` (8 functions)
📄 `backend.db_module.schema` (2 functions)
📄 `backend.db_module.tenants` (4 functions)
📄 `backend.db_module.tenants_orm` (3 functions)
📄 `backend.db_module.users` (9 functions)
📄 `backend.db_module.users_orm` (6 functions)
📄 `backend.db_module.wrappers` (28 functions)
📄 `backend.db_session` (2 functions)
📦 `backend.events`
📄 `backend.events.models` (5 functions, 3 classes)
📄 `backend.quality_gate` (12 functions, 3 classes)
📄 `backend.routers.audit` (8 functions)
📄 `backend.routers.auth` (9 functions)
📄 `backend.routers.autopr` (12 functions, 3 classes)
📄 `backend.routers.badge` (4 functions)
📄 `backend.routers.billing` (12 functions, 2 classes)
📦 `backend.routers.marketplace`
📄 `backend.routers.marketplace.billing` (2 functions)
📄 `backend.routers.marketplace.browse` (3 functions)
📄 `backend.routers.marketplace.connect` (3 functions, 2 classes)
📄 `backend.routers.marketplace.deploy` (6 functions)
📄 `backend.routers.marketplace.models` (7 classes)
📄 `backend.routers.marketplace.publish` (5 functions)
📦 `backend.routers.mcp` (1 functions)
📄 `backend.routers.mcp.models` (4 classes)
📄 `backend.routers.mcp.resources` (9 functions)
📄 `backend.routers.mcp.tools` (11 functions)
📄 `backend.routers.metrics` (6 functions)
📄 `backend.routers.mirror` (5 functions, 4 classes)
📄 `backend.routers.report` (1 functions)
📄 `backend.routers.system` (2 functions)
📄 `backend.routers.trend` (8 functions)
📄 `backend.routers.webhook` (6 functions)
📄 `backend.routers.webhook_v2` (5 functions)
📄 `backend.sample_projects` (1 functions)
📄 `backend.scheduler.cron` (11 functions, 2 classes)
📄 `backend.scheduler.scan_job` (5 functions)
📄 `backend.scripts.scan_samples` (1 functions)
📄 `backend.server` (1 functions)
📄 `backend.services.analyzer` (13 functions)
📄 `backend.services.autofix` (8 functions, 4 classes)
📄 `backend.services.billing` (16 functions, 3 classes)
📄 `backend.services.github_client` (1 functions)
📄 `backend.services.mirror` (11 functions, 1 classes)
📄 `backend.services.mirror_models` (2 classes)
📄 `backend.services.scan_service`
📄 `backend.services.scoring` (3 functions)
📄 `backend.services.stripe_connect` (5 functions)
📄 `backend.services.webhook_service` (8 functions)
📄 `backend.store`
📦 `backend.worker`
📄 `backend.worker._celery_stub` (6 functions, 1 classes)
📦 `backend.worker.tasks`
📄 `backend.worker.tasks.autopr` (3 functions)
📄 `backend.worker.tasks.maintenance` (2 functions)
📄 `backend.worker.tasks.marketplace` (3 functions)
📄 `backend.worker.tasks.scan` (7 functions)
📄 `e2e.playwright.config`
📄 `e2e.specs.audit.spec` (1 functions)
📄 `e2e.specs.badge.spec` (1 functions)
📄 `e2e.specs.demo-login.spec`
📄 `e2e.specs.demo-mode.spec` (4 functions)
📄 `e2e.specs.gui-views.spec` (13 functions)
📄 `e2e.specs.metrics.spec` (14 functions)
📄 `e2e.specs.recent-scans.spec` (8 functions)
📄 `e2e.specs.sandbox-recent-scans.spec` (11 functions)
📄 `e2e.specs.scan-workflow.spec` (9 functions)
📄 `e2e.specs.smoke.spec` (2 functions)
📄 `e2e.specs.social-sharing.spec` (33 functions)
📄 `frontend.e2e.audit.spec`
📄 `frontend.e2e.badge.spec` (1 functions)
📄 `frontend.e2e.metrics.spec` (13 functions)
📄 `frontend.e2e.recent-scans.spec` (8 functions)
📄 `frontend.e2e.scan-workflow.spec` (9 functions)
📄 `frontend.e2e.smoke.spec` (1 functions)
📄 `frontend.e2e.social-sharing.spec` (10 functions)
📄 `frontend.playwright.config`
📄 `frontend.src.App`
📄 `frontend.src.api` (42 functions)
📦 `frontend.src.components`
📄 `frontend.src.components.AppCard` (3 functions)
📄 `frontend.src.components.GradeCircle` (6 functions)
📄 `frontend.src.components.Header` (2 functions)
📄 `frontend.src.components.InstallButton` (5 functions)
📄 `frontend.src.components.LanguageBar` (3 functions)
📄 `frontend.src.components.LoginMultiPlatform` (3 functions)
📄 `frontend.src.components.MarketplaceDashboard` (4 functions)
📄 `frontend.src.components.MetricCard` (1 functions)
📄 `frontend.src.components.PaywallModal` (2 functions)
📄 `frontend.src.components.Preview` (4 functions)
📄 `frontend.src.components.ProgressSteps` (5 functions)
📄 `frontend.src.components.RecommendationCard` (1 functions)
📄 `frontend.src.components.ShareButtons` (3 functions)
📦 `frontend.src.components.phases`
📄 `frontend.src.components.phases.AuthPhase` (4 functions)
📄 `frontend.src.components.phases.LandingPhase` (6 functions)
📄 `frontend.src.components.phases.ReposPhase` (1 functions)
📄 `frontend.src.components.phases.ScanningPhase` (1 functions)
📄 `frontend.src.components.phases.result.DownloadButtons` (2 functions)
📄 `frontend.src.components.phases.result.ErrorResult` (1 functions)
📄 `frontend.src.components.phases.result.ResultHeader` (1 functions)
📄 `frontend.src.components.phases.result.ResultMetrics` (1 functions)
📄 `frontend.src.components.phases.result.ResultRecommendations` (1 functions)
📄 `frontend.src.components.phases.result.ResultTabPanel` (1 functions)
📦 `frontend.src.components.phases.result.index` (6 functions)
📦 `frontend.src.components.tabs`
📄 `frontend.src.components.tabs.AddScheduleForm` (2 functions)
📄 `frontend.src.components.tabs.BadgeTab` (7 functions)
📄 `frontend.src.components.tabs.MarketplaceTab` (2 functions)
📄 `frontend.src.components.tabs.PRBotTab` (1 functions)
📄 `frontend.src.components.tabs.RecentScansTab` (1 functions)
📄 `frontend.src.components.tabs.RecentScansTab.parts` (7 functions)
📄 `frontend.src.components.tabs.RepoTab` (1 functions)
📄 `frontend.src.components.tabs.ScheduleRow` (2 functions)
📄 `frontend.src.components.tabs.SettingsTab` (7 functions)
📄 `frontend.src.components.tabs.TrendChart` (9 functions)
📄 `frontend.src.components.tabs.TrendSummaryCard` (3 functions)
📄 `frontend.src.components.tabs.TrendTab` (7 functions)
📄 `frontend.src.components.tabs.recentScansHelpers` (8 functions)
📦 `frontend.src.components.ui`
📄 `frontend.src.components.ui.GradeCircle`
📄 `frontend.src.components.ui.LanguageBar`
📄 `frontend.src.components.ui.MetricCard`
📄 `frontend.src.components.ui.RecommendationCard`
📄 `frontend.src.config` (1 functions)
📄 `frontend.src.constants` (2 functions)
📄 `frontend.src.hooks.useAppState` (7 functions)
📄 `frontend.src.hooks.useAuditActions` (8 functions)
📄 `frontend.src.hooks.useAuth` (9 functions)
📄 `frontend.src.hooks.useBilling` (5 functions)
📄 `frontend.src.hooks.useDownloads` (21 functions)
📄 `frontend.src.hooks.usePolling` (10 functions)
📄 `frontend.src.hooks.useUrlState` (19 functions)
📄 `frontend.src.main`
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