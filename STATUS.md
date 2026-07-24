# STATUS

Last updated: 2026-07-25

## Repo

- Local: `~/repos/other/cancherism`
- Remote: https://github.com/r-uben/cancherism

## Stage

**Write-up locked** (`output/writeup_cancherism.md`).  
Evidence stack: foul-level Opta + multi-country F01/F02 + Egypt aggregate.  
L3 video still empty (needs human + tape).

## Headline scorecard

| Incident | Level | Families under_carded | AR stance |
|----------|-------|----------------------:|-----------|
| F01 Mac Allister 14′ | foul | UK ES FR DE IN IT (6) | oppose/silent |
| F02 Tagliafico–Yamal | foul pattern | UK ES FR IN IT (5) | silent |
| E01 Egypt | match aggregate | EN + MENA_AR + DE + EG_FA | n/a |
| FIFA Collina | institutional | defends VAR/integrity | not independent |

## High-frequency data pack

`data/analysis/` — rebuild with `python3 scripts/07_prepare_hf_data.py`

| File | Unit |
|------|------|
| `hf_fouls.csv` | Foul event |
| `hf_cards.csv` | Card event |
| `hf_coverage_long.csv` | Media hit (country × outlet) |
| `hf_coverage_by_foul.csv` | Media intensity per foul |
| `hf_minute_grid_final.csv` | Minute 0–120 final |
| `DATA_DICTIONARY.md` | Schema |

## Key paths

| Path | Role |
|------|------|
| **`output/writeup_cancherism.md`** | **Public-facing locked note** |
| `output/multicountry_consensus_summary.md` | Short scorecard |
| `data/processed/foul_level.csv` | Primary unit |
| `coding/SOURCE_PANEL.md` | Country-family rules |
| `coding/L3_VIDEO_SHEET.md` | Video protocol (uncoded) |

## Outstanding

1. Human L3 codes for F01 / F02 29′ (requires video)
2. Optional Spain path L1 control
3. Optional thread/blog publish from write-up

## Next action

L3 video coding when tape is available; otherwise publish/share write-up.
