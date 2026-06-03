---
title: brooks
parent: Models
nav_order: 4
---

# brooks

Cell: [`fragile`](../glossary.md#fragile "Neither axis CONFIRMs in majority") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -147.50) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -0.58)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -0.58 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 188.32 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 186.41 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 65.91 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 12 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 68 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`fragile`](../glossary.md#fragile "Neither axis CONFIRMs in majority") |

## Tier 1 — Structural V&V (prudence)

| test | result |
|---|---|
| [`boundary_adq`](../glossary.md#boundary_adq "F&S 4/7: tmax=80 verdict still holds") | PASS |
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
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | N/A — no lift rows |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | N/A — no lift rows |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | N/A — default=CONFIRM; no overridable params |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 8 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `brooks_tax_mean` | `brooks_tax_median` | `n_hires` | `seed` | `window_days` |
|---|---|---|---|---|---|
| airflow | 0.3116968507 | 0.3109919571 | 1285 | 1 | 90 |
| ambari | -Inf | 0.0294384057 | 126 | 1 | 90 |
| camel | 0.0096826238 | -0.144230769 | 5 | 1 | 90 |
| helix | -Inf | 0.1126760563 | 65 | 1 | 90 |
| junit5 | 0.0308596574 | 0.2222222222 | 169 | 1 | 90 |
| kaiaulu | -2.646494708 | -1.133928571 | 6 | 1 | 90 |
| openssl | 0.0930948058 | 0.1464646464 | 1019 | 1 | 90 |
| tomcat | 0.0232660259 | 0.0551530533 | 50 | 1 | 90 |

## Source

- SD model: `paper/sd.py::brooks()`
- Audit row: `paper/outputs/full_audit.csv` (line for `brooks`)
- Lift Rmd: `sci4seng/lifts/vignettes/lift_brooks.Rmd`

