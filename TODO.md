# Semcod — TODO

## ✅ Done (2026-04-10)

- **Bug fix:** sandbox/guest scans not appearing in recent scans — `save_scan()` was missing in both pipeline functions
- **Config:** all hardcoded values extracted to `.env` (20 variables: `DB_PATH`, `SCAN_HISTORY_LIMIT`, `REPOS_PER_PAGE`, `GITHUB_OAUTH_SCOPE`, `CORS_ORIGINS`, `LARGE_FILE_THRESHOLD`, etc.)
- **Network:** Docker containers accessible from LAN via `http://nvidia:3000` (frontend) and `http://nvidia:8003` (backend)
- **Docs:** README, CHANGELOG, .env.example updated

## 📋 Next

### Product / Biznes
- Walidacja co nowego wykrywa skan — czy to nowa jakość?
- Propozycja co może zostać poprawione po skanie
- Pytanie do użytkownika: wdrożyć na swoim GitHub/GitLab czy na naszym środowisku?
- Nasze środowisko bezplatne przez 1 miesiąc → oferować od razu generowanie automatyzacji z opcją PR
- Druga opcja: automatyzacja na GitLab/GitHub z opcją deploymentu na naszej infra
- Z partnerami: środowisko uruchomieniowe + generowanie automatyczne na bazie ticketów (zmiany, bugfix, features)
- Marketplace: oferowanie deploymentu artefaktów (SaaS, desktop, mobile) — płatne, z łatwą dystrybucją i rozliczaniem (tokeny, czas, usługa)

### Tech
- [ ] Testy E2E dla sandbox scans w recent scans
- [ ] Quadlet: update `semcod-backend.container` z nowymi env vars (`DB_PATH`, `CORS_ORIGINS`, itp.)
- [ ] Quadlet README: update env vars list
- [ ] CI/CD: GitHub Actions deploy z nowymi env vars



można też dodać paczke python semcod ktora bedzie robiła te metryki przez cli shell, api rest i api mcp
