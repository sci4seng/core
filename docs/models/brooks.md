---
title: brooks
parent: Models
nav_order: 4
---

# brooks

Cell: [`process-conditional`](../glossary.md#process-conditional "Inputs CONFIRM, params not") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -147.50) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -6.07)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -6.07 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 234.65 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 223.29 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 82.13 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 12 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 139 / 200 CONFIRM |
| [`2x2 cell`](../glossary.md#cell "{universal, process, world, fragile} from (inp_cnt, par_cnt)") | [`process-conditional`](../glossary.md#process-conditional "Inputs CONFIRM, params not") |

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
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | FAIL |

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

## Lift methodology (from vignette)

The Brooks model expresses the central thesis of *The Mythical
Man-Month* (Brooks 1975): adding people to a late project makes it
later. In SD form, two stocks track personnel — veteran developers
(`Vet`) and new hires (`New`) — and a productivity tax falls on
veterans whenever newcomers join (training cost + intra-team
communication overhead). The SD model is in `models/sd.py:brooks()`.

This notebook lifts the model's productivity-tax parameter from
Apache Helix's git history. We need only the git log and kaiaulu's
`identity_match` (no proprietary tooling).

**Lift output**: a calibrated value of `brooks_tax` =
`(pre_velocity - post_velocity) / pre_velocity`, where the velocities
are veteran commit rates in symmetric windows before and after each
late-hire event. A positive median supports Brooks; a negative or
near-zero median is itself a useful falsification — late hires
*accelerated* veterans on this project.

**Method outline**:
1. Parse git log via `parse_gitlog(perceval, repo)`.
2. Resolve developer aliases via `identity_match(...)`.
3. Detect late-hire events (first-commit ≥ 365 days after project
   start) with `detect_late_hires()`.
4. For each late hire, compute pre/post veteran commit rates with
   `compute_velocity_changes()`.
5. Aggregate `brooks_tax` median + mean.

The two helper functions are in `lifts/functions.R`; both are
candidates for upstream contribution into `kaiaulu/R/`.

## Lift verdict on the project

The median `brooks_tax` (final cell, below) is **positive on Helix**
(≈ 0.11). Veterans lose roughly 11% of their commit velocity in the
90 days after a new committer joins. The size is modest but the
direction matches Brooks's claim. Family-member tests on 7 more
projects (in `findings.md` F3) show the same sign for 5 of them, with
magnitudes 0.03 → 0.31 — large project-to-project variance suggests
team-size and mentoring practices modulate the effect heavily.

## Sanity checks

SME's two-part check:

**(1) Bug-count dependency**: this lift does NOT use bug count, so
the choice of communication source (mbox/github/jira) is irrelevant.
The lift would work on any git-only project.

**(2) Identity bridging**: we used identity_match on a single source
(git). The lift does not require comms-to-code bridging. If the
brooks model were later extended to discriminate bug-introducing
late-hires from feature-introducing late-hires, JIRA + git
identity_match would be required, and GitHub would need an extra
alias source.

## References

- Brooks, F. P. (1975). *The Mythical Man-Month*. Addison-Wesley.
- coder's SD-framework `models/sd.py:brooks()` (this repo) — encodes
- the thesis as a `Model(init, step, y, rq, ctrl)` namedtuple.
- Replication: re-run this notebook on a different Apache project
- by swapping `../conf/helix.yml` for `../conf/<project>.yml`.

## Source

- SD model: `paper/sd.py::brooks()`
- Audit row: `paper/outputs/full_audit.csv` (line for `brooks`)
- Lift Rmd: [`brooks_late_hire_velocity.Rmd`](https://github.com/sci4seng/lifts/blob/main/vignettes/brooks_late_hire_velocity.Rmd)

