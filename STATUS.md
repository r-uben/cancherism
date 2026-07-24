# STATUS

Last updated: 2026-07-25

## Repo

- Local: `~/repos/other/cancherism`
- Remote: https://github.com/r-uben/cancherism

## Stage

**Foul-level + multi-country panels for F01/F02; Egypt E01 multi-country aggregate.**  
Primary unit remains the foul; country-family scoring in `SOURCE_PANEL.md`.

## Live artefacts

| Path | What |
|------|------|
| `data/processed/foul_level.csv` | One row per called foul |
| `data/processed/foul_mbm_alignment_final.csv` | Foul × journalist (final) |
| `coding/SOURCE_PANEL.md` | Multi-country rules |
| `data/processed/foul_source_panel_F01.csv` | F01 outlet panel |
| `data/processed/foul_source_panel_F02.csv` | F02 outlet panel |
| `data/processed/country_consensus_F01.csv` | F01 families |
| `data/processed/country_consensus_F02.csv` | F02 families |
| `data/processed/country_consensus_E01.csv` | Egypt aggregate families |
| `data/raw/articles/multicountry/` | FR/DE/UK/IN/AR/VN archives |
| `output/multicountry_consensus_summary.md` | Debate-ready scorecard |

## Key findings

1. **F01** Mac Allister–Olmo: under_carded in **UK+ES+FR+DE+IN**; **AR oppose/silent**.
2. **F02** Tagliafico–Yamal: under_carded in **UK+ES+FR+IN**; AR silent.
3. **E01** Egypt: EN + **Arabic MENA** (Alyaum soft on ARG cards) + EG FA; still **aggregate**, not 13 foul-level consensus rows.
4. Path-dependent card rates: soft JOR/EGY; not free pass late KO.

## Outstanding TODOs

1. ES/FR/DE press specifically on Egypt card counts
2. L3 video on F01 (+ F02 29′)
3. Optional Italy full archive
4. Auto-ingest multicountry into `06_foul_mbm_alignment.py`

## Next action

Video L3 on F01, or short public note / thread from multicountry scorecard.
