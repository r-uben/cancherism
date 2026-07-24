#!/usr/bin/env python3
"""
Build minute-level narration for EVERY Argentina WC2026 path match.

Layers:
  1. Opta/ESPN commentary (dense, already on disk) → structured event stream
  2. Journalist liveblogs (BBC etc.) when URL known → timed posts
  3. Join to hf_fouls for foul_id ↔ nearest narration lines

Outputs in data/analysis/:
  hf_narration_opta.csv          all Opta commentary lines, all matches
  hf_narration_media.csv         journalist MbM lines (sparse)
  hf_narration_long.csv          stacked (source_type, event_id, minute, text, flags)
  hf_minute_grid_path.csv        minute bins × match for fouls/cards/narration density
  hf_foul_narration_join.csv     each foul + nearby Opta lines + media hits

Also archives BBC live text under data/raw/liveblogs/path/.
"""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OPTA = ROOT / "data" / "raw" / "opta"
RAW_LB = ROOT / "data" / "raw" / "liveblogs" / "path"
OUT = ROOT / "data" / "analysis"
RAW_LB.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (research; cancherism)"}

# BBC live text pages (full ARG path — 2026-07-25)
BBC_LIVES = {
    "760433": "https://www.bbc.com/sport/football/live/ckg78g6pnyzt",  # ALG GS
    "760456": "https://www.bbc.com/sport/football/live/cze914jw558t",  # AUT GS
    "760483": "https://www.bbc.com/sport/football/live/c20ye67xgykt",  # JOR GS
    "760500": "https://www.bbc.com/sport/football/live/cvglenkkdlwt",  # CPV R32
    "760509": "https://www.bbc.com/sport/football/live/cdr4m2122lgt",  # EGY R16
    "760513": "https://www.bbc.com/sport/football/live/c4gyj35k3n3t",  # SUI QF
    "760515": "https://www.bbc.com/sport/football/live/c77yp11e4r6t",  # ENG SF
    "760517": "https://www.bbc.com/sport/football/live/cgk4ymn3n72t",  # Final
}

# Guardian liveblogs (JSON preferred)
GUARDIAN_LIVES = {
    "760456": "https://www.theguardian.com/football/live/2026/jun/22/argentina-v-austria-world-cup-2026-live",
    "760517": "https://www.theguardian.com/football/live/2026/jul/19/spain-v-argentina-world-cup-2026-final-live-updates",
}

MATCHES = {
    "760433": ("ARG-ALG GS", "2026-06-17"),
    "760456": ("ARG-AUT GS", "2026-06-22"),
    "760483": ("JOR-ARG GS", "2026-06-28"),
    "760500": ("ARG-CPV R32", "2026-07-03"),
    "760509": ("ARG-EGY R16", "2026-07-07"),
    "760513": ("ARG-SUI QF", "2026-07-12"),
    "760515": ("ENG-ARG SF", "2026-07-15"),
    "760517": ("ESP-ARG Final", "2026-07-19"),
}


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        print(f"  {path.name}: 0")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  {path.name}: {len(rows)}")


def parse_minute(raw: str) -> float | None:
    if not raw:
        return None
    raw = raw.replace("′", "'").strip()
    m = re.match(r"(\d+)\s*'\s*\+\s*(\d+)", raw)
    if m:
        return int(m.group(1)) + int(m.group(2)) / 100.0
    m = re.match(r"(\d+)", raw)
    return float(m.group(1)) if m else None


def flag_text(text: str) -> dict:
    t = text.lower()
    return {
        "flag_foul": int(bool(re.search(r"\bfoul\b|free kick|free-kick", t))),
        "flag_card": int(bool(re.search(r"yellow|red card|booked|second yellow", t))),
        "flag_goal": int(bool(re.search(r"\bgoal\b|scores?", t))),
        "flag_var": int(bool(re.search(r"\bvar\b", t))),
        "flag_penalty": int(bool(re.search(r"penalty", t))),
        "flag_sub": int(bool(re.search(r"substitution", t))),
        "flag_severity": int(
            bool(
                re.search(
                    r"bad foul|reckless|cynical|lenien|should have|nasty|late challenge",
                    t,
                )
            )
        ),
    }


def parse_opta_commentary(event_id: str) -> list[dict]:
    path = OPTA / f"commentary_{event_id}.txt"
    if not path.exists():
        return []
    match, date = MATCHES[event_id]
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        # format: "   14' | text" or " 90'+3' | text"
        m = re.match(r"^\s*([0-9+']+)\s*\|\s*(.*)$", line)
        if m:
            minute_raw = m.group(1).strip()
            text = m.group(2).strip()
        else:
            minute_raw = ""
            text = line
        mn = parse_minute(minute_raw)
        flags = flag_text(text)
        rows.append(
            {
                "narration_id": f"opta_{event_id}_{i}",
                "source_type": "opta",
                "source": "espn_opta",
                "country_family": "OFFICIAL",
                "event_id": event_id,
                "match": match,
                "date": date,
                "seq": i,
                "minute_raw": minute_raw,
                "minute_num": mn if mn is not None else "",
                "text": text,
                **flags,
            }
        )
    return rows


def fetch_guardian(event_id: str, url: str) -> list[dict]:
    """Guardian MbM via .json endpoint when available."""
    match, date = MATCHES[event_id]
    json_url = url if url.endswith(".json") else url.rstrip("/") + ".json"
    try:
        req = urllib.request.Request(json_url, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        print(f"  Guardian fail {event_id}: {e}")
        return []

    html = data.get("html") or ""
    (RAW_LB / f"guardian_{event_id}.json").write_text(
        json.dumps({"url": json_url, "html_len": len(html)}), encoding="utf-8"
    )
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    rows = []
    seq = 0
    for b in soup.select(".block"):
        title_el = b.select_one("h2")
        title = title_el.get_text(" ", strip=True) if title_el else ""
        body = b.get_text("\n", strip=True)
        body = re.sub(r"Share on Facebook.*", "", body, flags=re.S)
        text = f"{title}\n{body}".strip()
        if len(text) < 40:
            continue
        mins = []
        for m in re.finditer(r"(\d{1,3})\s*\+\s*(\d{1,2})", title + " " + body[:80]):
            mins.append(int(m.group(1)) + int(m.group(2)) / 100.0)
        for m in re.finditer(
            r"(?:^|[^\d])(\d{1,3})\s*(?:min(?:ute)?s?|'|′)", title + " " + body[:100], re.I
        ):
            v = int(m.group(1))
            if 0 <= v <= 130:
                mins.append(float(v))
        flags = flag_text(text)
        if not mins and not (
            flags["flag_foul"] or flags["flag_card"] or flags["flag_severity"]
        ):
            if not re.search(r"Argentina|foul|yellow|card|Messi", text, re.I):
                continue
            mins = [None]
        if not mins:
            mins = [None]
        for mn in mins:
            rows.append(
                {
                    "narration_id": f"guardian_{event_id}_{seq}",
                    "source_type": "media_mbm",
                    "source": "guardian",
                    "country_family": "UK",
                    "event_id": event_id,
                    "match": match,
                    "date": date,
                    "seq": seq,
                    "minute_raw": "" if mn is None else str(mn),
                    "minute_num": mn if mn is not None else "",
                    "text": text[:500],
                    **flags,
                }
            )
            seq += 1
    print(f"  Guardian {event_id}: {len(rows)} lines")
    return rows


def fetch_bbc(event_id: str, url: str) -> list[dict]:
    match, date = MATCHES[event_id]
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=40) as r:
            html = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  BBC fail {event_id}: {e}")
        return []

    (RAW_LB / f"bbc_{event_id}.html").write_text(html[:600000], encoding="utf-8")
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    text = soup.get_text("\n", strip=True)
    (RAW_LB / f"bbc_{event_id}.txt").write_text(text[:120000], encoding="utf-8")

    rows = []
    # Split into lines; keep those with minute tokens or foul/card language
    seq = 0
    for line in re.split(r"\n+", text):
        line = line.strip()
        if len(line) < 30:
            continue
        mins = []
        for m in re.finditer(r"(\d{1,3})\s*\+\s*(\d{1,2})", line):
            mins.append(int(m.group(1)) + int(m.group(2)) / 100.0)
        for m in re.finditer(
            r"(?:^|[^\d])(\d{1,3})\s*(?:min(?:ute)?s?|'|′|:)", line, re.I
        ):
            v = int(m.group(1))
            if 0 <= v <= 130:
                mins.append(float(v))
        flags = flag_text(line)
        if not mins and not (
            flags["flag_foul"] or flags["flag_card"] or flags["flag_severity"]
        ):
            # keep goal/VAR undated for density? skip pure nav
            if not (flags["flag_goal"] or flags["flag_var"]):
                if not re.search(
                    r"foul|yellow|card|Argentina|Spain|Egypt|England|Switzerland",
                    line,
                    re.I,
                ):
                    continue
        if not mins:
            mins = [None]
        for mn in mins:
            rows.append(
                {
                    "narration_id": f"bbc_{event_id}_{seq}",
                    "source_type": "media_mbm",
                    "source": "bbc",
                    "country_family": "UK",
                    "event_id": event_id,
                    "match": match,
                    "date": date,
                    "seq": seq,
                    "minute_raw": "" if mn is None else str(mn),
                    "minute_num": mn if mn is not None else "",
                    "text": line[:500],
                    **flags,
                }
            )
            seq += 1
    print(f"  BBC {event_id}: {len(rows)} lines")
    return rows


def join_fouls_narration(opta_rows: list[dict], media_rows: list[dict]) -> list[dict]:
    fouls = list(csv.DictReader((PROC / "foul_level.csv").open(encoding="utf-8")))
    opta_by = defaultdict(list)
    for r in opta_rows:
        if r["minute_num"] == "":
            continue
        opta_by[r["event_id"]].append(r)
    media_by = defaultdict(list)
    for r in media_rows:
        media_by[r["event_id"]].append(r)

    out = []
    for f in fouls:
        eid = f["event_id"]
        try:
            fm = float(f["minute_num"]) if f["minute_num"] != "" else None
        except ValueError:
            fm = None
        near_opta = []
        near_media = []
        if fm is not None:
            for r in opta_by.get(eid, []):
                try:
                    rm = float(r["minute_num"])
                except (TypeError, ValueError):
                    continue
                if abs(rm - fm) <= 1.0 and r.get("flag_foul") == 1:
                    near_opta.append(r)
            for r in media_by.get(eid, []):
                if r["minute_num"] == "":
                    # undated severity with player name
                    pl = (f.get("foul_player") or "").split()
                    sn = pl[-1] if pl else ""
                    if sn and len(sn) > 3 and sn.lower() in r["text"].lower():
                        if r.get("flag_foul") or r.get("flag_card") or r.get(
                            "flag_severity"
                        ):
                            near_media.append(r)
                    continue
                try:
                    rm = float(r["minute_num"])
                except (TypeError, ValueError):
                    continue
                if abs(rm - fm) <= 2.0:
                    near_media.append(r)

        out.append(
            {
                "foul_id": f["foul_id"],
                "event_id": eid,
                "match": f["match"],
                "minute_raw": f["minute_raw"],
                "minute_num": f["minute_num"],
                "foul_team": f["foul_team"],
                "is_argentina": f["is_argentina"],
                "foul_player": f["foul_player"],
                "carded": f["carded"],
                "n_opta_foul_lines_pm1": len(near_opta),
                "opta_snip": " || ".join(r["text"][:120] for r in near_opta[:3]),
                "n_media_lines_pm2": len(near_media),
                "media_sources": "|".join(sorted({r["source"] for r in near_media})),
                "media_snip": " || ".join(
                    f"[{r['source']}] {r['text'][:100]}" for r in near_media[:3]
                ),
                "has_media_narration": int(len(near_media) > 0),
            }
        )
    return out


def minute_grid_path(opta_rows, media_rows, fouls, cards) -> list[dict]:
    """Integer minute bins per match."""
    rows = []
    for eid, (match, date) in MATCHES.items():
        max_m = 120 if eid in ("760517", "760513", "760500") else 95
        f_e = [f for f in fouls if f["event_id"] == eid]
        c_e = [c for c in cards if c["event_id"] == eid]
        o_e = [r for r in opta_rows if r["event_id"] == eid]
        m_e = [r for r in media_rows if r["event_id"] == eid]

        def bin_m(x):
            try:
                return int(float(x))
            except (TypeError, ValueError):
                return None

        for m in range(0, max_m + 1):
            af = sum(
                1
                for f in f_e
                if bin_m(f.get("minute_num")) == m and f.get("is_argentina") in (1, "1")
            )
            of_ = sum(
                1
                for f in f_e
                if bin_m(f.get("minute_num")) == m and f.get("is_argentina") in (0, "0")
            )
            ac = sum(
                1
                for c in c_e
                if bin_m(c.get("minute_num")) == m and "Argentina" in (c.get("team") or "")
            )
            oc = sum(
                1
                for c in c_e
                if bin_m(c.get("minute_num")) == m
                and "Argentina" not in (c.get("team") or "")
            )
            on = sum(1 for r in o_e if bin_m(r.get("minute_num")) == m)
            ofl = sum(
                1
                for r in o_e
                if bin_m(r.get("minute_num")) == m and r.get("flag_foul") == 1
            )
            ocd = sum(
                1
                for r in o_e
                if bin_m(r.get("minute_num")) == m and r.get("flag_card") == 1
            )
            mn = sum(1 for r in m_e if bin_m(r.get("minute_num")) == m)
            rows.append(
                {
                    "event_id": eid,
                    "match": match,
                    "date": date,
                    "minute": m,
                    "arg_fouls": af,
                    "opp_fouls": of_,
                    "arg_cards": ac,
                    "opp_cards": oc,
                    "opta_lines": on,
                    "opta_foul_lines": ofl,
                    "opta_card_lines": ocd,
                    "media_lines": mn,
                    "any_activity": int(af + of_ + ac + oc + on + mn > 0),
                }
            )
    return rows


def main() -> None:
    print("Parsing Opta commentary (all matches)…")
    opta_all = []
    for eid in MATCHES:
        rows = parse_opta_commentary(eid)
        print(f"  Opta {eid} {MATCHES[eid][0]}: {len(rows)}")
        opta_all.extend(rows)
    write_csv(OUT / "hf_narration_opta.csv", opta_all)

    print("Fetching BBC lives (full path)…")
    media_all = []
    for eid, url in BBC_LIVES.items():
        media_all.extend(fetch_bbc(eid, url))
    print("Fetching Guardian lives…")
    for eid, url in GUARDIAN_LIVES.items():
        media_all.extend(fetch_guardian(eid, url))
    write_csv(OUT / "hf_narration_media.csv", media_all)

    # stacked long
    long_rows = []
    for r in opta_all:
        long_rows.append(r)
    for r in media_all:
        long_rows.append(r)
    write_csv(OUT / "hf_narration_long.csv", long_rows)

    # coverage inventory
    inv = []
    for eid, (match, date) in MATCHES.items():
        inv.append(
            {
                "event_id": eid,
                "match": match,
                "date": date,
                "opta_lines": sum(1 for r in opta_all if r["event_id"] == eid),
                "opta_foul_lines": sum(
                    1
                    for r in opta_all
                    if r["event_id"] == eid and r["flag_foul"] == 1
                ),
                "bbc_url": BBC_LIVES.get(eid, ""),
                "bbc_lines": sum(
                    1
                    for r in media_all
                    if r["event_id"] == eid and r["source"] == "bbc"
                ),
                "guardian_url": GUARDIAN_LIVES.get(eid, ""),
                "guardian_lines": sum(
                    1
                    for r in media_all
                    if r["event_id"] == eid and r["source"] == "guardian"
                ),
                "media_lines": sum(1 for r in media_all if r["event_id"] == eid),
                "has_bbc": int(eid in BBC_LIVES),
                "has_guardian": int(eid in GUARDIAN_LIVES),
                "notes": (
                    "BBC+Guardian"
                    if eid in BBC_LIVES and eid in GUARDIAN_LIVES
                    else ("BBC live" if eid in BBC_LIVES else "Opta only")
                ),
            }
        )
    write_csv(OUT / "hf_narration_inventory.csv", inv)

    fouls = list(csv.DictReader((PROC / "foul_level.csv").open(encoding="utf-8")))
    # cards with minute_num for grid
    cards_raw = list(
        csv.DictReader((PROC / "opta_cards_arg_path.csv").open(encoding="utf-8"))
    )
    cards = []
    for c in cards_raw:
        c = dict(c)
        c["minute_num"] = parse_minute(c.get("minute_raw") or "")
        cards.append(c)

    print("Joining fouls ↔ narration…")
    joins = join_fouls_narration(opta_all, media_all)
    write_csv(OUT / "hf_foul_narration_join.csv", joins)

    print("Minute grids (full path)…")
    grid = minute_grid_path(opta_all, media_all, fouls, cards)
    write_csv(OUT / "hf_minute_grid_path.csv", grid)

    # summary stats
    with_media = sum(1 for j in joins if j["has_media_narration"] == 1)
    arg_unc = [
        j
        for j in joins
        if j["is_argentina"] in (1, "1") and j["carded"] in (0, "0")
    ]
    arg_unc_media = sum(1 for j in arg_unc if j["has_media_narration"] == 1)
    print(
        f"\nFouls with nearby media narration: {with_media}/{len(joins)}\n"
        f"ARG uncarded with nearby media: {arg_unc_media}/{len(arg_unc)}\n"
        f"Opta narration lines total: {len(opta_all)}\n"
        f"Media narration lines total: {len(media_all)}"
    )

    # write coverage gaps note
    note = OUT / "NARRATION_COVERAGE.md"
    lines = [
        "# Minute-level narration coverage (ARG path)",
        "",
        "Agree: we want **narration at the minute for every match**, not only the final.",
        "",
        "## Layers",
        "",
        "1. **Opta/ESPN** — dense official stream (all 8 matches) → `hf_narration_opta.csv`",
        "2. **Journalist MbM** — BBC where URL known → `hf_narration_media.csv`",
        "3. **Join** — foul_id × nearby lines → `hf_foul_narration_join.csv`",
        "4. **Grid** — minute × match → `hf_minute_grid_path.csv`",
        "",
        "## Inventory",
        "",
        "| Match | Opta lines | BBC | Guardian |",
        "|-------|----------:|:---:|:--------:|",
    ]
    for r in inv:
        lines.append(
            f"| {r['match']} | {r['opta_lines']} | "
            f"{'yes' if r['has_bbc'] else '**no**'} | "
            f"{'yes' if r['has_guardian'] else 'no'} |"
        )
    lines += [
        "",
        f"- Opta total lines: **{len(opta_all)}**",
        f"- Media (BBC+Guardian) lines: **{len(media_all)}**",
        f"- ARG uncarded fouls with nearby media text: **{arg_unc_media}/{len(arg_unc)}**",
        "",
        "## Gaps",
        "",
        "- Guardian: only Austria + Final wired (other live URLs 404 or unknown)",
        "- ES/AR liveblogs: not yet wired",
        "- BBC now covers **all 8** ARG path matches",
        "",
        "Opta = dense foul clocks. BBC = UK journalist density path-wide.",
        "",
    ]
    note.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {note}")


if __name__ == "__main__":
    main()
