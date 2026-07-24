# L3 video coding sheet

Code **only** foul_ids already in the multi-country panels (or Egypt uncarded list).  
Two independent coders; resolve disagreements by third or mark `disagree`.

## Scale (no magic thresholds — ordinal only)

| Field | Values |
|-------|--------|
| `intensity` | 1 routine / 2 hard / 3 dangerous-reckless |
| `phase` | counter / settled / restart / other |
| `own_half` | Y/N (attacking direction from Opta x if known) |
| `recadito` | Y/N (late after ball gone / settling scores) |
| `card_deserved` | none / yellow / red |
| `confidence` | low / med / high |
| `notes` | free text |

## Priority foul_ids (final)

| Priority | Minute | Player | Incident | Multi-country |
|----------|--------|--------|----------|---------------|
| P1 | 14′ | Mac Allister | F01 on Olmo | UK ES FR DE IN IT |
| P2 | 29′ | Tagliafico | F02 on Yamal (TOI pin) | UK ES FR IN IT |
| P3 | 18′ / 36′ | Tagliafico | F02 pattern | pattern |

Lookup `play_id` / `foul_id` in `data/processed/foul_level.csv` where  
`event_id=760517` and player+minute match.

## Egypt uncarded (aggregate E01 only)

Do **not** claim multi-country per foul unless a source names minute+player.  
Optional video sample: first 5 ARG fouls (5′, 7′, 11′, 13′, 21′) for intensity distribution.

## Output

Append rows to `data/processed/l3_video_codes.csv` (template below).  
Empty until human-coded.

```csv
coder_id,foul_id,event_id,minute_raw,foul_player,intensity,phase,own_half,recadito,card_deserved,confidence,notes,date_coded
```
