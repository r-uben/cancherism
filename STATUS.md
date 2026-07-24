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

1. **F01** Mac Allister–Olmo final: EN+ES under-carding consensus; **not AR**.
2. **E01** Egypt: strongest L1 soft notebook + multi-source EN/FA protest.
3. Card rates **path-dependent** — soft mid-path (JOR, EGY); not free pass late.
4. Clarín: Vincic *permisivo*, but Enzo first Y “exagerada” (reverse of EN F04).

## Outstanding TODOs

1. Expand L2→foul maps (more incidents with minute+player → `L2_FOUL_MAP`)
2. Egypt: foul-by-foul video/panel for 13 uncarded ARG rows (E01 is aggregate only)
3. SF01 second source or video
4. L3 intensity/recadito on L2-matched foul_ids
5. Optional: Spain path same foul-level pipeline

## Next action

Video/panel pass on L2-matched foul_ids (F01, F02×3, SF01) + Egypt uncarded list.
