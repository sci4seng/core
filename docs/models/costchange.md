---
title: costchange
parent: Models
nav_order: 11
---

# costchange
Cell: **universal** &middot; `verdict`: CONFIRM (gap -5165.13) &middot; `verdict_n`: CONFIRM (gap -187185.02)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -187185.02 |
| `sd0_n` | 245668.73 |
| `sd1_n` | 303956.33 |
| `eps_n` | 85984.05 |
| stress(inputs) | 183 / 200 CONFIRM |
| stress(params) | 200 / 200 CONFIRM |
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
| `param_plausibility` | N/A — no lift rows |
| `boundary_adq_data` | N/A — no lift rows |
| `calibrated_rq_rerun` | N/A — model not in calibrate.py |
| `family_member_coherence` | N/A — no lift rows |
| `behavior_reproduction` | not run — requires monthly historical CSV |

## Source
- SD model: `paper/sd.py::costchange()`
- Audit row: `paper/outputs/full_audit.csv` (line for `costchange`)

