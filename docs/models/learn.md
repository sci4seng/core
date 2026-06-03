---
title: learn
parent: Models
nav_order: 20
---

# learn

Cell: **universal** &middot; `verdict`: CONFIRM (gap -5.28) &middot; `verdict_n`: neutral (gap -3.67)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -3.67 |
| `sd0_n` | 29.32 |
| `sd1_n` | 30.71 |
| `eps_n` | 10.26 |
| stress(inputs) | 159 / 200 CONFIRM |
| stress(params) | 198 / 200 CONFIRM |
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
| `mr_bound_consist` | PASS |
| `mr_scale` | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| `param_plausibility` | **FAIL** &middot; 3/38 out_of_range, 7 at_boundary, 28 in_range |
| `boundary_adq_data` | PASS — lifted values reach or exceed declared [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 8 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `Jr_n` | `Sr_n` | `Tr_n` | `n_slices` | `promote_rate` |
|---|---|---|---|---|---|
| airflow | 1221 | 23 | 94 | 28 | 0.1338393894 |
| ambari | 80 | 18 | 36 | 58 | 0.2419103313 |
| camel | 9 | — | 5 | 7 | 0 |
| helix | 43 | 9 | 21 | 59 | 0.2385620915 |
| junit5 | 155 | 16 | 14 | 44 | 0.4252391127 |
| kaiaulu | 7 | 1 | — | 14 | 0 |
| openssl | 854 | 94 | 81 | 111 | 0 |
| tomcat | 37 | 18 | 7 | 58 | 0 |

_(showing first 5 of 8 metrics; full data in `paper/outputs/lifts.csv`)_

## Boundary violations

| project | param | lifted | lo | hi |
|---|---|---|---|---|
| junit5 | `Jr` | 155 | 0 | 100 |
| airflow | `Jr` | 1221 | 0 | 100 |
| openssl | `Jr` | 854 | 0 | 100 |

## Source

- SD model: `paper/sd.py::learn()`
- Audit row: `paper/outputs/full_audit.csv` (line for `learn`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_learn.Rmd`

