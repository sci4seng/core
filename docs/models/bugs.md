---
title: bugs
parent: Models
nav_order: 6
---

# bugs

Cell: **universal** &middot; `verdict`: CONFIRM (gap +38.06) &middot; `verdict_n`: CONFIRM (gap +22.16)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | +22.16 |
| `sd0_n` | 47.22 |
| `sd1_n` | 33.59 |
| `eps_n` | 16.53 |
| stress(inputs) | 130 / 200 CONFIRM |
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
| `param_plausibility` | N/A — no lift rows |
| `boundary_adq_data` | N/A — no lift rows |
| `calibrated_rq_rerun` | N/A — model not in calibrate.py |
| `family_member_coherence` | 3 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `fit_r2` | `gokumoto_a` | `gokumoto_b` | `n_bugs_resolved` | `n_issues_total` |
|---|---|---|---|---|---|
| camel | 0.5980 | 177.60 | 1.000e-07 | 185 | 500 |
| helix | 0.6162524156 | 244.8 | 1e-08 | — | 1879 |
| kaiaulu | 0.9098 | 26.40 | 1.000e-08 | — | — |

_(showing first 5 of 9 metrics; full data in `paper/outputs/lifts.csv`)_

## Source

- SD model: `paper/sd.py::bugs()`
- Audit row: `paper/outputs/full_audit.csv` (line for `bugs`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_bugs.Rmd`

