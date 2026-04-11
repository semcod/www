# Gitea Local Development Cycle

Zastępuje mock-github prawdziwą instancją Gitea w Docker do pełnego testowania cyklu developerskiego.

## Dlaczego Gitea zamiast mock-github?

| Aspekt | Mock GitHub | Gitea |
|--------|------------|-------|
| OAuth | Symulowany (fake tokens) | Prawdziwy OAuth2 flow |
| Repos | Hardcoded JSON | Prawdziwe repozytoria z kodem |
| PR | Brak | Prawdziwe pull requesty z diffem |
| Webhooks | Brak | Prawdziwe dostarczanie webhooków |
| Git operations | Brak | Pełny git push/pull/clone |
| PR Comment Bot | Nie testowany | Pełny cykl: webhook → analiza → komentarz |
| Adapter coverage | Tylko mock | Testuje prawdziwy `GiteaAdapter` |

## Szybki start

```bash
# Uruchom cały cykl
make gitea-cycle
```

Lub krok po kroku:

```bash
make gitea-up       # Start stack z Gitea
make gitea-setup    # Provision: user, repos, OAuth, webhooks
make gitea-test     # Test: branch → commit → PR → webhook → comment
```

## Co testuje `test-full-cycle.sh`

```
Test 1: Service connectivity     — Gitea API + Backend health
Test 2: Repository access        — List repos, default branch
Test 3: Branch → Commit → PR     — Tworzy branch, pushuje refactored code, otwiera PR
Test 4: Webhook delivery         — Sprawdza czy gitea dostarczył webhook do backendu
Test 5: PR comment bot           — Sprawdza czy bot dodał komentarz z analizą
Test 6: Badge endpoint           — /badge/{repo}.svg zwraca SVG
Test 7: Audit via API            — POST /api/analyze → poll → grade
Test 8: PR diff retrieval        — Weryfikuje diff przez Gitea API
Test 9: Cleanup                  — Zamyka PR, usuwa branch
```

## Sample repos

Skrypt `setup-gitea.sh` tworzy 3 repozytoria z prawdziwym kodem:

### `sample-python`
Python z intentional problems: duplikat metody `validate()`, wysoki CC w `complex_function()`.
Semcod powinien wykryć: duplikację, CC>10, brak type hints.

### `sample-js`
JavaScript z duplikatem `handleRequest`/`processRequest`. Testuje JS parser.

### `infra-scripts`
Shell scripts — testuje multi-language support.

## Architektura

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Frontend    │────▶│  Backend     │────▶│  Gitea       │
│  :3000       │     │  :8003       │     │  :3100       │
│              │     │              │◀────│              │
│  OAuth login │     │  GiteaAdapter│     │  Webhooks    │
│  Audit UI    │     │  PR Bot      │     │  OAuth2      │
│  Badge       │     │  Analysis    │     │  Git repos   │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                     ┌─────┴─────┐
                     │  Worker   │
                     │  Celery   │
                     │  Pipeline │
                     └───────────┘
```

## Porty

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8003 | http://localhost:8003 |
| Gitea | 3100 | http://localhost:3100 |
| Gitea SSH | 2222 | ssh://localhost:2222 |
| PostgreSQL | 5432 | |
| Redis | 6379 | |

## Zaimplementowane zmiany w backendzie

Backend ma `GiteaAdapter`, `parse_gitea_event`, i następujące endpointy:

1. **`config.py`** — odczyt `GITEA_*` env vars:
```python
GITEA_URL = os.getenv("GITEA_URL", "")
GITEA_API_BASE_URL = os.getenv("GITEA_API_BASE_URL", GITEA_URL or GITEA_BASE_URL)
GITEA_CLIENT_ID = os.getenv("GITEA_CLIENT_ID", "")
GITEA_CLIENT_SECRET = os.getenv("GITEA_CLIENT_SECRET", "")
GITEA_OAUTH_AUTHORIZE_URL = os.getenv("GITEA_OAUTH_AUTHORIZE_URL", "")
GITEA_OAUTH_TOKEN_URL = os.getenv("GITEA_OAUTH_TOKEN_URL", "")
GITEA_WEBHOOK_SECRET = os.getenv("GITEA_WEBHOOK_SECRET", "")
DEFAULT_GIT_PROVIDER = os.getenv("DEFAULT_GIT_PROVIDER", "github")
```

2. **`routers/auth.py`** — endpointy `/auth/gitea` + `/auth/callback/gitea`:
   - `/auth/gitea` — redirect do Gitea OAuth2 authorize
   - `/auth/callback/gitea` — exchange code → token → profile → JWT session

3. **`routers/webhook_v2.py`** — endpoint `/v2/webhook/gitea` parsuje `X-Gitea-Event` header i `X-Gitea-Signature`.
