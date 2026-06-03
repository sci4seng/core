---
title: rework
parent: Models
nav_order: 31
---

# rework

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -48.32) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): CONFIRM ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -31.69)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | CONFIRM |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -31.69 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 6.11 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 12.62 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 2.14 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 200 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 200 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| [`dim_check`](../glossary.md#dim_check "Every init param exposes a well-formed unit string") | PASS |
| [`boundary_adq`](../glossary.md#boundary_adq "F&S 4/7: tmax=80 verdict still holds") | PASS |
| [`anomaly_check`](../glossary.md#anomaly_check "F&S behaviour-anomaly: hi inputs do not flip y sign") | PASS |
| [`extreme_eqn`](../glossary.md#extreme_eqn "F&S extreme-conditions: no NaN/Inf at lo/hi inputs") | ERR:ValueError |
| [`mr_zero_input`](../glossary.md#mr_zero_input "Chen MR3: ctrl=lo idempotent") | PASS |
| [`mr_monotone`](../glossary.md#mr_monotone "Chen MR1: y monotone in ctrl over 5 grid points") | PASS |
| [`mr_dt_halving`](../glossary.md#mr_dt_halving "Chen MR8 / Sterman 6: y invariant to dt/2") | PASS |
| [`mr_bound_consist`](../glossary.md#mr_bound_consist "Chen MR9: clip vs reject agree") | PASS |
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | PASS &middot; 8/8 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | warn — all lifted values strictly inside [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 8 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `failrate_mean` | `failrate_median` | `n_windows` | `seed` | `window_days` |
|---|---|---|---|---|---|
| airflow | 0.3514683097 | 0.3976261127 | 29 | 1 | 90 |
| ambari | 0.2551348497 | 0.2740566889 | 50 | 1 | 90 |
| camel | 0.1916071097 | 0.1691829805 | 8 | 1 | 90 |
| helix | 0.1213372517 | 0.0188394652 | 60 | 1 | 90 |
| junit5 | 0.2981804820 | 0.2727272727 | 45 | 1 | 90 |
| kaiaulu | 0.3695665445 | 0.4107142857 | 9 | 1 | 90 |
| openssl | 0.0805659082 | 0.0705505279 | 112 | 1 | 90 |
| tomcat | 0.1935612146 | 0.1794258373 | 59 | 1 | 90 |

## Lift methodology (from vignette)

The `rework` model (Abdel-Hamid & Madnick 1991) expresses the hidden
rework cycle: Req → Dev → Test → (pass | Rew → Dev again). Its `ctrl`
parameter is `failrate`. Thesis: `failrate` 0.1 → 0.7 lets rework
dominate, killing net Done output.

This notebook lifts `failrate` from Apache Helix as the share of
commits in each window that the SZZ pass marks as bug-introducing.

## Lift verdict on the project

`rework`'s thesis predicts net `Done` drops when `failrate` crosses
the 0.5 mark. Compare Helix's median `failrate` to that threshold.

## Source

- SD model: `paper/sd.py::rework()`
- Audit row: `paper/outputs/full_audit.csv` (line for `rework`)
- Lift Rmd: `sci4seng/lifts/vignettes/rework_failrate_estimation.Rmd`

