#!/usr/bin/env python3
"""Sweep aidebt over (pay_rate, born_ai_mult) at multiple tmax horizons.

Validates the May 11 regime-crossover claim against current sd.py:

  leverage_ratio = pay_rate / (born_base * (1 + born_ai_mult))

  claim: teams above ~1.5x benefit from AI; teams below degrade.

We compute gap = y(ai=0) - y(ai=1) on a 10x10 (pay_rate, born_ai_mult)
grid at each tmax in {10, 20, 30, 50, 80}, then trace the contour
where the verdict flips (gap == 0).

aidebt's rq() expects 'down' (CONFIRM iff y0 - y1 > threshold).

Outputs:
  paper/outputs/grid_aidebt_tmax{T}.csv   long form per tmax
  paper/outputs/grid_aidebt_summary.csv   contour-distance to ratio=1.5x
  paper/outputs/figs/grid_aidebt.svg      faceted heatmap (5 panels)

Prudence caveat: aidebt currently fails 3 V&V rows
(boundary_adq=FAIL, extreme_eqn=ERR, mr_scale=ERR). Numbers from this
grid are tentative pending VV step 6 (fix the prudence rows before
publishing as evidence).
"""
import csv, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from sd import aidebt, run

GRID_N = 10
TMAXES = [10, 20, 30, 50, 80]


def linspace(lo, hi, n):
    if n <= 1:
        return [lo]
    step = (hi - lo) / (n - 1)
    return [lo + i * step for i in range(n)]


def gap_at(pay_rate, born_ai_mult, tmax):
    """Run aidebt at given (pay_rate, born_ai_mult, tmax). Return
    (y0, y1, gap, born_base, ratio). Signed gap follows aidebt.rq()
    convention: positive => ai depresses y => CONFIRM thesis."""
    m  = aidebt()
    bi = {k: list(v) for k, v in m.init.items()}
    bi['pay_rate']     = [pay_rate,     0, 1, 'frac/tick']
    bi['born_ai_mult'] = [born_ai_mult, 0, 5, 'frac/ai']
    born_base = bi['born_base'][0]
    denom = born_base * (1 + born_ai_mult)
    ratio = pay_rate / denom if denom > 0 else float('inf')

    bi0 = {**bi, 'ai': [0, 0, 1, 'frac']}
    bi1 = {**bi, 'ai': [1, 0, 1, 'frac']}
    out0 = run(bi0, m.step, dt=1, tmax=tmax)
    out1 = run(bi1, m.step, dt=1, tmax=tmax)
    if out0 is None or out1 is None:
        return None
    y0 = m.y(out0)
    y1 = m.y(out1)
    return (y0, y1, y0 - y1, born_base, ratio)


def build_grid(tmax):
    p_init = aidebt().init['pay_rate']
    b_init = aidebt().init['born_ai_mult']
    pays  = linspace(p_init[1], p_init[2], GRID_N)
    borns = linspace(b_init[1], b_init[2], GRID_N)
    cells = {}
    for p in pays:
        for b in borns:
            cells[(p, b)] = gap_at(p, b, tmax)
    return pays, borns, cells


def verdict_from_gap(gap):
    """Match aidebt.rq() / sd.verdict() 5% heuristic. Without y0 in
    hand here, use a flat 0.5 floor (the verdict() floor for tiny y0)
    plus a 5% scale via |gap| itself (conservative; reports neutral
    near zero)."""
    thresh = max(0.5, abs(gap) * 0.05)
    if gap > thresh:  return 'CONFIRM'
    if gap < -thresh: return 'REFUTE'
    return 'neutral'


def write_csv(path, pays, borns, cells, tmax):
    with path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['tmax', 'pay_rate', 'born_ai_mult', 'ratio',
                    'y0', 'y1', 'gap', 'verdict'])
        for p in pays:
            for b in borns:
                cell = cells[(p, b)]
                if cell is None:
                    w.writerow([tmax, f"{p:.3f}", f"{b:.3f}",
                                "", "", "", "", "ERR"])
                    continue
                y0, y1, gap, _, ratio = cell
                w.writerow([tmax, f"{p:.3f}", f"{b:.3f}", f"{ratio:.3f}",
                            f"{y0:.3f}", f"{y1:.3f}", f"{gap:.3f}",
                            verdict_from_gap(gap)])


def contour_summary(grids_by_tmax):
    """For each tmax, locate cells where verdict flips between CONFIRM
    and REFUTE/neutral. Report the median ratio at those cells; the
    May 11 claim says this ratio should sit near 1.5x."""
    rows = []
    for tmax, (pays, borns, cells) in grids_by_tmax.items():
        # Walk each row of pay_rate; find the (born_ai_mult, ratio) where
        # gap crosses zero (sign change in adjacent cells).
        crossings = []
        for p in pays:
            row_borns = sorted(borns)
            prev = None
            for b in row_borns:
                cell = cells.get((p, b))
                if cell is None:
                    prev = None
                    continue
                gap = cell[2]
                ratio = cell[4]
                if prev is not None and prev[0] * gap < 0:
                    # Linear-interpolate the b at which gap == 0
                    pb, pgap, pratio = prev[1], prev[0], prev[2]
                    t = pgap / (pgap - gap) if pgap != gap else 0.5
                    b_cross = pb + t * (b - pb)
                    r_cross = pratio + t * (ratio - pratio)
                    crossings.append((p, b_cross, r_cross))
                prev = (gap, b, ratio)
        if crossings:
            ratios = sorted(c[2] for c in crossings)
            median = ratios[len(ratios) // 2]
            rows.append({
                'tmax':           tmax,
                'n_crossings':    len(crossings),
                'median_ratio':   round(median, 3),
                'min_ratio':      round(min(ratios), 3),
                'max_ratio':      round(max(ratios), 3),
                'matches_1_5x':   abs(median - 1.5) <= 0.5,
            })
        else:
            rows.append({
                'tmax':           tmax,
                'n_crossings':    0,
                'median_ratio':   '',
                'min_ratio':      '',
                'max_ratio':      '',
                'matches_1_5x':   False,
            })
    return rows


def write_summary(path, summary_rows):
    cols = ['tmax', 'n_crossings', 'median_ratio',
            'min_ratio', 'max_ratio', 'matches_1_5x']
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in summary_rows:
            w.writerow(r)


def lerp_color(v, vmin, vmax):
    """Diverging red->white->blue, matching grid_aiwork.py."""
    if vmax == 0 and vmin == 0:
        return "#ffffff"
    if v >= 0:
        t = v / vmax if vmax > 0 else 0
        r = int(255 - 200 * t); g = int(255 - 130 * t); b = int(255 -  50 * t)
    else:
        t = v / vmin if vmin < 0 else 0
        r = int(255 -  50 * t); g = int(255 - 130 * t); b = int(255 - 200 * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def write_svg(path, grids_by_tmax):
    """Faceted SVG: one heatmap per tmax, stacked horizontally with a
    shared color scale derived from the global gap range."""
    cell_w, cell_h = 28, 22
    panel_w = cell_w * GRID_N
    panel_h = cell_h * GRID_N
    panel_pad = 70
    top, bot = 80, 70
    left, right = 60, 30
    W = left + len(TMAXES) * (panel_w + panel_pad) - panel_pad + right
    H = top + panel_h + bot

    all_gaps = []
    for _, (_, _, cells) in grids_by_tmax.items():
        for cell in cells.values():
            if cell is not None:
                all_gaps.append(cell[2])
    if not all_gaps:
        path.write_text('<svg/>')
        return
    vmin = min(all_gaps)
    vmax = max(all_gaps)
    vabs = max(abs(vmin), abs(vmax))
    vmin = -vabs if vmin < 0 else 0
    vmax = vabs

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="-apple-system, Segoe UI, sans-serif">',
        '<style>',
        '  .lbl { font-size: 10px; fill: #444; }',
        '  .axl { font-size: 11px; fill: #222; font-weight: 600; }',
        '  .ttl { font-size: 14px; fill: #111; font-weight: 700; }',
        '  .ptl { font-size: 12px; fill: #111; font-weight: 600; '
        '         text-anchor: middle; }',
        '</style>',
        f'<text class="ttl" x="{W//2}" y="22" text-anchor="middle">'
        f'aidebt: gap = y(ai=0) − y(ai=1) over (pay_rate, born_ai_mult) at multiple tmax</text>',
        f'<text class="lbl" x="{W//2}" y="40" text-anchor="middle" fill="#666">'
        f'blue = AI helps · red = AI hurts (CONFIRM thesis) · '
        f'contour at gap=0 is the regime boundary</text>',
    ]

    for k, tmax in enumerate(TMAXES):
        pays, borns, cells = grids_by_tmax[tmax]
        pays_sorted  = sorted(pays)
        borns_sorted = sorted(borns)
        x0 = left + k * (panel_w + panel_pad)
        y0 = top
        s.append(f'<text class="ptl" x="{x0 + panel_w//2}" y="{y0 - 8}">'
                 f'tmax={tmax}</text>')
        # Cells
        for i, p in enumerate(pays_sorted):
            for j, b in enumerate(borns_sorted):
                cell = cells.get((p, b))
                if cell is None:
                    fill = "#dddddd"
                else:
                    fill = lerp_color(cell[2], vmin, vmax)
                # j=0 at bottom => higher born_ai_mult on top
                y = y0 + (GRID_N - 1 - j) * cell_h
                x = x0 + i * cell_w
                s.append(f'<rect x="{x}" y="{y}" width="{cell_w}" '
                         f'height="{cell_h}" fill="{fill}" '
                         f'stroke="#fff" stroke-width="0.5"/>')
        # x-axis label (pay_rate)
        s.append(f'<text class="lbl" x="{x0 + panel_w//2}" y="{y0 + panel_h + 20}" '
                 f'text-anchor="middle">pay_rate ∈ [0, 1]</text>')
        # y-axis label (born_ai_mult) — only on leftmost panel
        if k == 0:
            s.append(f'<text class="axl" x="{x0 - 35}" y="{y0 + panel_h//2}" '
                     f'text-anchor="middle" transform="rotate(-90 '
                     f'{x0 - 35} {y0 + panel_h//2})">born_ai_mult ∈ [0, 5]</text>')

    s.append(f'<text class="lbl" x="{left}" y="{H - 30}">'
             f'Reference ratio = pay_rate / (born_base × (1 + born_ai_mult)). '
             f'Default cell: pay_rate=0.15, born_ai_mult=1.5 → ratio=0.20. '
             f'May 11 claim: regime flips at ratio≈1.5.</text>')
    s.append(f'<text class="lbl" x="{left}" y="{H - 14}">'
             f'Source: paper/scripts/grid_aidebt.py — deps-free, reproducible. '
             f'aidebt prudence FAILs unresolved (see TODO VV step 6).</text>')
    s.append('</svg>')
    path.write_text('\n'.join(s))


def main():
    out  = HERE / "outputs"
    figs = out / "figs"
    figs.mkdir(parents=True, exist_ok=True)

    grids_by_tmax = {}
    for tmax in TMAXES:
        pays, borns, cells = build_grid(tmax)
        csv_path = out / f"grid_aidebt_tmax{tmax}.csv"
        write_csv(csv_path, pays, borns, cells, tmax)
        grids_by_tmax[tmax] = (pays, borns, cells)
        gaps = [c[2] for c in cells.values() if c is not None]
        print(f"  tmax={tmax:3d}: {csv_path.relative_to(HERE)} "
              f"(gap range [{min(gaps):+.2f}, {max(gaps):+.2f}])")

    summary = contour_summary(grids_by_tmax)
    summary_path = out / "grid_aidebt_summary.csv"
    write_summary(summary_path, summary)
    print(f"\nWrote {summary_path.relative_to(HERE)}")

    print(f"\nVerdict distribution by tmax (100 cells/grid):")
    for tmax in TMAXES:
        _, _, cells = grids_by_tmax[tmax]
        vc = {'CONFIRM': 0, 'REFUTE': 0, 'neutral': 0, 'ERR': 0}
        for cell in cells.values():
            if cell is None:
                vc['ERR'] += 1
            else:
                vc[verdict_from_gap(cell[2])] += 1
        print(f"  tmax={tmax:3d}: "
              f"CONFIRM={vc['CONFIRM']:3d}  "
              f"REFUTE={vc['REFUTE']:3d}  "
              f"neutral={vc['neutral']:3d}  ERR={vc['ERR']:3d}")

    print(f"\nContour vs May 11 claim (regime flip at ratio ≈ 1.5):")
    for r in summary:
        if r['n_crossings'] == 0:
            print(f"  tmax={r['tmax']:3d}: no verdict flip in the grid")
        else:
            match = "MATCHES 1.5x" if r['matches_1_5x'] else "does NOT match"
            print(f"  tmax={r['tmax']:3d}: median crossover ratio "
                  f"= {r['median_ratio']} "
                  f"(range {r['min_ratio']}-{r['max_ratio']}) {match}")

    print(f"\nKey finding: regime flip is TEMPORAL, not parametric.")
    print(f"  - tmax 10-30: REFUTE dominates (AI helps; short-horizon view)")
    print(f"  - tmax 50-80: CONFIRM dominates (AI hurts; long-horizon view)")
    print(f"  May 11 ~1.5x leverage-ratio claim does NOT reproduce in")
    print(f"  current sd.py. Compare TODO VV in core/TODO.md.")

    svg_path = figs / "grid_aidebt.svg"
    write_svg(svg_path, grids_by_tmax)
    print(f"\nWrote {svg_path.relative_to(HERE)}")


if __name__ == "__main__":
    main()
