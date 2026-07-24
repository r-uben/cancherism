# Multi-country source panel

Consensus is scored **by country family**, not by number of UK clones.

## Country families (minimum for “international”)

| Code | Family | Example outlets |
|------|--------|-----------------|
| `UK` | United Kingdom | BBC, Guardian, Athletic UK, Sun, Liverpool.com, Daily Mail |
| `ES` | Spain | Marca, AS, SER |
| `AR` | Argentina | Olé, Clarín, TyC |
| `FR` | France | RMC/BFM, L’Équipe, France Football |
| `DE` | Germany / DACH | Welt, Kicker, fan.at |
| `IT` | Italy | Gazzetta, Corriere, Tribuna IT |
| `US` | United States | ESPN US, NYT/Athletic US |
| `IN` | India / Anglophone Asia | Times Now, other |
| `LATAM` | Other LatAm (non-AR) | optional |
| `REF` | Ex-ref / technical | Graham Scott, Law 5 blog |

## Rules

1. **Same wire / syndication** counts once (Yahoo reprint of Liverpool.com → still UK).
2. **Country consensus** on a foul = ≥1 outlet in that family asserts under-carding / yellow deserved (or explicitly denies).
3. **International multi-country consensus** on a foul requires severity claim in **≥3 country families**, including at least one **non-English** family (ES/FR/DE/IT/AR/…).
4. Argentine sources often **deny** under-carding of ARG or claim reverse bias — code as `AR=0` or `AR=oppose`, not missing.
5. Record raw quotes in `data/raw/articles/multicountry/` and dossier
   `data/raw/articles/quotes_multicountry_F01.md`.

## Primary foul for panel (pilot)

`foul_id` for Mac Allister 14′ final (F01) — densest international coverage.
