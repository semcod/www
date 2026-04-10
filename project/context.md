# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/www
- **Primary Language**: javascript
- **Languages**: javascript: 49, python: 18, shell: 1
- **Analysis Mode**: static
- **Total Functions**: 212
- **Total Classes**: 4
- **Modules**: 68
- **Entry Points**: 174

## Architecture by Module

### frontend.src.hooks.useAppState
- **Functions**: 29
- **File**: `useAppState.js`

### frontend.src.components.phases.ResultPhase
- **Functions**: 21
- **File**: `ResultPhase.jsx`

### frontend.e2e.metrics.spec
- **Functions**: 13
- **File**: `metrics.spec.js`

### e2e.specs.metrics.spec
- **Functions**: 13
- **File**: `metrics.spec.js`

### frontend.src.components.tabs.RecentScansTab
- **Functions**: 10
- **File**: `RecentScansTab.jsx`

### frontend.e2e.social-sharing.spec
- **Functions**: 10
- **File**: `social-sharing.spec.js`

### e2e.specs.social-sharing.spec
- **Functions**: 10
- **File**: `social-sharing.spec.js`

### frontend.e2e.scan-workflow.spec
- **Functions**: 9
- **File**: `scan-workflow.spec.js`

### e2e.specs.scan-workflow.spec
- **Functions**: 9
- **File**: `scan-workflow.spec.js`

### frontend.src.api
- **Functions**: 8
- **File**: `api.js`

### frontend.src.components.phases.LandingPhase
- **Functions**: 8
- **File**: `LandingPhase.jsx`

### backend.routers.audit
- **Functions**: 8
- **File**: `audit.py`

### frontend.src.utils.share
- **Functions**: 8
- **File**: `share.js`

### frontend.e2e.recent-scans.spec
- **Functions**: 8
- **File**: `recent-scans.spec.js`

### e2e.specs.recent-scans.spec
- **Functions**: 8
- **File**: `recent-scans.spec.js`

### frontend.src.components.tabs.BadgeTab
- **Functions**: 7
- **File**: `BadgeTab.jsx`

### backend.routers.metrics
- **Functions**: 6
- **File**: `metrics.py`

### frontend.src.components.GradeCircle
- **Functions**: 6
- **File**: `GradeCircle.jsx`

### backend.routers.webhook
- **Functions**: 5
- **File**: `webhook.py`

### frontend.src.components.ProgressSteps
- **Functions**: 5
- **File**: `ProgressSteps.jsx`

## Key Entry Points

Main execution flows into the system:

### backend.routers.mcp.mcp_invoke_tool
> Invoke an MCP tool with the provided arguments.
- **Calls**: router.post, HTTPException, request.arguments.get, request.arguments.get, request.arguments.get, HTTPException, None.hexdigest, None.isoformat

### frontend.src.hooks.useAppState.useAppState
- **Calls**: frontend.src.hooks.useAppState.useState, frontend.src.hooks.useAppState.useEffect, frontend.src.hooks.useAppState.slice, frontend.src.hooks.useAppState.URLSearchParams, frontend.src.hooks.useAppState.get, frontend.src.hooks.useAppState.setToken, frontend.src.hooks.useAppState.includes, frontend.src.hooks.useAppState.setTab

### backend.routers.mcp.mcp_get_resource
> Get content of a specific MCP resource by URI.
- **Calls**: router.get, HTTPException, backend.database.get_recent_scans, MCPResourceResponse, uri.startswith, uri.replace, audit_results.get, MCPResourceResponse

### backend.scripts.scan_samples.scan_sample_projects
> Scan all sample projects and save to database.
- **Calls**: backend.sample_projects.get_sample_projects, print, print, enumerate, print, print, print, sum

### backend.routers.metrics.get_standard_metrics
> Get standardized metrics for recent scans.
This endpoint provides a consistent format for remote clients.

Response format:
{
    "meta": {
        "g
- **Calls**: router.get, backend.database.get_recent_scans, backend.database.get_total_scan_count, formatted_scans.append, HTTPException, None.lower, scan.get, backend.routers.metrics._utc_now_iso

### frontend.src.components.tabs.RecentScansTab.RecentScansTab
- **Calls**: frontend.src.components.tabs.RecentScansTab.useState, frontend.src.components.tabs.RecentScansTab.useEffect, frontend.src.components.tabs.RecentScansTab.fetchRecentScans, frontend.src.components.tabs.RecentScansTab.fetch, frontend.src.components.tabs.RecentScansTab.json, frontend.src.components.tabs.RecentScansTab.setScans, frontend.src.components.tabs.RecentScansTab.error, frontend.src.components.tabs.RecentScansTab.setLoading

### frontend.src.components.phases.ResultPhase.ResultPhase
- **Calls**: frontend.src.components.phases.ResultPhase.getShareUrls, frontend.src.components.phases.ResultPhase.open, frontend.src.components.phases.ResultPhase.Blob, frontend.src.components.phases.ResultPhase.stringify, frontend.src.components.phases.ResultPhase.createObjectURL, frontend.src.components.phases.ResultPhase.createElement, frontend.src.components.phases.ResultPhase.replace, frontend.src.components.phases.ResultPhase.appendChild

### frontend.src.components.phases.LandingPhase.LandingPhase
- **Calls**: frontend.src.components.phases.LandingPhase.useState, frontend.src.components.phases.LandingPhase.useEffect, frontend.src.components.phases.LandingPhase.fetchRecentScans, frontend.src.components.phases.LandingPhase.fetch, frontend.src.components.phases.LandingPhase.json, frontend.src.components.phases.LandingPhase.setRecentScans, frontend.src.components.phases.LandingPhase.error, frontend.src.components.phases.LandingPhase.getShareUrls

### backend.routers.audit.analyze_repo
> Analyze any public repository by URL (sandbox mode).
- **Calls**: router.post, body.get, body.get, backend.routers.audit._schedule_background_task, request.json, HTTPException, re.search, re.search

### backend.routers.metrics.get_metrics_summary
> Get summary statistics of all scans.
Useful for dashboards and monitoring.
- **Calls**: router.get, backend.database.get_recent_scans, sum, sum, sum, len, HTTPException, grade_dist.get

### frontend.src.components.phases.ResultPhase.handleDownloadToon
- **Calls**: frontend.src.components.phases.ResultPhase.Date, frontend.src.components.phases.ResultPhase.toISOString, frontend.src.components.phases.ResultPhase.split, frontend.src.components.phases.ResultPhase.stringify, frontend.src.components.phases.ResultPhase.toFixed, frontend.src.components.phases.ResultPhase.map, frontend.src.components.phases.ResultPhase.toUpperCase, frontend.src.components.phases.ResultPhase.join

### backend.routers.webhook.github_webhook
> Handle GitHub webhook events.
- **Calls**: router.post, request.headers.get, request.headers.get, json.loads, request.body, payload.get, payload.get, None.hexdigest

### frontend.src.components.phases.ResultPhase.handleDownloadPrompt
- **Calls**: frontend.src.components.phases.ResultPhase.Date, frontend.src.components.phases.ResultPhase.toISOString, frontend.src.components.phases.ResultPhase.stringify, frontend.src.components.phases.ResultPhase.toFixed, frontend.src.components.phases.ResultPhase.map, frontend.src.components.phases.ResultPhase.join, frontend.src.components.phases.ResultPhase.Blob, frontend.src.components.phases.ResultPhase.createObjectURL

### frontend.src.components.phases.ResultPhase.handleDownloadMarkdown
- **Calls**: frontend.src.components.phases.ResultPhase.Date, frontend.src.components.phases.ResultPhase.toISOString, frontend.src.components.phases.ResultPhase.entries, frontend.src.components.phases.ResultPhase.map, frontend.src.components.phases.ResultPhase.join, frontend.src.components.phases.ResultPhase.toFixed, frontend.src.components.phases.ResultPhase.Blob, frontend.src.components.phases.ResultPhase.createObjectURL

### backend.routers.metrics.get_repository_metrics
> Get metrics for a specific repository.
repo_path format: "owner/repo" or with platform prefix "github:owner/repo"
- **Calls**: router.get, backend.database.get_recent_scans, repo_path.split, HTTPException, HTTPException, backend.routers.metrics._utc_now_iso, len, latest_scan.get

### backend.routers.auth.list_repos
> List user's repos for audit selection.
- **Calls**: router.get, resp.json, httpx.AsyncClient, client.get, r.get, r.get, r.get, r.get

### frontend.src.hooks.useAppState.startSandbox
- **Calls**: frontend.src.hooks.useAppState.useCallback, frontend.src.hooks.useAppState.trim, frontend.src.hooks.useAppState.match, frontend.src.hooks.useAppState.setSelectedRepo, frontend.src.hooks.useAppState.setIsSandbox, frontend.src.hooks.useAppState.setPhase, frontend.src.hooks.useAppState.analyzePublicRepo, frontend.src.hooks.useAppState.then

### backend.routers.audit.run_audit
> Run one-click audit on a repo. Body: { "repo": "owner/name", "token": "ghp_..." }
- **Calls**: router.post, backend.routers.audit._schedule_background_task, request.json, None.hexdigest, backend.routers.audit._utc_now_iso, backend.routers.audit._run_audit_pipeline, hashlib.sha256, None.encode

### frontend.src.components.phases.ResultPhase.handleDownloadMetrics
- **Calls**: frontend.src.components.phases.ResultPhase.Blob, frontend.src.components.phases.ResultPhase.stringify, frontend.src.components.phases.ResultPhase.createObjectURL, frontend.src.components.phases.ResultPhase.createElement, frontend.src.components.phases.ResultPhase.replace, frontend.src.components.phases.ResultPhase.appendChild, frontend.src.components.phases.ResultPhase.click, frontend.src.components.phases.ResultPhase.removeChild

### frontend.src.components.GradeCircle.GradeCircle
- **Calls**: frontend.src.components.GradeCircle.useState, frontend.src.components.GradeCircle.gradeColor, frontend.src.components.GradeCircle.useEffect, frontend.src.components.GradeCircle.setTimeout, frontend.src.components.GradeCircle.setAnimatedOffset, frontend.src.components.GradeCircle.clearTimeout, frontend.src.components.GradeCircle.rotate, frontend.src.components.GradeCircle.bezier

### backend.database.save_scan
> Save a scan to the database.
- **Calls**: sqlite3.connect, conn.cursor, cursor.execute, conn.commit, conn.close, json.dumps, scan_data.get, scan_data.get

### backend.routers.auth.github_oauth_callback
> Step 2: Exchange code for token, redirect to frontend.
- **Calls**: router.get, data.get, RedirectResponse, httpx.AsyncClient, resp.json, HTTPException, client.post

### backend.routers.metrics.download_project_prompt_markdown
> Download the project prompt as markdown format.
- **Calls**: router.get, Response, prompt_path.exists, HTTPException, open, f.read, Path

### frontend.src.hooks.useAppState.reset
- **Calls**: frontend.src.hooks.useAppState.useCallback, frontend.src.hooks.useAppState.setPhase, frontend.src.hooks.useAppState.setSelectedRepo, frontend.src.hooks.useAppState.setAudit, frontend.src.hooks.useAppState.setIsSandbox, frontend.src.hooks.useAppState.setRepoUrl, frontend.src.hooks.useAppState.setAuditId

### frontend.src.components.tabs.BadgeTab.BadgeTab
- **Calls**: frontend.src.components.tabs.BadgeTab.useState, frontend.src.components.tabs.BadgeTab.getBadgeUrl, frontend.src.components.tabs.BadgeTab.Repository, frontend.src.components.tabs.BadgeTab.setBadgeRepo, frontend.src.components.tabs.BadgeTab.writeText, frontend.src.components.tabs.BadgeTab.map, frontend.src.components.tabs.BadgeTab.gradeColor

### frontend.e2e.recent-scans.spec.recentSection
- **Calls**: frontend.e2e.recent-scans.spec.locator, frontend.e2e.recent-scans.spec.filter, frontend.e2e.recent-scans.spec.count, frontend.e2e.recent-scans.spec.expect, frontend.e2e.recent-scans.spec.toBeGreaterThan, frontend.e2e.recent-scans.spec.first, frontend.e2e.recent-scans.spec.toBeVisible

### frontend.e2e.recent-scans.spec.isVisible
- **Calls**: frontend.e2e.recent-scans.spec.locator, frontend.e2e.recent-scans.spec.filter, frontend.e2e.recent-scans.spec.count, frontend.e2e.recent-scans.spec.expect, frontend.e2e.recent-scans.spec.toBeGreaterThan, frontend.e2e.recent-scans.spec.first, frontend.e2e.recent-scans.spec.toBeVisible

### frontend.e2e.scan-workflow.spec.currentUrl
- **Calls**: frontend.e2e.scan-workflow.spec.includes, frontend.e2e.scan-workflow.spec.expect, frontend.e2e.scan-workflow.spec.getByText, frontend.e2e.scan-workflow.spec.toBeVisible, frontend.e2e.scan-workflow.spec.locator, frontend.e2e.scan-workflow.spec.first, frontend.e2e.scan-workflow.spec.getByRole

### e2e.specs.recent-scans.spec.recentSection
- **Calls**: e2e.specs.recent-scans.spec.locator, e2e.specs.recent-scans.spec.filter, e2e.specs.recent-scans.spec.count, e2e.specs.recent-scans.spec.expect, e2e.specs.recent-scans.spec.toBeGreaterThan, e2e.specs.recent-scans.spec.first, e2e.specs.recent-scans.spec.toBeVisible

### e2e.specs.recent-scans.spec.isVisible
- **Calls**: e2e.specs.recent-scans.spec.locator, e2e.specs.recent-scans.spec.filter, e2e.specs.recent-scans.spec.count, e2e.specs.recent-scans.spec.expect, e2e.specs.recent-scans.spec.toBeGreaterThan, e2e.specs.recent-scans.spec.first, e2e.specs.recent-scans.spec.toBeVisible

## Process Flows

Key execution flows identified:

### Flow 1: mcp_invoke_tool
```
mcp_invoke_tool [backend.routers.mcp]
```

### Flow 2: useAppState
```
useAppState [frontend.src.hooks.useAppState]
```

### Flow 3: mcp_get_resource
```
mcp_get_resource [backend.routers.mcp]
  └─ →> get_recent_scans
```

### Flow 4: scan_sample_projects
```
scan_sample_projects [backend.scripts.scan_samples]
  └─ →> get_sample_projects
```

### Flow 5: get_standard_metrics
```
get_standard_metrics [backend.routers.metrics]
  └─ →> get_recent_scans
  └─ →> get_total_scan_count
```

### Flow 6: RecentScansTab
```
RecentScansTab [frontend.src.components.tabs.RecentScansTab]
```

### Flow 7: ResultPhase
```
ResultPhase [frontend.src.components.phases.ResultPhase]
```

### Flow 8: LandingPhase
```
LandingPhase [frontend.src.components.phases.LandingPhase]
```

### Flow 9: analyze_repo
```
analyze_repo [backend.routers.audit]
  └─> _schedule_background_task
```

### Flow 10: get_metrics_summary
```
get_metrics_summary [backend.routers.metrics]
  └─ →> get_recent_scans
```

## Key Classes

### backend.routers.mcp.MCPResource
> MCP Resource definition.
- **Methods**: 0
- **Inherits**: BaseModel

### backend.routers.mcp.MCPTool
> MCP Tool definition.
- **Methods**: 0
- **Inherits**: BaseModel

### backend.routers.mcp.MCPResourceResponse
> MCP resource content response.
- **Methods**: 0
- **Inherits**: BaseModel

### backend.routers.mcp.MCPToolRequest
> MCP tool invocation request.
- **Methods**: 0
- **Inherits**: BaseModel

## Data Transformation Functions

Key functions that process and transform data:

### frontend.src.components.phases.LandingPhase.formatDate
- **Output to**: frontend.src.components.phases.LandingPhase.Date, frontend.src.components.phases.LandingPhase.toLocaleDateString

### frontend.src.components.tabs.RecentScansTab.formatDate
- **Output to**: frontend.src.components.tabs.RecentScansTab.Date, frontend.src.components.tabs.RecentScansTab.toLocaleDateString

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `backend.routers.mcp.mcp_invoke_tool` - 41 calls
- `frontend.src.hooks.useAppState.useAppState` - 40 calls
- `backend.routers.mcp.mcp_get_resource` - 36 calls
- `backend.scripts.scan_samples.scan_sample_projects` - 30 calls
- `backend.routers.metrics.get_standard_metrics` - 28 calls
- `frontend.src.components.tabs.RecentScansTab.RecentScansTab` - 23 calls
- `frontend.src.components.phases.ResultPhase.ResultPhase` - 22 calls
- `frontend.src.components.phases.LandingPhase.LandingPhase` - 19 calls
- `backend.routers.audit.analyze_repo` - 19 calls
- `backend.routers.metrics.get_metrics_summary` - 17 calls
- `frontend.src.components.phases.ResultPhase.handleDownloadToon` - 16 calls
- `backend.routers.webhook.github_webhook` - 15 calls
- `frontend.src.components.phases.ResultPhase.handleDownloadPrompt` - 14 calls
- `frontend.src.components.phases.ResultPhase.handleDownloadMarkdown` - 14 calls
- `backend.routers.metrics.get_repository_metrics` - 12 calls
- `backend.services.analyzer.count_code_stats` - 11 calls
- `backend.services.github_client.get_installation_token` - 10 calls
- `backend.routers.auth.list_repos` - 10 calls
- `backend.services.scoring.calculate_health_score` - 9 calls
- `backend.services.scoring.generate_recommendations` - 9 calls
- `frontend.src.hooks.useAppState.startSandbox` - 9 calls
- `backend.routers.audit.run_audit` - 9 calls
- `frontend.src.components.phases.ResultPhase.handleDownloadMetrics` - 9 calls
- `frontend.src.components.GradeCircle.GradeCircle` - 8 calls
- `backend.database.save_scan` - 8 calls
- `backend.database.get_recent_scans` - 8 calls
- `backend.routers.auth.github_oauth_callback` - 7 calls
- `backend.routers.metrics.download_project_prompt_markdown` - 7 calls
- `frontend.src.hooks.useAppState.reset` - 7 calls
- `frontend.src.components.tabs.BadgeTab.BadgeTab` - 7 calls
- `frontend.e2e.recent-scans.spec.recentSection` - 7 calls
- `frontend.e2e.recent-scans.spec.isVisible` - 7 calls
- `frontend.e2e.scan-workflow.spec.currentUrl` - 7 calls
- `e2e.specs.recent-scans.spec.recentSection` - 7 calls
- `e2e.specs.recent-scans.spec.isVisible` - 7 calls
- `e2e.specs.scan-workflow.spec.currentUrl` - 7 calls
- `backend.routers.badge.health_badge` - 6 calls
- `frontend.src.hooks.useAppState.startAudit` - 6 calls
- `frontend.src.components.tabs.RepoTab.RepoTab` - 6 calls
- `backend.services.analyzer.run_tool` - 5 calls

## System Interactions

How components interact:

```mermaid
graph TD
    mcp_invoke_tool --> post
    mcp_invoke_tool --> HTTPException
    mcp_invoke_tool --> get
    useAppState --> useState
    useAppState --> useEffect
    useAppState --> slice
    useAppState --> URLSearchParams
    useAppState --> get
    mcp_get_resource --> get
    mcp_get_resource --> HTTPException
    mcp_get_resource --> get_recent_scans
    mcp_get_resource --> MCPResourceResponse
    mcp_get_resource --> startswith
    scan_sample_projects --> get_sample_projects
    scan_sample_projects --> print
    scan_sample_projects --> enumerate
    get_standard_metrics --> get
    get_standard_metrics --> get_recent_scans
    get_standard_metrics --> get_total_scan_count
    get_standard_metrics --> append
    get_standard_metrics --> HTTPException
    RecentScansTab --> useState
    RecentScansTab --> useEffect
    RecentScansTab --> fetchRecentScans
    RecentScansTab --> fetch
    RecentScansTab --> json
    ResultPhase --> getShareUrls
    ResultPhase --> open
    ResultPhase --> Blob
    ResultPhase --> stringify
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.