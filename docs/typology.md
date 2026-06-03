---
title: Typology
nav_order: 3
---

# 2×2 stress-matrix cell typology

After `stress_matrix(model, n=200, seed=1)` each model lands in one
cell, based on majority verdicts across input-only vs param-only
perturbations.

|                  | robust to inputs    | fragile to inputs   |
|---               |---                  |---                  |
| robust to params | **universal**       | world-conditional   |
| fragile to params| process-conditional | **fragile**         |

- **universal**: thesis holds across both world variation (inputs)
  and process tweaks (params). Strongest cell.
- **world-conditional**: thesis robust to process tweaks but breaks
  under world variation. Hold input regime constant before believing.
- **process-conditional**: thesis robust to world variation but
  breaks if process knobs move. Calibrate the process knob before
  believing.
- **fragile**: thesis only holds under restricted backgrounds in
  both dimensions. Weakest cell.

Majority threshold per axis:
- ≥ 50% CONFIRM out of 200 → axis "CONFIRM"
- ≥ 20% REFUTE → axis "REFUTE"
- else → "neutral"

Source: `paper/tests.py::stress_matrix()`,
`paper/full_audit.py::cell_label()`.

## Current counts

Auto-derived from `paper/outputs/full_audit.csv` after the latest
`full_audit.py` run. See [models](models/) for the per-model
placement.
