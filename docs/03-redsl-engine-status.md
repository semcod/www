---
title: "ReDSL — autonomiczny silnik refaktoryzacji kodu"
slug: redsl-refactoring-engine-status
date: 2026-04-10
category: Engineering
tags: [redsl, refactoring, dsl, llm, autonomy, code-quality]
excerpt: "ReDSL to silnik refaktoryzacji, który analizuje kod, podejmuje decyzje o naprawach i wykonuje je autonomicznie. Status: 117 plików, CC̄=4.2, plan autonomii w 5 fazach."
author: Tom Softreck
---

# ReDSL — autonomiczny silnik refaktoryzacji kodu

## Czym jest ReDSL

ReDSL (Refactoring Domain-Specific Language) to silnik, który automatyzuje refaktoryzację kodu. Nie jest linterem ani statycznym analizatorem — jest agentem, który:

1. Analizuje repozytorium i rozumie jego strukturę
2. Podejmuje decyzje co naprawić, w jakiej kolejności i jaką strategią
3. Generuje propozycje refaktoryzacji z walidacją
4. Aplikuje zmiany z rollbackiem jeśli coś pójdzie nie tak
5. Uczy się z wyników — zapamiętuje co działało, a co nie

ReDSL jest rdzeniem silnika analizy platformy Semcod. To on stoi za rekomendacjami, auto-PR i pipeline'em napraw.

## Metryki jakości

Dane z automatycznej analizy z dnia 2026-04-09:

| Metryka | Wartość | Ocena |
|---------|---------|-------|
| Pliki | 117 | — |
| Linie kodu | 28 948 | — |
| Funkcje | 847 | — |
| CC̄ | 4.2 | 🟡 do poprawy |
| Critical hotspots | 62 | 🔴 krytyczne |
| High-CC (≥15) | 7 | 🔴 krytyczne |
| God modules (>500L) | 4 | 🔴 krytyczne |
| Duplikacja | 3 grupy | 🟢 niska |
| Cykle | 0 | 🟢 czysto |

Trend CC̄: 5.1 → 4.5 → 4.2 (dobry kierunek, ale LOC rośnie 2x na iterację).

## Architektura

ReDSL składa się z 12 pakietów:

**Rdzeń:**
- `dsl/` — silnik reguł DSL (warunki → akcja z priorytetem), generator reguł z pamięci
- `execution/` — pipeline wykonania: selekcja → decyzja → wykonanie → walidacja → refleksja
- `orchestrator.py` — mózg systemu, łączy wszystkie warstwy

**Analiza:**
- `analyzers/` — parsery .toon, Python AST analyzer, radon bridge, semantic chunker, incremental cache
- `validation/` — regix bridge (regression), pyqual bridge (quality gates), vallm bridge (semantic)

**Refaktoryzacja:**
- `refactors/` — engine LLM, direct AST transformers (imports, guards, constants, types), diff manager, body restorer
- `llm/` — router modeli (local/cloud), estymacja kosztów

**Autonomia:**
- `autonomy/` — quality gate (pre-commit), auto-fix pipeline, growth controller, scheduler, adaptive executor, smart scorer, code review, intent analyzer
- `awareness/` — git timeline, trend analysis, health model, ecosystem graph, self-model, proactive alerts, change patterns

**Pamięć:**
- `memory/` — trzy warstwy: episodic (co robiłem), semantic (wzorce), strategic (strategie). ChromaDB lub in-memory fallback.

## Kluczowe hotspoty

**4 god modules do rozbicia:**

| Moduł | LOC | Max CC | Priorytet |
|-------|-----|--------|-----------|
| batch_pyqual.py | 781L | CC=62 (_process_project) | 🔴 IMPACT: 48422 |
| cli.py | 667L | CC=7 | 🟡 IMPACT: 4669 |
| formatters.py | 614L | CC=13, dup=4 | 🟡 IMPACT: 7982 |
| autofix.py | 506L | CC=23 | 🟡 |

**7 funkcji z CC≥15:**

| Funkcja | CC | Strategia |
|---------|-----|-----------|
| _process_project | 62 | extract 8 sub-functions per pipeline stage |
| _build_summary | 45 | extract per-metric aggregators |
| run_pyqual_batch | 27 | extract loop body |
| _compute_verdict | 25 | extract predicate functions |
| _generate_todo_md | 23 | extract section builders |
| _save_report | 20 | extract format writers |
| _process_project (autofix) | 19 | extract phase functions |

## Jak ReDSL podejmuje decyzje

System reguł DSL ewaluuje kontekst metryczny każdego pliku/funkcji:

```
JEŚLI cyclomatic_complexity > 15 I lines > 300
  TO split_module z priorytetem = CC × fan_in × trend_multiplier
```

Smart scorer dodaje 4 wymiary: trend (czy się pogarsza), ecosystem impact (ile projektów zależy), coupling (ile modułów importuje), confidence (czy umiemy to naprawić na podstawie historii).

Adaptive executor adaptuje strategię w runtime — jeśli extract_functions failuje 2x, przełącza się na simplify_conditionals.

## Plan autonomii — 5 faz

**Faza A — Zamknięta pętla:** Quality gate (pre-commit hook blokujący regresje), auto-fix pipeline (próbuje naprawić violations automatycznie), scheduled self-improvement (cykliczne skanowanie i naprawy co 30-60 minut).

**Faza B — Samokontrola wzrostu:** Growth limiter (budżet LOC/tydzień: max 2000), complexity budget per moduł (max 300L, max 15 funkcji, max CC=10 per typ modułu).

**Faza C — Inteligentna priorytetyzacja:** Impact-weighted scoring (trend × ecosystem × coupling × confidence), adaptive action selection (fallback strategies po failures).

**Faza D — Proaktywne działanie:** Code review assistant (analiza staged changes przed commitem), commit intent analyzer (klasyfikacja: feature/bugfix/refactor + ocena ryzyka).

**Faza E — Natychmiastowe akcje:** Split god modules, rozbij high-CC functions, zainstaluj quality gate, włącz scheduled watch.

## Metryki docelowe

| Metryka | Teraz | Cel | Mechanizm |
|---------|-------|-----|-----------|
| CC̄ | 4.2 | ≤3.0 | split + quality gate |
| Critical | 62 | ≤10 | split + growth control |
| God modules | 4 | 0 | gate blocks >400L |
| High-CC (≥15) | 7 | 0 | gate blocks CC>12 |
| LOC growth/week | ~11000 | <2000 | growth budget |
| Auto-fix rate | 0% | >60% | auto_fix pipeline |

## Rola w ekosystemie Semcod

ReDSL jest silnikiem, który napędza platformę Semcod:

- **Scan Engine** (code2llm + redup + pyqual) dostarcza dane
- **ReDSL** analizuje dane, podejmuje decyzje, generuje propozycje
- **Semcod WWW** prezentuje wyniki użytkownikowi i umożliwia interakcję
- **Auto-PR** system tworzy PR-y z naprawami które ReDSL zaproponował
- **Marketplace** dystrybuuje artefakty, które przeszły quality gate ReDSL

To nie jest narzędzie dla developera do ręcznego uruchamiania. To warstwa AI, która ciągle monitoruje, naprawia i poprawia kod w tle.
