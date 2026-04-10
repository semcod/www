---
title: "Semcod — platforma AI do zarządzania jakością kodu i deploymentem"
slug: semcod-platform-overview
date: 2026-04-10
category: Product
tags: [semcod, ai, code-quality, saas, marketplace]
excerpt: "Semcod to nie kolejny linter. To platforma, która skanuje, naprawia i deployuje kod — od pierwszego commita do produkcji."
author: Tom Softreck
---

# Semcod — platforma AI do zarządzania jakością kodu i deploymentem

## Problem, który rozwiązujemy

Każdy zespół programistyczny zna ten scenariusz: CI pipeline sprawdza testy i linting, code review łapie oczywiste błędy, ale nikt systematycznie nie patrzy na architekturę, złożoność i trendy jakości w czasie. Problemy narastają niewidocznie — plik po pliku, commit po commicie — aż god module ma 800 linii i nikt nie chce go dotykać.

Istniejące narzędzia (SonarQube, CodeClimate, CodeRabbit) rozwiązują kawałki tego problemu, ale żadne z nich nie zamyka pętli: wykryj → zrozum → napraw → zdeployuj → rozlicz.

Semcod zamyka tę pętlę.

## Co robi Semcod

Semcod łączy cztery warstwy w jedną platformę:

**Warstwa 1 — Analiza.** Skanuje repozytorium czterema narzędziami jednocześnie: code2llm (złożoność cyklomatyczna, fan-out, hotspoty architektoniczne), redup (duplikacja na poziomie AST), pyqual (bramy jakości: ruff, mypy, bandit) i vallm (walidacja semantyczna). Wynik to nie lista warningów, ale spójny raport z health score 0-100 i oceną literową A+ do F.

**Warstwa 2 — Rekomendacja.** Każdy wykryty problem ma przypisaną propozycję naprawy z priorytetem, szacowanym effort i impact score. Nie mówi „ten plik jest za duży" — mówi „podziel ResultPhase.jsx na 5 komponentów, oto plan splitowania, szacowany czas: 1h, wpływ na CC: -46 punktów".

**Warstwa 3 — Automatyzacja.** Propozycja może zostać automatycznie zamieniona w branch i PR. LLM generuje patch, pipeline walidacyjny sprawdza czy testy przechodzą i czy metryki się poprawiły, i dopiero wtedy tworzy PR do review. Jeśli walidacja nie przechodzi — rollback i alternatywna strategia.

**Warstwa 4 — Deployment i Marketplace.** Gotowy artefakt (SaaS, desktop, mobile, API) może zostać opublikowany na Semcod Marketplace. Klient końcowy kupuje subskrypcję lub płaci za tokeny. Developer dostaje 70-85% przychodu.

## Dwa modele wdrożenia

**Self-managed:** Klient instaluje Semcod GitHub App na swoich repozytoriach. Automatyczne review PR, scheduled scany, alerty degradacji. Klient zachowuje pełną kontrolę. Od $9/mies.

**Managed Infrastructure:** Klient łączy repo — Semcod robi resztę: skanuje, naprawia, testuje, deployuje. Pierwszy miesiąc za darmo. Potem token-based lub compute hours. Idealny dla firm, które chcą skupić się na produkcie, nie na infrastrukturze.

## Dlaczego nie kolejna wtyczka do IDE

Semcod celowo omija model wtyczek i narzędzi dla developerów. Zamiast tego wchodzi na poziom, gdzie AI zarządza całym repozytorium:

- Nie wymaga instalacji w IDE — działa na poziomie repo i CI/CD.
- Nie wymaga konfiguracji per-developer — działa per-organizacja.
- Nie generuje todo listy do ręcznego wykonania — generuje gotowe PR-y.
- Nie kończy się na analizie — prowadzi od ticketu do deploymentu.

To model biznesowy, w którym AI jest platformą, nie narzędziem.

## Obecny stan

Platforma jest w fazie MVP z działającym:

- One-click audit dla publicznych i prywatnych repozytoriów
- GitHub OAuth + webhook integration
- PR comment bot z wynikami analizy
- Health badge do README (shields.io style)
- MCP integration (Model Context Protocol) dla agentów AI
- SQLite persistence + recent scans dashboard
- E2E testy (Playwright)

Aktualny stan techniczny platformy: 73 pliki, 5776 linii kodu, CC̄=3.0, 244 funkcje. Backend w Python (FastAPI), frontend w React (Vite).

## Co dalej

Pracujemy nad: scheduled scans (cykliczne skanowanie co 1-6h), trend dashboard (historia health score w czasie), Stripe billing, auto-PR generation (LLM → patch → walidacja → PR), i Marketplace MVP.

Szczegóły techniczne w osobnych artykułach o poszczególnych projektach organizacji.
