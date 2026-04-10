# Szablon benchmarku walidacyjnego Semcod

Skopiuj ten plik do wersji roboczej dla konkretnego benchmarku i uzupełniaj jeden blok na każdy `case_id`.

## Metadane benchmarku

| Pole | Wartość |
|---|---|
| Nazwa benchmarku | |
| Klient / zespół | |
| Owner po stronie Semcod | |
| Owner po stronie klienta | |
| Zakres dat | |
| Cel benchmarku | |
| Tryb wdrożenia startowy | |
| Kryterium sukcesu | |

## Podsumowanie KPI

| KPI | Wynik | Próg minimalny | Próg dobry | Status |
|---|---:|---:|---:|---|
| Novel actionable finding rate | | 25% | 40% | |
| Recommendation acceptance rate | | 50% | 70% | |
| False positive rate | | <=20% | <=10% | |
| Time to first useful recommendation | | <=15 min | <=5 min | |
| PR conversion rate | | 20% | 35% | |
| Deployment decision rate | | 60% | 80% | |

## Przypadki benchmarkowe

---

### Case `BM-001`

#### Identyfikacja

| Pole | Wartość |
|---|---|
| `case_id` | BM-001 |
| Repo / moduł / ticket | |
| `source_type` | |
| `change_type` | |
| Język / stack | |
| Krytyczność | |
| Czy przypadek klient-facing | |

#### Baseline klienta

| Pole | Wartość |
|---|---|
| Narzędzia baseline | |
| Wynik baseline | |
| Czas analizy baseline | |
| Czy baseline wykrył problem | |
| Czy baseline prowadzi do PR | |
| Czy baseline prowadzi do deploymentu | |

#### Wynik Semcod

| Pole | Wartość |
|---|---|
| `audit_id` | |
| Health score | |
| Grade | |
| Top finding category | |
| Top recommendation | |
| Time to first result | |
| Time to first useful recommendation | |
| Czy wygenerowano rekomendację | |
| Czy przypadek jest kandydatem do PR | |
| Czy przypadek jest kandydatem do deploymentu | |

#### Ocena ekspercka

| Wymiar | Skala 0-3 | Uzasadnienie |
|---|---:|---|
| Nowość | | |
| Użyteczność | | |
| Trafność | | |
| Gotowość do działania | | |
| Wartość biznesowa | | |

#### Klasyfikacja wyniku

- [ ] Nowe i wartościowe
- [ ] Znane, ale lepiej podane
- [ ] Poprawne, ale słabo użyteczne
- [ ] Nietrafne lub szum

#### Decyzje

| Pole | Wartość |
|---|---|
| Recommendation accepted | |
| PR candidate | |
| Deployment candidate | |
| Preferred deployment model | |
| Reviewer verdict | |
| Next action | |

#### Notatki

- |
- |
- |

---

### Case `BM-002`

Skopiuj blok `BM-001` dla kolejnych przypadków.

## Wnioski końcowe

### Co Semcod wykrywa lepiej niż baseline

- |
- |
- |

### Gdzie rekomendacje mają najwyższą wartość

- |
- |
- |

### Gdzie produkt wymaga poprawy

- |
- |
- |

### Decyzja wdrożeniowa

- [ ] Własny GitHub/GitLab
- [ ] Nasza infrastruktura
- [ ] Hybryda

### Decyzja końcowa benchmarku

- [ ] Go
- [ ] Conditional go
- [ ] No-go
