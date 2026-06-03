---
title: defmap
parent: Models
nav_order: 14
---

# defmap

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -100.00) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): CONFIRM ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -19.33)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | CONFIRM |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -19.33 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 19.87 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 24.14 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 6.95 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 156 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 163 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| [`dim_check`](../glossary.md#dim_check "Every init param exposes a well-formed unit string") | PASS |
| [`boundary_adq`](../glossary.md#boundary_adq "F&S 4/7: tmax=80 verdict still holds") | PASS |
| [`anomaly_check`](../glossary.md#anomaly_check "F&S behaviour-anomaly: hi inputs do not flip y sign") | PASS |
| [`extreme_eqn`](../glossary.md#extreme_eqn "F&S extreme-conditions: no NaN/Inf at lo/hi inputs") | ERR:ValueError |
| [`mr_zero_input`](../glossary.md#mr_zero_input "Chen MR3: ctrl=lo idempotent") | PASS |
| [`mr_monotone`](../glossary.md#mr_monotone "Chen MR1: y monotone in ctrl over 5 grid points") | FAIL |
| [`mr_dt_halving`](../glossary.md#mr_dt_halving "Chen MR8 / Sterman 6: y invariant to dt/2") | PASS |
| [`mr_bound_consist`](../glossary.md#mr_bound_consist "Chen MR9: clip vs reject agree") | FAIL |
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | N/A — no lift rows |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | N/A — no lift rows |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | N/A — default=CONFIRM; no overridable params |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 8 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `n_phases` | `seed` | `total_caught` | `total_inject` | `total_leaked` |
|---|---|---|---|---|---|
| airflow | 190 | 1 | 640 | 7271 | 6631 |
| ambari | 81 | 1 | 1739 | 8384 | 6645 |
| camel | 2 | 1 | 465 | 477 | 12 |
| helix | 17 | 1 | 140 | 538 | 398 |
| junit5 | 94 | 1 | 1219 | 4940 | 3721 |
| kaiaulu | 1 | 1 | 0 | 56 | 0 |
| openssl | 217 | 1 | 243 | 3841 | 3598 |
| tomcat | 136 | 1 | 1017 | 5742 | 4725 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `defmap` model (Abdel-Hamid & Madnick 1991 defect submodel) tracks
Injected / Caught / Latent / Prod stocks. `ctrl` is `tst` (testing
intensity). Thesis: `tst` 2.5 → 0.5 increases operational defects.

This notebook lifts the model's defect-flow stocks across Helix
release-tag phases. Each phase = (tag_i, tag_{i+1}].

## Source

- SD model: `paper/sd.py::defmap()`
- Audit row: `paper/outputs/full_audit.csv` (line for `defmap`)
- Lift Rmd: `sci4seng/lifts/vignettes/defmap_bug_caught_ratio.Rmd`

