---
title: Findings
nav_order: 2
---

# Headline findings (F0–F5)

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

