---
title: dora
parent: Models
nav_order: 17
---

# dora
Cell: **universal** &middot; `verdict`: CONFIRM (gap -45.35) &middot; `verdict_n`: CONFIRM (gap -58.67)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -58.67 |
| `sd0_n` | 40.94 |
| `sd1_n` | 46.25 |
| `eps_n` | 14.33 |
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
| `param_plausibility` | PASS &middot; 23/23 in_range |
| `boundary_adq_data` | warn — all lifted values strictly inside [lo, hi] |
| `calibrated_rq_rerun` | CONFIRM — verdict stable (default=CONFIRM) |
| `family_member_coherence` | 8 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project
| project | `arrival_rate` | `batch_size` | `cfr` | `n_tags` | `rec_rate` |
|---|---|---|---|---|---|
| airflow | 3.3776818333 | 9.1058823529 | 0.2502936340 | 936 | 0.0061599038 |
| ambari | 1.2162553676 | 48.287878787 | 0.3413868842 | 133 | 0.0064919529 |
| camel | 2.8497232259 | 8.7610619469 | 0.0772727272 | 227 | 0.0092531488 |
| helix | 0.5885649000 | 73.906976744 | 0.0494021397 | 44 | 0.0113618834 |
| junit5 | 1.0734255618 | 38.383928571 | 0.2719237031 | 113 | 0.0137119895 |
| kaiaulu | 0.0932932348 | — | 0.2436974789 | 0 | 0.0882097554 |
| openssl | 2.3643658126 | 54.784722222 | 0.0512527992 | 433 | 0.0014577313 |
| tomcat | 2.8697458617 | 65.055793991 | 0.1616967937 | 234 | 0.0013478556 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Source
- SD model: `paper/sd.py::dora()`
- Audit row: `paper/outputs/full_audit.csv` (line for `dora`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_dora.Rmd`

