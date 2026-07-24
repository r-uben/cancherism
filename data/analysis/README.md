# Analysis-ready high-frequency data

Build: `python3 scripts/07_prepare_hf_data.py`

| File | Unit | n |
|------|------|---|
| `hf_fouls.csv` | Called foul | ~217 |
| `hf_cards.csv` | Card | ~28 |
| `hf_coverage_long.csv` | Media claim hit | panel + MbM |
| `hf_coverage_by_foul.csv` | Foul × media intensity | 217 |
| `hf_minute_grid_final.csv` | Minute bin (final) | 121 |
| `hf_match_summary.csv` | Match | 8 |

See **DATA_DICTIONARY.md** for columns and joins.

Quick peek:

```bash
# multi-country fouls
python3 -c "import csv; r=list(csv.DictReader(open('hf_coverage_by_foul.csv')));
print([x for x in r if int(x['n_country_families'])>=3][:5])"
```

## Minute narration (full path)

```bash
python3 scripts/08_path_minute_narration.py
```

| File | Content |
|------|---------|
| `hf_narration_opta.csv` | Opta line stream, all 8 matches (~996) |
| `hf_narration_media.csv` | BBC MbM where URL known |
| `hf_narration_long.csv` | Both stacked |
| `hf_foul_narration_join.csv` | Every foul + nearby narration |
| `hf_minute_grid_path.csv` | Activity by minute × match |
| `NARRATION_COVERAGE.md` | Which matches lack journalist MbM |

Opta is dense for every match. Journalist live text is still sparse for group stage.
