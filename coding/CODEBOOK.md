# Codebook — foul / card claims

## Units (priority order)

1. **Foul (primary unit of analysis)** — one called free-kick foul in the Opta
   stream (`data/processed/foul_level.csv`, key `foul_id` = `event_id_play_id`).
   Everything else aggregates or tags these rows.
2. **Card link** — yellow/red matched to a foul (same player ±3′, or close
   same-team “bad foul” card). Field: `carded`, `card_link_type`.
3. **Journalist claim** — sentence/post asserting under-carding / uncalled /
   spoiling for a **specific** action (minute + player preferred).
4. **L2 incident** — claim cluster matched onto one or more foul rows
   (`l2_incident_ids` on `foul_level.csv`). Do **not** inflate one aggregate
   claim (e.g. Egypt “0 cards”) into N independent foul-level consensus events.
5. **Match aggregate** — secondary only (rates, path dependence).

### Canonical foul-level file

`data/processed/foul_level.csv` — build with `scripts/05_foul_level_table.py`.

## Claim classes

| Code | Name | Definition |
|------|------|------------|
| `under_carded` | Under-carded | Free kick given (or clearly a foul) but card not given / soft; writer says yellow or red should have been shown |
| `uncalled_foul` | Uncalled foul | Writer says free kick should have been given and was not |
| `over_carded` | Over-carded | Writer says card was too harsh (control for opposite bias) |
| `spoiling_style` | Spoiling style | Team-level or player-role narrative (time-wasting, tactical fouling pattern) without a single timestamp |
| `off_ball` | Off-ball / post-whistle | Elbow, punch, shove after play stopped or after full time |
| `other` | Other | Simulation claims, advantage disputes, etc. |

## Matching rules (claim → Opta / claim → claim)

Two records match if **all** hold:

1. Same match.
2. Minute within **±2** of each other (extra-time minutes kept as written, e.g. 106).
3. Same **offending team** (player match preferred; team-only still counts as weak match).
4. Same claim class family (`under_carded` with `under_carded`, etc.).

`spoiling_style` rows are **not** matched to single Opta fouls; they are
narrative tags at match level.

## Agreement scoring

- **Source hit:** outlet mentions the incident (binary).
- **Strength:** `strong` = names player + action + card should; `weak` = vague “leniency” only.
- **n_sources:** count of independent outlets with a hit.
- Provisional consensus if `n_sources ≥ 3` **and** at least two organisational families
  (e.g. newspaper + ex-ref, or EN + ES).

## Intensity / recadito (video layer only)

Not inferred from liveblogs alone.

| Field | Values |
|-------|--------|
| `phase` | `counter` / `settled` / `restart` / `other` / `unknown` |
| `own_half` | Y/N from attacking direction + x,y |
| `intensity` | 1 routine, 2 hard, 3 dangerous/reckless |
| `recadito` | Y if late/settling-scores after ball gone |

## Bias protocol

Always code **both** teams’ claims. Archive at least:

- 2× English-language (e.g. BBC, Guardian / Athletic)
- 1× Spanish (Marca / AS / SER)
- 1× Argentine (Olé / TyC / Clarín)

Report agreement **within** and **across** language camps separately.
