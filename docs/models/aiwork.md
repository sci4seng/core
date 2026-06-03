---
title: aiwork
parent: Models
nav_order: 2
---

# aiwork
Cell: **universal** &middot; `verdict`: CONFIRM (gap -51.69) &middot; `verdict_n`: neutral (gap -50.54)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -50.54 |
| `sd0_n` | 263.62 |
| `sd1_n` | 252.89 |
| `eps_n` | 92.27 |
| stress(inputs) | 188 / 200 CONFIRM |
| stress(params) | 170 / 200 CONFIRM |
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
- SD model: `paper/sd.py::aiwork()`
- Audit row: `paper/outputs/full_audit.csv` (line for `aiwork`)

