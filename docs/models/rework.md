---
title: rework
parent: Models
nav_order: 31
---

# rework

Cell: **universal** &middot; `verdict`: CONFIRM (gap -48.32) &middot; `verdict_n`: CONFIRM (gap -31.69)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -31.69 |
| `sd0_n` | 6.11 |
| `sd1_n` | 12.62 |
| `eps_n` | 2.14 |
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
| `param_plausibility` | PASS &middot; 8/8 in_range |
| `boundary_adq_data` | warn — all lifted values strictly inside [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 8 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `failrate_mean` | `failrate_median` | `n_windows` | `seed` | `window_days` |
|---|---|---|---|---|---|
| airflow | 0.3514683097 | 0.3976261127 | 29 | 1 | 90 |
| ambari | 0.2551348497 | 0.2740566889 | 50 | 1 | 90 |
| camel | 0.1916071097 | 0.1691829805 | 8 | 1 | 90 |
| helix | 0.1213372517 | 0.0188394652 | 60 | 1 | 90 |
| junit5 | 0.2981804820 | 0.2727272727 | 45 | 1 | 90 |
| kaiaulu | 0.3695665445 | 0.4107142857 | 9 | 1 | 90 |
| openssl | 0.0805659082 | 0.0705505279 | 112 | 1 | 90 |
| tomcat | 0.1935612146 | 0.1794258373 | 59 | 1 | 90 |

## Source

- SD model: `paper/sd.py::rework()`
- Audit row: `paper/outputs/full_audit.csv` (line for `rework`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_rework.Rmd`

