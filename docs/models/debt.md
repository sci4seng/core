---
title: debt
parent: Models
nav_order: 13
---

# debt

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -56.65) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): CONFIRM ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -34.00)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | CONFIRM |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -34.00 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 46.24 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 75.62 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 16.19 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 200 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 200 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| [`dim_check`](../glossary.md#dim_check "Every init param exposes a well-formed unit string") | PASS |
| [`boundary_adq`](../glossary.md#boundary_adq "F&S 4/7: tmax=80 verdict still holds") | PASS |
| [`anomaly_check`](../glossary.md#anomaly_check "F&S behaviour-anomaly: hi inputs do not flip y sign") | PASS |
| [`extreme_eqn`](../glossary.md#extreme_eqn "F&S extreme-conditions: no NaN/Inf at lo/hi inputs") | PASS |
| [`mr_zero_input`](../glossary.md#mr_zero_input "Chen MR3: ctrl=lo idempotent") | PASS |
| [`mr_monotone`](../glossary.md#mr_monotone "Chen MR1: y monotone in ctrl over 5 grid points") | PASS |
| [`mr_dt_halving`](../glossary.md#mr_dt_halving "Chen MR8 / Sterman 6: y invariant to dt/2") | PASS |
| [`mr_bound_consist`](../glossary.md#mr_bound_consist "Chen MR9: clip vs reject agree") | PASS |
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | PASS |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | PASS &middot; 10/10 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | warn — all lifted values strictly inside [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 5 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `born_rate_mean` | `born_rate_median` | `n_commits` | `n_refactor_events` | `pay_rate_mean` |
|---|---|---|---|---|---|
| ambari | 0.2614923114 | 0.2700270027 | 6374 | 66037 | 0.4765075729 |
| camel | 0.2492640660 | 0.2261245809 | 1980 | 208118 | 0.4134706147 |
| helix | 0.2605503273 | 0.25 | 3178 | 21945 | 0.5687748992 |
| junit5 | 0.1906922074 | 0.1949152542 | 4299 | 36204 | 0.5644367405 |
| tomcat | 0.1044314209 | 0.1 | 15158 | 45814 | 0.3718426062 |

_(showing first 5 of 8 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `debt` model (Cunningham 1992) expresses the thesis that shipping
fast accrues technical debt, which then slows future shipping. The SD
form has stocks `Feat` (cumulative features), `Debt` (current debt),
`Vel` (velocity); parameters `born_rate` (debt born per ship),
`intr_rate` (compounding interest on existing debt), `pay_rate` (debt
paid by refactoring).

This notebook lifts `debt` from Apache Helix using:

| sd.py param  | source                                            |
|--------------|---------------------------------------------------|
| `pay_rate`   | RefactoringMiner: refactor commits / total commits|
| `born_rate`  | gitlog: share of "big" multi-file commits         |
| `intr_rate`  | proxy: bug-touch revisit rate on prior-changed files (TODO) |

`intr_rate` remains imperfect from git-alone; either accept fitting via
`sd.opt()` or refine later using SZZ pairs joined to gitlog churn.

## Sanity checks

**(1) Bug-count dependency**: this lift does NOT depend on bug-count,
so JIRA/GitHub/mbox choice is irrelevant. The lift would work on any
Java-or-similar project with a git history.

**(2) Identity bridging**: `debt` is whole-project, not per-developer.
`identity_match` is not required for the lift, though it would be for
any extension that breaks pay_rate by developer cohort.

## Source

- SD model: `paper/sd.py::debt()`
- Audit row: `paper/outputs/full_audit.csv` (line for `debt`)
- Lift Rmd: `sci4seng/lifts/vignettes/debt_refactoring_pay_rate.Rmd`

