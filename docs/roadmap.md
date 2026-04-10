# Roadmap celu produktu Semcod

## Cel dokumentu

Ten dokument rozwija cel projektu na podstawie aktualnych artefaktów analitycznych:

- `project/analysis.toon.yaml`
- `project/duplication.toon.yaml`
- `project/evolution.toon.yaml`
- `project/map.toon.yaml`
- `project/project.toon.yaml`

Roadmapa ma odpowiedzieć na trzy pytania:

1. Czy Semcod wykrywa coś nowego i realnie wartościowego względem standardowych narzędzi?
2. Czy po wykryciu problemu potrafi od razu zaproponować, co należy poprawić?
3. W jakim modelu wdrożeniowym i biznesowym to oferować: na GitHub/GitLab klienta, na naszej infrastrukturze, czy hybrydowo?

## Wnioski z obecnego stanu projektu

### Co już działa i stanowi fundament produktu

Na podstawie `map.toon.yaml` i `project.toon.yaml` widać, że produkt ma już gotowe filary rozwiązania:

- `backend/routers/audit.py` realizuje główny pipeline analizy repozytorium.
- `backend/routers/webhook.py` daje punkt wejścia do automatyzacji PR.
- `backend/routers/metrics.py` udostępnia metryki i eksport wyników.
- `backend/routers/mcp.py` otwiera integrację z agentami AI i automatyzacją narzędziową.
- `frontend/src/components/phases/ResultPhase.jsx` oraz `frontend/src/hooks/useAppState.js` obsługują główną ścieżkę użytkownika: od skanu do wyniku.
- Istnieją już funkcje produktu, które można sprzedażowo spiąć w jedną ofertę: audit, recent scans, PR bot, badge, MCP, sandbox analysis.

### Co mówi analiza jakości kodu

Na podstawie `analysis.toon.yaml`, `evolution.toon.yaml` i `project.toon.yaml`:

- średnia złożoność projektu jest niska: `CC̄=3.0`,
- brak cykli architektonicznych,
- duplikacja jest niska,
- największe ryzyko leży nie w całym systemie, tylko w kilku hotspotach orkiestracji i UI.

Najważniejsze hotspoty do opanowania przed skalowaniem roadmapy:

- `useAppState` — wysoka złożoność i bardzo duży fan-out,
- `ResultPhase` — wysoka złożoność i centralna rola w prezentacji wyniku,
- `mcp_get_resource` — ważne dla integracji automatyzacyjnych,
- `mcp_invoke_tool` — ważne dla warstwy agentowej,
- `backend.routers` — wysoki fan-out, co może utrudniać rozszerzanie flow o deployment i automatyczne PR-y.

### Co mówi analiza duplikacji

`duplication.toon.yaml` pokazuje tylko jedną małą grupę duplikacji. To ważny wniosek produktowy:

- przewaga Semcod nie powinna być komunikowana jako zwykłe wykrywanie duplikacji,
- „nowa jakość” powinna być oparta na połączeniu: wykrycie problemu + interpretacja + propozycja poprawy + opcja automatycznego wdrożenia zmiany.

## Cel nadrzędny

Celem Semcod nie jest wyłącznie analiza kodu. Celem jest zbudowanie produktu, który:

- wykrywa problemy i sygnały jakościowe, których klient nie widzi w standardowym CI,
- tłumaczy, co z tych wyników wynika biznesowo i technicznie,
- proponuje konkretne poprawki,
- potrafi wygenerować zmianę jako branch lub PR,
- opcjonalnie przejmuje też uruchomienie i deployment na naszej infrastrukturze lub na środowisku klienta.

Docelowo Semcod ma być warstwą pomiędzy:

- repozytorium i ticketami zmian,
- analizą jakości i rekomendacjami,
- automatyzacją implementacji,
- deploymentem artefaktów,
- rozliczeniem usługi i dystrybucją do klienta końcowego.

## Główne hipotezy do zwalidowania

### Hipoteza 1 — nowa jakość detekcji

Semcod powinien wykrywać problemy, których nie pokazują same linery, testy i podstawowy code review.

Przykłady obszarów do walidacji:

- problemy architektoniczne,
- nadmierna złożoność ścieżek użytkownika,
- słabe miejsca w orkiestracji modułów,
- sugestie refaktoryzacji wynikające z relacji i hotspotów, a nie tylko z pojedynczego pliku,
- gotowość kodu do automatyzacji PR i deploymentu.

### Hipoteza 2 — rekomendacja jest ważniejsza niż sama detekcja

Sam wykryty problem ma ograniczoną wartość, jeśli użytkownik nie dostaje od razu odpowiedzi:

- co poprawić,
- w jakiej kolejności,
- jaki będzie wpływ poprawki,
- czy można od razu wygenerować branch, commit albo PR.

### Hipoteza 3 — deployment zwiększa wartość produktu

Dla części klientów wartość nie kończy się na rekomendacji. Wartość kończy się dopiero, gdy:

- zmiana zostaje wdrożona,
- środowisko działa,
- klient może szybko rozliczyć usługę lub dostarczyć artefakt dalej.

### Hipoteza 4 — model wdrożenia wpływa na konwersję

Trzeba sprawdzić, która ścieżka ma większą konwersję:

- wdrożenie na GitHub/GitLab klienta,
- wdrożenie na naszej infrastrukturze,
- model hybrydowy: automatyzacja na repo klienta, deployment na naszej infrastrukturze.

## Roadmapa wykonania

Sugerowany horyzont realizacji:

- Faza 0 — 1-2 tygodnie
- Faza 1 — 2-3 tygodnie
- Faza 2 — 2-4 tygodnie
- Faza 3 — 1-2 tygodnie
- Faza 4 — 3-6 tygodni
- Faza 5 — 4-8 tygodni

### Faza 0 — stabilizacja pod roadmapę (1-2 tyg.)

### Cel

Przygotować produkt do rozszerzania o kolejne ścieżki decyzyjne bez zwiększania chaosu w kluczowych modułach.

### Zakres

- rozbić `useAppState` na mniejsze odpowiedzialności,
- rozbić `ResultPhase` na sekcje wyniku i akcje użytkownika,
- uprościć `mcp_get_resource` i `mcp_invoke_tool`,
- zredukować lokalną duplikację w `backend/database.py`,
- dołożyć instrumentację produktu pod benchmark: logowanie typów wykryć, rekomendacji, akcji użytkownika i wyników PR,
- dopiąć testy E2E dla najważniejszych flow związanych ze skanem i wynikiem.

### Uzasadnienie

To nie jest refaktoryzacja „dla porządku”. To warunek, żeby bezpiecznie dodać:

- warianty deploymentu,
- generowanie PR,
- automatyzację z ticketów,
- dodatkowe ścieżki sprzedażowe i partnerskie.

### Definition of Done

- kluczowe hotspoty z `evolution.toon.yaml` mają rozpisany i rozpoczęty plan rozbicia,
- wynik skanu i działania użytkownika są mierzalne,
- główne flow audytu i prezentacji wyniku są zabezpieczone testami regresyjnymi.

### Faza 1 — test walidacyjny „co nowego wykrywa?” (2-3 tyg.)

### Cel

Udowodnić na danych, że Semcod dostarcza nową jakość względem standardowego stacku narzędzi.

Szczegółowy plan wykonawczy znajduje się w `docs/validation-benchmark.md`.

### Zakres testu

Należy przygotować benchmark obejmujący:

- 10–20 repozytoriów lub reprezentatywną pulę zmian,
- mix projektów Python i JavaScript,
- przypadki typu: bugfix, feature, refactor, maintenance,
- porównanie do obecnego procesu klienta: CI, lintery, testy, manual review.

### Dla każdego przypadku mierzymy

- co wykrył Semcod,
- czego nie wykryły pozostałe narzędzia,
- które sygnały były rzeczywiście użyteczne,
- które były false positive,
- jaki był czas od skanu do pierwszej sensownej rekomendacji,
- czy użytkownik uznał wynik za gotowy do dalszego działania.

### Oczekiwane artefakty

- raport benchmarkowy,
- tabela kategorii wykryć,
- 3–5 studiów przypadku pokazujących „nową jakość”,
- lista sytuacji, w których Semcod nie wnosi dodatkowej wartości i wymaga dopracowania.

### Kluczowe KPI

- udział wykryć uznanych za nowe względem bazowego procesu,
- udział wykryć uznanych za użyteczne,
- poziom false positive,
- czas od skanu do rekomendacji,
- liczba wyników, które przeszły do etapu poprawki lub PR.

### Faza 2 — warstwa rekomendacji i propozycji poprawy (2-4 tyg.)

### Cel

Każdy wynik analizy ma prowadzić do następnej akcji, a nie kończyć się na liście problemów.

### Zakres

Dla każdego istotnego wykrycia Semcod powinien generować:

- opis problemu,
- uzasadnienie, dlaczego to ma znaczenie,
- rekomendowaną kolejność działań,
- szacowany wpływ i wysiłek,
- propozycję poprawki technicznej,
- propozycję testu lub sposobu walidacji,
- opcję wygenerowania patcha, brancha albo PR.

### Wyjścia produktu

Ta warstwa powinna być widoczna równolegle w:

- UI wyniku skanu,
- komentarzu PR,
- eksporcie do markdown lub promptu,
- interfejsie MCP,
- automatyzacjach uruchamianych z ticketów.

### Definition of Done

- każdy wynik krytyczny lub ważny ma przypisaną rekomendację działania,
- użytkownik widzi nie tylko „co jest źle”, ale też „co zrobić teraz”,
- możliwe jest przejście z rekomendacji do szkicu PR bez ręcznego przepisywania analizy.

### Faza 3 — produktowe ścieżki wdrożenia (1-2 tyg.)

### Cel

Ustandaryzować ofertę wdrożeniową i nie zostawiać klienta z otwartym pytaniem „co dalej?”.

### Wariant A — wdrożenie na GitHub/GitLab klienta

Najlepsze dla zespołów, które:

- mają własny proces release,
- chcą zachować pełną kontrolę nad repozytorium i runnerami,
- potrzebują głównie analizy, rekomendacji i automatyzacji PR.

Semcod dostarcza wtedy:

- integrację z repo,
- analizę zmian,
- rekomendacje,
- generowanie branchy i PR,
- opcjonalne hooki do istniejącego CI/CD.

### Wariant B — wdrożenie na naszej infrastrukturze

Najlepsze dla klientów, którzy chcą skrócić czas wejścia i nie chcą od razu przygotowywać własnego środowiska.

Semcod dostarcza wtedy:

- gotowe środowisko uruchomieniowe,
- onboarding bez dużego narzutu operacyjnego,
- możliwość uruchomienia pilota i benchmarku,
- opcję „1 miesiąc gratis” jako wejście sprzedażowe,
- możliwość przejęcia deploymentu i automatyzacji po stronie partnerów.

### Wariant C — model hybrydowy

Najlepsze dla klientów, którzy chcą zachować repo u siebie, ale delegować środowisko wykonawcze i deployment.

Semcod dostarcza wtedy:

- automatyzację na GitHub/GitLab klienta,
- deployment na naszej infrastrukturze,
- spójny przepływ od ticketu do wdrożenia,
- możliwość rozliczania osobno automatyzacji i runtime.

### Definition of Done

- w UI i ofercie istnieją trzy jasne ścieżki wdrożenia,
- każda ścieżka ma opis: dla kogo, co obejmuje, jakie są ograniczenia,
- klient po skanie dostaje jasne pytanie o preferowany model wdrożenia.

### Faza 4 — automatyzacja na bazie ticketów i zmian (3-6 tyg.)

### Cel

Przenieść produkt z poziomu „analiza repo” na poziom „obsługa konkretnej zmiany biznesowej”.

### Zakres

System powinien przyjmować wejście z:

- ticketów zmian,
- zgłoszeń bugfix,
- feature requestów,
- pull requestów,
- backlogu klienta.

Na tej podstawie Semcod powinien:

- sklasyfikować typ pracy,
- zaproponować plan wykonania,
- wskazać obszary kodu do zmiany,
- wygenerować rekomendacje i szkic implementacji,
- przygotować testy lub checklistę walidacyjną,
- wygenerować branch/PR,
- opcjonalnie przekazać zmianę do deploymentu.

### Rola partnerów

Z partnerami można dostarczać:

- środowisko uruchomieniowe,
- obsługę deploymentu,
- operacyjne utrzymanie wygenerowanych rozwiązań,
- rozszerzone przepływy dla klientów enterprise.

### Definition of Done

- co najmniej jeden pilotowy flow działa od ticketu do PR,
- istnieje approval gate człowieka przed merge lub deploymentem,
- wynik automatyzacji jest mierzalny: czas, jakość, liczba poprawek manualnych.

### Faza 5 — marketplace artefaktów i rozliczenie usługi (4-8 tyg.)

### Cel

Rozszerzyć model biznesowy z analizy i automatyzacji na dystrybucję gotowych artefaktów i łatwe rozliczanie.

### Zakres

Semcod powinien wspierać oferowanie i dostarczanie artefaktów dla:

- SaaS,
- desktop,
- mobile.

W praktyce oznacza to przygotowanie warstwy:

- pakowania artefaktów,
- deploymentu lub publikacji,
- dystrybucji do klienta końcowego,
- licencjonowania i rozliczania.

### Możliwe modele rozliczeniowe

- opłata za usługę,
- opłata za deployment,
- opłata za czas działania środowiska,
- opłata za wykorzystane tokeny lub operacje AI,
- abonament za pakiet możliwości,
- rozliczenie partnerskie dla wdrożeń specjalnych.

### Definition of Done

- istnieje spójna oferta dla co najmniej jednego typu artefaktu,
- proces publikacji i rozliczenia nie wymaga ręcznego składania usługi od zera,
- klient rozumie, za co płaci: analiza, automatyzacja, runtime, deployment lub dystrybucja.

## Priorytety techniczne wspierające roadmapę

Na bazie plików analitycznych priorytet techniczny powinien być następujący:

1. Rozbić `frontend/src/hooks/useAppState.js`.
2. Rozbić `frontend/src/components/phases/ResultPhase.jsx`.
3. Uprościć `backend/routers/mcp.py` w punktach integracyjnych.
4. Ograniczyć przeciążenie warstwy `backend.routers` przez lepszą separację orkiestracji.
5. Dodać benchmarkowe metryki produktu: wykrycie, rekomendacja, akceptacja, PR, deployment.
6. Rozszerzyć testy E2E o ścieżki, które będą wspierały sprzedaż i pilotaże.

## Minimalny pilot komercyjny

Najmniejszy sensowny pilot, który warto sprzedać i uruchomić, powinien obejmować:

1. Podpięcie repozytorium lub zestawu ticketów.
2. Wykonanie benchmarku „co nowego wykrywa?”.
3. Wygenerowanie rekomendacji działań dla wykrytych problemów.
4. Uruchomienie jednego flow automatycznego PR.
5. Wybór ścieżki wdrożenia: klient, nasze środowisko albo hybryda.
6. Raport końcowy pokazujący wartość i kolejne kroki.

## Kryteria sukcesu roadmapy

Roadmapa jest zrealizowana skutecznie, jeśli Semcod potrafi jednocześnie:

- udowodnić nową jakość detekcji,
- przełożyć wynik na konkretne rekomendacje,
- wygenerować zmianę jako PR lub automatyzację,
- obsłużyć przynajmniej jeden model deploymentu end-to-end,
- zamienić to w prostą, zrozumiałą ofertę dla klienta i partnera.
