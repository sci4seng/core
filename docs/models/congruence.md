---
title: congruence
parent: Models
nav_order: 8
---

# congruence

Cell: [`universal`](../glossary.md#universal "Both inputs and params CONFIRM") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") -314.85) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): CONFIRM ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") -268.68)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | CONFIRM |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | -268.68 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 54.18 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 309.78 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 18.96 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 177 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 196 / 200 CONFIRM |
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
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | PASS &middot; 6/6 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | warn — all lifted values strictly inside [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 3 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `Brokers_n` | `Clusters_n` | `largest_cluster` | `n_devs` | `n_devs_main` |
|---|---|---|---|---|---|
| airflow | 4 | 7 | 46 | 142 | 142 |
| helix | 3 | 4 | 33 | 77 | 77 |
| tomcat | 39 | 33 | 1361 | 3435 | 3295 |

_(showing first 5 of 9 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `congruence` model (Newman 2015; radio-silence smell port from
kaiaulu R/smells.R:207; SD form in `models/sd.py:congruence()`) tests
whether **boundary-spanning developers** ("brokers") hold a
communication-fragmented project together. Stocks:

```
Clusters ──merge_rate──> Brokers ──broker_form──> Cohesion
  ↑                          ↓
fragment_rate            broker_loss (ctrl)
```

`ctrl` = `broker_loss`. Thesis: `broker_loss = 0.3` (sudden loss of
key brokers) collapses Cohesion because fragmented clusters can no
longer exchange context.

This lift exercises **SME's sanity-check #2**: a model that needs
*both* communication and source code, requiring kaiaulu's
`identity_match` to bridge mbox sender addresses ↔ git author emails.
Without that bridge, a single human appearing as `asebastian@linkedin`
in mbox and `asebastian@apache.org` in git is double-counted as two
nodes — distorting cluster size and broker detection.

**Method outline**:
1. Parse mbox via `parse_mbox_dir()` (Perceval over all `*.mbox`
   files; helper in `functions.R`).
2. Parse gitlog via `parse_gitlog()`.
3. `identity_match` over BOTH sources with
   `name_column = c("author_name_email", "sender")` to merge
   identities across mbox + git.
4. Build undirected reply graph on identity_id nodes.
5. Louvain community detection on largest connected component.
6. Radio-silence broker pass per kaiaulu R/smells.R:207 logic.
7. Output: Brokers, Clusters, n_incidents, cluster_size_dist.

## Lift verdict on the project

Helix's communication graph (on identity-matched developers):

- **Brokers**: see count above. Compares to the pre-identity-match
  Python run (`smells/radio_silence.py` on raw mbox senders) which
  found 3 brokers. Any difference is due to identity_match merging
  cross-source aliases that were previously double-counted.
- **Clusters**: the partition shape says whether Helix has a
  uni-modal or multi-modal communication structure. Helix
  historically shows a [42, 25, 14, 13, 2] cluster-size distribution
  pre-identity-match; with identity_match this should slightly
  consolidate.

The lifted `Brokers` stock plugs into `models/sd.py:congruence()`'s
init via `scripts/calibrate.py`. Helix's defaults already match the
model's defaults (Brokers=3, Clusters=5) — this is partly because
the model was specified with knowledge of an earlier radio_silence
run. See `findings.md` F4-related methodology note.

## References

- Newman, M. E. J. (2015). Networks: An Introduction. Oxford UP.
- Blondel, V. D. et al. (2008). Fast unfolding of communities in
- large networks. *J. Stat. Mech.*.
- kaiaulu R/smells.R:207 — the original radio-silence smell.
- `smells/radio_silence.py` — earlier Python port (this .Rmd
- supersedes it for paper deliverables).
- `models/sd.py:congruence()` — the SD model.

## Source

- SD model: `paper/sd.py::congruence()`
- Audit row: `paper/outputs/full_audit.csv` (line for `congruence`)
- Lift Rmd: `sci4seng/lifts/vignettes/congruence_radio_silence_brokers.Rmd`

