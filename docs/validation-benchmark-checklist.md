## Jak używać

Ta checklista jest operacyjnym uzupełnieniem `docs/validation-benchmark.md`.

Najlepiej używać jej w trzech momentach:

- przed startem benchmarku,
- w trakcie realizacji przypadków,
- przed decyzją o pilocie i modelu wdrożenia.

## 1. Kickoff i zakres

- [ ] Ustalono właściciela benchmarku po stronie Semcod.
- [ ] Ustalono właściciela benchmarku po stronie klienta.
- [ ] Ustalono cel benchmarku: detekcja, rekomendacje, PR, deployment lub pełny pilot.
- [ ] Ustalono zakres czasowy benchmarku.
- [ ] Ustalono liczbę przypadków do oceny.
- [ ] Ustalono kryteria sukcesu i próg `go / conditional go / no-go`.
- [ ] Ustalono, czy benchmark kończy się tylko raportem, czy także pilotem.

## 2. Dobór przypadków

- [ ] Wybrano przypadki zgodnie z matrycą z `docs/validation-benchmark.md`.
- [ ] Pokryto co najmniej 2 języki lub 2 typy stacku.
- [ ] Pokryto co najmniej przypadki typu `bugfix`, `feature`, `refactor`, `maintenance`.
- [ ] Wybrano minimum 1 przypadek z istniejącym PR lub gotowym zakresem zmian.
- [ ] Wybrano minimum 1 przypadek z potencjałem do deploymentu.
- [ ] Każdy przypadek ma przypisany `case_id`.
- [ ] Każdy przypadek ma opis kontekstu biznesowego.

## 3. Baseline klienta

- [ ] Zebrano listę narzędzi używanych obecnie przez klienta.
- [ ] Zebrano wynik obecnego CI lub review dla wybranych przypadków.
- [ ] Zapisano, które problemy baseline już wykrywa.
- [ ] Zapisano, ile trwa dziś standardowa analiza przypadku.
- [ ] Zapisano, kto dziś podejmuje decyzję o poprawce.
- [ ] Zapisano, czy istnieje obecnie ścieżka `ticket -> branch -> PR -> deployment`.

## 4. Dostępy i środowisko

- [ ] Ustalono, czy benchmark działa na repo klienta, naszej infrastrukturze, czy hybrydowo.
- [ ] Potwierdzono dostęp do repozytoriów lub ticketów.
- [ ] Potwierdzono dostęp do danych potrzebnych do baseline.
- [ ] Potwierdzono dostęp do pipeline deploymentowego, jeśli dotyczy.
- [ ] Ustalono, czy przypadki obejmują repo prywatne, publiczne czy oba typy.
- [ ] Ustalono ograniczenia bezpieczeństwa i zakres danych w benchmarku.

## 5. Przygotowanie Semcod

- [ ] Potwierdzono wersję środowiska benchmarkowego Semcod.
- [ ] Potwierdzono działanie głównego flow audytu.
- [ ] Potwierdzono działanie flow sandbox, jeśli jest potrzebne.
- [ ] Potwierdzono eksport wyników w JSON/Markdown.
- [ ] Potwierdzono, że rekomendacje są widoczne w UI wyniku.
- [ ] Potwierdzono, że zapis scan history działa poprawnie.
- [ ] Przygotowano miejsce na zapis wyników benchmarku w Markdown/CSV.

## 6. Realizacja benchmarku per przypadek

Dla każdego `case_id`:

- [ ] Zapisano wejście: repo, PR albo ticket.
- [ ] Zapisano typ zmiany.
- [ ] Zapisano wynik baseline.
- [ ] Uruchomiono Semcod.
- [ ] Zapisano pełny wynik Semcod.
- [ ] Oceniono nowość wykryć.
- [ ] Oceniono użyteczność wykryć.
- [ ] Oceniono trafność wykryć.
- [ ] Oceniono gotowość do działania.
- [ ] Oceniono wartość biznesową.
- [ ] Oceniono rekomendacje.
- [ ] Oceniono gotowość do PR.
- [ ] Oceniono gotowość do deploymentu.
- [ ] Uzupełniono rekord w Markdown lub CSV.

## 7. Decyzje produktowe per przypadek

- [ ] Oznaczono, czy wykrycie było `nowe i wartościowe`.
- [ ] Oznaczono, czy było tylko `lepiej podane` niż w baseline.
- [ ] Oznaczono, czy rekomendacja została zaakceptowana.
- [ ] Oznaczono, czy przypadek nadaje się do PR.
- [ ] Oznaczono, czy przypadek nadaje się do deploymentu.
- [ ] Wybrano preferowany model wdrożenia.
- [ ] Zapisano `next action` dla przypadku.

## 8. Przejście do pilota

- [ ] Wybrano 1-3 przypadki do dalszej realizacji.
- [ ] Ustalono, które przypadki przechodzą do szkicu poprawki.
- [ ] Ustalono, które przypadki przechodzą do brancha lub PR.
- [ ] Ustalono, które przypadki wymagają review człowieka przed następnym krokiem.
- [ ] Ustalono, czy deployment jest w zakresie pilota.
- [ ] Ustalono rolę partnerów, jeśli benchmark przechodzi do managed service.

## 9. Raport końcowy

- [ ] Policzono wszystkie KPI z benchmarku.
- [ ] Zidentyfikowano top kategorie wykryć.
- [ ] Zidentyfikowano false positive.
- [ ] Zidentyfikowano przypadki, gdzie Semcod nie wniósł wartości.
- [ ] Przygotowano 2-3 mocne case studies.
- [ ] Przygotowano backlog ulepszeń produktu.
- [ ] Przygotowano rekomendację modelu wdrożenia.
- [ ] Przygotowano decyzję `go / conditional go / no-go`.

## 10. Artefakty, które muszą powstać

- [ ] Uzupełniony plik `docs/validation-benchmark-template.md` lub jego kopia robocza.
- [ ] Uzupełniony plik `docs/validation-benchmark-template.csv` lub jego kopia robocza.
- [ ] Raport benchmarkowy dla klienta.
- [ ] Lista zmian produktowych wynikających z benchmarku.
- [ ] Propozycja kolejnego etapu współpracy.
