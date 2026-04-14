#### `GET /auth/github`
Redirect to GitHub OAuth authorization.

**Query Parameters:**
- `redirect_uri` (optional) - Custom redirect URI after authorization

**Response:** Redirects to GitHub OAuth page

---

#### `GET /auth/callback`
GitHub OAuth callback handler.

**Query Parameters:**
- `code` - Authorization code from GitHub

**Response:**
```json
{
  "token": "ghp_xxx",
  "user": {
    "login": "username",
    "id": 12345
  }
}
```

---

#### `POST /api/audit`
Start a new code health audit for a repository.

**Request Body:**
```json
{
  "repo": "owner/name",
  "token": "ghp_xxx"
}
```

**Response:**
```json
{
  "audit_id": "abc123",
  "status": "running"
}
```

---

#### `GET /api/audit/{audit_id}`
Get audit status and results.

**Path Parameters:**
- `audit_id` - Audit ID returned from POST /api/audit

**Response (Running):**
```json
{
  "status": "running",
  "repo": "owner/name",
  "started": "2024-01-01T12:00:00Z"
}
```

**Response (Complete):**
```json
{
  "status": "complete",
  "repo": "owner/name",
  "completed": "2024-01-01T12:05:00Z",
  "health_score": 85,
  "grade": "A",
  "stats": {
    "total_files": 150,
    "total_lines": 25000,
    "languages": {"Python": 18000, "JavaScript": 7000}
  },
  "metrics": {
    "complexity": {"cc_avg": 3.5, "functions": 500},
    "duplication": {"duplication_groups": 5, "recoverable_lines": 200},
    "quality": {"passed": 95, "warnings": 3, "errors": 2}
  },
  "recommendations": [
    {
      "category": "complexity",
      "message": "Consider refactoring complex functions",
      "priority": "medium"
    }
  ],
  "badge_url": "https://semcod.com/badge/owner-name.svg"
}
```

---

#### `POST /api/analyze`
Analyze any public repository by URL (sandbox mode).

**Request Body:**
```json
{
  "repo_url": "https://github.com/owner/repo",
  "sandbox": true
}
```

**Response:**
```json
{
  "audit_id": "abc123",
  "status": "running",
  "sandbox": true
}
```

---

#### `GET /api/metrics/standard`
Get standardized metrics for recent scans.

**Query Parameters:**
- `limit` (optional, default: 10) - Number of scans to return

**Response:**
```json
{
  "meta": {
    "generated_at": "2024-01-01T12:00:00Z",
    "total_scans": 123,
    "returned_scans": 10
  },
  "scans": [
    {
      "repository": "owner/repo",
      "platform": "github",
      "health_score": 85,
      "grade": "A",
      "metrics": {
        "files": 150,
        "lines_of_code": 25000,
        "languages": {"Python": 18000, "JavaScript": 7000},
        "complexity": {"avg_cyclomatic": 3.5, "functions": 500},
        "duplication": {"groups": 5, "recoverable_lines": 200},
        "quality": {"passed": 95, "warnings": 3, "errors": 2}
      },
      "scanned_at": "2024-01-01T10:00:00Z",
      "badge_url": "https://semcod.com/badge/owner-repo.svg"
    }
  ]
}
```

---

#### `GET /api/metrics/summary`
Get summary statistics of all scans.

**Response:**
```json
{
  "meta": {
    "generated_at": "2024-01-01T12:00:00Z",
    "total_scans": 100
  },
  "summary": {
    "avg_health_score": 75.5,
    "grade_distribution": {"A+": 10, "A": 20, "B+": 30, "B": 25, "C": 10, "D": 3, "F": 2},
    "total_files": 15000,
    "total_lines": 2500000,
    "platform_distribution": {"github": 90, "gitlab": 8, "bitbucket": 2}
  }
}
```

---

#### `GET /api/metrics/repository/{repo_path}`
Get metrics for a specific repository.

**Path Parameters:**
- `repo_path` - Format: "owner/repo" or "github:owner/repo"

**Response:**
```json
{
  "meta": {
    "generated_at": "2024-01-01T12:00:00Z",
    "repository": "owner/repo",
    "platform": "github",
    "scan_count": 5
  },
  "scan": {
    "health_score": 85,
    "grade": "A",
    "metrics": {
      "files": 150,
      "lines_of_code": 25000,
      "languages": {"Python": 18000}
    },
    "scanned_at": "2024-01-01T10:00:00Z",
    "badge_url": "https://semcod.com/badge/owner-repo.svg"
  }
}
```

---

#### `GET /badge/{repo_slug}.svg`
Generate SVG badge with code health score.

**Path Parameters:**
- `repo_slug` - Repository slug (owner-name format)

**Query Parameters:**
- `style` (optional) - Badge style: "flat", "flat-square", "plastic", "for-the-badge"

**Response:** SVG image

---

#### `GET /api/scans/recent`
Get list of recent scans.

**Query Parameters:**
- `limit` (optional, default: 100) - Number of scans to return

**Response:**
```json
{
  "scans": [
    {
      "repo": "owner/repo",
      "health_score": 85,
      "grade": "A",
      "stats": {
        "total_files": 150,
        "total_lines": 25000
      },
      "completed": "2024-01-01T10:00:00Z",
      "badge_url": "https://semcod.com/badge/owner-repo.svg"
    }
  ],
  "total": 1
}
```

---

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "audits_cached": 42,
  "badges_cached": 15
}
```

---

#### `POST /api/benchmark/cases`
Create a new benchmark case.

**Request Body:**
```json
{
  "case_id": "BM-001",
  "repo": "owner/repo",
  "source_type": "pr",
  "change_type": "bugfix",
  "baseline_detected": true,
  "baseline_tools": ["ci", "ruff", "manual-pr-review"],
  "pr_reference": "https://github.com/owner/repo/pull/123",
  "benchmark_mode": true
}
```

**Response:**
```json
{
  "case_id": "BM-001",
  "repo": "owner/repo",
  "source_type": "pr",
  "change_type": "bugfix",
  "baseline_detected": true,
  "created_at": "2026-04-11T10:00:00Z"
}
```

---

#### `GET /api/benchmark/cases`
List all benchmark cases.

**Response:**
```json
{
  "cases": [
    {
      "case_id": "BM-001",
      "repo": "owner/repo",
      "source_type": "pr",
      "change_type": "bugfix",
      "baseline_detected": true,
      "reviewer_verdict": "go",
      "pr_candidate": true,
      "deployment_candidate": true,
      "deployment_model_selected": "hybrid",
      "created_at": "2026-04-11T10:00:00Z"
    }
  ]
}
```

---

#### `GET /api/benchmark/cases/{case_id}`
Get a specific benchmark case.

**Path Parameters:**
- `case_id` - Benchmark case ID

**Response:**
```json
{
  "case_id": "BM-001",
  "repo": "owner/repo",
  "source_type": "pr",
  "change_type": "bugfix",
  "baseline_detected": true,
  "reviewer_verdict": "go",
  "pr_candidate": true,
  "deployment_candidate": true,
  "deployment_model_selected": "hybrid",
  "time_to_first_result_seconds": 45,
  "time_to_first_useful_recommendation_seconds": 120,
  "created_at": "2026-04-11T10:00:00Z"
}
```

---

#### `PATCH /api/benchmark/cases/{case_id}`
Update a benchmark case.

**Path Parameters:**
- `case_id` - Benchmark case ID

**Request Body:**
```json
{
  "reviewer_verdict": "go",
  "pr_candidate": true,
  "deployment_candidate": true,
  "deployment_model_selected": "hybrid",
  "next_action": "prepare_pr"
}
```

---

#### `POST /api/benchmark/cases/{case_id}/decision`
Submit deployment decision for a case.

**Path Parameters:**
- `case_id` - Benchmark case ID

**Request Body:**
```json
{
  "pr_candidate": true,
  "deployment_candidate": true,
  "deployment_model_selected": "hybrid",
  "reviewer_verdict": "go",
  "next_action": "prepare_pr"
}
```

**Response:** Updated case object

---

#### `POST /api/benchmark/cases/{case_id}/recommendations/{recommendation_id}/feedback`
Submit feedback for a specific recommendation.

**Path Parameters:**
- `case_id` - Benchmark case ID
- `recommendation_id` - Recommendation ID (stable sha1[:12])

**Request Body:**
```json
{
  "accepted": true,
  "novelty_score": 3,
  "usefulness_score": 3,
  "accuracy_score": 2,
  "actionability_score": 3,
  "business_value_score": 2,
  "notes": "Dobra rekomendacja, gotowa do przejścia w PR"
}
```

**Response:**
```json
{
  "id": 1,
  "case_id": "BM-001",
  "recommendation_id": "abc123def456",
  "accepted": true,
  "novelty_score": 3,
  "usefulness_score": 3,
  "created_at": "2026-04-11T10:05:00Z"
}
```

---

#### `GET /api/benchmark/cases/{case_id}/recommendations/feedback`
Get all feedback for a case.

**Path Parameters:**
- `case_id` - Benchmark case ID

**Response:**
```json
{
  "feedback": [
    {
      "id": 1,
      "recommendation_id": "abc123def456",
      "accepted": true,
      "novelty_score": 3,
      "usefulness_score": 3,
      "notes": "Dobra rekomendacja"
    }
  ]
}
```

---

#### `POST /api/benchmark/cases/{case_id}/events`
Track a product event.

**Path Parameters:**
- `case_id` - Benchmark case ID

**Request Body:**
```json
{
  "event_name": "recommendation_seen",
  "event_value": "first_view",
  "audit_id": "audit-123",
  "metadata": {"recommendation_id": "abc123"}
}
```

**Response:**
```json
{
  "id": 1,
  "case_id": "BM-001",
  "event_name": "recommendation_seen",
  "created_at": "2026-04-11T10:05:00Z"
}
```

---

#### `GET /api/benchmark/cases/{case_id}/events`
Get all events for a case.

**Path Parameters:**
- `case_id` - Benchmark case ID

---

#### `GET /api/benchmark/summary`
Get benchmark KPI summary.

**Response:**
```json
{
  "total_cases": 50,
  "novel_actionable_finding_rate": 0.75,
  "recommendation_acceptance_rate": 0.68,
  "false_positive_rate": 0.12,
  "pr_conversion_rate": 0.45,
  "deployment_decision_rate": 0.38,
  "by_source_type": {"repo": 30, "pr": 15, "ticket": 5},
  "by_change_type": {"bugfix": 20, "feature": 20, "refactor": 10},
  "by_deployment_model": {"client_scm": 15, "semcod_managed": 10, "hybrid": 25}
}
```

---

#### `GET /api/benchmark/export.json`
Export all benchmark data as JSON.

**Response:**
```json
{
  "cases": [...],
  "summary": {...}
}
```

---

#### `GET /api/benchmark/export.csv`
Export benchmark cases as CSV.

**Response:** CSV file with columns:
- `case_id`, `repo`, `source_type`, `change_type`, `baseline_detected`
- `reviewer_verdict`, `recommendation_accepted`, `pr_candidate`
- `deployment_candidate`, `deployment_model_selected`
- `time_to_first_result_seconds`, `time_to_first_useful_recommendation_seconds`
- `next_action`, `created_at`

---

## ReDSL API

ReDSL (Refactoring DSL) integration for automated code refactoring.

#### `GET /api/redsl/status`
Check if reDSL engine is available.

**Response:**
```json
{
  "available": true,
  "url": "http://localhost:8000"
}
```

---

#### `POST /api/redsl/analyze`
Run reDSL analysis on a project.

**Request Body:**
```json
{
  "project_path": "/path/to/project",
  "project_toon": "optional YAML content"
}
```

**Response:**
```json
{
  "status": "analyzed",
  "result": {
    "files_analyzed": 150,
    "issues_found": 23,
    "recommendations": [...]
  }
}
```

---

#### `POST /api/redsl/health`
Get unified health score for a project.

**Request Body:**
```json
{
  "project_path": "/path/to/project"
}
```

**Response:**
```json
{
  "health_score": 85,
  "grade": "A",
  "metrics": {
    "complexity": 3.5,
    "duplication": 0.12,
    "quality": 0.95
  }
}
```

---

#### `POST /api/redsl/refactor`
Run reDSL refactoring on a project.

**Request Body:**
```json
{
  "project_path": "/path/to/project",
  "max_actions": 10,
  "dry_run": true
}
```

**Response:**
```json
{
  "status": "preview",
  "result": {
    "actions": [...],
    "files_affected": 5
  }
}
```

---

#### `POST /api/redsl/decide`
Evaluate DSL rules without execution — returns decisions only.

**Request Body:**
```json
{
  "project_path": "/path/to/project"
}
```

**Response:**
```json
{
  "decisions": [
    {
      "file": "src/utils.py",
      "action": "EXTRACT_FUNCTION",
      "confidence": 0.92
    }
  ]
}
```

---

#### `POST /api/redsl/batch-hybrid`
Run hybrid quality refactoring (no LLM needed).

**Query Parameters:**
- `project_path` - Absolute path to project
- `max_changes` - Maximum changes (default: 30)

**Response:**
```json
{
  "status": "completed",
  "result": {
    "changes_made": 12,
    "files_modified": 4
  }
}
```

---

#### `GET /api/redsl/badge/{owner}/{repo}`
Generate SVG badge with health score for README embedding.

**Path Parameters:**
- `owner` - Repository owner
- `repo` - Repository name

**Response:** SVG image

**Example:**
```markdown
![Code Health](https://semcod.com/api/redsl/badge/owner/repo)
```

---

## MCP (Model Context Protocol)

See [MCP Documentation](./MCP.md) for full details on AI assistant integration.

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /mcp/info` | Server information |
| `GET /mcp/resources` | List available resources |
| `GET /mcp/tools` | List available tools |
| `GET /mcp/resources/content?uri={uri}` | Get resource content |
| `POST /mcp/invoke` | Invoke a tool |

### Resources

- `scans://list` - List recent scans
- `scan://{audit_id}` - Get specific scan details
- `metrics://summary` - Aggregated metrics
- `badge://{repo_slug}` - Badge status

### Tools

- `start_audit` - Start new audit
- `get_scan_status` - Check scan status
- `get_repository_metrics` - Get repo metrics
- `analyze_public_repo` - Analyze public repo

---

#### `POST /webhook/github`
Handle GitHub webhook events.

**Headers:**
- `X-GitHub-Event` - Event type (e.g., "push", "pull_request")
- `X-Hub-Signature-256` - Signature for verification

**Request Body:** GitHub webhook payload

**Response:** `{"status": "ok"}` or `{"status": "ignored"}`

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid token)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

API requests are subject to rate limiting:
- Authenticated: 1000 requests/hour
- Anonymous: 100 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```
