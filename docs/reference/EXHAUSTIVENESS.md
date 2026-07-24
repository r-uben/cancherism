# Exhaustiveness protocol

What “exhaustive” means in this project — and what it cannot mean.

## Three layers (do not mix)

| Layer | Population | Exhaustive when |
|-------|------------|-----------------|
| **L1 Opta called** | Every free-kick foul + card in ESPN stream, ARG’s 8 matches — **unit = foul** (`foul_level.csv`) | Full path scraped; both teams; card linked per foul |
| **L2 Media claims** | Claims matched **onto foul rows** (minute+player) when possible; aggregates tagged separately | Search protocol; EN+ES+AR; foul_id links where possible |
| **L3 Video truth** | Uncalled fouls + intensity on broadcast for candidate foul_ids | Dual-coded sample |

**Primary unit of analysis is the foul**, not the match. Match rates are
summaries of `foul_level.csv`. An aggregate claim (e.g. Egypt 0 cards) does
not count as N multi-source under_carded events unless each foul is sourced.


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
