# MCP (Model Context Protocol) Integration

Semcod implements the [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) for AI assistant integration.

## Overview

MCP allows AI assistants (Claude, Cascade, etc.) to:
- Discover available resources and tools
- Query scan results programmatically
- Start new audits
- Retrieve metrics and summaries

## Base URL

All MCP endpoints are prefixed with `/mcp`:

```
https://semcod.com/mcp
```

## Endpoints

### Discovery

| Endpoint | Description |
|----------|-------------|
| `GET /mcp/info` | Server information and capabilities |
| `GET /mcp/resources` | List available resources |
| `GET /mcp/tools` | List available tools |

### Resources

| Resource URI | Description |
|--------------|-------------|
| `scans://list` | List recent scans with summaries |
| `scan://{audit_id}` | Full details of a specific scan |
| `metrics://summary` | Aggregated metrics across all scans |
| `badge://{repo_slug}` | Badge status for a repository |

Fetch resource content:
```
GET /mcp/resources/content?uri=scans://list
```

### Tools

| Tool | Description |
|------|-------------|
| `start_audit` | Start a new audit for a repository |
| `get_scan_status` | Check status of a running scan |
| `get_repository_metrics` | Get metrics for specific repository |
| `analyze_public_repo` | Analyze public repo in sandbox mode |

Invoke a tool:
```
POST /mcp/invoke
{
  "name": "start_audit",
  "arguments": {
    "repo": "owner/name",
    "sandbox": true
  }
}
```

## Examples

### Start an Audit

```bash
curl -X POST https://semcod.com/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "start_audit",
    "arguments": {
      "repo": "facebook/react",
      "sandbox": true
    }
  }'
```

Response:
```json
{
  "audit_id": "abc123def456",
  "status": "running",
  "message": "Audit started for facebook/react. Use get_scan_status to check progress."
}
```

### Check Scan Status

```bash
curl -X POST https://semcod.com/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_scan_status",
    "arguments": {
      "audit_id": "abc123def456"
    }
  }'
```

### Get Metrics Summary

```bash
curl "https://semcod.com/mcp/resources/content?uri=metrics://summary"
```

Response:
```json
{
  "uri": "metrics://summary",
  "mime_type": "application/json",
  "content": {
    "meta": {
      "generated_at": "2026-04-10T09:00:00",
      "total_scans": 150
    },
    "summary": {
      "avg_health_score": 78.5,
      "grade_distribution": {
        "A+": 25, "A": 35, "B+": 40, "B": 30, "C": 15, "D": 4, "F": 1
      },
      "total_files": 15000,
      "total_lines": 2500000,
      "platform_distribution": {
        "github": 145, "gitlab": 4, "bitbucket": 1
      }
    }
  }
}
```

## Protocol Version

Implements MCP Protocol Version: `2024-11-05`
