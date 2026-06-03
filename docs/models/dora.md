---
title: dora
parent: Models
nav_order: 17
---

# dora

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -45.35) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): CONFIRM ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -58.67)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | CONFIRM |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -58.67 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 40.94 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 46.25 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 14.33 |
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
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | PASS &middot; 23/23 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | warn — all lifted values strictly inside [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 8 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `arrival_rate` | `batch_size` | `cfr` | `n_tags` | `rec_rate` |
|---|---|---|---|---|---|
| airflow | 3.3776818333 | 9.1058823529 | 0.2502936340 | 936 | 0.0061599038 |
| ambari | 1.2162553676 | 48.287878787 | 0.3413868842 | 133 | 0.0064919529 |
| camel | 2.8497232259 | 8.7610619469 | 0.0772727272 | 227 | 0.0092531488 |
| helix | 0.5885649000 | 73.906976744 | 0.0494021397 | 44 | 0.0113618834 |
| junit5 | 1.0734255618 | 38.383928571 | 0.2719237031 | 113 | 0.0137119895 |
| kaiaulu | 0.0932932348 | — | 0.2436974789 | 0 | 0.0882097554 |
| openssl | 2.3643658126 | 54.784722222 | 0.0512527992 | 433 | 0.0014577313 |
| tomcat | 2.8697458617 | 65.055793991 | 0.1616967937 | 234 | 0.0013478556 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `dora` model (Forsgren, Humble, Kim 2018) tracks Wip / Deploys /
Incidents / Recovery stocks. `ctrl` is `batch_size`. Thesis: large
batches drive change-failure rate (CFR) up, hurting net deploys.

This notebook lifts four DORA metrics from Apache Helix:
- `batch_size`: mean commits between consecutive release tags
- `cfr`: bug-fix commits / total commits
- `arrival_rate`: commits per day
- `rec_rate`: 1 / median bug-fix latency (days)

## Lift verdict on the project

`dora` predicts `batch_size = 50` hurts net deploys vs `batch_size =
5`. Helix's measured `batch_size` value here is the operating point;
plug into `sd.opt(dora, ...)` then `verdict()`.

## Source

- SD model: `paper/sd.py::dora()`
- Audit row: `paper/outputs/full_audit.csv` (line for `dora`)
- Lift Rmd: `sci4seng/lifts/vignettes/dora_four_keys_lift.Rmd`

