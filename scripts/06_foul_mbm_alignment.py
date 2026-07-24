#!/usr/bin/env python3
"""
Foul × minute × journalist alignment (final first).

Design:
  1. Opta foul_level rows = clock + player (ground truth of *called* fouls).
  2. Journalist texts = MbM blocks (Guardian) + match reports (BBC, Athletic,
     Clarín, Marca/AS quotes file).
  3. Link a claim to a foul if:
       (A) timed claim: claim minute within ±2 of foul minute, AND claim has
           foul/card language, AND (player surname OR generic 'Argentina' foul
           talk only if sole ARG foul in window), OR
       (B) named undated claim: player surname in claim + severity language
           + claim implies early/1H/that player — attach to best-matching
           uncarded foul by that player in the implied window.

This is how multi-journalist *discussion* attaches to a concrete foul_id.
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
RAW = ROOT / "data" / "raw" / "liveblogs"
ART = ROOT / "data" / "raw" / "articles"
OUT = PROC / "foul_mbm_alignment_final.csv"
OUT_HITS = PROC / "foul_mbm_consensus_final.csv"
SUMMARY = ROOT / "output" / "foul_mbm_alignment_summary.md"

UA = {"User-Agent": "Mozilla/5.0 (research; cancherism)"}

SEV = re.compile(
    r"should have|yellow|book(?:ed|ing)?|reckless|lenien|nasty|late |"
    r"mereci[oó]|permisiv|clear yellow|cynical|studs|deliberate|"
    r"bad foul|for a foul|free[- ]kick|tarjeta|amonest",
    re.I,
)
FOULISH = re.compile(
    r"foul|yellow|book|card|hack|late |reckless|cynical|lenien|"
    r"tackle|clip|trip|spoiling|nasty|studs|elbow|tarjeta|falta|amarilla",
    re.I,
)
NOISE = re.compile(
    r"formaci[oó]n|lineup|line-up|confirm[oó] la formaci|XI:|starting",
    re.I,
)


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def parse_minutes(s: str) -> list[float]:
    if not s:
        return []
    mins: list[float] = []
    for m in re.finditer(r"(\d{1,3})\s*\+\s*(\d{1,2})", s):
        mins.append(int(m.group(1)) + int(m.group(2)) / 100.0)
    for m in re.finditer(r"(\d{1,3})(?:st|nd|rd|th)\s+minute", s, re.I):
        mins.append(float(m.group(1)))
    for m in re.finditer(r"(?:^|[^\d])(\d{1,3})\s*(?:min(?:ute)?s?|'|′)", s, re.I):
        v = int(m.group(1))
        if 0 <= v <= 130:
            mins.append(float(v))
    # de-dupe approx
    out = []
    for x in mins:
        if not any(abs(x - y) < 0.01 for y in out):
            out.append(x)
    return out


def surname(player: str) -> str:
    if not player:
        return ""
    parts = player.replace("'", "").split()
    return parts[-1] if parts else ""


def load_claims() -> list[dict]:
    """List of {source, minute|None, text, severity}."""
    claims: list[dict] = []

    # Guardian MbM
    try:
        g = json.loads(
            get(
                "https://www.theguardian.com/football/live/2026/jul/19/"
                "spain-v-argentina-world-cup-2026-final-live-updates.json"
            )
        )
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(g.get("html") or "", "html.parser")
        RAW.mkdir(parents=True, exist_ok=True)
        blocks = []
        for b in soup.select(".block"):
            title = b.select_one("h2")
            title_t = title.get_text(" ", strip=True) if title else ""
            body = b.get_text("\n", strip=True)
            body = re.sub(r"Share on Facebook.*", "", body, flags=re.S)
            text = f"{title_t}\n{body}"
            if not FOULISH.search(text):
                continue
            mins = parse_minutes(title_t) or parse_minutes(body[:150])
            # also line-level minutes
            if not mins:
                mins = parse_minutes(body)
            if mins:
                for m in mins:
                    claims.append(
                        {
                            "source": "guardian",
                            "minute": m,
                            "text": text[:500],
                            "severity": bool(SEV.search(text)),
                        }
                    )
            else:
                claims.append(
                    {
                        "source": "guardian",
                        "minute": None,
                        "text": text[:500],
                        "severity": bool(SEV.search(text)),
                    }
                )
            blocks.append(text[:800])
        (RAW / "guardian_final_foulish.txt").write_text(
            "\n\n---\n\n".join(blocks), encoding="utf-8"
        )
    except Exception as e:
        print("guardian fail", e)

    # File-based reports
    files = {
        "bbc": ART / "bbc_eng.txt",  # may not exist
        "bbc_final": ART / "bbc_mundo_final.txt",
        "athletic": ART / "athletic_eng.txt",
        "clarin": None,  # concat
        "quotes": ART / "quotes_final.md",
    }
    # BBC England file was sf; use quotes_final + any bbc
    texts: dict[str, str] = {}
    if (ART / "athletic_eng.txt").exists():
        texts["athletic"] = (ART / "athletic_eng.txt").read_text(encoding="utf-8")
    # BBC final report was in earlier scrape - check
    for p in ART.glob("bbc*.txt"):
        texts[f"bbc_{p.stem}"] = p.read_text(encoding="utf-8")
    clarin = []
    for p in ART.glob("clarin_*.txt"):
        clarin.append(p.read_text(encoding="utf-8"))
    if clarin:
        texts["clarin"] = "\n".join(clarin)
    if (ART / "quotes_final.md").exists():
        texts["quotes_dossier"] = (ART / "quotes_final.md").read_text(
            encoding="utf-8"
        )
    # marca/as only in quotes
    if (RAW / "bbc_final.txt").exists():
        texts["bbc_mbm"] = (RAW / "bbc_final.txt").read_text(encoding="utf-8")

    for src, text in texts.items():
        # split paragraphs
        for para in re.split(r"\n+", text):
            para = para.strip()
            if len(para) < 40 or NOISE.search(para):
                continue
            if not FOULISH.search(para) and not SEV.search(para):
                continue
            mins = parse_minutes(para)
            if mins:
                for m in mins:
                    claims.append(
                        {
                            "source": src,
                            "minute": m,
                            "text": para[:500],
                            "severity": bool(SEV.search(para)),
                        }
                    )
            else:
                claims.append(
                    {
                        "source": src,
                        "minute": None,
                        "text": para[:500],
                        "severity": bool(SEV.search(para)),
                    }
                )

    # Hand-curated high-precision undated named claims (from quotes dossier)
    curated = [
        {
            "source": "bbc_report",
            "minute": 14.0,
            "window": 2.0,
            "player": "Mac Allister",
            "text": "Mac Allister was late on Dani Olmo; Spain complained about Vincic's leniency",
            "severity": True,
        },
        {
            "source": "guardian_report",
            "minute": 14.0,
            "window": 2.0,
            "player": "Mac Allister",
            "text": "Mac Allister could have been booked for an early foul on Dani Olmo",
            "severity": True,
        },
        {
            "source": "athletic_scott",
            "minute": 15.0,
            "window": 2.0,
            "player": "Mac Allister",
            "text": "clear yellow card for reckless play; crossed the line in the 15th minute",
            "severity": True,
        },
        {
            "source": "as_marca",
            "minute": 14.0,
            "window": 3.0,
            "player": "Mac Allister",
            "text": "Mereció la amarilla / cleats first on Olmo",
            "severity": True,
        },
        {
            "source": "athletic_scott",
            "minute": None,
            "window": None,
            "player": "Tagliafico",
            "phase": "1H",
            "text": "Tagliafico could easily have received a yellow for deliberately bringing down Yamal / studs",
            "severity": True,
        },
        {
            "source": "marca",
            "minute": None,
            "window": None,
            "player": "Tagliafico",
            "phase": "1H",
            "text": "Tagliafico glue on Yamal; ref preferred not to book early",
            "severity": True,
        },
        {
            "source": "athletic",
            "minute": 52.0,
            "window": 5.0,
            "player": "Paredes",
            "text": "Paredes booked for cynical elbow into Rodri's back",
            "severity": True,
        },
        {
            "source": "guardian",
            "minute": None,
            "window": None,
            "player": "Paredes",
            "phase": "2H+",
            "text": "Paredes could have been sent off several times; post-whistle red",
            "severity": True,
        },
    ]
    for c in curated:
        claims.append(
            {
                "source": c["source"],
                "minute": c.get("minute"),
                "text": c["text"],
                "severity": c["severity"],
                "player_hint": c.get("player"),
                "window": c.get("window", 2.0),
                "phase": c.get("phase"),
                "curated": True,
            }
        )
    return claims


def main() -> None:
    claims = load_claims()
    print(f"claims loaded: {len(claims)}")

    fouls = [
        r
        for r in csv.DictReader((PROC / "foul_level.csv").open(encoding="utf-8"))
        if r["event_id"] == "760517" and r["is_argentina"] == "1"
    ]

    rows = []
    for f in fouls:
        try:
            fm = float(f["minute_num"]) if f["minute_num"] != "" else None
        except ValueError:
            fm = None
        sn = surname(f.get("foul_player") or "")
        player = f.get("foul_player") or ""

        matched = []
        for c in claims:
            text = c["text"]
            if NOISE.search(text):
                continue
            # player match
            ph = c.get("player_hint") or ""
            has_name = bool(sn and sn.lower() in text.lower()) or (
                ph and ph.lower() in (player.lower() + " " + sn.lower())
            )
            # if curated with player_hint, require that player
            if c.get("curated") and c.get("player_hint"):
                if c["player_hint"].lower() not in player.lower():
                    # Tagliafico phase match all his 1H fouls
                    if not (
                        c["player_hint"].lower() in player.lower()
                        or (sn and c["player_hint"].lower() == sn.lower())
                    ):
                        continue
                has_name = True

            cm = c.get("minute")
            window = c.get("window")
            if window is None:
                window = 2.0

            timed_ok = False
            if cm is not None and fm is not None:
                timed_ok = abs(cm - fm) <= float(window)

            phase = c.get("phase")
            phase_ok = False
            if phase == "1H" and fm is not None and fm <= 45:
                phase_ok = has_name
            if phase == "2H+" and fm is not None and fm >= 45:
                phase_ok = has_name

            # Link rules
            link = False
            if c.get("curated") and c.get("phase"):
                # phase-scoped pattern (e.g. Tagliafico 1H only)
                link = phase_ok and has_name
            elif timed_ok and has_name:
                link = True
            elif timed_ok and c.get("curated") and c.get("player_hint"):
                link = has_name  # curated timed claim
            elif cm is None and has_name and c.get("severity") and c.get("curated"):
                # undated curated named claim without phase → only if sole
                # early foul by that player (minute ≤ 20) to avoid spam
                link = fm is not None and fm <= 20
            elif phase_ok and c.get("severity"):
                link = True

            if link:
                matched.append(c)

        # unique sources
        sources = sorted({c["source"] for c in matched})
        # collapse bbc_* 
        norm_sources = set()
        for s in sources:
            if s.startswith("bbc"):
                norm_sources.add("bbc")
            elif s in ("as_marca", "marca"):
                norm_sources.add("marca_as")
            elif "athletic" in s or s == "athletic_scott":
                norm_sources.add("athletic")
            elif "guardian" in s:
                norm_sources.add("guardian")
            elif "clarin" in s:
                norm_sources.add("clarin")
            elif "quotes" in s:
                norm_sources.add("quotes_dossier")
            else:
                norm_sources.add(s)

        sev = any(c.get("severity") for c in matched)
        snips = []
        seen_t = set()
        for c in matched:
            t = c["text"][:200]
            if t in seen_t:
                continue
            seen_t.add(t)
            snips.append(f"[{c['source']}] {t}")

        rows.append(
            {
                "foul_id": f["foul_id"],
                "minute_raw": f["minute_raw"],
                "minute_num": f["minute_num"],
                "foul_player": player,
                "carded": f["carded"],
                "fk_zone": f.get("fk_zone"),
                "l2_prior": f.get("l2_incident_ids"),
                "n_sources": len(norm_sources),
                "sources": "|".join(sorted(norm_sources)),
                "severity_discussion": int(sev),
                "consensus_ge2": int(len(norm_sources) >= 2 and sev),
                "consensus_ge3": int(len(norm_sources) >= 3 and sev),
                "n_claim_snips": len(snips),
                "claim_snippets": " || ".join(snips[:6]),
            }
        )

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    hits = [r for r in rows if int(r["n_sources"]) >= 1]
    with OUT_HITS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(hits)

    # summary
    uncarded = [r for r in rows if r["carded"] == "0"]
    lines = [
        "# Foul × journalist alignment — ESP–ARG Final",
        "",
        "Unit: each **Argentina called foul** in the final, linked to journalist",
        "discussion at that minute (or named undated claim).",
        "",
        f"- ARG fouls in final: **{len(rows)}**",
        f"- Uncarded: **{len(uncarded)}**",
        f"- Uncarded with ≥1 source discussion: **{sum(1 for r in uncarded if int(r['n_sources'])>=1)}**",
        f"- Uncarded with ≥2 sources + severity language: **{sum(1 for r in uncarded if int(r['consensus_ge2'])==1)}**",
        f"- Uncarded with ≥3 sources + severity: **{sum(1 for r in uncarded if int(r['consensus_ge3'])==1)}**",
        "",
        "## Uncarded fouls with multi-source severity discussion",
        "",
        "| Min | Player | Sources | n | Snippets |",
        "|-----|--------|---------|--:|----------|",
    ]
    for r in uncarded:
        if int(r["consensus_ge2"]) != 1 and int(r["n_sources"]) < 2:
            continue
        if int(r["severity_discussion"]) != 1 and int(r["n_sources"]) < 2:
            continue
        sn = (r["claim_snippets"] or "")[:180].replace("|", "/")
        lines.append(
            f"| {r['minute_raw']} | {r['foul_player']} | {r['sources']} | "
            f"{r['n_sources']} | {sn} |"
        )

    lines += [
        "",
        "## All uncarded ARG fouls (discussion coverage)",
        "",
        "| Min | Player | Carded | n_src | severity | sources |",
        "|-----|--------|--------|------:|----------|---------|",
    ]
    for r in uncarded:
        lines.append(
            f"| {r['minute_raw']} | {r['foul_player'] or '—'} | {r['carded']} | "
            f"{r['n_sources']} | {r['severity_discussion']} | {r['sources'] or '—'} |"
        )

    lines += [
        "",
        "## Method caveat",
        "",
        "Live MbM (Guardian) rarely narrates every soft foul; most severity",
        "language is in **half-time/post-match reports**. Those attach via",
        "player name + implied timing (e.g. '15th minute', 'early foul').",
        "True second-by-second cross-blog agreement is sparse; Opta is denser",
        "than prose.",
        "",
    ]
    SUMMARY.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(SUMMARY.read_text())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
