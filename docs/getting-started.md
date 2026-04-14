### 1. Clone and Install

```bash
git clone https://github.com/semcod/www.git
cd www
```

### 2. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configuration

Create `.env` file in `backend/` directory:

```env
# Required
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# Optional
DATABASE_URL=sqlite:///./scans.db
APP_URL=http://localhost:3000
JWT_SECRET=
```

### 5. Run Development Servers

**Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn server:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Open in Browser

Navigate to `http://localhost:3000`

---

### Public Repository (Sandbox Mode)

1. On the landing page, enter a public repo URL:
   ```
   https://github.com/vercel/next.js
   ```

2. Click "Analyze" - no GitHub login required!

3. Wait for analysis to complete

4. View results including:
   - Health Score (0-100)
   - Letter Grade (A+ to F)
   - Code metrics (files, lines, languages)
   - Recommendations

### Private Repository

1. Click "Connect GitHub" and authorize
2. Select repository from your list
3. Start audit with one click

---

### cURL Examples

**Health Check:**
```bash
curl http://localhost:9000/api/health
```

**Start Audit:**
```bash
curl -X POST http://localhost:9000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"repo": "facebook/react", "token": "ghp_your_token"}'
```

**Get Audit Status:**
```bash
curl http://localhost:9000/api/audit/{audit_id}
```

**Get Metrics:**
```bash
curl http://localhost:9000/api/metrics/standard?limit=5
```

### Python Client

```python
import httpx

client = httpx.Client(base_url="http://localhost:9000")

# Start audit
response = client.post("/api/audit", json={
    "repo": "owner/repo",
    "token": "ghp_xxx"
})
audit_id = response.json()["audit_id"]

# Poll for results
import time
while True:
    result = client.get(f"/api/audit/{audit_id}").json()
    if result["status"] in ["complete", "error"]:
        break
    time.sleep(2)

print(f"Health Score: {result['health_score']}")
print(f"Grade: {result['grade']}")
```

---

### Health Score Calculation

The health score (0-100) is calculated from:

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Complexity | -3 per point above 5 | `max(0, cc_avg - 5) × 3` |
| Duplication | -1 per 5 groups | `duplication_groups / 5` |
| Quality | -3 per error, -1 per warning | `errors × 3 + warnings` |
| Floor | Minimum 50 | `max(calculated, 50)` |

**Score Formula:**
```
score = 100
        - max(0, complexity - 5) × 3
        - min(30, duplication_groups / 5)
        - min(30, errors × 3 + warnings)
        
score = max(score, 50)  # Floor for small repos
score = max(score, 0)     # Never negative
```

### Grade Scale

| Score | Grade |
|-------|-------|
| 90-100 | A+ |
| 80-89 | A |
| 70-79 | B+ |
| 60-69 | B |
| 50-59 | C |
| 40-49 | D |
| 0-39 | F |

---

## MCP Integration

AI assistants can interact with Semcod via MCP:

### Claude Desktop Config

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "semcod": {
      "url": "https://semcod.com/mcp"
    }
  }
}
```

### Available Resources

Ask Claude:
- "Show me recent code scans"
- "Get scan details for [audit_id]"
- "What's the metrics summary?"

### Available Tools

Ask Claude:
- "Start an audit for owner/repo"
- "Check status of audit [id]"
- "Analyze https://github.com/owner/repo"

---

## Badge Integration

Add a health badge to your README:

```markdown
![Code Health](https://semcod.com/badge/owner-repo.svg)
```

### Badge Styles

- Default: `?style=flat`
- Flat Square: `?style=flat-square`
- Plastic: `?style=plastic`
- For The Badge: `?style=for-the-badge`

---

### "Failed to clone repository"
- For private repos: Check your GitHub token has `repo` scope
- For public repos: Ensure repo exists and is public

### "ModuleNotFoundError: No module named 'fastapi'"
- Make sure you're in the virtual environment
- Run: `pip install -r requirements.txt`

### CORS errors in browser
- Check `APP_URL` env var matches your frontend URL
- Default is `http://localhost:3000`

### Port already in use
- Backend: Change with `--port 8001`
- Frontend: Change in `vite.config.js`

---

## Next Steps

- [API Reference](./api.md) - Complete endpoint documentation
- [Architecture](./architecture.md) - System design details
- [MCP Integration](./MCP.md) - AI assistant setup
- [Contributing](../CONTRIBUTING.md) - How to contribute
