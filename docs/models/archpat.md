---
title: archpat
parent: Models
nav_order: 3
---

# archpat

Cell: **process-conditional** &middot; `verdict`: CONFIRM (gap +228.69) &middot; `verdict_n`: neutral (gap +15.56)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | +15.56 |
| `sd0_n` | 220.44 |
| `sd1_n` | 185.63 |
| `eps_n` | 77.15 |
| stress(inputs) | 34 / 200 CONFIRM |
| stress(params) | 122 / 200 CONFIRM |
| 2x2 cell | **process-conditional** |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| `boundary_adq` | PASS |
| `anomaly_check` | PASS |
| `extreme_eqn` | ERR:ValueError |
| `mr_zero_input` | PASS |
| `mr_monotone` | PASS |
| `mr_dt_halving` | PASS |
| `mr_bound_consist` | PASS |
| `mr_scale` | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| `param_plausibility` | PASS &middot; 4/4 in_range |
| `boundary_adq_data` | warn — all lifted values strictly inside [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 2 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `Legacy_n` | `Other_n` | `Patterned_n` | `modules` | `n_files` |
|---|---|---|---|---|---|
| ambari | 1890 | 4329 | 381 | ambari-serve | 6600 |
| helix | 384 | 1452 | 149 | helix-core,m | 1985 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Source

- SD model: `paper/sd.py::archpat()`
- Audit row: `paper/outputs/full_audit.csv` (line for `archpat`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_archpat.Rmd`

