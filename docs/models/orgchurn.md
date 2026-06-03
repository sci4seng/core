---
title: orgchurn
parent: Models
nav_order: 27
---

# orgchurn
Cell: **process-conditional** &middot; `verdict`: CONFIRM (gap -4504.53) &middot; `verdict_n`: neutral (gap -1025.21)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -1025.21 |
| `sd0_n` | 1700.55 |
| `sd1_n` | 1130.87 |
| `eps_n` | 595.19 |
| stress(inputs) | 38 / 200 CONFIRM |
| stress(params) | 197 / 200 CONFIRM |
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
- SD model: `paper/sd.py::orgchurn()`
- Audit row: `paper/outputs/full_audit.csv` (line for `orgchurn`)

