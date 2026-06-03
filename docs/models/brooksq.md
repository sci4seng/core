---
title: brooksq
parent: Models
nav_order: 5
---

# brooksq
Cell: **fragile** &middot; `verdict`: CONFIRM (gap -45.91) &middot; `verdict_n`: neutral (gap -0.38)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -0.38 |
| `sd0_n` | 191.46 |
| `sd1_n` | 191.12 |
| `eps_n` | 67.01 |
| stress(inputs) | 6 / 200 CONFIRM |
| stress(params) | 80 / 200 CONFIRM |
| 2x2 cell | **fragile** |

## Tier 1 — Structural V&V (prudence)
| test | result |
|---|---|
| `boundary_adq` | FAIL |
| `anomaly_check` | PASS |
| `extreme_eqn` | ERR:ValueError |
| `mr_zero_input` | PASS |
| `mr_monotone` | PASS |
| `mr_dt_halving` | PASS |
| `mr_bound_consist` | FAIL |
| `mr_scale` | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)
| test | result |
|---|---|
| `param_plausibility` | **FAIL** &middot; 10/16 out_of_range, 0 at_boundary, 6 in_range |
| `boundary_adq_data` | PASS — lifted values reach or exceed declared [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 8 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project
| project | `brooks_tax_median` | `inj_rate_increase` | `inj_rate_post_med` | `inj_rate_pre_med` | `latency_days` |
|---|---|---|---|---|---|
| airflow | 0.3109919571 | -0.011111111 | 1.4444444444 | 1.4444444444 | 30 |
| ambari | 0.0294384057 | 0.0944444444 | 1.7277777777 | 1.9277777777 | 30 |
| camel | -0.144230769 | -0.188888888 | 0.4888888888 | 0.5222222222 | 30 |
| helix | 0.1126760563 | 0 | 0.0111111111 | 0.0111111111 | 30 |
| junit5 | 0.2222222222 | -0.011111111 | 0.2111111111 | 0.2222222222 | 30 |
| kaiaulu | -1.133928571 | 0.0333333333 | 0.0833333333 | 0.0166666666 | 30 |
| openssl | 0.1464646464 | -0.022222222 | 0.3444444444 | 0.3444444444 | 30 |
| tomcat | 0.0551530533 | -0.033333333 | 0.2 | 0.2166666666 | 30 |

_(showing first 5 of 10 metrics; full data in `paper/outputs/lifts.csv`)_

## Boundary violations
| project | param | lifted | lo | hi |
|---|---|---|---|---|
| helix | `leak_rate` | 0.5713 | 0 | 0.5 |
| junit5 | `leak_rate` | 0.6044 | 0 | 0.5 |
| ambari | `inj_rate` | 1.928 | 0 | 0.5 |
| ambari | `leak_rate` | 0.6971 | 0 | 0.5 |
| airflow | `inj_rate` | 1.444 | 0 | 0.5 |
| airflow | `leak_rate` | 0.8253 | 0 | 0.5 |
| openssl | `leak_rate` | 0.9307 | 0 | 0.5 |
| tomcat | `leak_rate` | 0.8761 | 0 | 0.5 |
| camel | `inj_rate` | 0.5222 | 0 | 0.5 |
| camel | `leak_rate` | 0.7121 | 0 | 0.5 |

## Source
- SD model: `paper/sd.py::brooksq()`
- Audit row: `paper/outputs/full_audit.csv` (line for `brooksq`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_brooksq.Rmd`

