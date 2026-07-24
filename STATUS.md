# STATUS

Last updated: 2026-07-25

## Repo

- Local: `~/repos/other/cancherism`
- Remote: https://github.com/r-uben/cancherism

## Stage

**Foul-level unit live** — `foul_level.csv` is the primary analysis table
(217 called fouls). L2 claims attach to foul rows where minute+player known;
aggregates (E01) stay tagged separately.

## Live artefacts

| Path | What |
|------|------|
| **`data/processed/foul_level.csv`** | **Primary: one row per called foul** |
| `data/processed/foul_mbm_alignment_final.csv` | Foul × minute × journalist (final) |
| `output/foul_mbm_alignment_summary.md` | Consensus coverage of uncarded fouls |
| `coding/SOURCE_PANEL.md` | Multi-country family rules |
| `data/processed/foul_source_panel_F01.csv` | F01 outlet×country panel |
| `data/processed/country_consensus_F01.csv` | F01 country-family rollup |
| `output/multicountry_consensus_summary.md` | International consensus write-up |
| `data/raw/articles/multicountry/` | FR/DE/UK/IN archives |
| `data/processed/foul_level_l2_matched.csv` | Fouls with L2 claim attached |
| `output/foul_level_summary.md` | Card rates + L2-matched list |
| `docs/reference/EXHAUSTIVENESS.md` | L1/L2/L3 protocol |
| `data/processed/l1_match_summary.csv` | Match aggregates (secondary) |
| `data/processed/master_incident_registry.csv` | Claim clusters |
| `data/processed/final_incident_source_matrix.csv` | Final L2 |
| `data/processed/egypt_incident_source_matrix.csv` | Egypt L2 |
| `data/processed/england_incident_source_matrix.csv` | England L2 |
| `output/agreement_stats.md` | Summary tables |

## Key findings (stable)

1. **F01** Mac Allister–Olmo final: **multi-country** under-carding (UK+ES+FR+DE+IN);
   **AR oppose/silent**.
2. **E01** Egypt: strongest L1 soft notebook + multi-source EN/FA protest.
3. Card rates **path-dependent** — soft mid-path (JOR, EGY); not free pass late.
4. Clarín: Vincic *permisivo*, but Enzo first Y “exagerada” (reverse of EN F04).

## Outstanding TODOs

1. Same country panel for **F02** Tagliafico + **E01** Egypt aggregate
2. Arabic / Egyptian press on Egypt R16
3. IT full archive (Tribuna 403) + L’Équipe if paywall allows
4. L3 video on F01
5. Expand foul×MbM script to ingest `multicountry/` automatically

## Next action

Multi-country panel for F02 and Egypt E01 (same SOURCE_PANEL rules).
