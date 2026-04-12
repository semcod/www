# Semcod Auto-PR Examples

Przykłady użycia Auto-PR przez **`gh` CLI** (ma ważny token GitHub) + **Semcod REST API** (reDSL).

## 🔑 Kluczowe: `gh` ma token!

`gh` (GitHub CLI) jest już zalogowany z ważnym tokenem — używamy go zamiast ręcznego OAuth:

```bash
# Sprawdź
gh auth status
# ✓ Logged in to github.com account tom-sapletta-com
```

## 📁 Struktura

```
examples/
├── rest-api/auto-pr-example.sh    # 8 przykładów (gh + curl)
├── shell/auto-pr-cli.sh           # Interaktywne menu (gh + Semcod)
├── python-sdk/auto_pr_client.py   # Python SDK (GhClient + SemcodClient)
├── cycle-test/                    # Pełny cykl ticket→reDSL→PR — walidacja krok po kroku
│   ├── validate-steps.sh          # Sprawdza każdy endpoint (bez PR)
│   ├── full-cycle.sh              # Pełny cykl z PR i merge
│   └── README.md
└── README.md
```

## 🚀 Szybki start

### Shell CLI (najprostsze)
```bash
cd examples/shell
./auto-pr-cli.sh
# Menu z 8 opcjami — gh obsługuje GitHub, Semcod obsługuje reDSL
```

### REST API (gh + curl)
```bash
cd examples/rest-api

# Użyj tokenu z gh
export GH_TOKEN=$(gh auth token)

# Prosty Auto-PR przez gh
gh pr create --repo semcod/vallm \
  --head semcod-fix-test --base main \
  --title "semcod: auto-fix" \
  --body "Automated PR"

# ReDSL health przez Semcod API
curl -s http://localhost:8003/api/redsl/status
```

### Python SDK
```bash
cd examples/python-sdk
python3 auto_pr_client.py
# Automatycznie używa gh token — brak ręcznego OAuth
```

### Cycle Test (walidacja krok po kroku)
```bash
cd examples/cycle-test
chmod +x validate-steps.sh full-cycle.sh

# Walidacja endpointów (bezpieczne, bez PR)
./validate-steps.sh

# Pełny cykl z PR i merge
./full-cycle.sh
```

## 📊 Przykłady

| # | Przykład | gh CLI | Semcod API | Opis |
|---|----------|--------|------------|------|
| 1 | Quick Auto-PR | ✅ | — | Branch + commit + PR przez gh |
| 2 | ReDSL Health | — | ✅ | Health score z reDSL |
| 3 | Ticket + Auto-PR | ✅ | ✅ | Ticket → reDSL → PR |
| 4 | Batch Health | ✅ | ✅ | Health check wielu repo |
| 5 | Issue + Ticket | ✅ | ✅ | GitHub Issue → Semcod ticket |
| 6 | Monitor PR | ✅ | — | Śledzenie statusu PR |
| 7 | ReDSL Preview | — | ✅ | Dry-run refaktoryzacji |
| 8 | Full Flow | ✅ | ✅ | Kompletny proces |

## 🔄 Flow: gh + Semcod

```
1. gh auth status           → verify GitHub access ✅
2. gh repo list             → choose repo
3. curl /api/redsl/health   → get health score (Semcod)
4. curl /api/redsl/refactor → preview changes (dry-run)
5. gh pr create / curl /api/autopr/redsl → create PR
6. gh pr merge --auto       → auto-merge when CI passes
```

## 🔧 Komunikacja

| Metoda | Auth | Działa? | Użycie |
|--------|------|---------|--------|
| **`gh` CLI** | ✅ Token w keyring | ✅ Tak | GitHub operations (PR, branch, commit) |
| **Semcod API + gh token** | ✅ Bearer gh token | ⚠️ Zależy od backend | Tickets, reDSL, health |
| **Semcod API + OAuth** | 🔑 Session token | ⚠️ Wymaga logowania | Full Semcod features |
| **ReDSL direct** | — | ⚠️ Wymaga serwisu | Health, refactor, decide |

## 📝 Kompletny Flow (gh + Semcod)

### Bash
```bash
#!/bin/bash
REPO="semcod/vallm"

# 1. Verify gh
gh auth status || exit 1

# 2. Create branch + commit
BRANCH="semcod-fix-$(date +%s)"
SHA=$(gh api repos/${REPO}/git/refs/heads/main --jq '.object.sha')
gh api repos/${REPO}/git/refs -f ref="refs/heads/${BRANCH}" -f sha="${SHA}"
gh api repos/${REPO}/contents/fix.py -X PUT \
  -f message="semcod: auto-fix" \
  -f content="$(echo -n 'def fix(): pass' | base64)" \
  -f branch="${BRANCH}"

# 3. Create PR
gh pr create --repo ${REPO} --head ${BRANCH} --base main \
  --title "semcod: auto-fix" --body "Automated"

# 4. Check Semcod health
curl -s http://localhost:8003/api/redsl/status
```

### Python
```python
from auto_pr_client import GhClient, SemcodClient, SemcodConfig, TicketType

# gh handles GitHub — no manual auth
repo = GhClient.list_repos(limit=1)[0]["nameWithOwner"]

# Create PR directly with gh
GhClient.create_branch(repo, "semcod-fix-test", sha)
GhClient.commit_file(repo, "fix.py", "def fix(): pass", "semcod-fix-test")
pr = GhClient.create_pr(repo, "semcod-fix-test", "semcod: auto-fix")

# Use Semcod for reDSL analysis
client = SemcodClient(SemcodConfig())
health = client.redsl_health(f"/mnt/project/{repo.replace('/', '-')}")
```

## 🔗 Dokumentacja

- [README.md](../README.md) — Główna dokumentacja
- [CHANGELOG.md](../CHANGELOG.md) — Historia zmian
- [gh CLI docs](https://cli.github.com/manual/) — GitHub CLI reference

---

**Wersja:** 2.0.0 (2026-04-12) — Uses `gh` for GitHub auth
