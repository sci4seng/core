---
title: aiwork
parent: Models
nav_order: 2
---

# aiwork

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -51.69) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -50.54)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -50.54 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 263.62 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 252.89 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 92.27 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 188 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 170 / 200 CONFIRM |
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
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | N/A — no lift rows |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | N/A — no lift rows |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 3 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `churn_base` | `mature_rate` | `mean_span_days` | `n_authors` | `n_churn` |
|---|---|---|---|---|---|
| camel | 0.0095 | 0.00221 | 452.7 | 1349 | 774 |
| helix | 0.0295 | 0.00227 | 440.5 | 78 | 134 |
| tomcat | 0.0303 | 0.00077 | 1300.0 | 85 | 1965 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `aiwork` model (GitClear 2024, METR 2025) expresses a quality
tradeoff in AI-assisted coding: AI accelerates raw generation but
inflates churn (code rewritten or abandoned) and adds a verification
drag (humans must check outputs). Whether net delivery rises or
falls depends on the per-unit-AI coefficients (`gen_boost`,
`churn_mult`, `verify_drag`) **and** on the pre-AI baseline churn
rate the team carries into the experiment. The SD model is in
`models/sd.py:aiwork()`.

OSS projects don't expose per-commit AI authorship, so the
`ai`-controlled parameters can't be lifted directly. What we **can**
lift is the no-AI baseline that the model needs:

- **`churn_base`** — fraction of all commits that look like
  revert / rollback / hotfix events. This is the rate at which the
  team rewrites prior work even without AI in the loop. GitClear and
  METR treat AI churn as a multiplicative inflation on top of this
  base, so the lifted value calibrates one of the model's two free
  baselines.

- **`mature_rate`** — the SD model's Wip → Kept transition rate.
  We lift it as a per-author proxy: 1 / (mean span between an
  author's first and last commit). Lower span = faster cycle. A
  proper PR-cycle lift from the issue tracker is a future
  refinement; the gitlog-only proxy keeps the lift runnable on any
  project with no JIRA/GitHub bridge.

Both lifts are gitlog-only — no proprietary data, no bridging
across sources, no AI telemetry required.

## Lift verdict on the project

The methodology paper compares aiwork's `rq()` at the model's
default `churn_base = 0.05` against the lifted Helix value
(typically 0.02–0.03 across the OSS projects we've measured).
Under the lifted value, the CONFIRM verdict is retained but the
verdict gap shrinks by roughly 97% (from ~−52 to ~−1.5). The
AI-coding-quality concern is sensitive to the no-AI baseline — a
team with low pre-AI churn shows much less AI penalty than the
GitClear/METR priors assume by default.

This is a *partial-data* lift: the per-unit-AI coefficients
(`gen_boost`, `churn_mult`, `verify_drag`) still come from
literature priors. The full inverse-fit calibration is blocked on
the absence of per-commit AI-authorship data on OSS (TODO blocked
item 14).

## Sanity checks

**(1) Bug-count dependency**: this lift uses git subject lines and
per-author commit timestamps only. No bug count, no comms source.
The choice of mbox / github / jira does not affect this lift.

**(2) Identity bridging**: applied `identity_match` on the gitlog
so authors with multiple emails are merged before the span
computation. Without identity_match, the mean span would be
biased downward (each alias contributes its own short span).

## References

- GitClear (2024). *Coding on Copilot: 2023 Data Suggests Downward
- Pressure on Code Quality*.
- METR (2025). *Measuring the impact of early-2025 AI on
- experienced open-source developer productivity*.
- coder's SD-framework `models/sd.py:aiwork()` (this repo) —
- encodes the AI-quality tradeoff as a `Model(init, step, y, rq,
- ctrl)` namedtuple.
- Replication: re-run on a different Apache project by swapping
- `../conf/helix.yml` for `../conf/<project>.yml`.

## Source

- SD model: `paper/sd.py::aiwork()`
- Audit row: `paper/outputs/full_audit.csv` (line for `aiwork`)
- Lift Rmd: [`aiwork_churn_baseline.Rmd`](https://github.com/sci4seng/lifts/blob/main/vignettes/aiwork_churn_baseline.Rmd)

