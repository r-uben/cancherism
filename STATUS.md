# STATUS

Last updated: 2026-07-25

## Repo

- Local: `~/repos/other/cancherism`
- Remote: https://github.com/r-uben/cancherism
- Branch: `main` @ `e71009b` (clean, synced)

## Stage

**HF data + multi-country panels + path-wide minute narration live.**  
Write-up locked. L3 video still empty. Evidence stack usable for the
Werning-style foul-volume debate; next big gain is video or publication.

## Live drafts / artefacts

| Path | Role |
|------|------|
| `output/writeup_cancherism.md` | Locked public note |
| `output/multicountry_consensus_summary.md` | Country-family scorecard |
| `data/analysis/` | **Analysis-ready HF pack** |
| `data/analysis/DATA_DICTIONARY.md` | Schema + joins |
| `data/analysis/NARRATION_COVERAGE.md` | MbM inventory / gaps |
| `coding/SOURCE_PANEL.md` | Multi-country rules |
| `coding/L3_VIDEO_SHEET.md` | Video protocol (uncoded) |
| `coding/CODEBOOK.md` | Foul unit + claim classes |

### High-frequency tables (`data/analysis/`)

| File | Unit | Notes |
|------|------|-------|
| `hf_fouls.csv` | foul (~217) | Primary event stream |
| `hf_cards.csv` | card (~28) | |
| `hf_coverage_long.csv` | media hit | Multi-country panels + MbM |
| `hf_coverage_by_foul.csv` | foul × media | F01=6 families, F02 pattern=5 |
| `hf_narration_opta.csv` | Opta line (~996) | All 8 matches |
| `hf_narration_media.csv` | journalist line (~1.2k) | BBC×8 + Guardian×2 + ES/AR final |
| `hf_narration_long.csv` | stacked narration | |
| `hf_foul_narration_join.csv` | foul × nearby lines | 53/95 ARG uncarded have media nearby |
| `hf_minute_grid_path.csv` | match × minute | Full path |
| `hf_minute_grid_final.csv` | minute (final) | |

Rebuild:

```bash
python3 scripts/07_prepare_hf_data.py
python3 scripts/08_path_minute_narration.py
```

## Headline scorecard

| Incident | Level | Families under_carded | AR |
|----------|-------|----------------------:|----|
| **F01** Mac Allister ~14′ | foul | UK ES FR DE IN IT (6) | oppose/silent |
| **F02** Tagliafico–Yamal 1H | foul pattern | UK ES FR IN IT (5) | silent |
| **E01** Egypt R16 | match aggregate | EN + MENA_AR + DE + EG_FA | n/a |
| Collina | FIFA institutional | defends VAR/integrity | not independent |

## Recent decisions

- Unit of analysis = **foul** (`foul_id`), not match fouls/90.
- Multi-country scored by **country family**, not UK clone count; AR oppose counts as oppose.
- Collina coded as **FIFA defence**, not neutral audit.
- Minute narration: Opta dense path-wide; BBC all 8 matches; ES/AR live for **final only**.
- E01 stays **aggregate** (not 13 foul-level multi-source events).
- Repo lives under `~/repos/other/`, not `research/`.

## Outstanding TODOs

1. Human L3 video codes for F01 / F02 29′ (`l3_video_codes.csv`) — needs tape
2. ES/AR liveblogs for Egypt / SF / QF (if pages available)
3. More Guardian path URLs (many 404)
4. Optional Spain full-path L1 control
5. Optional publish write-up (blog / X)

## Next action

**Either** fill L3 for F01 (and F02 29′) from final video using `coding/L3_VIDEO_SHEET.md`,  
**or** publish/share `output/writeup_cancherism.md` as the locked claim.

Default if resuming analysis: L3 on F01.
