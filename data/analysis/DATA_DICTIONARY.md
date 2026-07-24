# High-frequency data dictionary

All analysis-ready files live in `data/analysis/`, built by:

```bash
python3 scripts/07_prepare_hf_data.py
```

Upstream (do not edit by hand for analysis): `data/processed/`.

---

## Design

| Frequency | File | Unit |
|-----------|------|------|
| **Foul event** | `hf_fouls.csv` | One called free-kick foul |
| **Card event** | `hf_cards.csv` | One yellow/red |
| **Media hit** | `hf_coverage_long.csv` | One outlet claim on a foul/incident |
| **Foul × media** | `hf_coverage_by_foul.csv` | Rollup of country families per foul |
| **Minute bin** | `hf_minute_grid_final.csv` | Integer minute 0–120 in the final |
| **Match** | `hf_match_summary.csv` | Secondary aggregate |

Primary research unit remains **`foul_id`**.

---

## `hf_fouls.csv`

| Column | Type | Description |
|--------|------|-------------|
| foul_id | string | `{event_id}_{play_id}` |
| event_id | string | ESPN match id |
| match | string | Label e.g. `ESP-ARG Final` |
| date | date | YYYY-MM-DD |
| play_id | string | Opta/ESPN play id |
| minute_raw | string | Display clock `14'`, `90'+3'` |
| minute_num | float | Sortable minute (`90.03` = 90+3) |
| period | int | 1, 2, ET periods if present |
| foul_team | string | Fouling team |
| is_argentina | 0/1 | |
| foul_player | string | |
| fk_zone | string | Free-kick zone text if any |
| x, y | float | Pitch coords if any |
| carded | 0/1 | Card linked to this foul |
| card_type | string | yellow-card / red-card / empty |
| l2_incident_ids | string | e.g. F01\|F02 |
| l2_matched | 0/1 | Prior L2 map flag |
| arg_uncarded_candidate | 0/1 | ARG foul without linked card |
| text | string | Short Opta text |

**n ≈ 217** (ARG path, both teams).

---

## `hf_cards.csv`

Card stream only (may not 1:1 match every carded foul).  
`minute_num`, `is_argentina`, `card_type`, `player`, `team`.

---

## `hf_coverage_long.csv`

High-frequency **media** layer (not Opta).

| Column | Description |
|--------|-------------|
| coverage_id | Unique row id |
| incident_id | F01, F02, E01, … |
| foul_id | Linked foul when known; `PATTERN_TAGLIAFICO_1H` for pattern |
| country_family | UK, ES, FR, DE, IT, IN, AR, MENA_AR, … |
| outlet | Named outlet |
| stance | under_carded / oppose / silent / severity_discussion / … |
| claim | under_carded / carded_context / … |
| quote | Short quote or paraphrase |
| coverage_type | multi_country_panel \| mbm_or_report_align |
| minute_label | Free-text minute from source |
| player, victim | |

**Use for:** counting families, building event studies around a foul minute, multi-country agreement.

Syndication rule: score **families** in `hf_coverage_by_foul`, not raw row counts.

---

## `hf_coverage_by_foul.csv`

| Column | Description |
|--------|-------------|
| foul_id | |
| n_coverage_rows | Raw media rows touching this foul |
| n_country_families | Distinct families (UK clones collapsed upstream when possible) |
| country_families | `UK\|ES\|FR\|…` |
| n_under_carded_stance | Rows with under_carded-type stance |
| has_multi_country_ge3 | 1 if ≥3 families |
| panel_incidents | F01, F02, … |

**Use for:** “which fouls have international media intensity?”

---

## `hf_minute_grid_final.csv`

Only **ESP–ARG Final** (`event_id=760517`).

| Column | Description |
|--------|-------------|
| minute | Integer 0–120 |
| arg_fouls, opp_fouls | Called fouls in that minute bin |
| arg_cards, opp_cards | Cards in bin |
| fouls_with_media_families | Fouls in bin with ≥1 media family |
| media_coverage_rows | Coverage long rows whose minute_label parses to this minute |
| any_event | 1 if any activity |

**Use for:** high-frequency plots (fouls vs media spikes over the match).

---

## `hf_match_summary.csv`

Derived only from `hf_fouls` card links. Secondary.

---

## Keys and joins

```text
hf_fouls.foul_id  ←→  hf_coverage_by_foul.foul_id
hf_fouls.foul_id  ←→  hf_coverage_long.foul_id  (when not PATTERN_*)
hf_fouls.event_id ←→  hf_cards.event_id
hf_fouls.event_id ←→  hf_minute_grid_final.event_id
```

---

## Minute-level narration (full ARG path)

Built by `python3 scripts/08_path_minute_narration.py`.

| File | Unit | Description |
|------|------|-------------|
| `hf_narration_opta.csv` | Opta commentary line | Dense official stream, **all 8 matches** (~996 lines) |
| `hf_narration_media.csv` | Journalist MbM line | BBC lives where URL known (~515) |
| `hf_narration_long.csv` | Stacked opta + media | Unified HF narration |
| `hf_narration_inventory.csv` | Match | Which sources exist per match |
| `hf_foul_narration_join.csv` | Foul | foul_id × nearby Opta foul lines × media |
| `hf_minute_grid_path.csv` | Match × minute | Fouls, cards, opta density, media density |
| `NARRATION_COVERAGE.md` | — | Gaps (GS often Opta-only) |

Narration flags: `flag_foul`, `flag_card`, `flag_goal`, `flag_var`, `flag_penalty`, `flag_severity`.

**BBC lives:** all 8 ARG path matches.  
**Guardian:** Austria + Final.  
**ES/AR final:** Marca EN, Marca ES, Olé, Clarín (local archives).

---

## Rebuild

```bash
# if Opta raw refreshed:
python3 scripts/01_fetch_opta_path.py
python3 scripts/05_foul_level_table.py
python3 scripts/06_foul_mbm_alignment.py   # final multi-country style
python3 scripts/07_prepare_hf_data.py
python3 scripts/08_path_minute_narration.py  # full-path minute narration
```

Panel CSVs under `data/processed/foul_source_panel_*.csv` are hand-curated inputs to 07.
