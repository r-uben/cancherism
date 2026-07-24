# Minute-level narration coverage (ARG path)

Agree: we want **narration at the minute for every match**, not only the final.

## Layers

1. **Opta/ESPN** — dense official stream (all 8 matches) → `hf_narration_opta.csv`
2. **Journalist MbM** — BBC where URL known → `hf_narration_media.csv`
3. **Join** — foul_id × nearby lines → `hf_foul_narration_join.csv`
4. **Grid** — minute × match → `hf_minute_grid_path.csv`

## Inventory

| Match | Opta | BBC | Guardian | ES | AR |
|-------|-----:|:---:|:--------:|---:|---:|
| ARG-ALG GS | 92 | yes | no | 0 | 0 |
| ARG-AUT GS | 109 | yes | yes | 0 | 0 |
| JOR-ARG GS | 98 | yes | no | 0 | 0 |
| ARG-CPV R32 | 140 | yes | no | 0 | 0 |
| ARG-EGY R16 | 116 | yes | no | 0 | 0 |
| ARG-SUI QF | 152 | yes | no | 0 | 0 |
| ENG-ARG SF | 116 | yes | no | 0 | 0 |
| ESP-ARG Final | 173 | yes | yes | 140 | 107 |

- Opta total lines: **996**
- Media lines (BBC+Guardian+ES+AR): **1183**
- ARG uncarded fouls with nearby media text: **53/95**

## Gaps

- Guardian: Austria + Final only
- ES/AR live: **final** (Marca EN, Olé, Clarín) — not full path
- BBC: **all 8** matches

Opta = dense foul clocks path-wide. Media = UK path-wide + ES/AR final.

