---
title: Findings
nav_order: 2
---

# Headline findings (F0–F10)

## F0 — Most published SE theses dissolve under stats

Of 35 models: 20 neutral, 14 CONFIRM, 1 REFUTE.

Roughly 57% are stats-grade neutral — the single-shot CONFIRM is hiding noise as signal. Either narrow ranges via lift, or accept the thesis is not statistically detectable under author-declared priors.

## F0 — Boundary-adequacy violations

0 `out_of_range`, 7 `at_boundary`, 98 `in_range` cells across all lifted (model × project) pairs.

Per-model breakdowns live on each [model page](models/).

## F3 — Brooks effect varies 11× across projects

| project | brooks_tax_median |
|---|---|
| kaiaulu | -1.134 |
| camel | -0.144 |
| ambari | +0.029 |
| tomcat | +0.055 |
| helix | +0.113 |
| openssl | +0.146 |
| junit5 | +0.222 |
| airflow | +0.311 |

See [brooks](models/brooks.md) for the full discussion.

## F9 — aiwork CONFIRM gap shrinks 97% under empirical no-AI baseline

GitClear / METR's aiwork model defaults `churn_base = 0.05` (the no-AI churn baseline AI is supposed to inflate). Gitlog-only lift on three Apache projects observes 0.01-0.03 — all below the model's default.

| project | churn_base |
|---|---|
| helix | 0.0295 |
| tomcat | 0.0303 |
| camel | 0.0095 |

At helix-lifted params the calibrated `rq()` gap shrinks from -51.69 to -1.52 (97% drop). Verdict stays CONFIRM but at the neutral threshold. AI-coding-quality concern is load-bearing on the modeller's no-AI baseline assumption — a low-pre-AI-churn team shows almost no AI penalty under the model's literature priors.

See [aiwork](models/aiwork.md) for the full discussion.

## F10 — archpat verdict FLIPS to neutral under empirical per-region commit rates

Helix's patterned region (3 modules: helix-core, metadata-store-directory-common, zookeeper-api) ships at 7.69 commits/module/month vs the legacy region's 0.47 — a 16.4x ratio against the model's 2.5x default.

Calibrated `archpat.rq()` gap collapses from +228.69 (CONFIRM) to -1.41 (**neutral, verdict flipped**). Patterned regions on helix already ship so fast per-module that aggressive migration adds nothing. Martin Clean Arch + Perry & Wolf's "patterns repair existing-bad-software" claim does NOT survive contact with a project where the patterned region is already the active-development core.

`sd.py archpat.gen_pat` hi widened 3 → 10 to absorb the empirical helix value (was clipping at 3).

See [archpat](models/archpat.md) for the full discussion.

