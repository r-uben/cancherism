# Exhaustiveness protocol

What “exhaustive” means in this project — and what it cannot mean.

## Three layers (do not mix)

| Layer | Population | Exhaustive when |
|-------|------------|-----------------|
| **L1 Opta called** | Every free-kick foul + card in ESPN stream, ARG’s 8 matches | Full path scraped; both teams; ratios computed |
| **L2 Media claims** | Every *published* claim of under-carding / uncalled / spoiling we can find for those matches | Search protocol run for each match; EN+ES+AR; archived quotes |
| **L3 Video truth** | Human-coded uncalled fouls on broadcast | Dual-coded sample of multi-agreed incidents (optional phase) |

L1 can be exhaustive with free data.  
L2 is exhaustive **relative to a search protocol**, not relative to “everything anyone thought.”  
L3 is never free-exhaustive without a full re-watch panel.

## L1 checklist (per match)

- [ ] Foul rows for both teams (deduped play_id)
- [ ] Card rows both teams
- [ ] Boxscore fouls/YC/RC/poss/tackles
- [ ] Fouls per card; first yellow minute
- [ ] List of fouls with no card within ±3′ for same player (soft candidates)

## L2 search protocol (per match)

Run for: BBC live/report, Guardian MbM or report, Athletic if any, Marca, AS, Olé, one more AR (TyC/Clarín/TN).

Query templates:

```
"{matchup}" (foul OR yellow OR card OR referee OR leniency OR spoiling OR dirty)
"{player}" (yellow OR amarilla OR should have been OR mereció)
```

Code every hit into master registry with source, minute, class, quote, URL.

Stop rule for a match: each of EN / ES / AR has either ≥1 article coded **or** explicit “no hit after search” log line.

## L3 (later)

Only for incidents with L2 n_sources ≥ 3. Code intensity, phase, recadito.

## Completeness status

Maintained in `STATUS.md` and `output/exhaustiveness_checklist.csv`.
