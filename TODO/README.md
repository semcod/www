# GitHub OAuth Login Simulation

Symulacja GitHub OAuth do testowania logowania użytkownika `tom-sapletta-com` bez prawdziwego GitHub.

## Architektura

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   Frontend     │────▶│   Backend      │────▶│  Mock GitHub    │
│  :3000         │     │  :8003         │     │  :4010          │
│                │     │                │     │                 │
│  Click Login   │     │  /auth/github  │     │  /login/oauth/* │
│  ← session ──  │◀────│  /auth/callback│◀────│  /user, /repos  │
└────────────────┘     └────────────────┘     └─────────────────┘
```

## Szybki start

```bash
# Uruchom cały stack z symulacją
docker compose -f docker-compose.yml -f docker-compose.sim.yml up -d

# Sprawdź czy mock działa
curl http://localhost:4010/health

# Otwórz frontend
open http://localhost:3000
```

## Testowanie

```bash
# Testy API (bez przeglądarki)
npx playwright test tests/github-login-sim.spec.js --grep "mock server"

# Pełny test z przeglądarką
npx playwright test tests/github-login-sim.spec.js --headed
```

## Symulowany użytkownik

| Pole         | Wartość                    |
|-------------|----------------------------|
| login       | `tom-sapletta-com`         |
| name        | Tom Sapletta               |
| id          | 5669315                    |
| email       | tom@sapletta.com           |
| repos       | semcod, letwhisper, dialogware |

## Jak to działa

1. Backend przekierowuje na `GITHUB_OAUTH_AUTHORIZE_URL` → mock serwer
2. Mock wyświetla stronę z przyciskiem "tom-sapletta-com"
3. Po kliknięciu generuje `code` i redirectuje do `/auth/callback`
4. Backend wymienia `code` na `access_token` przez mock
5. Backend pobiera profil z mock `/user` → tworzy sesję

## Zmienne środowiskowe (backend override)

```env
GITHUB_OAUTH_AUTHORIZE_URL=http://mock-github:4010/login/oauth/authorize
GITHUB_OAUTH_TOKEN_URL=http://mock-github:4010/login/oauth/access_token
GITHUB_API_BASE_URL=http://mock-github:4010
GITHUB_CLIENT_ID=Iv1.mock_test_client
GITHUB_CLIENT_SECRET=mock_secret_for_testing
```
