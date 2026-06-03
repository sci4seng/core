---
title: brooksq
parent: Models
nav_order: 5
---

# brooksq

Cell: [`fragile`](../glossary.md#fragile "Neither axis CONFIRMs in majority") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -45.91) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -0.38)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -0.38 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 191.46 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 191.12 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 67.01 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 6 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 80 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`fragile`](../glossary.md#fragile "Neither axis CONFIRMs in majority") |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| [`dim_check`](../glossary.md#dim_check "Every init param exposes a well-formed unit string") | PASS |
| [`boundary_adq`](../glossary.md#boundary_adq "F&S 4/7: tmax=80 verdict still holds") | FAIL |
| [`anomaly_check`](../glossary.md#anomaly_check "F&S behaviour-anomaly: hi inputs do not flip y sign") | PASS |
| [`extreme_eqn`](../glossary.md#extreme_eqn "F&S extreme-conditions: no NaN/Inf at lo/hi inputs") | ERR:ValueError |
| [`mr_zero_input`](../glossary.md#mr_zero_input "Chen MR3: ctrl=lo idempotent") | PASS |
| [`mr_monotone`](../glossary.md#mr_monotone "Chen MR1: y monotone in ctrl over 5 grid points") | PASS |
| [`mr_dt_halving`](../glossary.md#mr_dt_halving "Chen MR8 / Sterman 6: y invariant to dt/2") | PASS |
| [`mr_bound_consist`](../glossary.md#mr_bound_consist "Chen MR9: clip vs reject agree") | FAIL |
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | ERR:ValueError |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | **FAIL** &middot; 10/16 out_of_range, 0 at_boundary, 6 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | PASS — lifted values reach or exceed declared [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 8 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `brooks_tax_median` | `inj_rate_increase` | `inj_rate_post_med` | `inj_rate_pre_med` | `latency_days` |
|---|---|---|---|---|---|
| airflow | 0.3109919571 | -0.011111111 | 1.4444444444 | 1.4444444444 | 30 |
| ambari | 0.0294384057 | 0.0944444444 | 1.7277777777 | 1.9277777777 | 30 |
| camel | -0.144230769 | -0.188888888 | 0.4888888888 | 0.5222222222 | 30 |
| helix | 0.1126760563 | 0 | 0.0111111111 | 0.0111111111 | 30 |
| junit5 | 0.2222222222 | -0.011111111 | 0.2111111111 | 0.2222222222 | 30 |
| kaiaulu | -1.133928571 | 0.0333333333 | 0.0833333333 | 0.0166666666 | 30 |
| openssl | 0.1464646464 | -0.022222222 | 0.3444444444 | 0.3444444444 | 30 |
| tomcat | 0.0551530533 | -0.033333333 | 0.2 | 0.2166666666 | 30 |

_(showing first 5 of 10 metrics; full data in `paper/outputs/lifts.csv`)_

## Boundary violations

| project | param | lifted | lo | hi |
|---|---|---|---|---|
| helix | `leak_rate` | 0.5713 | 0 | 0.5 |
| junit5 | `leak_rate` | 0.6044 | 0 | 0.5 |
| ambari | `inj_rate` | 1.928 | 0 | 0.5 |
| ambari | `leak_rate` | 0.6971 | 0 | 0.5 |
| airflow | `inj_rate` | 1.444 | 0 | 0.5 |
| airflow | `leak_rate` | 0.8253 | 0 | 0.5 |
| openssl | `leak_rate` | 0.9307 | 0 | 0.5 |
| tomcat | `leak_rate` | 0.8761 | 0 | 0.5 |
| camel | `inj_rate` | 0.5222 | 0 | 0.5 |
| camel | `leak_rate` | 0.7121 | 0 | 0.5 |

## Lift methodology (from vignette)

The `brooksq` model extends Brooks with quality tracking: a late-hire
boost slows veteran velocity AND raises the bug injection rate, so
quality-adjusted progress `y = Done - 5*Esc` is hurt twice over. The
sd.py model declares `boost` as its `ctrl` variable; the thesis says
y drops when boost increases.

This notebook lifts the quality side of `brooksq` from Apache Helix
using B-SZZ output (PyDriller). The Brooks side (`brooks_tax`) is
reused from `lift_brooks.Rmd`.

Calibration outputs:

| sd.py param   | source                                           |
|---------------|--------------------------------------------------|
| `brooks_tax`  | veteran velocity drop in post-hire window        |
| `inj_rate`    | bug-introducing commits per day, pre-hire window |
| `inj_rate'`   | same, post-hire — the boost-driven increase      |
| `leak_rate`   | fraction of bugs unfixed past a latency threshold|

## Sanity checks

SME's two-part check:

**(1) Bug-count dependency**: this lift DOES depend on bug attribution.
We use the JIRA-key-in-commit-message heuristic to identify bug-fix
commits (see `scripts/szz_helix.py`). Datasets without JIRA keys in
commit messages — pure-GitHub-issue projects — would need a different
seed mechanism (e.g. linked PR closes).

**(2) Identity bridging**: the brooksq lift uses identity_match on
git only. SZZ pairs are joined on `commit_hash`, not on developer.
GitHub would still need an extra alias source if we extended this
to author-attributed injection rates.

## Source

- SD model: `paper/sd.py::brooksq()`
- Audit row: `paper/outputs/full_audit.csv` (line for `brooksq`)
- Lift Rmd: `sci4seng/lifts/vignettes/brooksq_injection_leak.Rmd`

