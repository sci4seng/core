---
title: Glossary
nav_order: 6
---

# Glossary

Each scorecard term on the model pages links here for a one-line definition, a literature citation, and a deep link into the implementation in `paper/`. Hover any linked term in a model scorecard for the same tooltip.

## Forrester &amp; Senge / Sterman structural tests

Nine automated structural tests run against every model. `dim_check` is a unit-string sanity probe. First three of the remaining are Forrester &amp; Senge (1980); last five are metamorphic relations after Chen et al. (1998). Source: `paper/tests.py`.

<h3 id="dim_check"><code>dim_check</code></h3>

Every init param entry must be `[default, lo, hi, units]` with `units` a non-empty identifier-shaped token (atom or `/`-separated atoms, optional `^N` power). Pragmatic dimensional probe; does NOT do full symbolic propagation.

_MYTHS framework primitive (S4 in Sterman 2000)._

Source: `paper/tests.py`

<h3 id="boundary_adq"><code>boundary_adq</code></h3>

Re-run `rq()` at `tmax=80` (4× default horizon). FAIL if the verdict flips — the time-horizon boundary is load-bearing.

_Forrester &amp; Senge (1980) test 4/7._

Source: `paper/tests.py:32`

<h3 id="anomaly_check"><code>anomaly_check</code></h3>

Compare baseline `y` to a stressed run with every UPPER input at its `hi`. FAIL on qualitative sign-flip.

_Forrester &amp; Senge (1980) behaviour-anomaly test._

Source: `paper/tests.py:50`

<h3 id="extreme_eqn"><code>extreme_eqn</code></h3>

Run with each UPPER input set to its `lo` and `hi` in turn. FAIL on any NaN, ±Inf in any state.

_Forrester &amp; Senge (1980) extreme-conditions test._

Source: `paper/tests.py:70`

<h3 id="mr_zero_input"><code>mr_zero_input</code></h3>

Setting `ctrl` to its `lo` bound must produce the same trajectory as a baseline with `ctrl` explicitly held at `lo`.

_Chen et al. (1998) metamorphic relation MR3._

Source: `paper/tests.py:97`

<h3 id="mr_monotone"><code>mr_monotone</code></h3>

Sweep `ctrl` across 5 grid points in `[lo,hi]`. `y` must be monotone in the direction predicted by `rq()`.

_Chen et al. (1998) MR1._

Source: `paper/tests.py:118`

<h3 id="mr_dt_halving"><code>mr_dt_halving</code></h3>

Halve the integration step `dt`. `y` must agree within 10% — Sterman's integration-error check.

_Chen et al. (1998) MR8; Sterman (2000) test 6._

Source: `paper/tests.py:143`

<h3 id="mr_bound_consist"><code>mr_bound_consist</code></h3>

Run with `mode='reject'` vs `'clip'`. FAIL if `reject` aborts or if outputs differ — clamping was load-bearing.

_Chen et al. (1998) MR9._

Source: `paper/tests.py:158`

<h3 id="mr_scale"><code>mr_scale</code></h3>

Scale all UPPER inputs by 2×. FAIL on sign-flip or 100× explosion. Nonlinear `y_ratio` is expected, not a bug.

_Chen et al. (1998) MR2 (linearity probe)._

Source: `paper/tests.py:176`

## rq() and verdict family

Per-model research-question test and its N-shot stats-grade replacement. Source: `paper/sd.py`.

<h3 id="rq"><code>rq</code></h3>

Single-shot research-question test. Returns `{verdict, y0, y1, gap, desc}`.

_MYTHS framework primitive._

Source: `paper/sd.py:82`

<h3 id="rq_n"><code>rq_n</code></h3>

Sample N perturbed backgrounds (default N=100, triangular). Run `y0` and `y1` per sample. Classify via `stats.same` (Cliff's δ + KS + median-ε).

_MYTHS framework primitive._

Source: `paper/sd.py:209`

<h3 id="verdict"><code>verdict</code></h3>

Single-shot verdict on `(y0, y1)`. CONFIRM if signed gap exceeds `max(5% · |y0|, 0.5)`; REFUTE if against; else neutral.

Source: `paper/sd.py:82`

<h3 id="verdict_n"><code>verdict_n</code></h3>

Stats-grade verdict over two y-lists. `neutral` iff `stats.same(y0s, y1s, ε)`; else sign of `mean(y0)−mean(y1)`.

Source: `paper/sd.py:93`

<h3 id="gap"><code>gap</code></h3>

Signed `y1 − y0` from a single-shot `rq()` call.

Source: `paper/sd.py:82`

<h3 id="gap_n"><code>gap_n</code></h3>

Pooled-mean gap from `rq_n`: `mean(y1s) − mean(y0s)`. Reported with `sd0_n`, `sd1_n`, `eps_n`.

Source: `paper/sd.py:93`

<h3 id="sd0_n"><code>sd0_n</code></h3>

Sample standard deviation of `y0s` from `rq_n`.

Source: `paper/sd.py:93`

<h3 id="sd1_n"><code>sd1_n</code></h3>

Sample standard deviation of `y1s` from `rq_n`.

Source: `paper/sd.py:93`

<h3 id="eps_n"><code>eps_n</code></h3>

Same-list tolerance used by `stats.same`: `0.35 · sd(y0s)`.

_Knob: `the.stats.eps = 0.35`._

Source: `paper/stats.py:65`

## Stress matrix and 2x2 typology

Per-model classification from 200 perturbed-background runs.

<h3 id="stress_inputs"><code>stress_inputs</code></h3>

Run `rq()` on 200 triangular-perturbed backgrounds with only UPPER-case state variables perturbed (the world axis).

Source: `paper/sd.py:161`

<h3 id="stress_params"><code>stress_params</code></h3>

Same harness, lower-case (parameter) perturbation only — the process axis.

Source: `paper/sd.py:161`

<h3 id="inp_cnt"><code>inp_cnt</code></h3>

CONFIRM count out of 200 input-perturbed runs.

Source: `paper/tests.py:208`

<h3 id="par_cnt"><code>par_cnt</code></h3>

CONFIRM count out of 200 param-perturbed runs.

Source: `paper/tests.py:208`

<h3 id="cell"><code>cell</code></h3>

2x2 classification from (inputs, params) verdict pair. CONFIRM on a side requires ≥50%; REFUTE requires ≥20%.

Source: `paper/tests.py:226`

<h3 id="universal"><code>universal</code></h3>

Both `stress(inputs)` and `stress(params)` return CONFIRM. Thesis holds across world and process variation.

<h3 id="process-conditional"><code>process-conditional</code></h3>

Inputs CONFIRM, params not. Mechanism robust to environment; whether it manifests depends on team/process configuration.

<h3 id="world-conditional"><code>world-conditional</code></h3>

Params CONFIRM, inputs not. Thesis holds for a fixed parameterisation but breaks under varied initial conditions.

<h3 id="fragile"><code>fragile</code></h3>

Neither axis returns a CONFIRM majority. Thesis depends on a narrow regime.

## Statistical primitives

Same-list test inside `verdict_n`.

<h3 id="cliffs_delta"><code>cliffs_delta</code></h3>

Non-parametric effect-size: `(gt − lt) / (n · m)`. Two lists are 'same' iff `|δ| ≤ 0.195`.

_Cliff (1993); threshold per Romano et al._

Source: `paper/stats.py:68`

<h3 id="ks"><code>ks</code></h3>

Two-sample Kolmogorov-Smirnov distance with the 5% critical value `1.36 · √((n+m)/(nm))`.

_Smirnov (1948); knob: `the.stats.conf = 1.36`._

Source: `paper/stats.py:70`

## Data-tier checks

Auto-derived from lift CSVs.

<h3 id="param_plausibility"><code>param_plausibility</code></h3>

Counts `in_range` / `at_boundary` / `out_of_range` from `boundary_check.csv`. Any `out_of_range` → FAIL.

Source: `core/docs/scripts/gen_md.py`

<h3 id="boundary_adq_data"><code>boundary_adq_data</code></h3>

Empirical companion to `boundary_adq`: PASS iff at least one lifted value reaches or exceeds the declared `[lo, hi]`.

Source: `core/docs/scripts/gen_md.py`

<h3 id="calibrated_rq_rerun"><code>calibrated_rq_rerun</code></h3>

Re-run `rq()` with params replaced by Helix-calibrated lifted values. From `calibrated_verdicts.csv`.

Source: `core/docs/scripts/gen_md.py`

<h3 id="family_member_coherence"><code>family_member_coherence</code></h3>

Per-project sign agreement across the family. Currently reports project count only; sign tally is hand-tuned per model.

Source: `core/docs/scripts/gen_md.py`

<h3 id="behavior_reproduction"><code>behavior_reproduction</code></h3>

Sim trajectory vs monthly historical CSV. Not run (requires per-project monthly time series).

## References

- Forrester, J. W. &amp; Senge, P. M. (1980). Tests for building confidence in system dynamics models. *System Dynamics*, TIMS Studies in the Management Sciences 14, 209–228.
- Sterman, J. D. (2000). *Business Dynamics: Systems Thinking and Modeling for a Complex World*. McGraw-Hill.
- Chen, T. Y., Cheung, S. C. &amp; Yiu, S. M. (1998). Metamorphic testing: a new approach for generating next test cases. HKUST-CS98-01.
- Cliff, N. (1993). Dominance statistics: ordinal analyses to answer ordinal questions. *Psychological Bulletin* 114(3), 494–509.
- Smirnov, N. (1948). Table for estimating the goodness of fit of empirical distributions. *Annals of Mathematical Statistics* 19(2), 279–281.
