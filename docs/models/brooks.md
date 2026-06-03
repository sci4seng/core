---
title: brooks
parent: Models
nav_order: 4
---

# brooks

Cell: **fragile** &middot; `verdict`: CONFIRM (gap -147.50) &middot; `verdict_n`: neutral (gap -0.58)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -0.58 |
| `sd0_n` | 188.32 |
| `sd1_n` | 186.41 |
| `eps_n` | 65.91 |
| stress(inputs) | 12 / 200 CONFIRM |
| stress(params) | 68 / 200 CONFIRM |
| 2x2 cell | **fragile** |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| `boundary_adq` | PASS |
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
| `param_plausibility` | N/A — no lift rows |
| `boundary_adq_data` | N/A — no lift rows |
| `calibrated_rq_rerun` | N/A — default=CONFIRM; no overridable params |
| `family_member_coherence` | 8 projects lifted (sign tally not auto-computed) |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Lift values per project

| project | `brooks_tax_mean` | `brooks_tax_median` | `n_hires` | `seed` | `window_days` |
|---|---|---|---|---|---|
| airflow | 0.3116968507 | 0.3109919571 | 1285 | 1 | 90 |
| ambari | -Inf | 0.0294384057 | 126 | 1 | 90 |
| camel | 0.0096826238 | -0.144230769 | 5 | 1 | 90 |
| helix | -Inf | 0.1126760563 | 65 | 1 | 90 |
| junit5 | 0.0308596574 | 0.2222222222 | 169 | 1 | 90 |
| kaiaulu | -2.646494708 | -1.133928571 | 6 | 1 | 90 |
| openssl | 0.0930948058 | 0.1464646464 | 1019 | 1 | 90 |
| tomcat | 0.0232660259 | 0.0551530533 | 50 | 1 | 90 |

## Source

- SD model: `paper/sd.py::brooks()`
- Audit row: `paper/outputs/full_audit.csv` (line for `brooks`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_brooks.Rmd`

