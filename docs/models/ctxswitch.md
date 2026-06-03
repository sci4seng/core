---
title: ctxswitch
parent: Models
nav_order: 12
---

# ctxswitch
Cell: **universal** &middot; `verdict`: CONFIRM (gap -902.26) &middot; `verdict_n`: CONFIRM (gap -1584.07)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -1584.07 |
| `sd0_n` | 2121.64 |
| `sd1_n` | 2867.10 |
| `eps_n` | 742.57 |
| stress(inputs) | 156 / 200 CONFIRM |
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
| `family_member_coherence` | N/A — no lift rows |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Source
- SD model: `paper/sd.py::ctxswitch()`
- Audit row: `paper/outputs/full_audit.csv` (line for `ctxswitch`)

