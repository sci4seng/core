#!/usr/bin/env python3
"""Item 8: sd.opt() calibration pass.

For each model, run sd.opt() over the middle 60% of each param's
declared [lo, hi] (narrow=0.6) and ask: at the discovered best-y
parameter setting, does the model's thesis (rq) still hold?

This sits between S15 (substitute Helix-lifted values, rerun rq)
and a true inverse-fit calibration. S15 swapped in observed param
values one project at a time; this pass instead searches the
declared param ranges for a y-maximising point and tests the
thesis there. The aim is a methodology paper finding:

  "Across the middle 60% of the author-declared param ranges,
   the V&V-passing models retain their CONFIRM verdicts at the
   opt-discovered best-y settings; the thesis is robust to
   plausible parameterisation."

ctrl is held at its declared default during the opt search (we
want to find best-y *background* params, then let rq's own ctrl
sweep evaluate the thesis on top).

Output: outputs/calibration_opt.csv with one row per model:

  model, default_y, opt_best_y, y_gain_pct,
  default_verdict, default_gap, opt_verdict, opt_gap,
  verdict_changed, top_shifts

top_shifts is a ';'-joined list of the three params with the
largest fractional shift from their author defaults under the
opt-best setting.
"""

import csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from sd import ALL_MODELS, run, opt


def _shift_metric(default, best, lo, hi):
    """Fractional shift normalised by the declared range. Returns
    (signed_shift, abs_shift). Used to rank which params moved
    furthest under opt."""
    span = max(hi - lo, 1e-9)
    s = (best - default) / span
    return s, abs(s)


def calibrate_one(factory, n=1000, seed=1):
    m = factory()
    ctrl = m.ctrl
    # Freeze ctrl during opt: shrink its [lo,hi] to [default,default]
    # so the sampler can't move it. Other specs unchanged.
    init0 = {}
    for k, spec in m.init.items():
        d, lo, hi = spec[0], spec[1], spec[2]
        units = spec[3] if len(spec) >= 4 else ''
        if k == ctrl:
            init0[k] = [d, d, d, units]
        else:
            init0[k] = list(spec)

    # Default-state metrics (run with author defaults).
    default_run = run(m.init, m.step)
    default_y = m.y(default_run)
    default_rq = m.rq()

    # opt search.
    result = opt(factory, init=init0, n=n, seed=seed)
    opt_best_y, opt_best_params = result['best']

    # Build a background dict from opt-best params (preserve units)
    # and ask rq() to evaluate the thesis under those params.
    opt_bg = {}
    for k, spec in m.init.items():
        lo, hi = spec[1], spec[2]
        units = spec[3] if len(spec) >= 4 else ''
        if k == ctrl:
            opt_bg[k] = list(spec)
        else:
            opt_bg[k] = [opt_best_params[k], lo, hi, units]
    opt_rq = m.rq(bg=opt_bg)

    # Rank params by fractional shift; report top 3 (excluding ctrl).
    shifts = []
    for k, spec in m.init.items():
        if k == ctrl:
            continue
        d, lo, hi = spec[0], spec[1], spec[2]
        signed, mag = _shift_metric(d, opt_best_params[k], lo, hi)
        shifts.append((mag, signed, k))
    shifts.sort(reverse=True)
    top_shifts = ';'.join(f"{k}{'+' if s > 0 else ''}{s:.2f}"
                          for _, s, k in shifts[:3])

    # Gain in % is ill-defined when default_y is near 0 (defmap's
    # param balance gives y=0 at default). Mark as 'inf' so the
    # CSV reader doesn't mistake the resulting astronomic ratio
    # for a meaningful gain.
    if abs(default_y) < 1.0:
        y_gain_disp = 'inf'
    else:
        y_gain_disp = f"{(opt_best_y - default_y) / abs(default_y) * 100:+.1f}"
    return {
        'model': factory.__name__,
        'default_y': f"{default_y:+.2f}",
        'opt_best_y': f"{opt_best_y:+.2f}",
        'y_gain_pct': y_gain_disp,
        'default_verdict': default_rq['verdict'],
        'default_gap': f"{default_rq['gap']:+.2f}",
        'opt_verdict': opt_rq['verdict'],
        'opt_gap': f"{opt_rq['gap']:+.2f}",
        'verdict_changed': (default_rq['verdict'] != opt_rq['verdict']),
        'top_shifts': top_shifts,
    }


def main():
    rows = []
    for factory in ALL_MODELS:
        try:
            rows.append(calibrate_one(factory))
            print(f"  {factory.__name__:18s} "
                  f"d={rows[-1]['default_verdict']:8s} "
                  f"o={rows[-1]['opt_verdict']:8s} "
                  f"gain={rows[-1]['y_gain_pct']:>8s}% "
                  f"shifts={rows[-1]['top_shifts']}")
        except Exception as e:
            print(f"  {factory.__name__:18s} ERR: {type(e).__name__}: {e}")
            rows.append({'model': factory.__name__,
                         'default_y': 'ERR', 'opt_best_y': 'ERR',
                         'y_gain_pct': '', 'default_verdict': 'ERR',
                         'default_gap': '', 'opt_verdict': 'ERR',
                         'opt_gap': '', 'verdict_changed': '',
                         'top_shifts': str(e)})

    out_path = HERE / 'outputs' / 'calibration_opt.csv'
    cols = ['model', 'default_y', 'opt_best_y', 'y_gain_pct',
            'default_verdict', 'default_gap',
            'opt_verdict', 'opt_gap', 'verdict_changed', 'top_shifts']
    with out_path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out_path}")

    # Headline counts and the verdict-shift breakdown.
    held = sum(1 for r in rows if r['verdict_changed'] is False)
    flipped = sum(1 for r in rows if r['verdict_changed'] is True)
    print(f"\n{held} models retain verdict at opt-best; "
          f"{flipped} flip.")
    shifts = {}
    for r in rows:
        if r['verdict_changed'] is True:
            key = f"{r['default_verdict']} -> {r['opt_verdict']}"
            shifts[key] = shifts.get(key, 0) + 1
    for key, n in sorted(shifts.items(), key=lambda kv: -kv[1]):
        print(f"  {key:24s} {n}")


if __name__ == '__main__':
    main()
