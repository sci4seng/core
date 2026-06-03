---
title: congruence
parent: Models
nav_order: 8
---

# congruence
Cell: **universal** &middot; `verdict`: CONFIRM (gap -314.85) &middot; `verdict_n`: CONFIRM (gap -202.19)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -202.19 |
| `sd0_n` | 68.11 |
| `sd1_n` | 175.55 |
| `eps_n` | 23.84 |
| stress(inputs) | 196 / 200 CONFIRM |
| stress(params) | 196 / 200 CONFIRM |
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
| `param_plausibility` | **FAIL** &middot; 2/6 out_of_range, 0 at_boundary, 4 in_range |
| `boundary_adq_data` | PASS — lifted values reach or exceed declared [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 3 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project
| project | `Brokers_n` | `Clusters_n` | `largest_cluster` | `n_devs` | `n_devs_main` |
|---|---|---|---|---|---|
| airflow | 4 | 7 | 46 | 142 | 142 |
| helix | 3 | 4 | 33 | 77 | 77 |
| tomcat | 39 | 33 | 1361 | 3435 | 3295 |

_(showing first 5 of 9 metrics; full data in `paper/outputs/lifts.csv`)_

## Boundary violations
| project | param | lifted | lo | hi |
|---|---|---|---|---|
| tomcat | `Brokers` | 39 | 0 | 20 |
| tomcat | `Clusters` | 33 | 1 | 20 |

## Source
- SD model: `paper/sd.py::congruence()`
- Audit row: `paper/outputs/full_audit.csv` (line for `congruence`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_congruence.Rmd`

