---
title: coordn2
parent: Models
nav_order: 10
---

# coordn2

Cell: **fragile** &middot; `verdict`: REFUTE (gap +860.00) &middot; `verdict_n`: neutral (gap +181.90)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | neutral |
| `gap_n` | +181.90 |
| `sd0_n` | 2498.37 |
| `sd1_n` | 2648.27 |
| `eps_n` | 874.43 |
| stress(inputs) | 0 / 200 CONFIRM |
| stress(params) | 91 / 200 CONFIRM |
| 2x2 cell | **fragile** |

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

- SD model: `paper/sd.py::coordn2()`
- Audit row: `paper/outputs/full_audit.csv` (line for `coordn2`)

