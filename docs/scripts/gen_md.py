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
CANDIDATES_YML = DOCS / "_data" / "candidates.yml"   # 47-entry inventory


def load_candidates():
    """Parse docs/_data/candidates.yml — flat single-line yaml-ish.
    Each block: `- name: X` then 5 lines of `  key: "value"`."""
    if not CANDIDATES_YML.exists():
        return []
    out, cur = [], None
    for line in CANDIDATES_YML.read_text().splitlines():
        if line.startswith("- name: "):
            if cur: out.append(cur)
            cur = {"name": line[len("- name: "):].strip()}
        elif cur and ": " in line:
            k, _, v = line.strip().partition(": ")
            cur[k] = v.strip().strip('"')
    if cur: out.append(cur)
    return out

# Canonical kaiaulu vignette filenames per model + the structured
# extractor. Both live in sync_vignettes.py so SS(a)+SS(b) share one
# source of truth.
sys.path.insert(0, str(HERE.parent))  # docs/scripts/ on path
from sync_vignettes import MODEL_TO_VIGNETTE, extract_one, VIG

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


# --- Glossary linking ------------------------------------------------------
# Each scorecard panel mentions terms whose canonical defs live in
# docs/glossary.md. gloss() emits a markdown link with a hover tooltip
# (rendered by Jekyll as <a href="..." title="...">).
#
# Anchor + tooltip are looked up from this dict; bare terms not in the
# dict pass through as `name` with no link.

GLOSS = {
    "boundary_adq":       ("boundary_adq",       "F&S 4/7: tmax=80 verdict still holds"),
    "anomaly_check":      ("anomaly_check",      "F&S behaviour-anomaly: hi inputs do not flip y sign"),
    "extreme_eqn":        ("extreme_eqn",        "F&S extreme-conditions: no NaN/Inf at lo/hi inputs"),
    "mr_zero_input":      ("mr_zero_input",      "Chen MR3: ctrl=lo idempotent"),
    "mr_monotone":        ("mr_monotone",        "Chen MR1: y monotone in ctrl over 5 grid points"),
    "mr_dt_halving":      ("mr_dt_halving",      "Chen MR8 / Sterman 6: y invariant to dt/2"),
    "mr_bound_consist":   ("mr_bound_consist",   "Chen MR9: clip vs reject agree"),
    "mr_scale":           ("mr_scale",           "Chen MR2: 2x inputs do not flip sign or explode"),
    "rq":                 ("rq",                 "Single-shot research-question test"),
    "rq_n":               ("rq_n",               "N-shot rq with Cliff's d + KS + median-eps"),
    "verdict":            ("verdict",            "CONFIRM / REFUTE / neutral on (y0, y1)"),
    "verdict_n":          ("verdict_n",          "N-shot verdict via stats.same"),
    "gap":                ("gap",                "signed y1 - y0 from single-shot rq()"),
    "gap_n":              ("gap_n",              "pooled-mean y1 - y0 from rq_n"),
    "sd0_n":              ("sd0_n",              "stddev of y0 samples in rq_n"),
    "sd1_n":              ("sd1_n",              "stddev of y1 samples in rq_n"),
    "eps_n":              ("eps_n",              "0.35 * sd(y0): same-list tolerance"),
    "stress(inputs)":     ("stress_inputs",      "200 perturbed UPPER-input backgrounds"),
    "stress(params)":     ("stress_params",      "200 perturbed lower-param backgrounds"),
    "inp_cnt":            ("inp_cnt",            "CONFIRM count out of 200 input-perturbed runs"),
    "par_cnt":            ("par_cnt",            "CONFIRM count out of 200 param-perturbed runs"),
    "2x2 cell":           ("cell",               "{universal, process, world, fragile} from (inp_cnt, par_cnt)"),
    "universal":          ("universal",          "Both inputs and params CONFIRM"),
    "process-conditional":("process-conditional","Inputs CONFIRM, params not"),
    "world-conditional":  ("world-conditional",  "Params CONFIRM, inputs not"),
    "fragile":            ("fragile",            "Neither axis CONFIRMs in majority"),
    "Cliff's delta":      ("cliffs_delta",       "Non-parametric effect size; same iff |d|<=0.195"),
    "KS":                 ("ks",                 "Kolmogorov-Smirnov distance"),
    "param_plausibility": ("param_plausibility", "in_range/at_boundary/out_of_range from boundary_check.csv"),
    "boundary_adq_data":  ("boundary_adq_data",  "Lifted value reaches or exceeds declared [lo, hi]"),
    "calibrated_rq_rerun":("calibrated_rq_rerun","rq() under Helix-calibrated init"),
    "family_member_coherence": ("family_member_coherence", "Per-project sign agreement across the family"),
    "behavior_reproduction":   ("behavior_reproduction",   "Sim trajectory vs monthly historical CSV"),
}


def gloss(term, label=None, from_dir="models"):
    """Markdown link to docs/glossary.md anchor with hover tooltip.

    from_dir picks the relative prefix:
      "models"  -> ../glossary.md  (per-model pages)
      "root"    -> glossary.md     (findings.md / data.md / index)
    Bare terms not in GLOSS pass through unwrapped (still in backticks).
    """
    spec = GLOSS.get(term)
    visible = label or term
    if not spec:
        return f"`{visible}`"
    anchor, tip = spec
    prefix = "../glossary.md" if from_dir == "models" else "glossary.md"
    # Escape double quotes inside the tooltip
    safe_tip = tip.replace('"', "&quot;")
    return f'[`{visible}`]({prefix}#{anchor} "{safe_tip}")'


def render_model(name, audit, idx):
    bc = BOUNDS.get(name, [])
    cv = CALIB.get(name)
    lf = LIFTS.get(name, [])

    cell = audit["cell"]
    cell_link = gloss(cell) if cell in GLOSS else f"**{cell}**"
    out = [front_matter(name, parent="Models", nav_order=idx)]
    out.append(f"# {name}\n\n")
    out.append(f"Cell: {cell_link} &middot; "
               f"{gloss('verdict')}: {audit['verdict']} ({gloss('gap')} {audit['gap']}) &middot; "
               f"{gloss('verdict_n')}: {audit['verdict_n']} ({gloss('gap_n')} {audit['gap_n']})\n\n")

    # --- Effect summary ---
    out.append("## Verdict (N=100 stats-grade)\n\n")
    out.append("| metric | value |\n|---|---|\n")
    for k in ["verdict_n", "gap_n", "sd0_n", "sd1_n", "eps_n"]:
        out.append(f"| {gloss(k)} | {audit[k]} |\n")
    out.append(f"| {gloss('stress(inputs)')} | {audit['inp_cnt']} / 200 CONFIRM |\n")
    out.append(f"| {gloss('stress(params)')} | {audit['par_cnt']} / 200 CONFIRM |\n")
    out.append(f"| {gloss('2x2 cell')} | {cell_link} |\n\n")

    # --- Tier 1: Structural V&V ---
    out.append("## Tier 1 — Structural V&V (prudence)\n\n")
    out.append("| test | result |\n|---|---|\n")
    for t in ["boundary_adq","anomaly_check","extreme_eqn","mr_zero_input",
              "mr_monotone","mr_dt_halving","mr_bound_consist","mr_scale"]:
        out.append(f"| {gloss(t)} | {audit.get(t,'')} |\n")
    out.append("\n")

    # --- Tier 2: Data-tier (auto from lift CSVs) ---
    out.append("## Tier 2 — Data-tier checks (auto from lift CSVs)\n\n")
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
    out.append(f"| {gloss('param_plausibility')} | {pp} |\n")

    # boundary_adq_data
    if not bc:
        ba = "N/A — no lift rows"
    elif any(r["status"] in ("at_boundary","out_of_range") for r in bc):
        ba = "PASS — lifted values reach or exceed declared [lo, hi]"
    else:
        ba = "warn — all lifted values strictly inside [lo, hi]"
    out.append(f"| {gloss('boundary_adq_data')} | {ba} |\n")

    # calibrated_rq_rerun
    if not cv:
        cr = "N/A — model not in calibrate.py"
    elif "no calib applied" in cv.get("notes",""):
        cr = f"N/A — default={cv['default_verdict']}; no overridable params"
    elif cv["changes_verdict"] == "False":
        cr = f"{cv['calib_verdict']} — verdict stable (default={cv['default_verdict']})"
    else:
        cr = f"{cv['calib_verdict']} — verdict changed (default={cv['default_verdict']})"
    out.append(f"| {gloss('calibrated_rq_rerun')} | {cr} |\n")

    # family_member_coherence
    if not lf:
        fc = "N/A — no lift rows"
    else:
        projs = {r["project"] for r in lf}
        fc = f"{len(projs)} projects lifted (sign tally not auto-computed)"
    out.append(f"| {gloss('family_member_coherence')} | {fc} |\n")

    out.append(f"| {gloss('behavior_reproduction')} | not run — requires monthly historical CSV |\n\n")

    # --- Lift values per project (if any) ---
    if lf:
        out.append("## Lift values per project\n\n")
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
        out.append("## Boundary violations\n\n")
        out.append("| project | param | lifted | lo | hi |\n|---|---|---|---|---|\n")
        for r in out_of_range:
            out.append(f"| {r['project']} | `{r['param']}` | {r['lifted']} | "
                       f"{r['lo']} | {r['hi']} |\n")
        out.append("\n")

    # --- Vignette excerpt (auto-synced from kaiaulu-style Rmd) ---
    vname = MODEL_TO_VIGNETTE.get(name)
    if vname:
        rmd = VIG / f"{vname}.Rmd"
        if rmd.exists():
            ex = extract_one(rmd)
            if ex["intro"]:
                out.append("## Lift methodology (from vignette)\n\n")
                out.append(ex["intro"] + "\n\n")
            if ex["verdict"]:
                out.append("## Lift verdict on the project\n\n")
                out.append(ex["verdict"] + "\n\n")
            if ex["discussion"]:
                out.append("## Sanity checks\n\n")
                out.append(ex["discussion"] + "\n\n")
            if ex["refs"]:
                out.append("## References\n\n")
                for r in ex["refs"]:
                    out.append(f"- {r}\n")
                out.append("\n")

    # --- Pointers ---
    out.append("## Source\n\n")
    out.append(f"- SD model: `paper/sd.py::{name}()`\n")
    out.append(f"- Audit row: `paper/outputs/full_audit.csv` (line for `{name}`)\n")
    if lf:
        vname2 = MODEL_TO_VIGNETTE.get(name, f"lift_{name}")
        out.append(f"- Lift Rmd: `sci4seng/lifts/vignettes/{vname2}.Rmd`\n")
    out.append("\n")
    return "".join(out)


def render_models_index(audit, candidates):
    n_active = len(audit)
    future = [c for c in candidates if c["name"] not in audit]
    out = [front_matter("Models", nav_order=4, has_children=True)]
    out.append(f"# Models — {n_active} active, {len(future)} future-work\n\n")
    out.append(f"- **{n_active} active**: SD model in `paper/sd.py`, "
               "audit row in `full_audit.csv`, per-model page below.\n")
    out.append(f"- **{len(future)} future-work**: named in the SE literature "
               "but not yet built. See [future-work candidates](future).\n\n")
    out.append("## Active models, grouped by 2x2 cell\n\n")
    by_cell = defaultdict(list)
    for name, row in audit.items():
        by_cell[row["cell"]].append(name)
    for cell in ["universal", "process-conditional", "fragile",
                 "world-conditional"]:
        items = sorted(by_cell.get(cell, []))
        if not items: continue
        out.append(f"### {cell} ({len(items)})\n\n")
        for n in items:
            r = audit[n]
            out.append(f"- [{n}]({n}.md) &middot; "
                       f"`verdict_n`: {r['verdict_n']} &middot; "
                       f"`inp_cnt`: {r['inp_cnt']}/200, "
                       f"`par_cnt`: {r['par_cnt']}/200\n")
        out.append("\n")
    return "".join(out)


def render_future(audit, candidates):
    """Emit models/future.md from candidates.yml minus current audit set."""
    future = [c for c in candidates if c["name"] not in audit]
    out = [front_matter("Future-work candidates", parent="Models", nav_order=99)]
    out.append(f"# Future-work candidates ({len(future)})\n\n")
    out.append("Named in the SE literature but not yet built into "
               "`paper/sd.py`. Source-quality tiers:\n\n")
    out.append("- **A** = peer-reviewed archival (DOI / IEEE / ACM / journal)\n")
    out.append("- **B** = book or grey-lit anchor; partial peer-reviewed companion\n")
    out.append("- **C** = tacit / named-only / not formally modelled\n\n")
    out.append("Data legend:\n\n")
    out.append("- **have**: data on disk now, lift could run\n")
    out.append("- **partial**: would need 1–2 days of new pipeline\n")
    out.append("- **none**: structurally absent on the 8-project family\n\n")

    # Group by tier
    by_tier = defaultdict(list)
    for c in future:
        by_tier[c["tier"]].append(c)
    for tier in ("A", "B", "C"):
        items = sorted(by_tier.get(tier, []), key=lambda x: x["name"])
        if not items: continue
        out.append(f"## Tier {tier} ({len(items)})\n\n")
        out.append("| name | year | source | data |\n|---|---|---|---|\n")
        for c in items:
            yr   = c.get("year", "—") or "—"
            src  = (c.get("source") or "").replace("|", "\\|")[:120]
            data = c.get("data", "?")
            note = (c.get("data_note") or "").replace("|", "\\|")[:80]
            dstr = f"**{data}**" if data == "have" else data
            if note: dstr += f" — {note}"
            out.append(f"| `{c['name']}` | {yr} | {src} | {dstr} |\n")
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


def render_glossary():
    out = [front_matter("Glossary", nav_order=6)]
    out.append("# Glossary\n\n")
    out.append(
      "Each scorecard term on the model pages links here for a one-line "
      "definition, a literature citation, and a deep link into the "
      "implementation in `paper/`. Hover any linked term in a model "
      "scorecard for the same tooltip.\n\n"
    )

    sections = [
      ("Forrester &amp; Senge / Sterman structural tests",
       "Eight automated structural tests run against every model. "
       "First three are Forrester &amp; Senge (1980); next five are "
       "metamorphic relations after Chen et al. (1998). "
       "Source: `paper/tests.py`.",
       [
         ("boundary_adq",
          "Re-run `rq()` at `tmax=80` (4× default horizon). FAIL if "
          "the verdict flips — the time-horizon boundary is load-bearing.",
          "Forrester &amp; Senge (1980) test 4/7.",
          "paper/tests.py:32"),
         ("anomaly_check",
          "Compare baseline `y` to a stressed run with every UPPER "
          "input at its `hi`. FAIL on qualitative sign-flip.",
          "Forrester &amp; Senge (1980) behaviour-anomaly test.",
          "paper/tests.py:50"),
         ("extreme_eqn",
          "Run with each UPPER input set to its `lo` and `hi` in turn. "
          "FAIL on any NaN, ±Inf in any state.",
          "Forrester &amp; Senge (1980) extreme-conditions test.",
          "paper/tests.py:70"),
         ("mr_zero_input",
          "Setting `ctrl` to its `lo` bound must produce the same "
          "trajectory as a baseline with `ctrl` explicitly held at `lo`.",
          "Chen et al. (1998) metamorphic relation MR3.",
          "paper/tests.py:97"),
         ("mr_monotone",
          "Sweep `ctrl` across 5 grid points in `[lo,hi]`. `y` must "
          "be monotone in the direction predicted by `rq()`.",
          "Chen et al. (1998) MR1.",
          "paper/tests.py:118"),
         ("mr_dt_halving",
          "Halve the integration step `dt`. `y` must agree within 10% — "
          "Sterman's integration-error check.",
          "Chen et al. (1998) MR8; Sterman (2000) test 6.",
          "paper/tests.py:143"),
         ("mr_bound_consist",
          "Run with `mode='reject'` vs `'clip'`. FAIL if `reject` "
          "aborts or if outputs differ — clamping was load-bearing.",
          "Chen et al. (1998) MR9.",
          "paper/tests.py:158"),
         ("mr_scale",
          "Scale all UPPER inputs by 2×. FAIL on sign-flip or 100× "
          "explosion. Nonlinear `y_ratio` is expected, not a bug.",
          "Chen et al. (1998) MR2 (linearity probe).",
          "paper/tests.py:176"),
       ]),
      ("rq() and verdict family",
       "Per-model research-question test and its N-shot stats-grade "
       "replacement. Source: `paper/sd.py`.",
       [
         ("rq",
          "Single-shot research-question test. Returns "
          "`{verdict, y0, y1, gap, desc}`.",
          "MYTHS framework primitive.",
          "paper/sd.py:82"),
         ("rq_n",
          "Sample N perturbed backgrounds (default N=100, triangular). "
          "Run `y0` and `y1` per sample. Classify via `stats.same` "
          "(Cliff's δ + KS + median-ε).",
          "MYTHS framework primitive.",
          "paper/sd.py:209"),
         ("verdict",
          "Single-shot verdict on `(y0, y1)`. CONFIRM if signed gap "
          "exceeds `max(5% · |y0|, 0.5)`; REFUTE if against; else neutral.",
          "",
          "paper/sd.py:82"),
         ("verdict_n",
          "Stats-grade verdict over two y-lists. `neutral` iff "
          "`stats.same(y0s, y1s, ε)`; else sign of `mean(y0)−mean(y1)`.",
          "",
          "paper/sd.py:93"),
         ("gap",
          "Signed `y1 − y0` from a single-shot `rq()` call.",
          "",
          "paper/sd.py:82"),
         ("gap_n",
          "Pooled-mean gap from `rq_n`: `mean(y1s) − mean(y0s)`. "
          "Reported with `sd0_n`, `sd1_n`, `eps_n`.",
          "",
          "paper/sd.py:93"),
         ("sd0_n",
          "Sample standard deviation of `y0s` from `rq_n`.",
          "",
          "paper/sd.py:93"),
         ("sd1_n",
          "Sample standard deviation of `y1s` from `rq_n`.",
          "",
          "paper/sd.py:93"),
         ("eps_n",
          "Same-list tolerance used by `stats.same`: `0.35 · sd(y0s)`.",
          "Knob: `the.stats.eps = 0.35`.",
          "paper/stats.py:65"),
       ]),
      ("Stress matrix and 2x2 typology",
       "Per-model classification from 200 perturbed-background runs.",
       [
         ("stress_inputs",
          "Run `rq()` on 200 triangular-perturbed backgrounds with only "
          "UPPER-case state variables perturbed (the world axis).",
          "",
          "paper/sd.py:161"),
         ("stress_params",
          "Same harness, lower-case (parameter) perturbation only — "
          "the process axis.",
          "",
          "paper/sd.py:161"),
         ("inp_cnt",
          "CONFIRM count out of 200 input-perturbed runs.",
          "",
          "paper/tests.py:208"),
         ("par_cnt",
          "CONFIRM count out of 200 param-perturbed runs.",
          "",
          "paper/tests.py:208"),
         ("cell",
          "2x2 classification from (inputs, params) verdict pair. "
          "CONFIRM on a side requires ≥50%; REFUTE requires ≥20%.",
          "",
          "paper/tests.py:226"),
         ("universal",
          "Both `stress(inputs)` and `stress(params)` return CONFIRM. "
          "Thesis holds across world and process variation.",
          "", ""),
         ("process-conditional",
          "Inputs CONFIRM, params not. Mechanism robust to environment; "
          "whether it manifests depends on team/process configuration.",
          "", ""),
         ("world-conditional",
          "Params CONFIRM, inputs not. Thesis holds for a fixed "
          "parameterisation but breaks under varied initial conditions.",
          "", ""),
         ("fragile",
          "Neither axis returns a CONFIRM majority. Thesis depends "
          "on a narrow regime.",
          "", ""),
       ]),
      ("Statistical primitives",
       "Same-list test inside `verdict_n`.",
       [
         ("cliffs_delta",
          "Non-parametric effect-size: `(gt − lt) / (n · m)`. Two "
          "lists are 'same' iff `|δ| ≤ 0.195`.",
          "Cliff (1993); threshold per Romano et al.",
          "paper/stats.py:68"),
         ("ks",
          "Two-sample Kolmogorov-Smirnov distance with the 5% "
          "critical value `1.36 · √((n+m)/(nm))`.",
          "Smirnov (1948); knob: `the.stats.conf = 1.36`.",
          "paper/stats.py:70"),
       ]),
      ("Data-tier checks",
       "Auto-derived from lift CSVs.",
       [
         ("param_plausibility",
          "Counts `in_range` / `at_boundary` / `out_of_range` from "
          "`boundary_check.csv`. Any `out_of_range` → FAIL.",
          "", "core/docs/scripts/gen_md.py"),
         ("boundary_adq_data",
          "Empirical companion to `boundary_adq`: PASS iff at least "
          "one lifted value reaches or exceeds the declared `[lo, hi]`.",
          "", "core/docs/scripts/gen_md.py"),
         ("calibrated_rq_rerun",
          "Re-run `rq()` with params replaced by Helix-calibrated "
          "lifted values. From `calibrated_verdicts.csv`.",
          "", "core/docs/scripts/gen_md.py"),
         ("family_member_coherence",
          "Per-project sign agreement across the family. Currently "
          "reports project count only; sign tally is hand-tuned per model.",
          "", "core/docs/scripts/gen_md.py"),
         ("behavior_reproduction",
          "Sim trajectory vs monthly historical CSV. Not run "
          "(requires per-project monthly time series).",
          "", ""),
       ]),
    ]

    for sec_title, sec_intro, entries in sections:
        out.append(f"## {sec_title}\n\n")
        out.append(sec_intro + "\n\n")
        for anchor, body, cite, src in entries:
            out.append(f'<h3 id="{anchor}"><code>{anchor}</code></h3>\n\n')
            out.append(body + "\n\n")
            if cite:
                out.append(f"_{cite}_\n\n")
            if src:
                out.append(f"Source: `{src}`\n\n")

    out.append("## References\n\n")
    out.append(
      "- Forrester, J. W. &amp; Senge, P. M. (1980). Tests for building "
      "confidence in system dynamics models. *System Dynamics*, "
      "TIMS Studies in the Management Sciences 14, 209–228.\n"
      "- Sterman, J. D. (2000). *Business Dynamics: Systems Thinking and "
      "Modeling for a Complex World*. McGraw-Hill.\n"
      "- Chen, T. Y., Cheung, S. C. &amp; Yiu, S. M. (1998). Metamorphic "
      "testing: a new approach for generating next test cases. HKUST-CS98-01.\n"
      "- Cliff, N. (1993). Dominance statistics: ordinal analyses to answer "
      "ordinal questions. *Psychological Bulletin* 114(3), 494–509.\n"
      "- Smirnov, N. (1948). Table for estimating the goodness of fit of "
      "empirical distributions. *Annals of Mathematical Statistics* 19(2), "
      "279–281.\n"
    )
    return "".join(out)


def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "models").mkdir(exist_ok=True)

    # Models index + future-work sub-page
    candidates = load_candidates()
    (DOCS / "models" / "index.md").write_text(
        render_models_index(AUDIT, candidates))
    (DOCS / "models" / "future.md").write_text(
        render_future(AUDIT, candidates))

    # Per-model
    for i, name in enumerate(sorted(AUDIT.keys()), start=1):
        (DOCS / "models" / f"{name}.md").write_text(
            render_model(name, AUDIT[name], i))

    # Top-level pages
    (DOCS / "findings.md").write_text(render_findings(AUDIT, LIFTS))
    (DOCS / "data.md").write_text(render_data(AUDIT, LIFTS))
    (DOCS / "glossary.md").write_text(render_glossary())

    n = len(AUDIT)
    print(f"Wrote {n} model pages + findings.md + data.md + glossary.md + models/index.md")
    print(f"  total: {n + 4} markdown files under {DOCS.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
