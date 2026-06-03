---
title: aidebt
parent: Models
nav_order: 1
---

# aidebt

Cell: **world-conditional** &middot; `verdict`: REFUTE (gap +6.50) &middot; `verdict_n`: CONFIRM (gap -17.23)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | CONFIRM |
| `gap_n` | -17.23 |
| `sd0_n` | 74.13 |
| `sd1_n` | 69.25 |
| `eps_n` | 25.94 |
| stress(inputs) | 183 / 200 CONFIRM |
| stress(params) | 74 / 200 CONFIRM |
| 2x2 cell | **world-conditional** |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| `boundary_adq` | FAIL |
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

- SD model: `paper/sd.py::aidebt()`
- Audit row: `paper/outputs/full_audit.csv` (line for `aidebt`)

