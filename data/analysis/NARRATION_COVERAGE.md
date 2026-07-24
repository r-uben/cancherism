# Minute-level narration coverage (ARG path)

Agree: we want **narration at the minute for every match**, not only the final.

## Layers

1. **Opta/ESPN** — dense official stream (all 8 matches) → `hf_narration_opta.csv`
2. **Journalist MbM** — BBC where URL known → `hf_narration_media.csv`
3. **Join** — foul_id × nearby lines → `hf_foul_narration_join.csv`
4. **Grid** — minute × match → `hf_minute_grid_path.csv`

## Inventory

| Match | Opta lines | BBC |
|-------|----------:|:---:|
| ARG-ALG GS | 92 | **no** |
| ARG-AUT GS | 109 | **no** |
| JOR-ARG GS | 98 | **no** |
| ARG-CPV R32 | 140 | **no** |
| ARG-EGY R16 | 116 | yes |
| ARG-SUI QF | 152 | yes |
| ENG-ARG SF | 116 | yes |
| ESP-ARG Final | 173 | yes |

- Opta total lines: **996**
- BBC/media lines: **515**
- ARG uncarded fouls with nearby media text: **30/95**

## Gaps (need URLs)

- ARG–ALG GS, ARG–AUT GS, JOR–ARG GS, ARG–CPV R32: **Opta only**
- Guardian MbM for path matches: not yet wired
- ES/AR liveblogs: not yet wired

Opta is enough for **high-frequency foul clocks**. Journalist MbM is for
**discussion intensity** and under-carding language — still sparse outside big matches.

