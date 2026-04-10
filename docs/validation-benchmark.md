# Benchmark walidacyjny i plan pilota Semcod

## Cel dokumentu

Ten dokument przekłada Fazę 1 z `docs/roadmap.md` na plan wykonawczy. Jego celem jest jednoczesne zwalidowanie trzech rzeczy:

1. Czy Semcod wykrywa nową wartość względem standardowego procesu klienta.
2. Czy wykrycia są wystarczająco użyteczne, aby przechodzić do rekomendacji, PR lub wdrożenia.
3. Który model wdrożeniowy najlepiej pasuje do klienta: jego GitHub/GitLab, nasza infrastruktura, czy model hybrydowy.

## Artefakty robocze

Do pracy operacyjnej z benchmarkiem używaj razem z tym dokumentem:

- `docs/validation-benchmark-checklist.md` — checklista wykonawcza benchmarku,
- `docs/validation-benchmark-template.md` — szablon Markdown do wypełniania case-by-case,
- `docs/validation-benchmark-template.csv` — szablon CSV do zbierania wyników,
- `docs/benchmark-kpi-product-plan.md` — plan zmian UI/API potrzebnych do zbierania KPI.

## Decyzje, które dokument ma umożliwić

Po wykonaniu benchmarku i pilota powinniśmy umieć odpowiedzieć:

- czy Semcod wnosi nową jakość, czy tylko porządkuje sygnały z innych narzędzi,
- które typy wykryć są naprawdę wyróżnikiem produktu,
- czy rekomendacje są wystarczająco konkretne, aby generować poprawki,
- czy klient jest gotowy na automatyzację ticket → branch → PR,
- czy lepsza będzie sprzedaż produktu jako narzędzia repo-only, managed service, czy oferty hybrydowej.

## Zakres benchmarku

### Minimalny zakres

- 8-12 repozytoriów lub równoważna pula zmian,
- 12-20 przypadków oceny,
- mix Python oraz JavaScript/TypeScript,
- przypadki typu: bugfix, feature, refactor, maintenance,
- minimum jeden przypadek z istniejącym PR lub gotowym zakresem zmian,
- minimum jeden przypadek z potencjałem deploymentowym po naszej stronie.

### Wariant rozszerzony

Jeżeli klient ma większy backlog lub wiele zespołów, benchmark można rozszerzyć o:

- porównanie wielu zespołów lub wielu repo,
- porównanie projektów o różnym poziomie dojrzałości CI/CD,
- ocenę gotowości do automatyzacji na podstawie ticketów,
- ocenę opłacalności deploymentu na naszej infrastrukturze.

## Matryca doboru przypadków

Każdy benchmark powinien być zbalansowany według poniższej matrycy.

| Wymiar | Minimum | Cel |
|---|---:|---:|
| Języki | 2 Python + 2 JS/TS | 4 Python + 4 JS/TS |
| Typ pracy | 1 bugfix, 1 feature, 1 refactor, 1 maintenance | po 3-5 przypadków na typ |
| Rozmiar repo | 1 małe, 1 średnie, 1 większe | pełny rozkład |
| Dojrzałość procesu | low, medium, high | pełny przekrój |
| Poziom krytyczności | wewnętrzne + klient-facing | oba typy |
| Tryb wejścia | repo, PR, ticket | wszystkie 3 |

Jeżeli klient nie ma wystarczającej liczby repozytoriów, przypadki można budować na podstawie:

- branchy z historycznych zmian,
- już zamkniętych PR,
- ticketów opisujących wdrożone lub planowane zmiany,
- wybranych modułów jednego większego repozytorium.

## Baseline do porównania

Benchmark nie może porównywać Semcod do „braku procesu”. Należy ustalić realny baseline klienta.

### Minimalny baseline

- testy automatyczne,
- lintery i statyczna analiza,
- podstawowy review PR,
- aktualny proces deploymentu,
- obecny sposób obsługi bugfixów i feature requestów.

### Dla każdego przypadku zapisujemy

- jakie narzędzia już były używane,
- jakie sygnały dał obecny pipeline,
- ile czasu zajmuje standardowa analiza,
- kto dziś podejmuje decyzję o poprawce,
- czy istnieje już ścieżka do PR i deploymentu.

## Procedura benchmarku

### Etap 1 — Przygotowanie wejścia

#### Cel

Zebrać materiał testowy i ustalić baseline.

#### Kroki

- wybrać przypadki zgodnie z matrycą,
- opisać kontekst biznesowy każdego przypadku,
- zebrać wynik istniejącego procesu klienta,
- oznaczyć przypadki, które nadają się do wygenerowania PR,
- oznaczyć przypadki, które nadają się do deploymentu pilotażowego.

#### Artefakt

- lista przypadków benchmarkowych z metadanymi.

### Etap 2 — Uruchomienie Semcod

#### Cel

Wygenerować porównywalne wyniki dla każdego przypadku.

#### Zakres wyjść Semcod

Dla każdego przypadku zapisujemy:

- wynik audytu,
- listę wykryć,
- metryki i priorytety,
- rekomendacje działań,
- sugestie techniczne,
- gotowość do PR,
- gotowość do deploymentu,
- proponowany model wdrożenia.

#### Kanały wyniku

Warto sprawdzić ten sam przypadek w kilku kanałach wyjścia:

- UI wyniku,
- komentarz PR,
- eksport markdown lub prompt,
- integracja MCP.

### Etap 3 — Ocena ekspercka i porównanie z baseline

#### Cel

Ocenić, czy Semcod wniósł wartość, a nie tylko wygenerował dodatkowy hałas.

#### Ocena dla każdego wykrycia

Każde wykrycie powinno dostać ocenę w pięciu wymiarach:

| Wymiar | Skala | Pytanie |
|---|---|---|
| Nowość | 0-3 | Czy Semcod pokazał coś, czego baseline nie wskazał? |
| Użyteczność | 0-3 | Czy wynik pomaga podjąć decyzję lub wykonać zmianę? |
| Trafność | 0-3 | Czy sygnał jest poprawny i nie jest false positive? |
| Gotowość do działania | 0-3 | Czy da się od razu przejść do taska, poprawki lub PR? |
| Wartość biznesowa | 0-3 | Czy wykrycie wpływa na koszt, ryzyko, czas lub jakość dostawy? |

#### Interpretacja wyniku

- `0` — brak wartości,
- `1` — sygnał słaby lub niejednoznaczny,
- `2` — sygnał przydatny,
- `3` — silna wartość i gotowość do działania.

### Etap 4 — Warstwa rekomendacji

#### Cel

Sprawdzić, czy wynik przechodzi z diagnozy do sensownej propozycji działania.

#### Dla każdego ważnego wykrycia oceniamy

- czy rekomendacja została wygenerowana,
- czy rekomendacja jest zrozumiała dla zespołu,
- czy wskazuje kolejność działań,
- czy zawiera propozycję walidacji lub testu,
- czy można na jej podstawie wygenerować szkic brancha lub PR.

#### Oczekiwany poziom jakości

Rekomendacja powinna być wystarczająco dobra, aby człowiek nie musiał od nowa analizować problemu od zera.

### Etap 5 — Przejście do pilota

#### Cel

Sprawdzić, czy Semcod potrafi wyjść poza analizę i doprowadzić do realnej zmiany.

#### Minimalny pilot

Dla przynajmniej 1-3 przypadków należy przejść dalej niż sam benchmark:

- zaakceptować rekomendację,
- przygotować szkic poprawki,
- wygenerować branch lub PR,
- uruchomić review,
- podjąć decyzję o deploymentcie,
- zamknąć przypadek raportem końcowym.

## KPI i progi sukcesu

### KPI produktu

- **Novel actionable finding rate** — odsetek przypadków, w których Semcod pokazał nowy i użyteczny sygnał.
- **Recommendation acceptance rate** — odsetek ważnych wykryć, dla których rekomendacja została zaakceptowana jako sensowna.
- **False positive rate** — odsetek sygnałów uznanych za nietrafne lub mylące.
- **Time to first useful recommendation** — czas od uruchomienia analizy do pierwszej rekomendacji uznanej za przydatną.
- **PR conversion rate** — odsetek przypadków, które przeszły do szkicu brancha lub PR.
- **Deployment decision rate** — odsetek przypadków, dla których po benchmarku podjęto decyzję o modelu wdrożenia.

### Progi rekomendowane na start

| KPI | Próg minimalny | Próg dobry |
|---|---:|---:|
| Novel actionable finding rate | 25% | 40% |
| Recommendation acceptance rate | 50% | 70% |
| False positive rate | <=20% | <=10% |
| Time to first useful recommendation | <=15 min | <=5 min |
| PR conversion rate | 20% | 35% |
| Deployment decision rate | 60% | 80% |

### Reguła go / conditional go / no-go

- **Go** — osiągnięte minimum dla co najmniej 4 z 6 KPI i istnieją co najmniej 2 mocne case study.
- **Conditional go** — wartość jest widoczna, ale wymaga dopracowania rekomendacji, precision albo ścieżki PR.
- **No-go** — Semcod nie pokazuje przewagi nad baseline lub nie przechodzi do działania.

## Klasyfikacja wyników benchmarku

Każde wykrycie kończy w jednej z kategorii:

- **Nowe i wartościowe** — baseline tego nie wykazał, a zespół uznał wynik za przydatny.
- **Znane, ale lepiej podane** — Semcod nie odkrył nic nowego, ale lepiej priorytetyzuje lub tłumaczy.
- **Poprawne, ale słabo użyteczne** — wykrycie jest trafne, ale nie przekłada się na działanie.
- **Nietrafne lub szum** — wykrycie nie powinno wpływać na decyzję.

To rozróżnienie jest ważne, bo Semcod może budować wartość nie tylko przez stricte nowe wykrycia, ale też przez przełożenie analizy na decyzję i wykonanie.

## Dane, które trzeba zbierać w produkcie

Żeby benchmark był powtarzalny, warto zbierać co najmniej poniższe pola:

- `case_id`
- `repo_id`
- `source_type` (`repo`, `pr`, `ticket`)
- `change_type` (`bugfix`, `feature`, `refactor`, `maintenance`)
- `language_mix`
- `finding_category`
- `severity`
- `baseline_detected`
- `semcod_novel`
- `recommendation_generated`
- `recommendation_accepted`
- `pr_generated`
- `deployment_candidate`
- `deployment_model_selected`
- `time_to_first_result`
- `time_to_first_useful_recommendation`
- `reviewer_verdict`

## Szablon rekordu benchmarkowego

Poniższy szablon można stosować jako jeden rekord oceny dla każdego przypadku.

| Pole | Wartość |
|---|---|
| `case_id` | |
| `repo / moduł / ticket` | |
| `source_type` | |
| `change_type` | |
| `baseline tools` | |
| `baseline findings` | |
| `semcod findings` | |
| `novelty score (0-3)` | |
| `usefulness score (0-3)` | |
| `accuracy score (0-3)` | |
| `actionability score (0-3)` | |
| `business value score (0-3)` | |
| `recommendation accepted` | |
| `pr candidate` | |
| `deployment candidate` | |
| `preferred deployment model` | |
| `reviewer verdict` | |
| `next action` | |

## Decyzja wdrożeniowa po benchmarku

Po zakończeniu benchmarku klient powinien dostać proste pytanie decyzyjne.

### Pytanie główne

Który model chcecie uruchomić po pilocie?

- **Własny GitHub/GitLab** — Semcod działa na repo i procesie klienta.
- **Nasza infrastruktura** — szybki start, benchmark i pilot z opcją 1 miesiąca gratis.
- **Hybryda** — repo i workflow u klienta, środowisko wykonawcze i deployment po naszej stronie.

### Pytania uzupełniające

- Czy chcecie ograniczyć się do analizy i rekomendacji, czy od razu przejść do automatyzacji PR?
- Czy chcecie włączyć obsługę ticketów jako wejście do generowania zmian?
- Czy deployment ma być częścią oferty od początku, czy dopiero po potwierdzeniu wartości benchmarku?
- Czy potrzebne są artefakty do dalszej dystrybucji: SaaS, desktop, mobile?

## Plan pilota 2-4 tygodnie

### Tydzień 1 — Onboarding i baseline

- wybór przypadków,
- zebranie dostępu do repo lub ticketów,
- opis aktualnego procesu klienta,
- ustalenie mierników i osób oceniających.

### Tydzień 2 — Benchmark i pierwsze rekomendacje

- uruchomienie Semcod,
- ocena wykryć,
- porównanie z baseline,
- wybór 1-3 przypadków do przejścia w PR.

### Tydzień 3 — Automatyzacja i decyzja wdrożeniowa

- wygenerowanie szkiców zmian,
- review z klientem,
- wybór ścieżki deploymentu,
- identyfikacja roli partnerów i zakresu managed service.

### Tydzień 4 — Raport końcowy i oferta

- raport benchmarkowy,
- case studies,
- lista ulepszeń produktu,
- rekomendowany model współpracy,
- oferta kolejnego etapu.

## Artefakty końcowe

Po benchmarku i pilocie powinny powstać:

- raport benchmarkowy per przypadek,
- ranking kategorii wykryć,
- lista false positive i braków produktu,
- backlog ulepszeń Semcod,
- 2-3 case studies sprzedażowe,
- decyzja o modelu wdrożenia,
- szkic oferty dla klienta lub partnera.

## Kiedy benchmark uznajemy za sukces

Benchmark jest udany, jeśli jednocześnie:

- Semcod pokazał przynajmniej kilka wykryć uznanych za nowe i wartościowe,
- rekomendacje były wystarczająco konkretne, by przejść do działania,
- co najmniej jeden przypadek przeszedł do etapu PR lub przygotowania wdrożenia,
- klient potrafi wskazać preferowany model wdrożenia,
- z benchmarku powstaje materiał sprzedażowy i backlog produktowy.

## Powiązanie z roadmapą

Ten dokument rozwija przede wszystkim:

- Fazę 1 — walidacja nowej jakości,
- Fazę 2 — rekomendacje i propozycje poprawy,
- Fazę 3 — wybór modelu wdrożenia,
- Fazę 4 — przejście w automatyzację ticket → PR.
