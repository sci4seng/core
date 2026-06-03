---
title: successful
parent: Models
nav_order: 34
---

# successful

Cell: **process-conditional** &middot; `verdict`: CONFIRM (gap -1100.00) &middot; `verdict_n`: REFUTE (gap +10532.43)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| `verdict_n` | REFUTE |
| `gap_n` | +10532.43 |
| `sd0_n` | 28514.61 |
| `sd1_n` | 28923.46 |
| `eps_n` | 9980.11 |
| stress(inputs) | 47 / 200 CONFIRM |
| stress(params) | 200 / 200 CONFIRM |
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

- SD model: `paper/sd.py::successful()`
- Audit row: `paper/outputs/full_audit.csv` (line for `successful`)

