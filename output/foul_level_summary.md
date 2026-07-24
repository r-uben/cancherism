# Foul-level unit of analysis

Each row in `data/processed/foul_level.csv` is **one called foul**.

- Total fouls: **217** (ARG 111, opp 106)
- Carded (linked): ARG **16/111** (14.4%), opp **11/106** (10.4%)
- ARG uncarded candidates: **95**
- L2 multi-source matched to specific foul(s): **5** rows (3 incident ids)

## Per match (foul-level card link rate)

| Match | ARG fouls | ARG carded | ARG rate | Opp fouls | Opp carded | Opp rate |
|-------|----------:|-----------:|---------:|----------:|-----------:|---------:|
| ARG-ALG GS | 13 | 0 | 0.000 | 7 | 0 | 0.000 |
| ARG-AUT GS | 12 | 2 | 0.167 | 13 | 2 | 0.154 |
| JOR-ARG GS | 7 | 0 | 0.000 | 13 | 3 | 0.231 |
| ARG-CPV R32 | 12 | 1 | 0.083 | 13 | 1 | 0.077 |
| ARG-EGY R16 | 13 | 0 | 0.000 | 11 | 2 | 0.182 |
| ARG-SUI QF | 14 | 2 | 0.143 | 16 | 2 | 0.125 |
| ENG-ARG SF | 15 | 3 | 0.200 | 12 | 1 | 0.083 |
| ESP-ARG Final | 25 | 8 | 0.320 | 21 | 0 | 0.000 |

## L2-matched fouls (claim attached to a concrete free kick)

- **SF01** `ENG-ARG SF` 3' Enzo Fernández — carded=0 — Enzo early foul Anderson; Athletic only (n_sources=1, no)
- **F01** `ESP-ARG Final` 14' Alexis Mac Allister — carded=0 — Mac Allister on Olmo; FK yes card no (n_sources=7, yes_en_es_not_ar)
- **F02** `ESP-ARG Final` 18' Nicolás Tagliafico — carded=0 — Tagliafico on Yamal pattern 1H (n_sources=3, yes_en_es_not_ar)
- **F02** `ESP-ARG Final` 29' Nicolás Tagliafico — carded=0 — Tagliafico on Yamal pattern 1H (n_sources=3, yes_en_es_not_ar)
- **F02** `ESP-ARG Final` 36' Nicolás Tagliafico — carded=0 — Tagliafico on Yamal pattern 1H (n_sources=3, yes_en_es_not_ar)

## Design note

E01 (Egypt aggregate) is **not** foul-level L2: no outlet named
minute+player for each of the 13 uncarded ARG fouls. Those remain
`arg_uncarded_candidate=1` for video/panel coding.

Aggregate claim ≠ 13 independent multi-source under_carded events.

