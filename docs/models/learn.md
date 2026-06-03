---
title: learn
parent: Models
nav_order: 20
---

# learn

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -5.28) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -3.67)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -3.67 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 29.32 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 30.71 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 10.26 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 159 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 198 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| [`boundary_adq`](../glossary.md#boundary_adq "F&S 4/7: tmax=80 verdict still holds") | PASS |
| [`anomaly_check`](../glossary.md#anomaly_check "F&S behaviour-anomaly: hi inputs do not flip y sign") | PASS |
| [`extreme_eqn`](../glossary.md#extreme_eqn "F&S extreme-conditions: no NaN/Inf at lo/hi inputs") | ERR:ValueError |
| [`mr_zero_input`](../glossary.md#mr_zero_input "Chen MR3: ctrl=lo idempotent") | PASS |
| [`mr_monotone`](../glossary.md#mr_monotone "Chen MR1: y monotone in ctrl over 5 grid points") | FAIL |
| [`mr_dt_halving`](../glossary.md#mr_dt_halving "Chen MR8 / Sterman 6: y invariant to dt/2") | PASS |
| [`mr_bound_consist`](../glossary.md#mr_bound_consist "Chen MR9: clip vs reject agree") | PASS |
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | **FAIL** &middot; 3/38 out_of_range, 7 at_boundary, 28 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | PASS — lifted values reach or exceed declared [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 8 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `Jr_n` | `Sr_n` | `Tr_n` | `n_slices` | `promote_rate` |
|---|---|---|---|---|---|
| airflow | 1221 | 23 | 94 | 28 | 0.1338393894 |
| ambari | 80 | 18 | 36 | 58 | 0.2419103313 |
| camel | 9 | — | 5 | 7 | 0 |
| helix | 43 | 9 | 21 | 59 | 0.2385620915 |
| junit5 | 155 | 16 | 14 | 44 | 0.4252391127 |
| kaiaulu | 7 | 1 | — | 14 | 0 |
| openssl | 854 | 94 | 81 | 111 | 0 |
| tomcat | 37 | 18 | 7 | 58 | 0 |

_(showing first 5 of 8 metrics; full data in `paper/outputs/lifts.csv`)_

## Boundary violations

| project | param | lifted | lo | hi |
|---|---|---|---|---|
| junit5 | `Jr` | 155 | 0 | 100 |
| airflow | `Jr` | 1221 | 0 | 100 |
| openssl | `Jr` | 854 | 0 | 100 |

## Source

- SD model: `paper/sd.py::learn()`
- Audit row: `paper/outputs/full_audit.csv` (line for `learn`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_learn.Rmd`

