#!/usr/bin/env python3
"""
Build the foul-level analysis table (unit of analysis = one called foul).

Each row is one Opta free-kick foul. We attach:
  - whether a card is linked to that foul (same player ±3', or same-team
    'bad foul' card within ±2' if player name matches card text)
  - L2 multi-source claim tags when a known incident maps to this foul
  - under_carded candidate flags for later review

This is the correct micro unit: match aggregates and 'spoiling' narratives
are secondary summaries of these rows.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
FOULS_IN = PROC / "opta_fouls_arg_path.csv"
CARDS_IN = PROC / "opta_cards_arg_path.csv"
OUT = PROC / "foul_level.csv"
OUT_MATCHED = PROC / "foul_level_l2_matched.csv"
SUMMARY = ROOT / "output" / "foul_level_summary.md"

# Hand-mapped L2 incidents → Opta play identifiers (minute + player + match)
# Filled where multi-source claims refer to a specific called foul.
L2_FOUL_MAP = [
    # Final F01 Mac Allister–Olmo ~14'
    {
        "incident_id": "F01",
        "event_id": "760517",
        "foul_player_contains": "Mac Allister",
        "minute_min": 13,
        "minute_max": 16,
        "claim_class": "under_carded",
        "n_sources": 7,
        "consensus": "yes_en_es_not_ar",
        "note": "Mac Allister on Olmo; FK yes card no",
    },
    # Final F02 Tagliafico — multiple; tag all 1H Tagliafico fouls without card
    {
        "incident_id": "F02",
        "event_id": "760517",
        "foul_player_contains": "Tagliafico",
        "minute_min": 1,
        "minute_max": 45,
        "claim_class": "under_carded",
        "n_sources": 3,
        "consensus": "yes_en_es_not_ar",
        "note": "Tagliafico on Yamal pattern 1H",
        "only_if_no_card": True,
    },
    # SF01 Enzo ~3' on Anderson
    {
        "incident_id": "SF01",
        "event_id": "760515",
        "foul_player_contains": "Enzo",
        "minute_min": 2,
        "minute_max": 5,
        "claim_class": "under_carded",
        "n_sources": 1,
        "consensus": "no",
        "note": "Enzo early foul Anderson; Athletic only",
    },
    # Final Enzo 84' foul after 82' yellow — not under_carded mapping
    # Egypt: no single foul has multi-source card-should claim with player+minute
    # E01 is aggregate-only; do not fake foul-level L2 for all 13
]


def parse_minute(raw: str | None) -> float | None:
    if not raw:
        return None
    raw = str(raw).replace("′", "'").strip()
    m = re.match(r"(\d+)\s*'\s*\+\s*(\d+)", raw)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 100.0
    m = re.match(r"(\d+)", raw)
    return float(m.group(1)) if m else None


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm_name(s: str | None) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^a-zà-ü\s]", "", s)
    # drop common particles noise
    return " ".join(s.split())


def names_match(a: str, b: str) -> bool:
    a, b = norm_name(a), norm_name(b)
    if not a or not b:
        return False
    if a == b:
        return True
    # surname last token
    ta, tb = a.split(), b.split()
    if ta[-1] == tb[-1] and len(ta[-1]) > 3:
        return True
    if ta[-1] in b or tb[-1] in a:
        return True
    return False


def main() -> None:
    fouls = load(FOULS_IN)
    cards = load(CARDS_IN)

    # index cards by event
    cards_by_event: dict[str, list] = {}
    for c in cards:
        c["_min"] = parse_minute(c.get("minute_raw"))
        cards_by_event.setdefault(c["event_id"], []).append(c)

    rows = []
    for i, f in enumerate(fouls):
        eid = f["event_id"]
        fm = parse_minute(f.get("minute_raw"))
        player = f.get("foul_player") or ""
        team = f.get("foul_team") or ""
        is_arg = 1 if "Argentina" in team else 0

        # link card
        linked = None
        link_type = ""
        for c in cards_by_event.get(eid, []):
            cm = c.get("_min")
            if fm is None or cm is None:
                continue
            if abs(cm - fm) > 3.0:
                continue
            # same player preferred
            if names_match(player, c.get("player") or ""):
                linked = c
                link_type = "player_pm3"
                break
            # card text mentions bad foul + same team + very close
            if abs(cm - fm) <= 1.5 and names_match(team, c.get("team") or ""):
                if "bad foul" in (c.get("text") or "").lower() or c.get(
                    "card_type"
                ) in ("yellow-card", "red-card"):
                    # only if player empty on foul or card team matches
                    if not linked:
                        linked = c
                        link_type = "team_close"

        carded = 1 if linked else 0
        card_type = linked.get("card_type") if linked else ""
        card_minute = linked.get("minute_raw") if linked else ""
        card_player = linked.get("player") if linked else ""

        # L2 map
        l2_ids = []
        l2_classes = []
        l2_n = []
        l2_cons = []
        l2_notes = []
        for m in L2_FOUL_MAP:
            if m["event_id"] != str(eid):
                continue
            if fm is None:
                continue
            if not (m["minute_min"] <= fm <= m["minute_max"]):
                continue
            if m["foul_player_contains"].lower() not in player.lower():
                continue
            if m.get("only_if_no_card") and carded:
                continue
            l2_ids.append(m["incident_id"])
            l2_classes.append(m["claim_class"])
            l2_n.append(str(m["n_sources"]))
            l2_cons.append(m["consensus"])
            l2_notes.append(m["note"])

        has_l2 = 1 if l2_ids else 0
        # candidate: ARG foul, not carded — for review panel
        under_card_cand = 1 if (is_arg and not carded) else 0

        foul_id = f"{eid}_{f.get('play_id')}"
        rows.append(
            {
                "foul_id": foul_id,
                "event_id": eid,
                "match": f.get("match"),
                "date": f.get("date"),
                "play_id": f.get("play_id"),
                "minute_raw": f.get("minute_raw"),
                "minute_num": fm if fm is not None else "",
                "period": f.get("period"),
                "foul_team": team,
                "is_argentina": is_arg,
                "foul_player": player,
                "fk_winner_player": f.get("fk_winner_player"),
                "fk_winner_team": f.get("fk_winner_team"),
                "fk_zone": f.get("fk_zone"),
                "x": f.get("x"),
                "y": f.get("y"),
                "text": f.get("text") or f.get("play_text"),
                "carded": carded,
                "card_link_type": link_type,
                "card_type": card_type,
                "card_minute": card_minute,
                "card_player": card_player,
                "l2_matched": has_l2,
                "l2_incident_ids": "|".join(l2_ids),
                "l2_claim_class": "|".join(l2_classes),
                "l2_n_sources": "|".join(l2_n),
                "l2_consensus": "|".join(l2_cons),
                "l2_note": "|".join(l2_notes),
                "arg_uncarded_candidate": under_card_cand,
            }
        )

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    matched = [r for r in rows if r["l2_matched"]]
    with OUT_MATCHED.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(matched)

    # summary
    n = len(rows)
    n_arg = sum(r["is_argentina"] for r in rows)
    n_opp = n - n_arg
    arg_carded = sum(1 for r in rows if r["is_argentina"] and r["carded"])
    opp_carded = sum(1 for r in rows if not r["is_argentina"] and r["carded"])
    arg_unc = sum(1 for r in rows if r["arg_uncarded_candidate"])
    l2m = len(matched)

    by_match = {}
    for r in rows:
        m = r["match"]
        by_match.setdefault(m, {"arg_f": 0, "arg_c": 0, "opp_f": 0, "opp_c": 0})
        if r["is_argentina"]:
            by_match[m]["arg_f"] += 1
            by_match[m]["arg_c"] += r["carded"]
        else:
            by_match[m]["opp_f"] += 1
            by_match[m]["opp_c"] += r["carded"]

    lines = [
        "# Foul-level unit of analysis",
        "",
        "Each row in `data/processed/foul_level.csv` is **one called foul**.",
        "",
        f"- Total fouls: **{n}** (ARG {n_arg}, opp {n_opp})",
        f"- Carded (linked): ARG **{arg_carded}/{n_arg}** ({100*arg_carded/n_arg:.1f}%), "
        f"opp **{opp_carded}/{n_opp}** ({100*opp_carded/n_opp:.1f}%)",
        f"- ARG uncarded candidates: **{arg_unc}**",
        f"- L2 multi-source matched to specific foul(s): **{l2m}** rows "
        f"({len(set(r['l2_incident_ids'] for r in matched))} incident ids)",
        "",
        "## Per match (foul-level card link rate)",
        "",
        "| Match | ARG fouls | ARG carded | ARG rate | Opp fouls | Opp carded | Opp rate |",
        "|-------|----------:|-----------:|---------:|----------:|-----------:|---------:|",
    ]
    for m, d in by_match.items():
        ar = d["arg_c"] / d["arg_f"] if d["arg_f"] else 0
        orr = d["opp_c"] / d["opp_f"] if d["opp_f"] else 0
        lines.append(
            f"| {m} | {d['arg_f']} | {d['arg_c']} | {ar:.3f} | {d['opp_f']} | {d['opp_c']} | {orr:.3f} |"
        )

    lines += [
        "",
        "## L2-matched fouls (claim attached to a concrete free kick)",
        "",
    ]
    for r in matched:
        lines.append(
            f"- **{r['l2_incident_ids']}** `{r['match']}` {r['minute_raw']} "
            f"{r['foul_player']} — carded={r['carded']} — {r['l2_note']} "
            f"(n_sources={r['l2_n_sources']}, {r['l2_consensus']})"
        )

    lines += [
        "",
        "## Design note",
        "",
        "E01 (Egypt aggregate) is **not** foul-level L2: no outlet named",
        "minute+player for each of the 13 uncarded ARG fouls. Those remain",
        "`arg_uncarded_candidate=1` for video/panel coding.",
        "",
        "Aggregate claim ≠ 13 independent multi-source under_carded events.",
        "",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SUMMARY.read_text())
    print(f"wrote {OUT} ({n} rows)")
    print(f"wrote {OUT_MATCHED} ({l2m} rows)")


if __name__ == "__main__":
    main()
