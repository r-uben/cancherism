#!/usr/bin/env python3
"""
Prepare high-frequency analysis datasets.

Outputs under data/analysis/ (clean, analysis-ready):

  hf_fouls.csv
      One row per called foul (primary HF unit). Clean types, keys, flags.

  hf_cards.csv
      One row per card event on the ARG path.

  hf_coverage_long.csv
      Long media coverage: one row per (foul_or_incident, country_family, outlet)
      for multi-country panels + final MbM severity hits.

  hf_coverage_by_foul.csv
      Wide-ish rollup: foul_id × n_country_families × family list × severity flags.

  hf_minute_grid_final.csv
      Minute grid for the final (0–120+): foul counts both teams, cards,
      media mention intensity (from MbM alignment + panels).

  hf_match_summary.csv
      Match-level aggregates derived only from hf_fouls/hf_cards (secondary).

See data/analysis/DATA_DICTIONARY.md.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "data" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows")


def fnum(x):
    if x is None or x == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None


def main() -> None:
    fouls = load(PROC / "foul_level.csv")
    cards = load(PROC / "opta_cards_arg_path.csv")
    mbm = load(PROC / "foul_mbm_alignment_final.csv")
    panels = []
    for name in ("foul_source_panel_F01.csv", "foul_source_panel_F02.csv"):
        p = PROC / name
        if p.exists():
            panels.extend(load(p))

    # --- hf_fouls ---
    hf_fouls = []
    for r in fouls:
        mn = fnum(r.get("minute_num"))
        hf_fouls.append(
            {
                "foul_id": r["foul_id"],
                "event_id": r["event_id"],
                "match": r["match"],
                "date": r.get("date"),
                "play_id": r.get("play_id"),
                "minute_raw": r.get("minute_raw"),
                "minute_num": mn if mn is not None else "",
                "period": r.get("period"),
                "foul_team": r.get("foul_team"),
                "is_argentina": int(r.get("is_argentina") or 0),
                "foul_player": r.get("foul_player") or "",
                "fk_winner_player": r.get("fk_winner_player") or "",
                "fk_zone": r.get("fk_zone") or "",
                "x": fnum(r.get("x")) if r.get("x") not in (None, "") else "",
                "y": fnum(r.get("y")) if r.get("y") not in (None, "") else "",
                "carded": int(r.get("carded") or 0),
                "card_type": r.get("card_type") or "",
                "card_minute": r.get("card_minute") or "",
                "l2_incident_ids": r.get("l2_incident_ids") or "",
                "l2_matched": int(r.get("l2_matched") or 0),
                "arg_uncarded_candidate": int(r.get("arg_uncarded_candidate") or 0),
                "text": (r.get("text") or "")[:200],
            }
        )
    write(OUT / "hf_fouls.csv", hf_fouls)

    # --- hf_cards ---
    hf_cards = []
    for r in cards:
        # parse minute
        raw = r.get("minute_raw") or ""
        m = re.match(r"(\d+)\s*'\s*\+\s*(\d+)", raw.replace("′", "'"))
        if m:
            mn = int(m.group(1)) + int(m.group(2)) / 100.0
        else:
            m2 = re.match(r"(\d+)", raw)
            mn = float(m2.group(1)) if m2 else ""
        hf_cards.append(
            {
                "event_id": r["event_id"],
                "match": r["match"],
                "date": r.get("date"),
                "minute_raw": raw,
                "minute_num": mn,
                "card_type": r.get("card_type"),
                "player": r.get("player") or "",
                "team": r.get("team") or "",
                "is_argentina": int("Argentina" in (r.get("team") or "")),
                "text": (r.get("text") or "")[:200],
            }
        )
    write(OUT / "hf_cards.csv", hf_cards)

    # --- hf_coverage_long (media) ---
    # From multi-country panels
    coverage = []
    for r in panels:
        # map to foul ids where possible
        incident = r.get("incident_id") or ""
        minute = r.get("minute") or r.get("minute_focus") or ""
        player = r.get("player") or ""
        coverage.append(
            {
                "coverage_id": f"{incident}_{r.get('country_family')}_{r.get('outlet', '')[:40]}",
                "incident_id": incident,
                "foul_id": "",  # filled below for F01/F02
                "event_id": "760517" if incident.startswith("F") else (
                    "760509" if incident.startswith("E") else ""
                ),
                "match": (
                    "ESP-ARG Final"
                    if incident.startswith("F")
                    else ("ARG-EGY R16" if incident.startswith("E") else "")
                ),
                "minute_label": minute,
                "player": player,
                "victim": r.get("victim") or "",
                "country_family": r.get("country_family") or "",
                "outlet": r.get("outlet") or "",
                "stance": r.get("stance") or "",
                "claim": r.get("claim") or "under_carded",
                "quote": (r.get("quote_or_paraphrase") or "")[:300],
                "source_file": r.get("archived_file") or "",
                "url": r.get("url") or "",
                "coverage_type": "multi_country_panel",
            }
        )

    # Link panel rows to foul_ids for final ARG fouls by player+minute
    foul_by_key = {}
    for f in hf_fouls:
        if f["event_id"] != "760517":
            continue
        sn = (f["foul_player"] or "").split()[-1].lower() if f["foul_player"] else ""
        mn = f["minute_num"]
        if sn and mn != "":
            foul_by_key.setdefault((sn, float(mn)), []).append(f["foul_id"])

    for c in coverage:
        if c["incident_id"] == "F01":
            # Mac Allister ~14-15
            for (sn, mn), ids in foul_by_key.items():
                if "allister" in sn or sn == "mac":
                    if 13 <= mn <= 16:
                        c["foul_id"] = ids[0]
                        break
            if not c["foul_id"]:
                # fallback name only
                for f in hf_fouls:
                    if f["event_id"] == "760517" and "Mac Allister" in f["foul_player"]:
                        if f["minute_num"] != "" and 13 <= float(f["minute_num"]) <= 16:
                            c["foul_id"] = f["foul_id"]
                            break
        elif c["incident_id"] == "F02":
            # Tagliafico pattern — attach to all 1H uncarded Tagliafico later in by_foul
            c["foul_id"] = "PATTERN_TAGLIAFICO_1H"

    # MbM final alignment as coverage rows (severity discussion)
    for r in mbm:
        if int(r.get("n_sources") or 0) < 1:
            continue
        if int(r.get("severity_discussion") or 0) != 1 and int(r.get("n_sources") or 0) < 2:
            continue
        for src in (r.get("sources") or "").split("|"):
            if not src:
                continue
            # map source tag to family
            fam = {
                "bbc": "UK",
                "guardian": "UK",
                "athletic": "UK",
                "marca_as": "ES",
                "marca": "ES",
                "as": "ES",
                "clarin": "AR",
                "quotes_dossier": "MIXED",
            }.get(src, src.upper()[:8])
            coverage.append(
                {
                    "coverage_id": f"mbm_{r['foul_id']}_{src}",
                    "incident_id": r.get("l2_prior") or "",
                    "foul_id": r["foul_id"],
                    "event_id": "760517",
                    "match": "ESP-ARG Final",
                    "minute_label": r.get("minute_raw") or "",
                    "player": r.get("foul_player") or "",
                    "victim": "",
                    "country_family": fam,
                    "outlet": src,
                    "stance": "severity_discussion" if r.get("severity_discussion") == "1" else "mention",
                    "claim": "under_carded" if r.get("carded") == "0" else "carded_context",
                    "quote": (r.get("claim_snippets") or "")[:300],
                    "source_file": "data/processed/foul_mbm_alignment_final.csv",
                    "url": "",
                    "coverage_type": "mbm_or_report_align",
                }
            )

    write(OUT / "hf_coverage_long.csv", coverage)

    # --- hf_coverage_by_foul ---
    by_foul: dict[str, dict] = {}
    for f in hf_fouls:
        by_foul[f["foul_id"]] = {
            "foul_id": f["foul_id"],
            "event_id": f["event_id"],
            "match": f["match"],
            "minute_num": f["minute_num"],
            "minute_raw": f["minute_raw"],
            "foul_player": f["foul_player"],
            "is_argentina": f["is_argentina"],
            "carded": f["carded"],
            "n_coverage_rows": 0,
            "n_country_families": 0,
            "country_families": "",
            "n_under_carded_stance": 0,
            "has_multi_country_ge3": 0,
            "panel_incidents": "",
        }

    # pattern attach F02
    tag_1h = [
        f["foul_id"]
        for f in hf_fouls
        if f["event_id"] == "760517"
        and "Tagliafico" in f["foul_player"]
        and f["minute_num"] != ""
        and float(f["minute_num"]) <= 45
        and f["carded"] == 0
    ]

    families_by_foul: dict[str, set] = defaultdict(set)
    under_by_foul: dict[str, int] = defaultdict(int)
    incidents_by_foul: dict[str, set] = defaultdict(set)
    counts_by_foul: dict[str, int] = defaultdict(int)

    def norm_family(fam: str) -> str:
        fam = (fam or "").strip()
        if not fam or fam == "MIXED":
            return ""
        if fam.startswith("UK"):
            return "UK"
        if fam.startswith("FR"):
            return "FR"
        if fam in ("US_EN", "UK_EN"):
            return "UK"
        if fam.startswith("MENA"):
            return "MENA_AR"
        return fam

    for c in coverage:
        fids = []
        if c["foul_id"] == "PATTERN_TAGLIAFICO_1H":
            fids = tag_1h
        elif c["foul_id"]:
            fids = [c["foul_id"]]
        stance = (c.get("stance") or "").lower()
        # supporting under-carding only (not oppose/silent)
        supports = (
            "under_carded" in stance
            or c.get("claim") == "under_carded"
            or stance in ("severity_discussion", "mention")
        ) and ("oppose" not in stance and "silent" not in stance)

        for fid in fids:
            if fid not in by_foul:
                continue
            counts_by_foul[fid] += 1
            fam = norm_family(c.get("country_family") or "")
            if fam and supports:
                families_by_foul[fid].add(fam)
            if supports and "under_carded" in stance or (
                supports and c.get("claim") == "under_carded"
            ):
                under_by_foul[fid] += 1
            if c.get("incident_id"):
                incidents_by_foul[fid].add(c["incident_id"])

    by_foul_rows = []
    for fid, row in by_foul.items():
        fams = sorted(families_by_foul.get(fid, []))
        # only count under_carded families from panel consensus style:
        # use family set size
        row["n_coverage_rows"] = counts_by_foul.get(fid, 0)
        row["n_country_families"] = len(fams)
        row["country_families"] = "|".join(fams)
        row["n_under_carded_stance"] = under_by_foul.get(fid, 0)
        row["has_multi_country_ge3"] = int(len(fams) >= 3)
        row["panel_incidents"] = "|".join(sorted(incidents_by_foul.get(fid, [])))
        by_foul_rows.append(row)

    # sort: multi-country first, then ARG uncarded
    by_foul_rows.sort(
        key=lambda r: (
            -r["has_multi_country_ge3"],
            -r["n_country_families"],
            -r["is_argentina"],
            -int(r["carded"] == 0),
            str(r["event_id"]),
            float(r["minute_num"]) if r["minute_num"] != "" else 999,
        )
    )
    write(OUT / "hf_coverage_by_foul.csv", by_foul_rows)

    # --- hf_minute_grid_final ---
    # minutes 0..120 integer + stoppage as .01*add for key events only
    # Use integer minute bins 0-120 for density
    final_fouls = [f for f in hf_fouls if f["event_id"] == "760517"]
    final_cards = [c for c in hf_cards if c["event_id"] == "760517"]

    def bin_minute(mn) -> int | None:
        if mn == "" or mn is None:
            return None
        try:
            return int(float(mn))  # 90.03 -> 90
        except ValueError:
            return None

    grid = []
    for m in range(0, 121):
        af = sum(
            1
            for f in final_fouls
            if bin_minute(f["minute_num"]) == m and f["is_argentina"] == 1
        )
        of_ = sum(
            1
            for f in final_fouls
            if bin_minute(f["minute_num"]) == m and f["is_argentina"] == 0
        )
        ac = sum(
            1
            for c in final_cards
            if bin_minute(c["minute_num"]) == m and c["is_argentina"] == 1
        )
        oc = sum(
            1
            for c in final_cards
            if bin_minute(c["minute_num"]) == m and c["is_argentina"] == 0
        )
        # coverage rows timed near this minute
        cov = sum(
            1
            for row in by_foul_rows
            if row["event_id"] == "760517"
            and row["minute_num"] != ""
            and bin_minute(row["minute_num"]) == m
            and row["n_country_families"] > 0
        )
        # media intensity: coverage rows in long for this minute label approx
        med = 0
        for c in coverage:
            if c["event_id"] != "760517":
                continue
            # extract first number from minute_label
            ml = c.get("minute_label") or ""
            mm = re.search(r"(\d{1,3})", str(ml))
            if mm and int(mm.group(1)) == m:
                med += 1
        grid.append(
            {
                "event_id": "760517",
                "match": "ESP-ARG Final",
                "minute": m,
                "arg_fouls": af,
                "opp_fouls": of_,
                "arg_cards": ac,
                "opp_cards": oc,
                "fouls_with_media_families": cov,
                "media_coverage_rows": med,
                "any_event": int(af + of_ + ac + oc + med > 0),
            }
        )
    write(OUT / "hf_minute_grid_final.csv", grid)

    # --- hf_match_summary from hf_fouls ---
    matches = {}
    for f in hf_fouls:
        m = f["match"]
        if m not in matches:
            matches[m] = {
                "event_id": f["event_id"],
                "match": m,
                "date": f.get("date"),
                "arg_fouls": 0,
                "opp_fouls": 0,
                "arg_carded_fouls": 0,
                "opp_carded_fouls": 0,
            }
        if f["is_argentina"]:
            matches[m]["arg_fouls"] += 1
            matches[m]["arg_carded_fouls"] += f["carded"]
        else:
            matches[m]["opp_fouls"] += 1
            matches[m]["opp_carded_fouls"] += f["carded"]
    ms = []
    for m, d in matches.items():
        d["arg_card_rate"] = (
            round(d["arg_carded_fouls"] / d["arg_fouls"], 4) if d["arg_fouls"] else ""
        )
        d["opp_card_rate"] = (
            round(d["opp_carded_fouls"] / d["opp_fouls"], 4) if d["opp_fouls"] else ""
        )
        ms.append(d)
    write(OUT / "hf_match_summary.csv", ms)

    # top multi-country fouls preview
    top = [r for r in by_foul_rows if r["n_country_families"] >= 2]
    print(f"\nFouls with ≥2 country families of media: {len(top)}")
    for r in top[:15]:
        print(
            f"  {r['match']:16} {str(r['minute_raw']):>6} {r['foul_player'][:20]:20} "
            f"fams={r['n_country_families']} {r['country_families']} carded={r['carded']}"
        )

    print(f"\nWrote analysis pack → {OUT}")


if __name__ == "__main__":
    main()
