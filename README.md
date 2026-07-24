# cancherism

Multi-source study of **tactical fouling, under-carding, and “dirty play” claims**
in Argentina’s 2026 World Cup path — built against naive “fouls per 90, *p* = 0.45”
exercises that only use **called** fouls.

*Cancherismo* (River Plate slang → broader Argentine football culture): street-smart,
edge-seeking competitiveness. This repo measures the statistical and journalistic
residue of that style — without treating official free-kick counts as ground truth.

## Layers

| Layer | Question | Status |
|-------|----------|--------|
| **L1 Opta** | Called fouls & cards, both teams, full ARG path | Complete |
| **L2 media** | Multi-outlet agreement on under-carding / uncalled / spoiling | Partial (final strong; Egypt medium) |
| **L3 video** | Intensity, recadito, true non-calls | Not started |

## Quick start

```bash
cd ~/repos/research/cancherism
python3 scripts/01_fetch_opta_path.py   # ESPN commentary → data/
python3 scripts/03_opta_match_tables.py
python3 scripts/04_agreement_stats.py
```

See `STATUS.md` for stage and next action. Methods: `coding/CODEBOOK.md`,
`docs/reference/EXHAUSTIVENESS.md`.

## Headline pilot findings

1. **F01** Final ~15′: Mac Allister on Olmo — free kick yes, yellow no; EN+ES multi-source consensus.
2. **E01** Egypt R16: ARG 13 fouls / 0 YC vs Egypt 11 / 4; formal Egyptian protest.
3. Full-path card rates are **path-dependent** — soft mid-tournament, not a free pass through the final.

## Layout

```
coding/          Codebook + seed sheets
data/raw/        Opta commentary, article quotes
data/processed/  CSVs (fouls, cards, incident matrices)
docs/            Notes, log, reference protocol
output/          Stats + exhaustiveness checklist
scripts/         Fetch + build pipeline
```

## Licence

Research code and tables: use freely with attribution. Third-party quotes remain
with their publishers; ESPN/Opta event text is for research archival only.
