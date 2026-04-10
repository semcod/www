# API Reference

## Backend API

### Authentication

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

### Audit

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

### Metrics

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

### Badges

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

### Health

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

## Webhooks

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
