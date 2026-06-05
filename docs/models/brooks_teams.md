---
title: brooks_teams
parent: Models
nav_order: 5
---

# brooks_teams

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -2505.81) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -486.00)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -486.00 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 2362.91 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 2386.18 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 827.02 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 100 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 185 / 200 CONFIRM |
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
| [`mr_scale`](../glossary.md#mr_scale "Chen MR2: 2x inputs do not flip sign or explode") | FAIL |

## Tier 2 — Data-tier checks (auto from lift CSVs)

| test | result |
|---|---|
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | N/A — no lift rows |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | N/A — no lift rows |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | N/A — model not in calibrate.py |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | N/A — no lift rows |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Source

- SD model: `paper/sd.py::brooks_teams()`
- Audit row: `paper/outputs/full_audit.csv` (line for `brooks_teams`)

## R lift helpers (kaiaulu-style)

**Status (2026-06-04): no lift shipped yet.** `brooks_teams` is
a new model; nothing in
[`lifts/R/functions.R`](https://github.com/sci4seng/lifts/blob/main/R/functions.R)
or [`lifts/vignettes/`](https://github.com/sci4seng/lifts/tree/main/vignettes)
targets it. The sketches below describe the helpers a future
`brooks_teams_org_shape.Rmd` would call. Names and signatures
are proposals; revise during the actual lift PR.

### `infer_team_topology(project_git, team_size_target = 8)`

Group developers into approximate teams by clustering on shared
file paths over the project's life. Each commit names one or
more files; co-authors of overlapping file sets land in the
same team. Output rows: `(team_id, devs, top_files,
first_commit, last_commit)`. The lifted `Team` for the SD model
is the median team size; `Devs` is the total identity count
across all teams.

### `compute_vet_share(project_git, teams, vet_threshold_days = 365)`

For each team identity, classify members as veteran (joined at
least `vet_threshold_days` before the team's last activity) or
new. Returns one row per team with `(team_id, vet_n, new_n,
vet_frac = vet_n / (vet_n + new_n))`. The project-level lifted
`vet_frac` is the mean (or median) across teams.

### `compute_team_comm_coef(project_git, teams, window_days = 90)`

Within each team, estimate the per-pair coordination cost as the
share of commit time spent on cross-author files (proxy for
context switches). Output: `(team_id, comm_coef_team)`; lifted
project value = the median.

**Why all three matter to the SD model.** `Team` calibrates the
quadratic-in-team-size drag; `vet_frac` is the `rq()` control
(mature-vs-startup arm); `comm_coef` scales the within-team
overhead. Without the lift, `brooks_teams` runs only on
literature-prior defaults (Team=8, vet_frac=0.8, comm_coef=0.005).


