#!/usr/bin/env python3
"""Generate Just-the-Docs markdown site from paper/outputs/*.csv.

Replaces the older HTML generator (gen_rich.py). Each model page is
one small MD file (~50–100 lines). Site is walkable by reading the
raw MD files in nested dirs — Jekyll just adds nav + search on top.

Outputs (under docs/):
  models/index.md
  models/<name>.md   (one per model in full_audit.csv)
  findings.md        (derived from outputs/* highlights)
  data.md            (per-project lift coverage from lifts.csv)
"""
import csv, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE    = Path(__file__).resolve()
DOCS    = HERE.parents[1]              # core/docs
ROOT    = HERE.parents[2]              # core/
OUTPUTS = ROOT / "paper" / "outputs"

AUDIT   = {r["model"]: r for r in csv.DictReader((OUTPUTS / "full_audit.csv").open())}
BOUNDS  = defaultdict(list)
for r in csv.DictReader((OUTPUTS / "boundary_check.csv").open()):
    BOUNDS[r["model"]].append(r)
CALIB   = {r["model"]: r for r in csv.DictReader((OUTPUTS / "calibrated_verdicts.csv").open())}
LIFTS   = defaultdict(list)
for r in csv.DictReader((OUTPUTS / "lifts.csv").open()):
    LIFTS[r["model"]].append(r)


def front_matter(title, parent=None, nav_order=None, has_children=False):
    lines = ["---", f"title: {title}"]
    if parent:       lines.append(f"parent: {parent}")
    if nav_order is not None: lines.append(f"nav_order: {nav_order}")
    if has_children: lines.append("has_children: true")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def render_model(name, audit, idx):
    bc = BOUNDS.get(name, [])
    cv = CALIB.get(name)
    lf = LIFTS.get(name, [])

    cell = audit["cell"]
    out = [front_matter(name, parent="Models", nav_order=idx)]
    out.append(f"# {name}\n")
    out.append(f"Cell: **{cell}** &middot; "
               f"`verdict`: {audit['verdict']} (gap {audit['gap']}) &middot; "
               f"`verdict_n`: {audit['verdict_n']} (gap {audit['gap_n']})\n")

    # --- Effect summary ---
    out.append("## Verdict (N=100 stats-grade)\n")
    out.append("| metric | value |\n|---|---|\n")
    for k in ["verdict_n", "gap_n", "sd0_n", "sd1_n", "eps_n"]:
        out.append(f"| `{k}` | {audit[k]} |\n")
    out.append(f"| stress(inputs) | {audit['inp_cnt']} / 200 CONFIRM |\n")
    out.append(f"| stress(params) | {audit['par_cnt']} / 200 CONFIRM |\n")
    out.append(f"| 2x2 cell | **{cell}** |\n\n")

    # --- Tier 1: Structural V&V ---
    out.append("## Tier 1 — Structural V&V (prudence)\n")
    out.append("| test | result |\n|---|---|\n")
    for t in ["boundary_adq","anomaly_check","extreme_eqn","mr_zero_input",
              "mr_monotone","mr_dt_halving","mr_bound_consist","mr_scale"]:
        out.append(f"| `{t}` | {audit.get(t,'')} |\n")
    out.append("\n")

    # --- Tier 2: Data-tier (auto from lift CSVs) ---
    out.append("## Tier 2 — Data-tier checks (auto from lift CSVs)\n")
    out.append("| test | result |\n|---|---|\n")

    # param_plausibility
    if not bc:
        pp = "N/A — no lift rows"
    else:
        n_in  = sum(1 for r in bc if r["status"] == "in_range")
        n_at  = sum(1 for r in bc if r["status"] == "at_boundary")
        n_out = sum(1 for r in bc if r["status"] == "out_of_range")
        n    = len(bc)
        if n_out:
            pp = f"**FAIL** &middot; {n_out}/{n} out_of_range, {n_at} at_boundary, {n_in} in_range"
        elif n_at:
            pp = f"warn &middot; {n_at}/{n} at_boundary, {n_in} in_range"
        else:
            pp = f"PASS &middot; {n_in}/{n} in_range"
    out.append(f"| `param_plausibility` | {pp} |\n")

    # boundary_adq_data
    if not bc:
        ba = "N/A — no lift rows"
    elif any(r["status"] in ("at_boundary","out_of_range") for r in bc):
        ba = "PASS — lifted values reach or exceed declared [lo, hi]"
    else:
        ba = "warn — all lifted values strictly inside [lo, hi]"
    out.append(f"| `boundary_adq_data` | {ba} |\n")

    # calibrated_rq_rerun
    if not cv:
        cr = "N/A — model not in calibrate.py"
    elif "no calib applied" in cv.get("notes",""):
        cr = f"N/A — default={cv['default_verdict']}; no overridable params"
    elif cv["changes_verdict"] == "False":
        cr = f"{cv['calib_verdict']} — verdict stable (default={cv['default_verdict']})"
    else:
        cr = f"{cv['calib_verdict']} — verdict changed (default={cv['default_verdict']})"
    out.append(f"| `calibrated_rq_rerun` | {cr} |\n")

    # family_member_coherence
    if not lf:
        fc = "N/A — no lift rows"
    else:
        projs = {r["project"] for r in lf}
        fc = f"{len(projs)} projects lifted (sign tally not auto-computed)"
    out.append(f"| `family_member_coherence` | {fc} |\n")

    out.append("| `behavior_reproduction` | not run — requires monthly historical CSV |\n\n")

    # --- Lift values per project (if any) ---
    if lf:
        out.append("## Lift values per project\n")
        # collect (project, metric) → value
        by_proj = defaultdict(dict)
        metrics_seen = []
        for r in lf:
            if r["metric"] not in metrics_seen:
                metrics_seen.append(r["metric"])
            by_proj[r["project"]][r["metric"]] = r["value"]
        # limit to top 5 metrics to keep page short
        metrics = metrics_seen[:5]
        out.append("| project | " + " | ".join(f"`{m}`" for m in metrics) + " |\n")
        out.append("|---" * (len(metrics) + 1) + "|\n")
        for proj in sorted(by_proj.keys()):
            row = [proj] + [str(by_proj[proj].get(m, "—"))[:12] for m in metrics]
            out.append("| " + " | ".join(row) + " |\n")
        if len(metrics_seen) > 5:
            out.append(f"\n_(showing first 5 of {len(metrics_seen)} metrics; "
                       f"full data in `paper/outputs/lifts.csv`)_\n")
        out.append("\n")

    # --- Boundary violations (if any) ---
    out_of_range = [r for r in bc if r["status"] == "out_of_range"]
    if out_of_range:
        out.append("## Boundary violations\n")
        out.append("| project | param | lifted | lo | hi |\n|---|---|---|---|---|\n")
        for r in out_of_range:
            out.append(f"| {r['project']} | `{r['param']}` | {r['lifted']} | "
                       f"{r['lo']} | {r['hi']} |\n")
        out.append("\n")

    # --- Pointers ---
    out.append("## Source\n")
    out.append(f"- SD model: `paper/sd.py::{name}()`\n")
    out.append(f"- Audit row: `paper/outputs/full_audit.csv` (line for `{name}`)\n")
    if lf:
        out.append(f"- Lift Rmd: `sci4seng/lifts/vignettes/lift_{name}.Rmd`\n")
    out.append("\n")
    return "".join(out)


def render_models_index(audit):
    out = [front_matter("Models", nav_order=4, has_children=True)]
    out.append("# Models (35)\n\n")
    out.append("One page per model. Sort by cell, then by name.\n\n")
    by_cell = defaultdict(list)
    for name, row in audit.items():
        by_cell[row["cell"]].append(name)
    for cell in ["universal", "process-conditional", "fragile",
                 "world-conditional"]:
        items = sorted(by_cell.get(cell, []))
        if not items: continue
        out.append(f"## {cell} ({len(items)})\n\n")
        for n in items:
            r = audit[n]
            out.append(f"- [{n}]({n}.md) &middot; "
                       f"`verdict_n`: {r['verdict_n']} &middot; "
                       f"`inp_cnt`: {r['inp_cnt']}/200, "
                       f"`par_cnt`: {r['par_cnt']}/200\n")
        out.append("\n")
    return "".join(out)


def render_findings(audit, lifts):
    out = [front_matter("Findings", nav_order=2)]
    out.append("# Headline findings (F0–F5)\n\n")
    # F0: stats-grade verdict distribution
    c = Counter(r["verdict_n"] for r in audit.values())
    total = sum(c.values())
    out.append("## F0 — Most published SE theses dissolve under stats\n\n")
    out.append(f"Of {total} models: ")
    out.append(", ".join(f"{v} {k}" for k, v in c.most_common()) + ".\n\n")
    pct_neutral = 100 * c.get("neutral", 0) / max(1, total)
    out.append(f"Roughly {pct_neutral:.0f}% are stats-grade neutral — "
               "the single-shot CONFIRM is hiding noise as signal. "
               "Either narrow ranges via lift, or accept the thesis is "
               "not statistically detectable under author-declared priors.\n\n")

    # F0 boundary violations
    out.append("## F0 — Boundary-adequacy violations\n\n")
    bc_path = OUTPUTS / "boundary_check.csv"
    bc = list(csv.DictReader(bc_path.open()))
    n_out = sum(1 for r in bc if r["status"] == "out_of_range")
    n_at  = sum(1 for r in bc if r["status"] == "at_boundary")
    n_in  = sum(1 for r in bc if r["status"] == "in_range")
    out.append(f"{n_out} `out_of_range`, {n_at} `at_boundary`, "
               f"{n_in} `in_range` cells across all lifted (model × project) pairs.\n\n")
    out.append("Per-model breakdowns live on each [model page](models/).\n\n")

    # F3 spread example
    out.append("## F3 — Brooks effect varies 11× across projects\n\n")
    brooks_rows = [r for r in lifts.get("brooks", [])
                   if r["metric"] == "brooks_tax_median"]
    if brooks_rows:
        vals = sorted((float(r["value"]), r["project"]) for r in brooks_rows)
        out.append("| project | brooks_tax_median |\n|---|---|\n")
        for v, p in vals:
            out.append(f"| {p} | {v:+.3f} |\n")
        out.append("\n")
    out.append("See [brooks](models/brooks.md) for the full discussion.\n\n")
    return "".join(out)


def render_data(audit, lifts):
    out = [front_matter("Data", nav_order=5)]
    out.append("# Data sources\n\n")
    out.append("Raw project data is **not** in this repo. Drop bundles into "
               "[sci4seng/data/dropzone/](https://github.com/sci4seng/data) "
               "and run `make refresh` (see `paper/Makefile`).\n\n")
    projects = sorted({r["project"] for rs in lifts.values() for r in rs})
    out.append(f"## Per-project lift coverage ({len(projects)} projects)\n\n")
    out.append("| project | models lifted |\n|---|---|\n")
    by_proj = defaultdict(set)
    for m, rs in lifts.items():
        for r in rs:
            by_proj[r["project"]].add(m)
    for p in sorted(projects):
        ms = sorted(by_proj[p])
        out.append(f"| {p} | {len(ms)} — {', '.join(ms)} |\n")
    return "".join(out)


def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "models").mkdir(exist_ok=True)

    # Models index
    (DOCS / "models" / "index.md").write_text(render_models_index(AUDIT))

    # Per-model
    for i, name in enumerate(sorted(AUDIT.keys()), start=1):
        (DOCS / "models" / f"{name}.md").write_text(
            render_model(name, AUDIT[name], i))

    # Top-level pages
    (DOCS / "findings.md").write_text(render_findings(AUDIT, LIFTS))
    (DOCS / "data.md").write_text(render_data(AUDIT, LIFTS))

    n = len(AUDIT)
    print(f"Wrote {n} model pages + findings.md + data.md + models/index.md")
    print(f"  total: {n + 3} markdown files under {DOCS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
