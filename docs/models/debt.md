---
title: debt
parent: Models
nav_order: 13
---

# debt

Cell: **universal** &middot; `verdict`: CONFIRM (gap -56.65) &middot; `verdict_n`: CONFIRM (gap -34.00)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -34.00 |
| `sd0_n` | 46.24 |
| `sd1_n` | 75.62 |
| `eps_n` | 16.19 |
| stress(inputs) | 200 / 200 CONFIRM |
| stress(params) | 200 / 200 CONFIRM |
| 2x2 cell | **universal** |

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
| `param_plausibility` | PASS &middot; 10/10 in_range |
| `boundary_adq_data` | warn — all lifted values strictly inside [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 5 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `born_rate_mean` | `born_rate_median` | `n_commits` | `n_refactor_events` | `pay_rate_mean` |
|---|---|---|---|---|---|
| ambari | 0.2614923114 | 0.2700270027 | 6374 | 66037 | 0.4765075729 |
| camel | 0.2492640660 | 0.2261245809 | 1980 | 208118 | 0.4134706147 |
| helix | 0.2605503273 | 0.25 | 3178 | 21945 | 0.5687748992 |
| junit5 | 0.1906922074 | 0.1949152542 | 4299 | 36204 | 0.5644367405 |
| tomcat | 0.1044314209 | 0.1 | 15158 | 45814 | 0.3718426062 |

_(showing first 5 of 8 metrics; full data in `paper/outputs/lifts.csv`)_

## Source

- SD model: `paper/sd.py::debt()`
- Audit row: `paper/outputs/full_audit.csv` (line for `debt`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_debt.Rmd`

