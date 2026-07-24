#!/usr/bin/env python3
"""Summarise L1 asymmetry + L2 master registry consensus counts."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
OUT = ROOT / "output" / "agreement_stats.md"


def load(name: str) -> list[dict]:
    with (PROC / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    summary = load("l1_match_summary.csv")
    master = load("master_incident_registry.csv")

    lines = ["# Agreement & asymmetry stats", "", "## L1 — cards per foul by match", ""]
    lines.append("| Match | ARG F | ARG C | ARG c/F | Opp F | Opp C | Opp c/F | Softer on ARG? |")
    lines.append("|-------|------:|------:|--------:|------:|------:|--------:|:---------------|")

    events = sorted({r["event_id"] for r in summary}, key=int)
    softer = []
    for eid in events:
        rows = [r for r in summary if r["event_id"] == eid]
        a = next(r for r in rows if r["is_argentina"] == "1")
        o = next(r for r in rows if r["is_argentina"] == "0")
        af, ac = int(a["opta_fouls"]), int(a["opta_cards"])
        of_, oc = int(o["opta_fouls"]), int(o["opta_cards"])
        ar = ac / af if af else 0
        orr = oc / of_ if of_ else 0
        # softer if ARG lower card rate and opp had enough fouls
        soft = ar < orr - 0.05 and of_ >= 5
        if soft:
            softer.append(a["match"])
        lines.append(
            f"| {a['match']} | {af} | {ac} | {ar:.3f} | {of_} | {oc} | {orr:.3f} | "
            f"{'YES' if soft else 'no'} |"
        )

    lines += [
        "",
        f"**Matches with clearly softer card rate on ARG (L1 only):** {', '.join(softer) or 'none'}",
        "",
        "Note: by the final and late KO, ARG often had *higher* card rates — the",
        "mid-tournament ‘most fouls fewest cards’ meme is path-dependent.",
        "",
        "## L2 — master registry consensus",
        "",
    ]

    cons = Counter(r["consensus_provisional"] for r in master)
    strength = Counter(r["evidence_strength"] for r in master)
    by_class = Counter(r["claim_class"] for r in master)
    strong = [
        r
        for r in master
        if r["evidence_strength"] == "strong"
        and r["consensus_provisional"].startswith("yes")
    ]

    lines.append("| consensus_provisional | n |")
    lines.append("|---|---:|")
    for k, v in cons.most_common():
        lines.append(f"| {k} | {v} |")

    lines += ["", "| claim_class | n |", "|---|---:|"]
    for k, v in by_class.most_common():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "### Strong multi-source favouritism / under-carding candidates",
        "",
    ]
    for r in strong:
        if r["claim_class"] in ("under_carded", "uncalled_foul", "spoiling_style"):
            lines.append(
                f"- **{r['incident_id']}** ({r['match']}): {r['description'][:100]} "
                f"[n≈{r['n_sources_total']}, {r['consensus_provisional']}]"
            )

    lines += [
        "",
        "## Exhaustiveness gap",
        "",
        "- L1: complete for ARG 8-match path.",
        "- L2: final EN+ES (+ Clarín AR reverse/partial); Egypt EN+FA strong;",
        "  England thin (SF01 single-source); group stage closed with no-hit logs.",
        "- AR media rarely agrees ARG was under-carded; often reverse bias claims.",
        "",
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text())


if __name__ == "__main__":
    main()
