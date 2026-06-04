---
title: archpat
parent: Models
nav_order: 3
---

# archpat

Cell: [`process-conditional`](../glossary.md#process-conditional "Inputs CONFIRM, params not") &middot; [`verdict`](../glossary.md#verdict "CONFIRM / REFUTE / neutral on (y0, y1)"): CONFIRM ([`gap`](../glossary.md#gap "signed y1 - y0 from single-shot rq()") +228.69) &middot; [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same"): neutral ([`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") +15.56)

## Verdict (N=100 stats-grade)

| metric | value |
|---|---|
| [`verdict_n`](../glossary.md#verdict_n "N-shot verdict via stats.same") | neutral |
| [`gap_n`](../glossary.md#gap_n "pooled-mean y1 - y0 from rq_n") | +15.56 |
| [`sd0_n`](../glossary.md#sd0_n "stddev of y0 samples in rq_n") | 220.44 |
| [`sd1_n`](../glossary.md#sd1_n "stddev of y1 samples in rq_n") | 185.63 |
| [`eps_n`](../glossary.md#eps_n "0.35 * sd(y0): same-list tolerance") | 77.15 |
| [`stress(inputs)`](../glossary.md#stress_inputs "200 perturbed UPPER-input backgrounds") | 34 / 200 CONFIRM |
| [`stress(params)`](../glossary.md#stress_params "200 perturbed lower-param backgrounds") | 122 / 200 CONFIRM |
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
| [`param_plausibility`](../glossary.md#param_plausibility "in_range/at_boundary/out_of_range from boundary_check.csv") | PASS &middot; 4/4 in_range |
| [`boundary_adq_data`](../glossary.md#boundary_adq_data "Lifted value reaches or exceeds declared [lo, hi]") | warn — all lifted values strictly inside [lo, hi] |
| [`calibrated_rq_rerun`](../glossary.md#calibrated_rq_rerun "rq() under Helix-calibrated init") | CONFIRM — verdict stable (default=CONFIRM) |
| [`family_member_coherence`](../glossary.md#family_member_coherence "Per-project sign agreement across the family") | 2 projects lifted (sign tally not auto-computed) |
| [`behavior_reproduction`](../glossary.md#behavior_reproduction "Sim trajectory vs monthly historical CSV") | not run — requires monthly historical CSV |

## Lift values per project

| project | `Legacy_n` | `Other_n` | `Patterned_n` | `modules` | `n_files` |
|---|---|---|---|---|---|
| ambari | 1890 | 4329 | 381 | ambari-serve | 6600 |
| helix | 384 | 1452 | 149 | helix-core,m | 1985 |

_(showing first 5 of 7 metrics; full data in `paper/outputs/lifts.csv`)_

## Lift methodology (from vignette)

The `archpat` model (architect Kazman's claim) tests whether design
patterns applied to an already-bad codebase can pay down architectural
debt. The SD form (`models/sd.py:archpat()`) has three architectural
stocks plus a Debt accumulator:

```
Legacy ──migrate──> Patterned ──decay_rate──> Drift ──drift_to_legacy──> Legacy
            (effort applied)     (Perry-Wolf erosion)
```

`ctrl` = `migrate`. Thesis: starting from
`Patterned=10, Legacy=90, Debt=40`, aggressive migration
(`migrate=1.5`) repairs the project faster than slow migration
(`migrate=0.2`).

**Method outline** (full chain):

1. `mvn compile -pl helix-core -am -DskipTests` — produces `.class`
   files in `target/classes/`.
2. `java -jar pattern4.jar -target <classes> -output <xml>` — GoF
   patterns per class. Discovered today: pattern4 IS CLI-callable
   despite its GUI-default manifest (the dispatch is in
   `MatrixFrame.main`). See memory:
   `reference_pattern4_gotcha.md` for full incantation.
3. `parse_pattern4_xml.py <pattern4-dir>` — Python parser, emits a
   `patterned_files.csv` with `file_pathname, pattern_type, role,
   module` columns. (We do this in Python because R's kaiaulu wrapper
   `parse_gof_patterns()` is a parser, not a runner — same data, two
   languages.)
4. Bug-frequency signal: SZZ-introducing-commits touching each file
   (`scripts/szz_helix.py` → `szz_pairs.csv`). Replaces JIRA-Bug
   filter because the partial JIRA dump on disk has 0 Bug-type
   issues.
5. File-churn: `compute_file_churn()` from `functions.R`.
6. Assign each .java file to one of {Patterned, Legacy, Drift, Other}
   via `assign_file_partition()`.

**Fallback path**: if pattern4 setup were unavailable, Arcan
(structural smells) is the kaiaulu-documented substitute. Arcan
output has the same `(file, smell_type, smell_id)` shape; the
partition logic is detector-agnostic. Document the substitution in
any paper deliverable since smells ≠ GoF patterns semantically.

## Lift verdict on the project

Helix's partition: ~6.5% Patterned (149 files), ~19% Legacy
(384 files), 0 Drift (no file passes the 0.5 churn threshold in the
recent 180-day window — Helix is a mature, stable codebase), ~74%
Other.

Running `models/sd.py:archpat.rq(bg=helix_calib)` with these stocks
(plugged in via `scripts/calibrate.py`) widens the thesis gap from
+229 (default) to +390. **Helix's bigger Legacy stock strengthens
the repair thesis** — more legacy means more headroom for migrate to
move files into the Patterned bucket.

**Family-member test on Ambari** (2nd Java + Maven project):

| project | Patterned | Legacy   | Drift | Other  | n_files |
|---------|----------:|---------:|------:|-------:|--------:|
| Helix   | 149       | 384 (OUT)| 0     | 1,452  | 1,985   |
| Ambari  | 381 (OUT) | 1,890 (OUT) | 0  | 4,329  | 6,600   |

**Boundary-adequacy failure**: archpat's `Legacy` stock has model
declared `hi = 200`. Both Helix (384) and Ambari (1,890) exceed.
`Patterned hi = 200` also exceeded by Ambari (381). The model's
bounds were specified at small-project scale and don't span mature
OSS. Recommend widening to ≥ 1000 / ≥ 3000 respectively. See
`findings.md` F0 for the full boundary-violation table.

## Sanity checks

**(1) Bug-count dependency**: this lift requires bug-classification
per commit. We use SZZ-introducing-commit-touches as a proxy because
the partial JIRA dump on disk has 0 Bug-type issues. With the full
SME-cleaned Helix JIRA dump (on his Drive), we could tighten this
to JIRA-Bug-type-filtered commits, narrowing false-positives.

**(2) Identity bridging**: this lift uses git only, not comms. No
cross-source identity_match required.

## References

- Martin, R. C. (2008). *Clean Architecture*.
- Perry, D. E. & Wolf, A. L. (1992). Foundations for the study of
- software architecture. *ACM SIGSOFT Software Engineering Notes*.
- Tsantalis, N. et al. — pattern4 GoF detector
- (https://users.encs.concordia.ca/~nikolaos/pattern_detection.html).
- Arcelli Fontana, F. et al. — Arcan smell detector
- (https://essere.disco.unimib.it/wiki/arcan/) — documented fallback.
- `models/sd.py:archpat()` — the SD model.
- `findings.md` F0 — multi-project boundary-violation summary.

## Source

- SD model: `paper/sd.py::archpat()`
- Audit row: `paper/outputs/full_audit.csv` (line for `archpat`)
- Lift Rmd: `sci4seng/lifts/vignettes/archpat_gof_pattern_partition.Rmd`

