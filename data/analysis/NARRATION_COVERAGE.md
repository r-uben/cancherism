# Minute-level narration coverage (ARG path)

Agree: we want **narration at the minute for every match**, not only the final.

## Layers

1. **Opta/ESPN** — dense official stream (all 8 matches) → `hf_narration_opta.csv`
2. **Journalist MbM** — BBC where URL known → `hf_narration_media.csv`
3. **Join** — foul_id × nearby lines → `hf_foul_narration_join.csv`
4. **Grid** — minute × match → `hf_minute_grid_path.csv`

## Inventory

| Match | Opta lines | BBC | Guardian |
|-------|----------:|:---:|:--------:|
| ARG-ALG GS | 92 | yes | no |
| ARG-AUT GS | 109 | yes | yes |
| JOR-ARG GS | 98 | yes | no |
| ARG-CPV R32 | 140 | yes | no |
| ARG-EGY R16 | 116 | yes | no |
| ARG-SUI QF | 152 | yes | no |
| ENG-ARG SF | 116 | yes | no |
| ESP-ARG Final | 173 | yes | yes |

- Opta total lines: **996**
- Media (BBC+Guardian) lines: **936**
- ARG uncarded fouls with nearby media text: **48/95**

## Gaps

- Guardian: only Austria + Final wired (other live URLs 404 or unknown)
- ES/AR liveblogs: not yet wired
- BBC now covers **all 8** ARG path matches

Opta = dense foul clocks. BBC = UK journalist density path-wide.

