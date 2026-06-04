#!/usr/bin/env python3
"""Inverse-fit brooks's (comm_coef, train_coef) against the
observed brooks_tax_median per project.

The existing brooks lift records a DERIVED metric — the
post-hire velocity drop:

    brooks_tax = (pre_velocity - post_velocity) / pre_velocity

— measured over symmetric 90-day windows around each late-hire
event. The SD model's `comm_coef` (per-pair drag) and
`train_coef` (per-newcomer drag) jointly produce this same
velocity drop when the simulated cohort joins at t=10. This
script finds the (comm_coef, train_coef) pair that minimises the
absolute distance between the simulated and observed taxes,
across the middle 60% of each param's declared [lo, hi] (same
narrowing convention as `sd.opt()`).

Output: paper/outputs/fit_brooks.csv with one row per project:
  project, observed_tax, best_comm_coef, best_train_coef,
  sim_tax_at_best, abs_error, n_grid_cells, seed.

This is the "what comm/train values would have produced the
observed velocity drop" inverse — the missing piece that
`calibrate_brooks` flagged ("brooks_tax_median is derived, not a
direct input"). A follow-up `calibrate.py` patch can read this
CSV and plug the best-fit values into `brooks.rq(bg=...)`.
"""

import csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from sd import brooks, run

OUTPUTS = HERE / "outputs"
LIFTS   = OUTPUTS / "lifts.csv"
GRID_N  = 20  # 20 x 20 = 400 cells per project; ~ instant
# Full [lo, hi] not narrowed: boost=10 already saturates the
# middle 60% (comm + train > 1 -> prod = 0 -> tax = 1 for every
# inner cell). Inverse-fit needs to see the entire surface.
NARROW  = 1.0
SEED    = 1


def linspace(lo, hi, n):
    if n <= 1:
        return [lo]
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]


def narrow_range(lo, hi, narrow=NARROW):
    mid  = (lo + hi) / 2
    half = (hi - lo) / 2 * narrow
    return max(lo, mid - half), min(hi, mid + half)


def simulate_tax(comm_coef, train_coef, boost=1, tmax=20, window=10):
    """Run brooks with the given comm/train + a boost cohort at
    t=10, then measure tax = (pre_velocity - post_velocity) /
    pre_velocity over symmetric windows around the boost."""
    m = brooks()
    bi = {k: list(v) for k, v in m.init.items()}
    bi['comm_coef']  = [comm_coef,  0, 0.05,  'frac/pair']
    bi['train_coef'] = [train_coef, 0, 1,     'frac/newhire']
    bi['boost']      = [boost,      0, 100,   'devs']
    out = run(bi, m.step, dt=1, tmax=tmax)
    if out is None:
        return None
    # Done is cumulative; velocity = delta(Done) per tick. sd.run
    # emits t = 0..tmax-1 (no t = tmax), so cap windows at the last
    # available tick.
    done_at = {t: r.Done for t, r in out}
    t_pre_start  = 0
    t_pre_end    = min(window, max(done_at))
    t_post_end   = min(2 * window, max(done_at))
    pre  = done_at[t_pre_end]  - done_at[t_pre_start]
    post = done_at[t_post_end] - done_at[t_pre_end]
    if pre <= 0:
        return None
    return (pre - post) / pre


def fit_one_project(observed_tax):
    """Grid search (comm_coef, train_coef) over their narrowed
    ranges; return the cell minimising |sim - obs|."""
    m = brooks()
    c_lo, c_hi = narrow_range(*m.init['comm_coef'][1:3])
    t_lo, t_hi = narrow_range(*m.init['train_coef'][1:3])
    best_err  = float('inf')
    best_cell = None
    n_cells   = 0
    for c in linspace(c_lo, c_hi, GRID_N):
        for tc in linspace(t_lo, t_hi, GRID_N):
            sim = simulate_tax(c, tc)
            if sim is None:
                continue
            n_cells += 1
            err = abs(sim - observed_tax)
            if err < best_err:
                best_err = err
                best_cell = (c, tc, sim)
    return best_cell, best_err, n_cells


def observed_taxes():
    """Return {project: brooks_tax_median} from lifts.csv."""
    taxes = {}
    with LIFTS.open() as f:
        for row in csv.DictReader(f):
            if (row['model'] == 'brooks'
                    and row['metric'] == 'brooks_tax_median'):
                try:
                    taxes[row['project']] = float(row['value'])
                except ValueError:
                    continue
    return taxes


def main():
    taxes = observed_taxes()
    rows  = []
    for project, obs in sorted(taxes.items()):
        cell, err, n_cells = fit_one_project(obs)
        if cell is None:
            rows.append({
                'project':         project,
                'observed_tax':    f"{obs:+.4f}",
                'best_comm_coef':  '', 'best_train_coef': '',
                'sim_tax_at_best': '', 'abs_error': '',
                'n_grid_cells':    n_cells, 'seed': SEED,
            })
            print(f"  {project:8s} obs={obs:+.4f}  no fit")
            continue
        c, tc, sim = cell
        rows.append({
            'project':         project,
            'observed_tax':    f"{obs:+.4f}",
            'best_comm_coef':  f"{c:.5f}",
            'best_train_coef': f"{tc:.4f}",
            'sim_tax_at_best': f"{sim:+.4f}",
            'abs_error':       f"{err:.4f}",
            'n_grid_cells':    n_cells,
            'seed':            SEED,
        })
        print(f"  {project:8s} obs={obs:+.4f}  sim={sim:+.4f} "
              f"(err={err:.4f})  comm={c:.5f}  train={tc:.4f}")

    out_path = OUTPUTS / 'fit_brooks.csv'
    cols = ['project', 'observed_tax', 'best_comm_coef',
            'best_train_coef', 'sim_tax_at_best',
            'abs_error', 'n_grid_cells', 'seed']
    with out_path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {out_path}")


if __name__ == '__main__':
    main()
