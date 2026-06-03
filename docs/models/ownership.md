---
title: ownership
parent: Models
nav_order: 29
---

# ownership

Cell: **universal** &middot; `verdict`: CONFIRM (gap -87.50) &middot; `verdict_n`: neutral (gap -12.11)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -12.11 |
| `sd0_n` | 1311.14 |
| `sd1_n` | 1309.91 |
| `eps_n` | 458.90 |
| stress(inputs) | 182 / 200 CONFIRM |
| stress(params) | 115 / 200 CONFIRM |
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

- SD model: `paper/sd.py::ownership()`
- Audit row: `paper/outputs/full_audit.csv` (line for `ownership`)

