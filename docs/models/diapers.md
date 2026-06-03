---
title: diapers
parent: Models
nav_order: 16
---

# diapers

Cell: **process-conditional** &middot; `verdict`: CONFIRM (gap -24.00) &middot; `verdict_n`: neutral (gap -19.60)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | -19.60 |
| `sd0_n` | 58.42 |
| `sd1_n` | 63.69 |
| `eps_n` | 20.45 |
| stress(inputs) | 84 / 200 CONFIRM |
| stress(params) | 200 / 200 CONFIRM |
| 2x2 cell | **process-conditional** |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| `boundary_adq` | PASS |
| `anomaly_check` | FAIL |
| `extreme_eqn` | ERR:ValueError |
| `mr_zero_input` | PASS |
| `mr_monotone` | PASS |
| `mr_dt_halving` | FAIL |
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

- SD model: `paper/sd.py::diapers()`
- Audit row: `paper/outputs/full_audit.csv` (line for `diapers`)

