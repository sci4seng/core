---
title: linus
parent: Models
nav_order: 22
---

# linus
Cell: **universal** &middot; `verdict`: CONFIRM (gap -10.48) &middot; `verdict_n`: neutral (gap -120.82)
## Verdict (N=100 stats-grade)
| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -120.82 |
| `sd0_n` | 1187.74 |
| `sd1_n` | 1177.45 |
| `eps_n` | 415.71 |
| stress(inputs) | 111 / 200 CONFIRM |
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
- SD model: `paper/sd.py::linus()`
- Audit row: `paper/outputs/full_audit.csv` (line for `linus`)

