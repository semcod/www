---
title: "Roadmap Semcod — od walidacji jakości do autonomicznego deploymentu"
slug: semcod-roadmap-validation-to-deployment
date: 2026-04-10
category: Roadmap
tags: [semcod, roadmap, validation, benchmark, auto-pr, deployment]
excerpt: "Sześć faz rozwoju Semcod: stabilizacja, walidacja nowej jakości, warstwa rekomendacji, modele wdrożenia, automatyzacja ticketów, marketplace. Z konkretnymi KPI i definition of done."
author: Tom Softreck
---

# Roadmap Semcod — od walidacji jakości do autonomicznego deploymentu

## Trzy pytania, na które odpowiada ten roadmap

1. **Czy Semcod wykrywa coś nowego?** Coś, czego nie pokazują standardowe lintery, testy i code review?
2. **Czy po wykryciu potrafi zaproponować naprawę?** Nie listę warningów, ale konkretną akcję z priorytetem i szacowanym effort?
3. **W jakim modelu to oferować?** Na GitHub klienta, na naszej infrastrukturze, czy hybrydowo?

## Co już mamy i co z tego wynika

Na podstawie analizy plików toon (project, analysis, evolution, duplication, map) widzimy:

Produkt ma gotowe filary: pipeline audytu, webhook na PR, eksport metryk, integrację MCP z agentami AI, sandbox mode dla publicznych repozytoriów. Średnia złożoność jest niska (CC̄=3.0), brak cykli architektonicznych, minimalna duplikacja. Problemy koncentrują się w kilku hotspotach orkiestracji (useAppState, ResultPhase, mcp.py), nie w całym systemie.

Wniosek: system jest gotowy do rozszerzania, ale wymaga stabilizacji hotspotów przed skalowaniem.

## Faza 0 — Stabilizacja (1-2 tyg.)

**Cel:** Przygotować produkt do rozszerzania bez zwiększania chaosu.

**Zakres:**
- Rozbić useAppState (CC=51) na mniejsze hooki
- Rozbić ResultPhase (CC=54) na sub-komponenty
- Uprościć mcp_get_resource (CC=22) i mcp_invoke_tool (CC=17)
- Dodać instrumentację: logowanie typów wykryć, rekomendacji, akcji użytkownika
- Dopiąć testy E2E dla skanowania i prezentacji wyników

**Definition of Done:** Hotspoty mają CC<10, główne flow zabezpieczone testami, metryki produktu mierzalne.

## Faza 1 — Test walidacyjny „co nowego wykrywa?" (2-3 tyg.)

**Cel:** Udowodnić na danych, że Semcod dostarcza wartość ponad standardowy CI.

**Benchmark:**
- 10-20 repozytoriów (Python + JavaScript)
- Mix: bugfix, feature, refactor, maintenance
- Porównanie z: CI, lintery, testy, manual review

**Dla każdego przypadku mierzymy:**
- Co wykrył Semcod, czego nie wykryły inne narzędzia
- Które sygnały były użyteczne vs false positive
- Czas od skanu do pierwszej rekomendacji
- Ile wyników przeszło do etapu poprawki/PR

**Artefakty:** Raport benchmarkowy, tabela kategorii wykryć, 3-5 case studies, lista luk do dopracowania.

**KPI:** Udział wykryć nowych (vs baseline), udział użytecznych, poziom false positive, czas do rekomendacji.

## Faza 2 — Warstwa rekomendacji (2-4 tyg.)

**Cel:** Każdy wynik analizy prowadzi do następnej akcji, nie do listy problemów.

Dla każdego istotnego wykrycia Semcod generuje: opis problemu, uzasadnienie biznesowe i techniczne, rekomendowaną kolejność działań, szacowany wpływ i wysiłek, propozycję techniczną, propozycję testu, opcję wygenerowania PR.

Widoczne równolegle w: UI wyniku, komentarzu PR, eksporcie markdown, interfejsie MCP, automatyzacjach z ticketów.

**Definition of Done:** Każdy wynik krytyczny ma rekomendację, użytkownik widzi „co zrobić teraz", możliwe przejście z rekomendacji do PR bez ręcznego przepisywania.

## Faza 3 — Modele wdrożenia (1-2 tyg.)

**Wariant A — Self-managed:** Integracja z GitHub/GitLab klienta. Scany, rekomendacje, auto-PR. Klient kontroluje proces. Od $9/mies.

**Wariant B — Managed Infrastructure:** Gotowe środowisko uruchomieniowe. Onboarding bez narzutu operacyjnego. 1 miesiąc gratis. Token-based lub compute hours.

**Wariant C — Hybrydowy:** Repo na GitHub klienta, compute i deployment na infrastrukturze Semcod. Spójny flow od ticketu do wdrożenia.

**Definition of Done:** W UI istnieją trzy jasne ścieżki, każda z opisem: dla kogo, co obejmuje, ograniczenia. Klient po skanie dostaje pytanie o preferowany model.

## Faza 4 — Automatyzacja na bazie ticketów (3-6 tyg.)

**Cel:** Przejście z „analiza repo" na „obsługa konkretnej zmiany biznesowej".

System przyjmuje wejście z: ticketów, zgłoszeń bugfix, feature requestów, PR, backlogu. Na tej podstawie: klasyfikuje typ pracy, proponuje plan, wskazuje pliki do zmiany, generuje szkic implementacji + testy, przygotuje branch/PR, opcjonalnie przekazuje do deploymentu.

Approval gate człowieka: konfigurowalny (przy każdym PR, co N zmian, lub full-auto).

**Definition of Done:** Co najmniej jeden flow ticket→PR działa, approval gate istnieje, wynik mierzalny (czas, jakość, poprawki manualne).

## Faza 5 — Marketplace (4-8 tyg.)

**Cel:** Rozszerzyć model z analizy na dystrybucję artefaktów.

Typy: SaaS, desktop, mobile, API. Rozliczanie: subskrypcja, tokeny, jednorazowo, per request. Revenue share: developer 70-85%, Semcod 15-30%. Stripe Connect, payouty co 2 tygodnie.

**Definition of Done:** Spójna oferta dla co najmniej jednego typu artefaktu, proces publikacji i rozliczenia nie wymaga ręcznego składania, klient rozumie za co płaci.

## Minimalny pilot komercyjny

Najmniejszy sensowny pilot do uruchomienia i sprzedania:

1. Podpięcie repozytorium lub zestawu ticketów
2. Benchmark „co nowego wykrywa?" na danych klienta
3. Wygenerowanie rekomendacji z priorytetami
4. Uruchomienie jednego flow auto-PR
5. Wybór modelu wdrożenia (A/B/C)
6. Raport końcowy z wartością i kolejnymi krokami

## Kryteria sukcesu

Roadmapa jest zrealizowana, jeśli Semcod potrafi jednocześnie: udowodnić nową jakość detekcji, przełożyć wynik na rekomendacje, wygenerować PR, obsłużyć przynajmniej jeden model deploymentu end-to-end, i zamienić to w prostą ofertę dla klienta i partnera.
