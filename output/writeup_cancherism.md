# Cancherism: fouls, cards, and the wrong *p*-value

**Working note · 2026-07-25**  
Repo: [r-uben/cancherism](https://github.com/r-uben/cancherism)

After Spain beat Argentina in the 2026 World Cup final, a familiar argument appeared in economist circles: official foul rates show no meaningful difference between the finalists; therefore the claim that Argentina played “dirty” is not data-consistent. The sharpest version used tournament-wide fouls per scheduled minute and a Poisson rate test against Spain (*p* ≈ 0.45).

That exercise answers a real question. It is not the question people were asking.

---

## 1. Two estimands

| | A — Called foul volume | B — Soft punishment / dirty style |
|--|------------------------|-----------------------------------|
| **Object** | Free kicks awarded | Severity, cards not shown, non-calls, tactical fouling |
| **Data** | Opta/ESPN totals | Foul-level events + multi-country media + (later) video |
| **Typical test** | Fouls/90, Poisson | Under-carding on named fouls; path of cards/foul |

**A can be true while B is true.** Equal *called* foul rates are compatible with dirtier play plus softer refereeing, or with different styles of fouling. Official foul counts measure the referee’s notebook, not the pitch alone.

Failure to reject equal rates is also not equivalence. With roughly eight games per deep run, power is limited; *p* = 0.45 is mostly “we did not learn much about volume.”

---

## 2. Unit of analysis: the foul

Match aggregates hide the mechanism. The primary table is one row per **called foul** (`data/processed/foul_level.csv`): minute, player, team, pitch coordinates where available, whether a card is linked, whether multi-country claims attach.

Across Argentina’s eight matches: **217** called fouls (111 ARG, 106 opponents). Argentina ends with a *higher* path-wide card-link rate than opponents (~14% vs ~10%). That already kills the cartoon “never booked.” Softness is **path-dependent**:

- Soft on ARG (lower cards per foul): **Jordan (group), Egypt (R16)**  
- Not soft late: England SF, final (once cards start; Spain 21 fouls / 0 cards)

The viral mid-tournament meme “most fouls, fewest yellows” fits **through Egypt**, not the full path to the final.

---

## 3. Multi-country under-carding (named fouls)

Consensus is scored by **country family** (UK, ES, FR, DE, IT, IN, AR, …), not by counting five UK reprints. International under-carding requires severity claims in ≥3 families including ≥1 non-English. Argentine sources that deny the claim or allege reverse bias count as **oppose**, not missing data.

### F01 — Mac Allister on Olmo (~14–15′, final)

- **Opta:** free kick to Spain; **no yellow**.  
- **Stance under_carded:** UK, ES, FR, DE, IN, IT (Corriere: *meritano il giallo*).  
- **AR:** silent or reverse (Clarín does not call for a yellow here; Olé-side petition narrative runs the other way).

This is the cleanest foul-level exhibit: clocked free kick, no card, multi-country severity language.

### F02 — Tagliafico on Yamal (first-half pattern)

- **Opta:** several Tagliafico fouls (e.g. 18′, 29′, 36′) without early booking.  
- **Under_carded families:** UK, ES, FR, IN (Times of India pins **29′**), IT (Corriere pairs him with Mac Allister).  
- **AR:** silent.  
- Treated as a **pattern** mapped onto those foul rows, not three fully independent country dossiers.

### E01 — Egypt R16 (match aggregate only)

- **Opta:** ARG **13 fouls, 0 yellows**; Egypt **11 fouls, 4 yellows** (mostly deep stoppage after the winner).  
- **EN + Arabic MENA** (e.g. Alyaum: ref soft on Argentina’s roughness) + Egyptian FA protest + DE (Sportschau) report the bias/soft frame.  
- **FIFA refereeing chief Pierluigi Collina** defends integrity and specific VAR calls (below).  
- **Important:** E01 is **not** thirteen multi-source foul-level consensus events. Aggregate soft notebook ≠ N independent yellow-should claims.

---

## 4. Collina is FIFA

Collina chairs FIFA’s refereeing structure. After Egypt’s protest he:

- rejected unfounded bias / Messi-favouritism claims;  
- warned that integrity allegations can endanger officials;  
- defended overturning Egypt’s disallowed goal (“a foul is a foul” for VAR intervention);  
- defended no penalty before Argentina’s winner as “normal football contact.”

He did **not** re-litigate Mac Allister–Olmo or Tagliafico–Yamal for the public, and he did not address Argentina’s 13–0 foul/yellow line as a disciplinary pattern. In the source panel he is coded **FIFA / defends system**, not as an independent country that cancels multi-outlet under-carding on F01/F02.

---

## 5. What the evidence does and does not support

**Supported (provisional):**

1. Foul-volume equality with Spain does not refute “dirty / soft cards.” Wrong estimand.  
2. At least two **named final fouls** drew multi-country under-carding language while remaining uncarded (F01 strong; F02 strong as pattern).  
3. Egypt is the sharpest **notebook** asymmetry on Argentina’s path; multi-country protest framing exists; foul-by-foul international sourcing does not.  
4. Path dependence: soft early/mid knockout notebooks ≠ free pass through the final.

**Not supported:**

1. “All 95 uncarded Argentina fouls were dirty.” Most have no journalist trail.  
2. “FIFA fixed the tournament” as a proven claim from these tables.  
3. Collina as neutral adjudication.  
4. Spanish and Argentine media agreeing on under-carding of Argentina (they often do not).

---

## 6. Next work (epistemic order)

1. **L3 video** on F01 and F02 (29′): intensity, phase, recadito, card deserved — `coding/L3_VIDEO_SHEET.md`.  
2. Optional: Spain full-path foul-level control; FR-only Egypt card-count piece.  
3. Stop expanding silent Opta rows without sources.

---

## Key files

| File | Content |
|------|---------|
| `data/processed/foul_level.csv` | Primary unit |
| `data/processed/country_consensus_F01.csv` | F01 families |
| `data/processed/country_consensus_F02.csv` | F02 families |
| `data/processed/country_consensus_E01.csv` | Egypt aggregate |
| `coding/SOURCE_PANEL.md` | Multi-country rules |
| `output/multicountry_consensus_summary.md` | Short scorecard |

---

*Cancherismo* here is a label for studying edge-seeking competitive style in the data, not a moral verdict on a nation. The methodological point is narrower: **if the claim is soft cards and cynical fouls, count fouls and cards and sources — not only free kicks per ninety minutes.**
