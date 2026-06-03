---
title: pareto
parent: Models
nav_order: 30
---

# pareto
Cell: **process-conditional** &middot; `verdict`: CONFIRM (gap -64.00) &middot; `verdict_n`: neutral (gap -47.15)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -47.15 |
| `sd0_n` | 1400.92 |
| `sd1_n` | 1370.12 |
| `eps_n` | 490.32 |
| stress(inputs) | 69 / 200 CONFIRM |
| stress(params) | 198 / 200 CONFIRM |
| 2x2 cell | **process-conditional** |

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
- SD model: `paper/sd.py::pareto()`
- Audit row: `paper/outputs/full_audit.csv` (line for `pareto`)

