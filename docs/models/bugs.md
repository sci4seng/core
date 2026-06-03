---
title: bugs
parent: Models
nav_order: 6
---

# bugs

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") +38.06) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): CONFIRM ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") +22.16)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | CONFIRM |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | +22.16 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 47.22 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 33.59 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 16.53 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 130 / 200 CONFIRM |
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
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | N/A — no lift rows |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | N/A — no lift rows |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | N/A — model not in calibrate.py |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 3 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `fit_r2` | `gokumoto_a` | `gokumoto_b` | `n_bugs_resolved` | `n_issues_total` |
|---|---|---|---|---|---|
| camel | 0.5980 | 177.60 | 1.000e-07 | 185 | 500 |
| helix | 0.6162524156 | 244.8 | 1e-08 | — | 1879 |
| kaiaulu | 0.9098 | 26.40 | 1.000e-08 | — | — |

_(showing first 5 of 9 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `bugs` model (Goel & Okumoto 1979) is the canonical software-
reliability-growth thesis: cumulative bug detection follows an
exponential approach to an asymptotic total. The SD form is in
`models/sd.py:bugs()`:

$$N(t) = a \cdot (1 - e^{-b \cdot t})$$

where `a` is the eventual total bug population and `b` is the
discovery rate.

**Input source choice**: bugs needs a bug-count signal with
timestamps. Helix provides three candidates:

- **GitHub issue dump** (label='bug', closed_at) — used here
- JIRA dump (issuetype='Bug', resolutiondate) — partial dump only;
  the available window has 0 Bug-type issues
- commit-message heuristic — too noisy without ground-truth filter

We choose GitHub issues because the dump is complete (1879 issues)
and the `bug` label provides a clean classifier.

**Method outline**:
1. Parse all GitHub issue JSON files.
2. Filter issues with label='bug' AND non-null `closed_at`.
3. Sort by close time. Build cumulative-N(t) trajectory.
4. Grid-search Goel-Okumoto fit (a × b parameter pairs).
5. Output: `a`, `b`, R² fit quality.

## Lift verdict on the project

The Goel-Okumoto fit predicts an eventual total of ~245 closed bugs
(`a`) on a discovery rate of `b ≈ 1e-8 per second`. The R² of ~0.62
indicates a moderate fit — the trajectory deviates from pure
exponential, suggesting Helix is still in the early discovery regime
where new sub-systems keep entering the bug-detectable population.

In `models/sd.py:bugs()` terms: the initial `Latent` stock would be
≈ 245 (the asymptote), of which 170 have been `Found` to date and
all 170 are `Fixed`. The model's RQ is "2x initial Latent → ~2x
eventual Fixed (linearity)" — Helix is the wrong test bed because
the trajectory hasn't saturated yet. A family-member test on a
project at or near saturation (e.g. an older project with declining
bug arrivals) would be a better falsification target.

## References

- Goel, A. L. & Okumoto, K. (1979). Time-dependent error-detection
- rate model for software reliability and other performance measures.
- IEEE Transactions on Reliability*, R-28(3), 206–211.
- `models/sd.py:bugs()` — the SD model.
- `scripts/lift_bugs_gh.py` + `scripts/lift_bugs_jira.py` — Python
- variants for the multi-project sweep that produced the family-
- member table above.

## Source

- SD model: `paper/sd.py::bugs()`
- Audit row: `paper/outputs/full_audit.csv` (line for `bugs`)
- Lift Rmd: `sci4seng/lifts/vignettes/bugs_goel_okumoto_fit.Rmd`

