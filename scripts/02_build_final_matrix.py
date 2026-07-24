#!/usr/bin/env python3
"""
Build pilot incident × source agreement matrix for ESP–ARG final.

Sources filled from hand-verified quotes collected 2026-07-25.
Spanish/Argentine columns start empty (to be filled) unless scrape finds hits.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "final_incident_source_matrix.csv"
CLAIMS = ROOT / "data" / "processed" / "final_claims_long.csv"

# Pilot incidents for ESP-ARG Final (event 760517)
# evidence_strength: strong = player+action+should-card; weak = vague; narrative = style
INCIDENTS = [
    {
        "incident_id": "F01",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "14-15",
        "period": 1,
        "offender_team": "Argentina",
        "offender_player": "Alexis Mac Allister",
        "victim_player": "Dani Olmo",
        "claim_class": "under_carded",
        "description": "Late/reckless challenge on Olmo; free kick given, no yellow",
        "opta_match": "yes",
        "opta_minute": "14'",
        "opta_note": "Foul by Alexis Mac Allister; Olmo wins FK defensive half; no card in stream",
        "bbc": 1,
        "guardian": 1,
        "athletic": 1,
        "mirror_exref_scott": 1,
        "liverpool_com_neville": 1,
        "marca": 1,
        "as": 1,
        "ole": 0,
        "tyc_or_clarin": "",
        "n_sources_en": 5,
        "n_sources_es": 2,
        "n_sources_ar": 0,
        "n_sources_total": 7,
        "consensus_provisional": "yes_cross_lang_en_es",
        "evidence_strength": "strong",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
    {
        "incident_id": "F02",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "1H various",
        "period": 1,
        "offender_team": "Argentina",
        "offender_player": "Nicolás Tagliafico",
        "victim_player": "Lamine Yamal",
        "claim_class": "under_carded",
        "description": "Studs / deliberate bring-downs on Yamal without early booking",
        "opta_match": "partial",
        "opta_minute": "multiple",
        "opta_note": "Several Tagliafico fouls in stream (e.g. 18', 29', 36'); no 1H yellow",
        "bbc": 0,
        "guardian": 0,
        "athletic": 1,
        "mirror_exref_scott": 1,
        "liverpool_com_neville": 0,
        "marca": 1,
        "as": 0,
        "ole": 0,
        "tyc_or_clarin": "",
        "n_sources_en": 2,
        "n_sources_es": 1,
        "n_sources_ar": 0,
        "n_sources_total": 3,
        "consensus_provisional": "yes_en_es",
        "evidence_strength": "strong",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
    {
        "incident_id": "F03",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "52+",
        "period": 2,
        "offender_team": "Argentina",
        "offender_player": "Leandro Paredes",
        "victim_player": "various (Olmo etc.)",
        "claim_class": "spoiling_style",
        "description": "Paredes as provocateur: shoves, barracking; later FT red for clash",
        "opta_match": "partial",
        "opta_minute": "52' YC; post-match red not in open play stream",
        "opta_note": "YC at 52'; post-whistle red covered in reports not Opta open-play",
        "bbc": 1,
        "guardian": 1,
        "athletic": 1,
        "mirror_exref_scott": 1,
        "liverpool_com_neville": 0,
        "marca": 1,
        "as": 0,
        "ole": 1,
        "tyc_or_clarin": "",
        "n_sources_en": 4,
        "n_sources_es": 1,
        "n_sources_ar": 1,
        "n_sources_total": 6,
        "consensus_provisional": "yes_cross_lang",
        "evidence_strength": "mixed",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
    {
        "incident_id": "F04",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "82",
        "period": 2,
        "offender_team": "Argentina",
        "offender_player": "Enzo Fernández",
        "victim_player": None,
        "claim_class": "under_carded",
        "description": "First yellow for dissent / sarcastic applause; lucky not worse",
        "opta_match": "yes",
        "opta_minute": "82'",
        "opta_note": "Yellow at 82'; second yellow + red 90'+3 for bad foul",
        "bbc": 0,
        "guardian": 0,
        "athletic": 1,
        "mirror_exref_scott": 0,
        "liverpool_com_neville": 0,
        "marca": 0,
        "as": 0,
        "ole": 0,
        "tyc_or_clarin": "",
        "n_sources_en": 1,
        "n_sources_es": 0,
        "n_sources_ar": 0,
        "n_sources_total": 1,
        "consensus_provisional": "no",
        "evidence_strength": "weak",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
    {
        "incident_id": "F05",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "match",
        "period": None,
        "offender_team": "Argentina",
        "offender_player": None,
        "victim_player": None,
        "claim_class": "spoiling_style",
        "description": "Team-level deliberate spoiling / kill the spectacle; ref leniency early",
        "opta_match": "n/a",
        "opta_minute": "",
        "opta_note": "Narrative; first YC only at 41'",
        "bbc": 1,
        "guardian": 1,
        "athletic": 1,
        "mirror_exref_scott": 1,
        "liverpool_com_neville": 0,
        "marca": 1,
        "as": 1,
        "ole": 0,
        "tyc_or_clarin": "",
        "n_sources_en": 4,
        "n_sources_es": 2,
        "n_sources_ar": 0,
        "n_sources_total": 6,
        "consensus_provisional": "yes_en_es_not_ar",
        "evidence_strength": "narrative",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
    {
        "incident_id": "F06",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "match",
        "period": None,
        "offender_team": "Spain",
        "offender_player": None,
        "victim_player": None,
        "claim_class": "under_carded",
        "description": "CONTROL: Spain 21 fouls, 0 cards — any multi-source under-carding claims?",
        "opta_match": "yes",
        "opta_minute": "aggregate",
        "opta_note": "Boxscore ESP 21 fouls 0 YC 0 RC",
        "bbc": 0,
        "guardian": 0,
        "athletic": 0,
        "mirror_exref_scott": 0,
        "liverpool_com_neville": 0,
        "marca": 0,
        "as": 0,
        "ole": 0,
        "tyc_or_clarin": "",
        "n_sources_en": 0,
        "n_sources_es": 0,
        "n_sources_ar": 0,
        "n_sources_total": 0,
        "consensus_provisional": "no",
        "evidence_strength": "control",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
    {
        "incident_id": "F07",
        "match": "ESP-ARG Final",
        "event_id": 760517,
        "minute_approx": "FT+",
        "period": None,
        "offender_team": "Argentina",
        "offender_player": "Leandro Paredes",
        "victim_player": "Eric García / Gavi",
        "claim_class": "off_ball",
        "description": "Post-whistle clash: throat grab / shove; red after full time",
        "opta_match": "no",
        "opta_minute": "after FT",
        "opta_note": "Not in open-play foul stream; widely reported; FIFA opened case",
        "bbc": 0,
        "guardian": 1,
        "athletic": 1,
        "mirror_exref_scott": 1,
        "liverpool_com_neville": 0,
        "marca": 1,
        "as": 1,
        "ole": 1,
        "tyc_or_clarin": "",
        "n_sources_en": 3,
        "n_sources_es": 2,
        "n_sources_ar": 1,
        "n_sources_total": 6,
        "consensus_provisional": "yes_cross_lang",
        "evidence_strength": "strong",
        "quotes_file": "data/raw/articles/quotes_final.md",
    },
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    keys = list(INCIDENTS[0].keys())
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(INCIDENTS)
    print(f"wrote {OUT} ({len(INCIDENTS)} incidents)")

    # long format for later stats
    source_cols = [
        "bbc",
        "guardian",
        "athletic",
        "mirror_exref_scott",
        "liverpool_com_neville",
        "marca",
        "as",
        "ole",
        "tyc_or_clarin",
    ]
    long_rows = []
    for inc in INCIDENTS:
        for src in source_cols:
            val = inc.get(src, "")
            if val == "" or val is None:
                hit = ""  # not coded
            else:
                hit = int(val)
            long_rows.append(
                {
                    "incident_id": inc["incident_id"],
                    "match": inc["match"],
                    "claim_class": inc["claim_class"],
                    "source": src,
                    "hit": hit,
                    "description": inc["description"],
                }
            )
    with CLAIMS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(long_rows[0].keys()))
        w.writeheader()
        w.writerows(long_rows)
    print(f"wrote {CLAIMS}")


if __name__ == "__main__":
    main()
