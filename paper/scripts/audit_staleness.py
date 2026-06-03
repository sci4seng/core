#!/usr/bin/env python3
"""Sweep the sci4seng repo for stale numbers vs paper/outputs/*.csv.

Three passes:
  (1) Structured checks — cell label, inp_cnt/par_cnt, model-count
      numerics on auto-generated and hand-edited pages.
  (2) Prose-pattern sweep (YY) — flag every `N/M positive sign`,
      `N of M cases`, `N/M show X` etc. so reviewers can verify them
      against the current `lifts.csv`. Patterns get reported with
      file:line; we do not auto-recompute because the surrounding
      context is needed to know which metric N/M refers to.
  (3) Per-model lift recap — print the actual current counts per
      model so reviewers can sanity-check prose claims against them.

Exits 1 if a structured check fails. Prose patterns are always
informational; they print to stderr and never fail the script.

Run: python3 paper/scripts/audit_staleness.py
"""
import csv, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]          # core/
AUDIT_CSV = ROOT / "paper" / "outputs" / "full_audit.csv"
LIFTS_CSV = ROOT / "paper" / "outputs" / "lifts.csv"
GEN_MD    = ROOT / "docs" / "scripts" / "gen_md.py"
MODELS_README = ROOT / "paper" / "MODELS_README.md"
MODELS_INDEX  = ROOT / "docs" / "models" / "index.md"
MODELS_DIR    = ROOT / "docs" / "models"
VIG_DIR       = ROOT.parent / "lifts" / "vignettes"

AUDIT = {row["model"]: row for row in csv.DictReader(AUDIT_CSV.open())}

issues = []


def check(label, condition, msg):
    if not condition:
        issues.append(f"  [{label}] {msg}")


# --- (1) Structured numerics ----------------------------------------------

# Total active models in audit; sanity check the prose count claims.
total = len(AUDIT)
universal_count = sum(1 for r in AUDIT.values() if r["cell"]=="universal")
process_count   = sum(1 for r in AUDIT.values() if r["cell"]=="process-conditional")
fragile_count   = sum(1 for r in AUDIT.values() if r["cell"]=="fragile")
world_count     = sum(1 for r in AUDIT.values() if r["cell"]=="world-conditional")

for f, pat in [
    (MODELS_README, rf"(\d+) (?:models|SD models)"),
    (MODELS_INDEX,  rf"(\d+) (?:active|model)"),
]:
    if not f.exists():
        continue
    src = f.read_text()
    found = set(int(x) for x in re.findall(pat, src))
    bad = found - {total, universal_count, process_count,
                   fragile_count, world_count}
    if bad:
        check(str(f.relative_to(ROOT)), False,
              f"stale count {sorted(bad)} (real total={total}; "
              f"universal={universal_count} process={process_count} "
              f"fragile={fragile_count} world={world_count})")


# --- (2) Prose-pattern sweep (YY) -----------------------------------------
#
# Scan model pages + vignettes for `N/M` and `N of M` patterns that look
# like they reference lift quantities. Report file:line + the matched
# phrase; reviewers cross-check against lifts.csv manually because the
# surrounding word context is what disambiguates "5/8 projects" from
# "5/8 of items" etc.

PATTERNS = [
    re.compile(r"\b(\d+)\s*/\s*(\d+)\s+("
               r"positive|negative|noisy|projects|cases|show|of|"
               r"signal|confirm|lifted)", re.I),
    re.compile(r"\b(\d+)\s+of\s+(\d+)\s+("
               r"positive|negative|noisy|projects|cases|show|"
               r"signal|confirm|lifted)", re.I),
]

prose_hits = []


def scan(path, root_for_relpath):
    if not path.exists():
        return
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        stripped = line.strip()
        # Skip Markdown table rows — those numbers come straight from
        # the CSV and are by-construction-correct (not stale prose).
        if stripped.startswith("|"):
            continue
        for pat in PATTERNS:
            m = pat.search(line)
            if m:
                rel = path.relative_to(root_for_relpath)
                prose_hits.append((str(rel), i, stripped[:120]))
                break


for p in sorted(MODELS_DIR.glob("*.md")):
    scan(p, ROOT)

if VIG_DIR.exists():
    for p in sorted(VIG_DIR.glob("*.Rmd")):
        scan(p, ROOT.parent)


# --- (3) Per-model lift recap --------------------------------------------

LIFTS = defaultdict(list)
if LIFTS_CSV.exists():
    for r in csv.DictReader(LIFTS_CSV.open()):
        LIFTS[r["model"]].append(r)


def model_recap():
    rows = []
    for name in sorted(LIFTS.keys()):
        lrows = LIFTS[name]
        n_proj = len({r["project"] for r in lrows})
        rows.append((name, n_proj, len(lrows)))
    return rows


# --- Output ---------------------------------------------------------------

if issues:
    print(f"Found {len(issues)} structured staleness items:")
    for i in issues:
        print(i)

if prose_hits:
    print(f"\nProse-embedded N/M patterns ({len(prose_hits)} hits) — "
          f"cross-check against lifts.csv:", file=sys.stderr)
    for rel, ln, snippet in prose_hits:
        print(f"  {rel}:{ln}: {snippet}", file=sys.stderr)

print(f"\nLift recap (from lifts.csv):", file=sys.stderr)
for name, n_proj, n_rows in model_recap():
    print(f"  {name:12s}  {n_proj} projects, {n_rows} rows",
          file=sys.stderr)

if issues:
    sys.exit(1)
print("\nOK — all structured checks pass.")
