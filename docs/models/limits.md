---
title: limits
parent: Models
nav_order: 21
---

# limits
Cell: **process-conditional** &middot; `verdict`: CONFIRM (gap +600.00) &middot; `verdict_n`: neutral (gap +865.67)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | +865.67 |
| `sd0_n` | 23704.89 |
| `sd1_n` | 23696.07 |
| `eps_n` | 8296.71 |
| stress(inputs) | 36 / 200 CONFIRM |
| stress(params) | 181 / 200 CONFIRM |
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
| `param_plausibility` | N/A — no lift rows |
| `boundary_adq_data` | N/A — no lift rows |
| `calibrated_rq_rerun` | N/A — model not in calibrate.py |
| `family_member_coherence` | N/A — no lift rows |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Source
- SD model: `paper/sd.py::limits()`
- Audit row: `paper/outputs/full_audit.csv` (line for `limits`)

