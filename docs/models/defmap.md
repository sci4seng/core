---
title: defmap
parent: Models
nav_order: 14
---

# defmap

Cell: **universal** &middot; `verdict`: CONFIRM (gap -100.00) &middot; `verdict_n`: CONFIRM (gap -19.33)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -19.33 |
| `sd0_n` | 19.87 |
| `sd1_n` | 24.14 |
| `eps_n` | 6.95 |
| stress(inputs) | 156 / 200 CONFIRM |
| stress(params) | 163 / 200 CONFIRM |
| 2x2 cell | **universal** |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| `boundary_adq` | PASS |
| `anomaly_check` | PASS |
| `extreme_eqn` | ERR:ValueError |
| `mr_zero_input` | PASS |
| `mr_monotone` | FAIL |
| `mr_dt_halving` | PASS |
| `mr_bound_consist` | FAIL |
| `mr_scale` | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| `param_plausibility` | N/A — no lift rows |
| `boundary_adq_data` | N/A — no lift rows |
| `calibrated_rq_rerun` | N/A — default=CONFIRM; no overridable params |
| `family_member_coherence` | 8 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `n_phases` | `seed` | `total_caught` | `total_inject` | `total_leaked` |
|---|---|---|---|---|---|
| airflow | 190 | 1 | 640 | 7271 | 6631 |
| ambari | 81 | 1 | 1739 | 8384 | 6645 |
| camel | 2 | 1 | 465 | 477 | 12 |
| helix | 17 | 1 | 140 | 538 | 398 |
| junit5 | 94 | 1 | 1219 | 4940 | 3721 |
| kaiaulu | 1 | 1 | 0 | 56 | 0 |
| openssl | 217 | 1 | 243 | 3841 | 3598 |
| tomcat | 136 | 1 | 1017 | 5742 | 4725 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Source

- SD model: `paper/sd.py::defmap()`
- Audit row: `paper/outputs/full_audit.csv` (line for `defmap`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_defmap.Rmd`

