#!/usr/bin/env python3
"""
L1 exhaustiveness: per-match foul/card tables for ARG path.
Produces under-carding *candidates* from Opta alone (no journalist layer).
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = PROC / "l1_match_summary.csv"
CAND = PROC / "l1_undercard_candidates.csv"
FOULS = PROC / "opta_fouls_arg_path.csv"
CARDS = PROC / "opta_cards_arg_path.csv"
BOX = PROC / "boxscore_discipline_arg_path.csv"


def parse_minute(raw: str | None) -> float | None:
    if not raw:
        return None
    raw = str(raw).replace("′", "'").strip()
    # 90'+3' or 45'+2 or 76'
    m = re.match(r"(\d+)\s*'\s*\+\s*(\d+)", raw)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 100.0
    m = re.match(r"(\d+)", raw)
    if m:
        return float(m.group(1))
    return None


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    fouls = load_csv(FOULS)
    cards = load_csv(CARDS)
    box = load_csv(BOX)

    # group by event
    by_event_f: dict[str, list] = defaultdict(list)
    by_event_c: dict[str, list] = defaultdict(list)
    for r in fouls:
        by_event_f[r["event_id"]].append(r)
    for r in cards:
        by_event_c[r["event_id"]].append(r)

    # box by event+team
    box_map: dict[tuple[str, str], dict] = {}
    for r in box:
        box_map[(r["event_id"], r["team"])] = r

    summaries = []
    candidates = []

    for eid in sorted(by_event_f.keys(), key=int):
        fl = by_event_f[eid]
        cl = by_event_c.get(eid, [])
        match = fl[0]["match"]
        date = fl[0].get("date", "")

        teams = sorted({f["foul_team"] for f in fl if f.get("foul_team")})
        # identify Argentina vs opponent
        arg_name = next((t for t in teams if "Argentina" in t), None)
        opp_name = next((t for t in teams if t != arg_name), None)

        for team in teams:
            tf = [f for f in fl if f["foul_team"] == team]
            tc = [c for c in cl if c.get("team") == team]
            # also match team names loosely for cards
            if not tc:
                tc = [
                    c
                    for c in cl
                    if c.get("team")
                    and (
                        c["team"] == team
                        or team.startswith(c["team"])
                        or c["team"] in team
                    )
                ]
            n_f = len(tf)
            n_yc = sum(1 for c in tc if c.get("card_type") == "yellow-card")
            n_rc = sum(1 for c in tc if c.get("card_type") == "red-card")
            n_cards = n_yc + n_rc
            first_card_min = None
            mins = [parse_minute(c.get("minute_raw")) for c in tc]
            mins = [m for m in mins if m is not None]
            if mins:
                first_card_min = min(mins)
            fpc = n_f / n_cards if n_cards else None  # fouls per card
            b = box_map.get((eid, team)) or {}
            # prefer boxscore if present
            box_f = b.get("fouls")
            box_yc = b.get("yc")
            box_rc = b.get("rc")
            summaries.append(
                {
                    "event_id": eid,
                    "match": match,
                    "date": date,
                    "team": team,
                    "is_argentina": int(team == arg_name),
                    "opta_fouls": n_f,
                    "opta_yc": n_yc,
                    "opta_rc": n_rc,
                    "opta_cards": n_cards,
                    "fouls_per_card": round(fpc, 2) if fpc else "",
                    "first_card_minute": first_card_min if first_card_min is not None else "",
                    "box_fouls": box_f or "",
                    "box_yc": box_yc or "",
                    "box_rc": box_rc or "",
                    "poss": b.get("poss") or "",
                    "tackles": b.get("tackles") or "",
                }
            )

            # under-card candidates: each foul; flag if no card for same team within ±3 min
            # and no card for same player later in match before next foul... simple: no card same player entire match until after this foul by >0
            card_mins_team = sorted(mins)
            players_booked = {
                (c.get("player") or "").lower()
                for c in tc
                if c.get("card_type") in ("yellow-card", "red-card")
            }
            for f in tf:
                fm = parse_minute(f.get("minute_raw"))
                player = (f.get("foul_player") or "").strip()
                # nearby team card?
                nearby = False
                if fm is not None:
                    for cm in card_mins_team:
                        if abs(cm - fm) <= 3.0:
                            nearby = True
                            break
                player_booked_match = (
                    player.lower() in players_booked if player else False
                )
                # candidate if foul and not nearby card
                if not nearby:
                    candidates.append(
                        {
                            "event_id": eid,
                            "match": match,
                            "minute_raw": f.get("minute_raw"),
                            "minute_num": fm if fm is not None else "",
                            "foul_team": team,
                            "is_argentina": int(team == arg_name),
                            "foul_player": player,
                            "fk_zone": f.get("fk_zone"),
                            "x": f.get("x"),
                            "y": f.get("y"),
                            "nearby_card_pm3": int(nearby),
                            "player_booked_in_match": int(player_booked_match),
                            "text": f.get("text") or f.get("play_text"),
                            "play_id": f.get("play_id"),
                            "priority_review": int(
                                team == arg_name and not nearby and not player_booked_match
                            ),
                        }
                    )

        # match-level asymmetry row helper printed later
        if arg_name and opp_name:
            a = next(s for s in summaries if s["event_id"] == eid and s["team"] == arg_name)
            o = next(s for s in summaries if s["event_id"] == eid and s["team"] == opp_name)
            # attach ratio of card rates
            a_rate = a["opta_cards"] / a["opta_fouls"] if a["opta_fouls"] else None
            o_rate = o["opta_cards"] / o["opta_fouls"] if o["opta_fouls"] else None

    # write summaries
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        w.writerows(summaries)

    with CAND.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(candidates[0].keys()))
        w.writeheader()
        w.writerows(candidates)

    # print readable table
    print(f"{'Match':18} {'Team':14} {'F':>3} {'YC':>3} {'RC':>2} {'F/C':>6} {'1stY':>5}")
    for s in summaries:
        fpc = s["fouls_per_card"] if s["fouls_per_card"] != "" else "inf"
        fc = s["first_card_minute"] if s["first_card_minute"] != "" else "—"
        mark = "*" if s["is_argentina"] else " "
        print(
            f"{mark}{s['match']:17} {s['team'][:14]:14} {s['opta_fouls']:3} "
            f"{s['opta_yc']:3} {s['opta_rc']:2} {str(fpc):>6} {str(fc):>5}"
        )

    # asymmetry focus: ARG cards/foul vs opp
    print("\n=== Card rate asymmetry (cards/foul) ARG vs opp ===")
    print(f"{'Match':18} {'ARG c/F':>8} {'OPP c/F':>8} {'ARG F':>5} {'OPP F':>5} {'ARG C':>5} {'OPP C':>5}")
    events = sorted({s["event_id"] for s in summaries}, key=int)
    for eid in events:
        rows = [s for s in summaries if s["event_id"] == eid]
        a = next(s for s in rows if s["is_argentina"])
        o = next(s for s in rows if not s["is_argentina"])
        ar = a["opta_cards"] / a["opta_fouls"] if a["opta_fouls"] else 0
        or_ = o["opta_cards"] / o["opta_fouls"] if o["opta_fouls"] else 0
        flag = " << ARG softer" if ar + 1e-9 < or_ and o["opta_fouls"] >= 5 else ""
        flag = " << ARG harsher" if ar > or_ + 1e-9 and a["opta_cards"] > o["opta_cards"] else flag
        print(
            f"{a['match']:18} {ar:8.3f} {or_:8.3f} {a['opta_fouls']:5} {o['opta_fouls']:5} "
            f"{a['opta_cards']:5} {o['opta_cards']:5}{flag}"
        )

    pri = [c for c in candidates if c["priority_review"]]
    print(f"\nL1 under-card candidates (ARG foul, no nearby card, player never booked): {len(pri)}")
    print(f"wrote {OUT}")
    print(f"wrote {CAND} ({len(candidates)} rows)")


if __name__ == "__main__":
    main()
