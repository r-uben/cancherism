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
