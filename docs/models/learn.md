---
title: learn
parent: Models
nav_order: 20
---

# learn

Cell: [`process-conditional`](../glossary.md#process-conditional "Inputs CONFIRM, params not") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -5.28) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -0.90)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -0.90 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 36.30 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 37.28 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 12.71 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 13 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 198 / 200 CONFIRM |
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
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | PASS |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | warn &middot; 7/38 at_boundary, 31 in_range |
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

## Lift methodology (from vignette)

The `learn` model (Sterman 2000, ch. 18) tracks the workforce-flow
pipeline that develops engineering capability over time:

```
Jr ──train──> Tr ──promote──> Sr ──mentor──> Ment(or)
```

The SD form is in `models/sd.py:learn()`. `ctrl` = `Sr` (the senior
stock). Thesis: removing seniors (`Sr = 0`) starves the training
pipeline because juniors and trainees have no mentors to graduate
toward; the cumulative `Sr + Ment` output collapses.

This notebook lifts the stocks and transition rates from a project's
git history alone. We require only `parse_gitlog` and
`identity_match` — no JIRA or mbox.

**Method outline**:
1. Parse git log; merge developer aliases via `identity_match`.
2. For each developer, compute tenure = last_commit − first_commit.
3. Bucket: tenure < 365d = Jr, 365d ≤ tenure < 1095d = Tr,
   tenure ≥ 1095d = Sr. (Ment is not directly observable from git
   alone; it represents a mentor *role* not a tenure bucket.)
4. Estimate transition rates by sliding 90-day windows through the
   history and counting Jr→Tr and Tr→Sr identity transitions per
   slice. Annualise by multiplying by 365/90.

A previous methodology mistake: using 365-day slices with a 365-day
Jr cutoff forced every surviving Jr to graduate per slice (saturating
train_rate at 1.0). The 90-day slice fixes this and gives realistic
0.7–0.9 train_rates across 8 OSS projects (see `findings.md` F0
methodology note).

## Lift verdict on the project

Helix's cohort distribution is **top-heavy junior** (Jr=43, Tr=21,
Sr=9). The train_rate ≈ 0.81 — most surviving Jrs graduate within a
year. The Sr stock is small relative to Jr (9 vs 43 = 21%).

Running `models/sd.py:learn.rq(bg=helix_calib)` (via
`scripts/calibrate.py`) re-runs the thesis test with these stocks
fixed. Baseline gap (Sr=5 → Sr=0) is −5.28; with Helix's Jr=43
calibration it widens to −6.54 — more juniors means more starvation
when seniors leave. Thesis CONFIRM in both cases.

## References

- Sterman, J. (2000). *Business Dynamics*, ch. 18 (workforce flow).
- `models/sd.py:learn()` — the SD model under test.
- Replication: swap `../conf/helix.yml` for any of the 8 project
- configs in `../conf/` and re-knit.

## Source

- SD model: `paper/sd.py::learn()`
- Audit row: `paper/outputs/full_audit.csv` (line for `learn`)
- Lift Rmd: `sci4seng/lifts/vignettes/learn_cohort_transitions.Rmd`

