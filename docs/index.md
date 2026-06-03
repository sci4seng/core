---
title: Home
nav_order: 1
---

# MYTHS — Models Yielding Testable Hypotheses in Software

A test-bench for SE theories cast as compartmental system-dynamics
models. Each model is a falsifiable conjecture; each is hit by a
10-test V&V bank under N=100 stress-matrix perturbation plus a
non-parametric two-sample verdict (Cliff's δ + KS + median-ε).
The whole battery runs in **~1.3 seconds**.

## Walk this site

- **[Findings](findings.md)** — F0–F5 headline results.
- **[Typology](typology.md)** — 2×2 stress-matrix cells explained.
- **[Models](models/)** — 35 models, one page each.
- **[Data](data.md)** — sources + lift status per project.

## Repo layout

This is `sci4seng/core`. Sibling repos:

- **[sci4seng/lifts](https://github.com/sci4seng/lifts)** — vignettes
  + R helpers + sample configs. PR'd into kaiaulu for review.
- **[sci4seng/data](https://github.com/sci4seng/data)** — manifest +
  drop-zone for project bundles. Raw data lives on Drive.

## Reproducing

```bash
git clone https://github.com/sci4seng/core
cd core/paper
python3 full_audit.py     # writes outputs/full_audit.csv
make refresh              # full pipeline + gates
```

Then `python3 docs/scripts/gen_md.py` regenerates this site's
`models/*.md` from the refreshed CSVs.
