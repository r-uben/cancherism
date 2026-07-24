#!/usr/bin/env python3
"""Fetch ESPN/Opta summary commentary for Argentina WC2026 path; write foul CSVs."""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "opta"
PROC = ROOT / "data" / "processed"
UA = {"User-Agent": "Mozilla/5.0 (research; cancherism)"}

# Argentina path (ESPN event ids) — verified 2026-07-25
MATCHES = [
    (760433, "ARG-ALG GS", "2026-06-17"),
    (760456, "ARG-AUT GS", "2026-06-22"),
    (760483, "JOR-ARG GS", "2026-06-28"),
    (760500, "ARG-CPV R32", "2026-07-03"),
    (760509, "ARG-EGY R16", "2026-07-07"),
    (760513, "ARG-SUI QF", "2026-07-12"),
    (760515, "ENG-ARG SF", "2026-07-15"),
    (760517, "ESP-ARG Final", "2026-07-19"),
]


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode())


def fetch_summary(event_id: int) -> dict:
    url = (
        "https://site.api.espn.com/apis/site/v2/sports/soccer/"
        f"fifa.world/summary?event={event_id}"
    )
    return get_json(url)


def extract_fouls(summary: dict, event_id: int, label: str, date: str) -> list[dict]:
    """Dedup foul plays by play_id. foul_team = play['team'] (fouling side in this feed)."""
    by_id: dict[str, dict] = {}
    for it in summary.get("commentary") or []:
        play = it.get("play") or {}
        t = play.get("type") or {}
        if t.get("type") != "foul" and t.get("text") != "Foul":
            continue
        pid = play.get("id")
        if not pid or pid in by_id:
            continue
        text = it.get("text") or play.get("text") or ""
        ptext = play.get("text") or ""
        foul_team = (play.get("team") or {}).get("displayName")
        foul_player = None
        m = re.search(r"Foul by ([^(]+)\(", ptext) or re.search(
            r"Foul by ([^(]+)\(", text
        )
        if m:
            foul_player = m.group(1).strip()
        fk_player = fk_team = fk_zone = None
        m = re.search(
            r"([^(]+)\(([^)]+)\) wins a free kick(?: in the | on the )?(.+)?\.",
            text,
        )
        if m:
            fk_player = m.group(1).strip()
            fk_team = m.group(2).strip()
            fk_zone = (m.group(3) or "").strip().rstrip(".")
        by_id[pid] = {
            "event_id": event_id,
            "match": label,
            "date": date,
            "play_id": pid,
            "minute_raw": (play.get("clock") or {}).get("displayValue")
            or (it.get("time") or {}).get("displayValue"),
            "period": (play.get("period") or {}).get("number"),
            "foul_team": foul_team,
            "foul_player": foul_player,
            "fk_winner_player": fk_player,
            "fk_winner_team": fk_team,
            "fk_zone": fk_zone or "",
            "x": play.get("fieldPositionX"),
            "y": play.get("fieldPositionY"),
            "text": text,
            "play_text": ptext,
        }
    return list(by_id.values())


def extract_cards(summary: dict, event_id: int, label: str, date: str) -> list[dict]:
    rows = []
    for it in summary.get("commentary") or []:
        play = it.get("play") or {}
        t = play.get("type") or {}
        if t.get("type") not in ("yellow-card", "red-card"):
            continue
        text = it.get("text") or play.get("text") or ""
        player = team = None
        m = re.search(r"([A-Za-zÀ-ú\.\'\- ]+?)\s*\(([^)]+)\)", text)
        if m:
            player = (
                m.group(1)
                .replace("Second yellow card to ", "")
                .replace("is shown the yellow card", "")
                .strip()
            )
            team = m.group(2).strip()
        rows.append(
            {
                "event_id": event_id,
                "match": label,
                "date": date,
                "minute_raw": (play.get("clock") or {}).get("displayValue"),
                "card_type": t.get("type"),
                "player": player,
                "team": team,
                "text": text,
            }
        )
    return rows


def boxscore_discipline(summary: dict, event_id: int, label: str) -> list[dict]:
    rows = []
    for t in (summary.get("boxscore") or {}).get("teams") or []:
        stats = {
            st["name"]: st.get("displayValue") for st in t.get("statistics") or []
        }

        def num(k):
            v = stats.get(k)
            if v is None:
                return None
            try:
                return float(str(v).replace("%", ""))
            except ValueError:
                return None

        rows.append(
            {
                "event_id": event_id,
                "match": label,
                "team": (t.get("team") or {}).get("displayName"),
                "abbr": (t.get("team") or {}).get("abbreviation"),
                "fouls": num("foulsCommitted"),
                "yc": num("yellowCards"),
                "rc": num("redCards"),
                "poss": num("possessionPct"),
                "tackles": num("totalTackles"),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    PROC.mkdir(parents=True, exist_ok=True)
    all_fouls: list[dict] = []
    all_cards: list[dict] = []
    all_box: list[dict] = []

    for eid, label, date in MATCHES:
        print(f"fetch {eid} {label}")
        s = fetch_summary(eid)
        (RAW / f"summary_{eid}.json").write_text(
            json.dumps(s, ensure_ascii=False), encoding="utf-8"
        )
        # full commentary dump
        lines = []
        for it in s.get("commentary") or []:
            clock = (it.get("time") or {}).get("displayValue") or ""
            lines.append(f"{clock:>7} | {it.get('text')}")
        (RAW / f"commentary_{eid}.txt").write_text(
            "\n".join(lines), encoding="utf-8"
        )
        fouls = extract_fouls(s, eid, label, date)
        cards = extract_cards(s, eid, label, date)
        box = boxscore_discipline(s, eid, label)
        all_fouls.extend(fouls)
        all_cards.extend(cards)
        all_box.extend(box)
        c = Counter(f["foul_team"] for f in fouls)
        print(f"  fouls={dict(c)} cards={len(cards)}")
        time.sleep(0.35)

    write_csv(PROC / "opta_fouls_arg_path.csv", all_fouls)
    write_csv(PROC / "opta_cards_arg_path.csv", all_cards)
    write_csv(PROC / "boxscore_discipline_arg_path.csv", all_box)

    # per-match coding seeds for priority matches
    for eid, label, _ in MATCHES:
        if eid not in (760509, 760515, 760517):
            continue
        sub = [f for f in all_fouls if f["event_id"] == eid]
        out = ROOT / "coding" / f"seed_fouls_{eid}_{label.replace(' ', '_')}.csv"
        # add blank coding cols
        coded = []
        for f in sub:
            row = dict(f)
            row.update(
                {
                    "phase_counter_settled_other": "",
                    "own_half_y_n": "",
                    "intensity_1_3": "",
                    "recadito_y_n": "",
                    "uncalled_nearby_y_n": "",
                    "notes": "",
                }
            )
            coded.append(row)
        write_csv(out, coded)
        print("wrote", out)

    print(f"done: {len(all_fouls)} fouls, {len(all_cards)} cards → {PROC}")


if __name__ == "__main__":
    main()
