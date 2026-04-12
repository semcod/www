<!-- code2docs:start --># www

![version](https://img.shields.io/badge/version-0.1.0-blue) ![python](https://img.shields.io/badge/python-%3E%3D3.9-blue) ![coverage](https://img.shields.io/badge/coverage-unknown-lightgrey) ![functions](https://img.shields.io/badge/functions-1052-green)
> **1052** functions | **81** classes | **195** files | CC̄ = 2.7

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
├── project├── run-sim    ├── generate-certs    ├── store    ├── server    ├── database    ├── config    ├── db_session    ├── sample_projects    ├── worker/        ├── scan_job    ├── db_models        ├── autopr_helpers        ├── webhook_service        ├── mirror    ├── quality_gate        ├── redsl_client        ├── scoring        ├── mirror_models        ├── autofix        ├── scan_service        ├── stripe_connect        ├── github_client        ├── tenants_orm        ├── users        ├── analyzer        ├── schema        ├── events        ├── tenants        ├── users_orm    ├── db_module/        ├── benchmark_orm        ├── installations        ├── repositories_orm        ├── installations_orm        ├── db_connection        ├── scans        ├── repositories        ├── billing        ├── scans_orm        ├── events_orm        ├── env        ├── wrappers        ├── _celery_stub            ├── maintenance            ├── marketplace        ├── tasks/            ├── autopr            ├── 0001_initial_schema            ├── redsl    ├── events/        ├── scan_samples        ├── loader            ├── scan        ├── registry    ├── apps/        ├── base            ├── hooks            ├── pipeline            ├── pipeline            ├── pipeline    ├── adapters/        ├── base        ├── gitea_events        ├── models        ├── gitlab        ├── gitea        ├── gitlab_events        ├── system        ├── webhook        ├── github        ├── auth        ├── trend        ├── cron        ├── metrics        ├── badge        ├── benchmark        ├── webhook_v2        ├── report        ├── audit        ├── billing        ├── marketplace/            ├── deploy            ├── publish            ├── models            ├── browse            ├── connect            ├── billing            ├── resources            ├── tools        ├── mcp/            ├── models        ├── config        ├── config        ├── constants        ├── config        ├── api        ├── App        ├── main        ├── autopr            ├── usePolling            ├── useBenchmarkTracking            ├── useAuth            ├── useSession            ├── useBenchmarkState            ├── useRepoList            ├── useUrlState        ├── redsl            ├── useAppState            ├── useAuditActions            ├── useBilling            ├── MarketplaceDashboard            ├── Header            ├── LanguageBar            ├── MetricCard            ├── ProgressSteps            ├── RecommendationCard            ├── useDownloads            ├── GradeCircle            ├── PaywallModal        ├── components/            ├── LoginMultiPlatform            ├── Preview            ├── ShareButtons            ├── AppCard            ├── RedslHealthCard            ├── InstallButton                ├── BenchmarkDecisionPanel                ├── BenchmarkReviewPanel                ├── RecommendationFeedbackForm            ├── phases/                ├── AuthPhase        ├── mirror                ├── ScanningPhase                ├── ReposPhase                    ├── ResultMetrics                    ├── ResultRecommendations                    ├── DownloadButtons                    ├── ErrorResult                    ├── index/                ├── LandingPhase                ├── LanguageBar                ├── MetricCard                ├── RecommendationCard                    ├── ResultHeader                ├── GradeCircle            ├── ui/                    ├── ResultTabPanel                ├── TrendTab                ├── recentScansHelpers                ├── PRBotTab                ├── RepoTab                    ├── parts                ├── TrendSummaryCard            ├── tabs/                    ├── parts                ├── SettingsTab                ├── AddScheduleForm                ├── MarketplaceTab                ├── BadgeTab                    ├── parts                ├── ScheduleRow                ├── RecentScansTab            ├── spec            ├── spec                ├── TrendChart            ├── share            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec                ├── cy            ├── spec    ├── setup-gitea            ├── spec        ├── config            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec        ├── spec            ├── spec            ├── spec            ├── spec            ├── spec            ├── spec        ├── karate-config    ├── server```

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
- **`BenchmarkCase`** — —
- **`BenchmarkEvent`** — —
- **`RecommendationFeedback`** — —
- **`BranchManager`** — Manages GitHub branch operations.
- **`PatchApplier`** — Applies patches to files in a GitHub repository.
- **`PRCreator`** — Creates GitHub PRs and issues.
- **`MirrorService`** — Service for mirroring repos to local Gitea.
- **`FunctionResult`** — —
- **`FileResult`** — —
- **`Violation`** — —
- **`RedslClient`** — HTTP client for the reDSL refactoring engine.
- **`MirrorConfig`** — Configuration for repo mirror.
- **`MirrorStatus`** — Status of mirror operation.
- **`Patch`** — Represents a single file patch.
- **`FixResult`** — Result of applying auto-fix.
- **`PatchGenerator`** — Generates patches for common code issues.
- **`AutoFixService`** — Service for creating auto-fix PRs.
- **`BillingEventType`** — —
- **`UsageTracker`** — Tracks usage per tenant for billing purposes.
- **`StripeBilling`** — Stripe integration for usage-based billing.
- **`AppRegistry`** — Central registry for all marketplace apps.
- **`AppResult`** — Standard result format for all apps.
- **`AppContext`** — Context passed to apps during execution.
- **`AppBase`** — Base class for all marketplace apps.
- **`AuditApp`** — Main code quality audit app.
- **`SecurityApp`** — Security vulnerability scanner.
- **`PerformanceApp`** — Performance bottleneck analyzer.
- **`GitProvider`** — Abstract base class for git platform integrations.
- **`EventType`** — Supported event types across all platforms.
- **`ProviderType`** — Supported git providers.
- **`Event`** — Unified event representation across all git platforms.
- **`GitLabAdapter`** — GitLab API implementation of GitProvider.
- **`GiteaAdapter`** — Gitea API implementation of GitProvider.
- **`GitHubAdapter`** — GitHub API implementation of GitProvider.
- **`ScheduleCreate`** — —
- **`ScheduleOut`** — —
- **`CaseCreate`** — —
- **`CaseUpdate`** — —
- **`DecisionPayload`** — —
- **`FeedbackPayload`** — —
- **`EventPayload`** — —
- **`CheckoutRequest`** — —
- **`BillingStatus`** — —
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
- **`RedslRefactorRequest`** — —
- **`RedslRefactorResult`** — —
- **`AnalyzeRequest`** — —
- **`RefactorRequest`** — —
- **`AutoPrRequest`** — —
- **`CreateMirrorRequest`** — —
- **`SyncMirrorRequest`** — —
- **`MirrorResponse`** — —
- **`MirrorInfo`** — —
- **`DataProcessor`** — —
- **`ApiServer`** — —

### Functions

- `lifespan(app)` — —
- `get_db()` — Get database session for dependency injection.
- `init_db()` — Initialize database with all tables.
- `get_sample_projects()` — Return list of sample projects for scanning.
- `get_celery_app()` — Get configured Celery application instance.
- `run_scheduled_scan(repo, token, webhook_url)` — Execute a full audit pipeline for *repo* (scheduled, no HTTP context).
- `generate_fix_id(repo, proposal_type)` — Generate a unique fix ID for tracking.
- `get_adapter_for_event(event, token)` — Factory function - get appropriate adapter for event provider.
- `process_pr_event(event, provider)` — Process pull request event - audit repo and comment results.
- `process_push_event(event, provider)` — Process push event - trigger analysis if main branch.
- `parse_github_webhook(payload)` — Parse GitHub webhook payload into Event.
- `parse_gitlab_webhook(payload)` — Parse GitLab webhook payload into Event.
- `parse_gitea_webhook(payload, gitea_event_header)` — Parse Gitea webhook payload into Event.
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
- `calculate_health_score(stats, complexity, duplication, quality)` — Calculate 0-100 health score from metrics.
- `score_to_grade(score)` — Convert score to letter grade.
- `generate_recommendations(complexity, duplication, quality)` — Generate actionable recommendations based on metrics.
- `create_connect_account(email, country)` — Create a Stripe Express Connect account for a publisher.
- `create_onboarding_link(account_id)` — Return onboarding URL for publisher to complete KYC.
- `get_account_status(account_id)` — Return payouts_enabled, charges_enabled, requirements.
- `transfer_revenue(amount_cents, account_id, metadata)` — Transfer publisher share (70%) to their Connect account.
- `get_installation_token(installation_id)` — Get GitHub App installation access token using JWT.
- `get_or_create_tenant(db, provider, provider_user_id, login)` — Get existing tenant or create new one.
- `get_tenant_by_id(db, tenant_id)` — Get tenant by ID.
- `update_tenant_plan(db, tenant_id, plan, billing_customer_id)` — Update tenant's billing plan.
- `convert_query(query)` — Convert query placeholders based on DB_TYPE.
- `execute_query(cursor, query, params)` — Execute query with automatic placeholder conversion.
- `upsert_user(github_id, login, name, avatar_url)` — Create or update a user. Returns the user dict.
- `get_user_by_github_id(github_id)` — Get user by GitHub ID.
- `get_user_by_id(user_id)` — Get user by internal ID.
- `get_subscription(user_id)` — Get active subscription for a user. Returns None if not found (treat as free).
- `upsert_subscription(user_id, plan, stripe_customer_id, stripe_subscription_id)` — Create or update subscription for a user.
- `increment_scan_count(user_id)` — Increment scans_this_week counter. Resets if a new week has started. Returns new count.
- `count_code_stats(repo_path)` — Count source files and lines.
- `analyze_complexity(repo_path)` — Analyze code complexity using Python (no external tools).
- `analyze_duplication(repo_path)` — Analyze code duplication using Python (no external tools).
- `analyze_quality(repo_path)` — Analyze code quality using Python (no external tools).
- `analyze_repo(repo, commit_sha, config)` — Analyze a repository and return health metrics.
- `run_tool(name, args, fallback)` — Run a semcod tool, return JSON result or fallback.
- `init_db()` — Initialize the database and create tables.
- `queue_event(event_id, event_type, provider, repo_full_name)` — Queue a new event for processing.
- `get_pending_events(limit)` — Get pending events for processing.
- `update_event_status(event_id, status, error_message)` — Update event processing status.
- `get_or_create_tenant(provider, provider_user_id, login, name)` — Get existing tenant or create new one.
- `get_tenant_by_id(tenant_id)` — Get tenant by ID.
- `update_tenant_plan(tenant_id, plan, billing_customer_id, billing_subscription_id)` — Update tenant's billing plan.
- `upsert_user(db, github_id, login, name)` — Create or update a user. Returns the user dict.
- `get_user_by_github_id(db, github_id)` — Get user by GitHub ID.
- `get_user_by_id(db, user_id)` — Get user by internal ID.
- `get_subscription(db, user_id)` — Get active subscription for a user. Returns None if not found (treat as free).
- `upsert_subscription(db, user_id, plan, stripe_customer_id)` — Create or update subscription for a user.
- `increment_scan_count(db, user_id)` — Increment scans_this_week counter. Resets if a new week has started. Returns new count.
- `create_benchmark_case(db, payload)` — —
- `get_benchmark_cases(db)` — —
- `get_benchmark_case(db, case_id)` — —
- `update_benchmark_case(db, case_id, updates)` — —
- `create_benchmark_event(db, case_id, payload)` — —
- `get_benchmark_events(db, case_id)` — —
- `upsert_recommendation_feedback(db, case_id, recommendation_id, payload)` — —
- `get_feedback_for_case(db, case_id)` — —
- `get_benchmark_summary(db)` — —
- `create_installation(tenant_id, repository_id, apps, webhook_id)` — Create app installation for a repository.
- `get_installation(tenant_id, repository_id)` — Get installation by tenant and repository.
- `get_tenant_installations(tenant_id)` — Get all installations for a tenant.
- `delete_installation(tenant_id, repository_id)` — Delete installation (soft delete - set inactive).
- `update_installation_scan(tenant_id, repository_id, score)` — Update last scan info for installation.
- `get_or_create_repository(db, tenant_id, provider, repo_provider_id)` — Get existing repository or create new one for tenant.
- `get_tenant_repositories(db, tenant_id)` — Get all repositories for a tenant.
- `get_repository_by_full_name(db, tenant_id, provider, full_name)` — Get repository by tenant + provider + full_name.
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
- `get_or_create_repository(tenant_id, provider, repo_provider_id, name)` — Get existing repository or create new one for tenant.
- `get_tenant_repositories(tenant_id)` — Get all repositories for a tenant.
- `get_repository_by_full_name(tenant_id, provider, full_name)` — Get repository by tenant + provider + full_name.
- `get_usage_tracker()` — Get singleton usage tracker.
- `get_stripe_billing()` — Get singleton Stripe billing.
- `save_scan(db, scan_data)` — Save a scan to the database.
- `get_recent_scans(db, limit)` — Get recent scans from the database.
- `get_repo_scans(db, repo, limit)` — Get scans for a specific repository ordered by date ascending.
- `get_total_scan_count(db)` — Get total number of scans in the database.
- `save_audit_result(db, audit_id, audit_data)` — Save audit result to database. Merges benchmark meta into audit_meta JSON.
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
- `create_benchmark_case(payload)` — —
- `get_benchmark_cases()` — —
- `get_benchmark_case(case_id)` — —
- `update_benchmark_case(case_id, updates)` — —
- `create_benchmark_event(case_id, payload)` — —
- `get_benchmark_events(case_id)` — —
- `upsert_recommendation_feedback(case_id, recommendation_id, payload)` — —
- `get_feedback_for_case(case_id)` — —
- `get_benchmark_summary()` — —
- `shared_task(fn)` — Drop-in replacement for celery.shared_task with no broker dependency.
- `check_health_regression(repo, previous_score, new_score, threshold)` — Check if health score regressed and create issue if needed.
- `check_score_and_notify(repo, previous_score, new_score, tenant_id)` — Check if score improved after auto-fix and send notifications.
- `sync_mirror_task(self, mirror_id, source_repo, source_provider)` — Sync mirror from source to Gitea asynchronously.
- `schedule_periodic_mirrors()` — Schedule periodic sync for all active mirrors.
- `create_auto_pr(self, repo, base_branch, patches)` — Create automated PR with fixes asynchronously.
- `create_auto_fix_pr(self, repo, base_branch, files)` — Create automated PR with fixes asynchronously.
- `upgrade()` — —
- `downgrade()` — —
- `task_redsl_analyze(self, project_path, repo)` — Background: run reDSL analysis and save results.
- `task_redsl_refactor(self, project_path, max_actions)` — Background: run reDSL refactoring.
- `task_redsl_health_check(self, project_path)` — Background: get health score for a project.
- `task_redsl_scheduled_quality_check()` — Scheduled: scan all repos with health < 70.
- `task_redsl_scheduled_auto_refactor()` — Scheduled weekly: auto-refactor up to 5 repos with health < 50.
- `scan_sample_projects()` — Scan all sample projects and save to database.
- `load_manifest(app_name)` — Load manifest.yaml for an app.
- `load_pricing(app_name)` — Load pricing.json for an app.
- `load_app(app_name)` — Load a single app by name.
- `load_apps()` — Load all available apps.
- `get_app_by_trigger(trigger)` — Get all apps that respond to a specific trigger.
- `validate_manifest(manifest)` — Validate manifest structure. Returns list of errors.
- `run_audit(self, repo, commit_sha, config)` — Run code audit on a repository asynchronously.
- `process_pr_event(self, event_dict)` — Process pull request event asynchronously.
- `process_push_event(event_dict)` — Process push event - trigger analysis for default branch.
- `analyze_diff(self, repo, diff, config)` — Analyze a diff asynchronously using actual analysis.
- `get_registry()` — Get singleton registry instance.
- `on_pr_comment(event, context)` — Handle PR comment commands.
- `get_adapter_for_event(event, token)` — Factory function - get appropriate adapter for event provider.
- `parse_gitea_event(payload, gitea_event_header)` — Parse Gitea webhook payload into unified Event.
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
- `gitea_oauth_start()` — Step 1: Redirect user to Gitea OAuth.
- `gitea_oauth_callback(code)` — Step 2: Exchange code for token, fetch profile, create user, issue JWT.
- `get_me(user)` — —
- `logout()` — —
- `list_repos(user)` — List user's repos for audit selection.
- `get_repo_trend(owner, repo, days)` — Get historical health scores for a repository.
- `compare_repo_trend(owner, repo, days)` — Compare the latest scan against the scan from {days} ago.
- `get_scan_diff(owner, repo)` — Compare the latest scan against the previous one for a repository.
- `get_scheduler()` — —
- `start_scheduler()` — —
- `stop_scheduler()` — —
- `create_schedule(body)` — Register a new periodic scan for a repository.
- `list_schedules()` — List all active scan schedules.
- `get_schedule(owner, repo)` — Get schedule details for a specific repository.
- `update_schedule(owner, repo, body)` — Update interval or webhook for an existing schedule.
- `delete_schedule(owner, repo)` — Remove a scheduled scan.
- `get_standard_metrics(limit)` — Get standardized metrics for recent scans.
- `get_metrics_summary()` — Get summary statistics of all scans.
- `get_repository_metrics(repo_path)` — Get metrics for a specific repository.
- `download_project_prompt()` — Download the project prompt.txt file for LLM analysis.
- `download_project_prompt_markdown()` — Download the project prompt as markdown format.
- `health_badge(repo_slug, style)` — Generate SVG badge with code health score.
- `scan_count_badge()` — Generate SVG badge showing total number of scans performed.
- `post_case(body)` — —
- `list_cases()` — —
- `get_case(case_id)` — —
- `patch_case(case_id, body)` — —
- `post_decision(case_id, body)` — —
- `post_feedback(case_id, recommendation_id, body)` — —
- `list_feedback(case_id)` — —
- `post_event(case_id, body)` — —
- `list_events(case_id)` — —
- `summary()` — —
- `export_json()` — —
- `export_csv()` — —
- `github_webhook(request)` — Handle GitHub webhook events using unified adapter system.
- `gitlab_webhook(request)` — Handle GitLab webhook events.
- `gitea_webhook(request)` — Handle Gitea webhook events.
- `report_page(owner, repo)` — Redirect to frontend report page.
- `run_audit(request, user)` — Run one-click audit on a repo. Requires authentication.
- `get_audit_result_endpoint(audit_id)` — Poll audit status and results.
- `get_recent_scans_api(limit)` — Get list of recent scans with metrics.
- `analyze_repo(request)` — Analyze any public repository by URL (sandbox mode). Supports file:// for local repos.
- `list_plans()` — Return available plans and pricing (no auth required).
- `billing_status(user)` — Return current plan, limits, and scan usage for the authenticated user.
- `create_checkout(body, user)` — Create a Stripe Checkout session.
- `billing_portal(user)` — Create a Stripe Customer Portal session.
- `stripe_webhook(request)` — Handle Stripe webhook events.
- `check_scan_allowed(user_id)` — Raise HTTP 402 if the user has hit their weekly scan limit.
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
- `createBenchmarkCase()` — —
- `updateBenchmarkCase()` — —
- `submitRecommendationFeedback()` — —
- `submitBenchmarkDecision()` — —
- `trackBenchmarkEvent()` — —
- `fetchBenchmarkSummary()` — —
- `downloadBenchmarkExport()` — —
- `getRedslStatus()` — —
- `redslAnalyze()` — —
- `redslHealth()` — —
- `redslRefactor()` — —
- `redslDecide()` — —
- `redslBadgeUrl()` — —
- `create_auto_pr(body, user)` — Apply LLM-generated patches to a repository and create a GitHub PR.
- `create_redsl_auto_pr(body, user)` — Use reDSL engine to analyze and refactor a project, then create a PR.
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
- `safeTrack()` — —
- `useBenchmarkTracking()` — —
- `prevPhase()` — —
- `trackedResultEntry()` — —
- `startedAt()` — —
- `prev()` — —
- `elapsed()` — —
- `trackExport()` — —
- `trackRecommendationOpened()` — —
- `trackDecision()` — —
- `useSessionCallbackBootstrap()` — —
- `searchParams()` — —
- `session()` — —
- `useSessionProfile()` — —
- `getOAuthStartUrl()` — —
- `confirmAuthFlow()` — —
- `logoutSession()` — —
- `useSession()` — —
- `startOAuth()` — —
- `confirmAuth()` — —
- `clearSession()` — —
- `useBenchmarkState()` — —
- `useRepoList()` — —
- `VALID_TABS()` — —
- `VALID_PHASES()` — —
- `parseRepositoryReference()` — —
- `trimmed()` — —
- `urlMatch()` — —
- `parts()` — —
- `createSelectedRepo()` — —
- `parsed()` — —
- `parseHashState()` — —
- `params()` — —
- `tab()` — —
- `phase()` — —
- `repo()` — —
- `sandbox()` — —
- `audit()` — —
- `restoreAuditFromHash()` — —
- `useHashBootstrap()` — —
- `state()` — —
- `repoData()` — —
- `useHashSync()` — —
- `get_status()` — Check if reDSL engine is available.
- `analyze(body, bg)` — Run reDSL analysis on a project.
- `get_health(body)` — Get unified health score for a project.
- `run_refactor(body, bg)` — Run reDSL refactoring on a project.
- `run_decide(body)` — Evaluate DSL rules without execution — returns decisions only.
- `run_batch_hybrid(project_path, max_changes)` — Run hybrid quality refactoring (no LLM needed).
- `health_badge(owner, repo)` — SVG badge with health score — for README.md embedding.
- `useAppState()` — —
- `session()` — —
- `billing()` — —
- `audit()` — —
- `benchmark()` — —
- `reset()` — —
- `doLogout()` — —
- `useAuditActions()` — —
- `startAudit()` — —
- `data()` — —
- `startSandbox()` — —
- `url()` — —
- `repoData()` — —
- `resetAudit()` — —
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
- `MetricCard()` — —
- `ProgressSteps()` — —
- `currentIdx()` — —
- `stepIdx()` — —
- `done()` — —
- `active()` — —
- `RecommendationCard()` — —
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
- `GradeCircle()` — —
- `color()` — —
- `r()` — —
- `circ()` — —
- `targetOffset()` — —
- `t()` — —
- `PlanCard()` — —
- `PaywallModal()` — —
- `GitHubIcon()` — —
- `GitLabIcon()` — —
- `GiteaIcon()` — —
- `loadPreview()` — —
- `result()` — —
- `formatComment()` — —
- `getSeverityIcon()` — —
- `ShareButtons()` — —
- `handleShare()` — —
- `shareUrls()` — —
- `isPro()` — —
- `getAppIcon()` — —
- `getTriggerIcon()` — —
- `MetricRow()` — —
- `ok()` — —
- `RedslHealthCard()` — —
- `handleRefactor()` — —
- `result()` — —
- `h()` — —
- `grade()` — —
- `score()` — —
- `checkStatus()` — —
- `result()` — —
- `handleInstall()` — —
- `handleUninstall()` — —
- `handleSubmit()` — —
- `caseId()` — —
- `setCaseId()` — —
- `handleCreate()` — —
- `ScoreSelect()` — —
- `handleSubmit()` — —
- `AuthPhase()` — —
- `handleLogin()` — —
- `create_mirror(request, user)` — Create new mirror from GitHub/GitLab to local Gitea.
- `sync_mirror(request, user)` — Sync existing mirror with latest changes from source.
- `list_mirrors(user)` — List all mirrors for current user.
- `get_mirror(mirror_id, user)` — Get mirror by ID.
- `delete_mirror(mirror_id, user)` — Delete mirror.
- `ScanningPhase()` — —
- `ReposPhase()` — —
- `ResultMetrics()` — —
- `ResultRecommendations()` — —
- `DownloadButtons()` — —
- `active()` — —
- `ErrorResult()` — —
- `ResultPhase()` — —
- `data()` — —
- `repoName()` — —
- `activeContent()` — —
- `handleCopy()` — —
- `handleDownload()` — —
- `LandingPhase()` — —
- `fetchRecentScans()` — —
- `response()` — —
- `data()` — —
- `formatDate()` — —
- `date()` — —
- `ResultHeader()` — —
- `ResultTabPanel()` — —
- `TrendTab()` — —
- `repoName()` — —
- `history()` — —
- `fetchRecentScans()` — —
- `response()` — —
- `data()` — —
- `formatRecentScanDate()` — —
- `date()` — —
- `getPrimaryLanguage()` — —
- `openRecentScanRepository()` — —
- `openRecentScanAudit()` — —
- `PRBotTab()` — —
- `RepoTab()` — —
- `TrendEmptyState()` — —
- `TrendHeader()` — —
- `DaySelector()` — —
- `DayButton()` — —
- `TrendLoadingState()` — —
- `TrendErrorState()` — —
- `TrendContent()` — —
- `latest()` — —
- `prev()` — —
- `delta()` — —
- `directionColor()` — —
- `getDirectionColor()` — —
- `TrendSummaryCards()` — —
- `TrendChartContainer()` — —
- `TrendSummaryCard()` — —
- `sign()` — —
- `deltaColor()` — —
- `SectionHeader()` — —
- `BillingSection()` — —
- `plan()` — —
- `planColor()` — —
- `handleBillingPortal()` — —
- `getPlanColor()` — —
- `BillingPortalButton()` — —
- `SchedulesSection()` — —
- `handleDelete()` — —
- `AddScheduleButton()` — —
- `SchedulesList()` — —
- `SettingsTab()` — —
- `loadSchedules()` — —
- `AddScheduleForm()` — —
- `handleSubmit()` — —
- `MarketplaceTab()` — —
- `provider()` — —
- `BadgeSVG()` — —
- `color()` — —
- `labelW()` — —
- `valueText()` — —
- `valueW()` — —
- `BadgeTab()` — —
- `badgeUrl()` — —
- `LanguageBadge()` — —
- `language()` — —
- `ScanMetrics()` — —
- `RecentScanCard()` — —
- `RecentScansEmptyState()` — —
- `RecentScansHeader()` — —
- `RecentScansBadgeInfo()` — —
- `ScheduleRow()` — —
- `handleDelete()` — —
- `RecentScansTab()` — —
- `input()` — —
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
- `recentSection()` — —
- `isVisible()` — —
- `scanCards()` — —
- `count()` — —
- `scanCard()` — —
- `viewButton()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `blueskyButton()` — —
- `anyVisible()` — —
- `shareButtons()` — —
- `count()` — —
- `recentSection()` — —
- `isVisible()` — —
- `baseURL()` — —
- `response()` — —
- `data()` — —
- `scan()` — —
- `listResponse()` — —
- `listData()` — —
- `repo()` — —
- `toggle()` — —
- `btn()` — —
- `sourceSelect()` — —
- `API()` — —
- `res()` — —
- `body()` — —
- `create()` — —
- `patch()` — —
- `decision()` — —
- `feedback()` — —
- `event()` — —
- `list()` — —
- `events()` — —
- `exp()` — —
- `exportBody()` — —
- `dup()` — —
- `API()` — —
- `res()` — —
- `ct()` — —
- `body()` — —
- `errorText()` — —
- `marketplaceContent()` — —
- `found()` — —
- `el()` — —
- `pricingText()` — —
- `hasPricing()` — —
- `auditTab()` — —
- `badgeTab()` — —
- `marketTab()` — —
- `jsonErrors()` — —
- `url()` — —
- `input()` — —
- `API()` — —
- `infoRes()` — —
- `info()` — —
- `resourcesRes()` — —
- `resources()` — —
- `toolsRes()` — —
- `tools()` — —
- `toolNames()` — —
- `invokeRes()` — —
- `invokeBody()` — —
- `create()` — —
- `patch()` — —
- `decision()` — —
- `feedback()` — —
- `event()` — —
- `exp()` — —
- `exportBody()` — —
- `res()` — —
- `ct()` — —
- `dup()` — —
- `currentUrl()` — —
- `recentScansSection()` — —
- `isVisible()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `recentTab()` — —
- `isTabVisible()` — —
- `FRONTEND_URL()` — —
- `MOCK_GITHUB_URL()` — —
- `FRONTEND_URL()` — —
- `MOCK_GITHUB_URL()` — —
- `res()` — —
- `loginElement()` — —
- `element()` — —
- `currentUrl()` — —
- `userBtn()` — —
- `isLoggedIn()` — —
- `content()` — —
- `testOAuthFlow()` — —
- `loginClicked()` — —
- `userButtonClicked()` — —
- `attemptLogin()` — —
- `attemptUserLogin()` — —
- `checkLoginStatus()` — —
- `api()` — —
- `create_repo_with_code()` — —
- `process()` — —
- `validate()` — —
- `transform()` — —
- `complex_function()` — —
- `constructor()` — —
- `listen()` — —
- `deploy()` — —
- `FRONTEND_URL()` — —
- `MOCK_GITHUB_URL()` — —
- `BACKEND_URL()` — —
- `res()` — —
- `body()` — —
- `issueRes()` — —
- `tokenRes()` — —
- `tokenBody()` — —
- `userRes()` — —
- `user()` — —
- `reposRes()` — —
- `repos()` — —
- `loginBtn()` — —
- `userBtn()` — —
- `input()` — —
- `skipInCI()` — —
- `recentSection()` — —
- `isVisible()` — —
- `scanCards()` — —
- `count()` — —
- `scanCard()` — —
- `viewButton()` — —
- `repoButtons()` — —
- `count()` — —
- `demoButton()` — —
- `isVisible()` — —
- `skipInCI()` — —
- `response()` — —
- `data()` — —
- `scan()` — —
- `listResponse()` — —
- `listData()` — —
- `repo()` — —
- `FRONTEND_URL()` — —
- `GITEA_URL()` — —
- `BACKEND_URL()` — —
- `ver()` — —
- `repos()` — —
- `body()` — —
- `data()` — —
- `branchRes()` — —
- `fileRes()` — —
- `fileSha()` — —
- `newContent()` — —
- `commitRes()` — —
- `prRes()` — —
- `pr()` — —
- `diffRes()` — —
- `diff()` — —
- `res()` — —
- `ct()` — —
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
- `currentUrl()` — —
- `recentScansSection()` — —
- `isVisible()` — —
- `twitterButton()` — —
- `linkedinButton()` — —
- `twitterVisible()` — —
- `linkedinVisible()` — —
- `recentTab()` — —
- `isTabVisible()` — —
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
- `fn()` — —
- `get_mock_user()` — Get mock user configuration from environment variables.
- `authorize(client_id, redirect_uri, scope, state)` — Show a simple login page that lets testers pick a user.
- `issue_code(request)` — Internal endpoint: register an auth code.
- `access_token(request)` — Exchange code for access token (mimics GitHub).
- `get_user(authorization)` — —
- `get_repos(authorization, per_page, page, sort)` — —
- `health()` — —


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
📄 `backend.db_models` (1 functions, 13 classes)
📦 `backend.db_module`
📄 `backend.db_module.benchmark_orm` (15 functions)
📄 `backend.db_module.db_connection` (1 functions)
📄 `backend.db_module.events` (3 functions)
📄 `backend.db_module.events_orm` (3 functions)
📄 `backend.db_module.installations` (5 functions)
📄 `backend.db_module.installations_orm` (5 functions)
📄 `backend.db_module.repositories` (3 functions)
📄 `backend.db_module.repositories_orm` (3 functions)
📄 `backend.db_module.scans` (8 functions)
📄 `backend.db_module.scans_orm` (8 functions)
📄 `backend.db_module.schema` (1 functions)
📄 `backend.db_module.tenants` (3 functions)
📄 `backend.db_module.tenants_orm` (3 functions)
📄 `backend.db_module.users` (8 functions)
📄 `backend.db_module.users_orm` (6 functions)
📄 `backend.db_module.wrappers` (37 functions)
📄 `backend.db_session` (3 functions)
📦 `backend.events`
📄 `backend.events.models` (5 functions, 3 classes)
📄 `backend.quality_gate` (12 functions, 3 classes)
📄 `backend.routers.audit` (8 functions)
📄 `backend.routers.auth` (10 functions)
📄 `backend.routers.autopr` (4 functions, 5 classes)
📄 `backend.routers.badge` (4 functions)
📄 `backend.routers.benchmark` (12 functions, 5 classes)
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
📄 `backend.routers.redsl` (9 functions, 3 classes)
📄 `backend.routers.report` (1 functions)
📄 `backend.routers.system` (2 functions)
📄 `backend.routers.trend` (8 functions)
📄 `backend.routers.webhook` (6 functions)
📄 `backend.routers.webhook_v2` (5 functions)
📄 `backend.sample_projects` (1 functions)
📄 `backend.scheduler.cron` (13 functions, 2 classes)
📄 `backend.scheduler.scan_job` (5 functions)
📄 `backend.scripts.scan_samples` (1 functions)
📄 `backend.server` (1 functions)
📄 `backend.services.analyzer` (18 functions)
📄 `backend.services.autofix` (8 functions, 4 classes)
📄 `backend.services.autopr_helpers` (11 functions, 3 classes)
📄 `backend.services.billing` (16 functions, 3 classes)
📄 `backend.services.github_client` (1 functions)
📄 `backend.services.mirror` (11 functions, 1 classes)
📄 `backend.services.mirror_models` (2 classes)
📄 `backend.services.redsl_client` (7 functions, 1 classes)
📄 `backend.services.scan_service`
📄 `backend.services.scoring` (4 functions)
📄 `backend.services.stripe_connect` (5 functions)
📄 `backend.services.webhook_service` (8 functions)
📄 `backend.store`
📦 `backend.worker`
📄 `backend.worker._celery_stub` (6 functions, 1 classes)
📦 `backend.worker.tasks`
📄 `backend.worker.tasks.autopr` (3 functions)
📄 `backend.worker.tasks.maintenance` (2 functions)
📄 `backend.worker.tasks.marketplace` (3 functions)
📄 `backend.worker.tasks.redsl` (8 functions)
📄 `backend.worker.tasks.scan` (7 functions)
📄 `e2e.gitea-oauth-cycle.spec` (19 functions)
📄 `e2e.karate.karate-config` (1 functions)
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
📄 `frontend.cypress.e2e.oauth-login.cy` (2 functions)
📄 `frontend.e2e.audit.spec`
📄 `frontend.e2e.badge.spec` (1 functions)
📄 `frontend.e2e.benchmark.spec` (18 functions)
📄 `frontend.e2e.github-login-sim.spec` (16 functions)
📄 `frontend.e2e.gui-login-enhanced.spec` (18 functions)
📄 `frontend.e2e.marketplace-flow.spec` (20 functions)
📄 `frontend.e2e.metrics.spec` (14 functions)
📄 `frontend.e2e.recent-scans.spec` (8 functions)
📄 `frontend.e2e.scan-workflow.spec` (9 functions)
📄 `frontend.e2e.smoke.spec` (1 functions)
📄 `frontend.e2e.social-sharing.spec` (10 functions)
📄 `frontend.e2e.system-integration.spec` (27 functions)
📄 `frontend.playwright.config`
📄 `frontend.src.App`
📄 `frontend.src.api` (64 functions)
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
📄 `frontend.src.components.RedslHealthCard` (8 functions)
📄 `frontend.src.components.ShareButtons` (3 functions)
📄 `frontend.src.components.benchmark.BenchmarkDecisionPanel` (1 functions)
📄 `frontend.src.components.benchmark.BenchmarkReviewPanel` (3 functions)
📄 `frontend.src.components.benchmark.RecommendationFeedbackForm` (2 functions)
📦 `frontend.src.components.phases`
📄 `frontend.src.components.phases.AuthPhase` (2 functions)
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
📄 `frontend.src.components.tabs.SettingsTab` (2 functions)
📄 `frontend.src.components.tabs.SettingsTab.parts` (11 functions)
📄 `frontend.src.components.tabs.TrendChart` (9 functions)
📄 `frontend.src.components.tabs.TrendSummaryCard` (3 functions)
📄 `frontend.src.components.tabs.TrendTab` (3 functions)
📄 `frontend.src.components.tabs.TrendTab.parts` (14 functions)
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
📄 `frontend.src.hooks.useAuth` (7 functions)
📄 `frontend.src.hooks.useBenchmarkState` (1 functions)
📄 `frontend.src.hooks.useBenchmarkTracking` (10 functions)
📄 `frontend.src.hooks.useBilling` (5 functions)
📄 `frontend.src.hooks.useDownloads` (21 functions)
📄 `frontend.src.hooks.usePolling` (10 functions)
📄 `frontend.src.hooks.useRepoList` (1 functions)
📄 `frontend.src.hooks.useSession` (4 functions)
📄 `frontend.src.hooks.useUrlState` (21 functions)
📄 `frontend.src.main`
📄 `frontend.src.utils.share` (8 functions)
📄 `frontend.vite.config`
📄 `mock-github.server` (8 functions)
📄 `project`
📄 `run-sim`
📄 `scripts.setup-gitea` (11 functions, 2 classes)
📄 `traefik.generate-certs`

## Requirements

- axios ^1.15.0

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