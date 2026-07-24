# Codebook — foul / card claims

## Units

- **Called foul (Opta row):** one free-kick award in ESPN `type=foul` stream
  (deduped by `play_id`).
- **Journalist claim:** one sentence or short post asserting a refereeing miss
  or a dirty-play characterisation of a specific action.
- **Incident:** a match event at approximately one minute, possibly linking
  one Opta foul to zero or more claims.

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
