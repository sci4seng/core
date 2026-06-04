#!/usr/bin/env python3
"""Extend the archpat lift with per-region commit-volume rates.

The existing archpat lift snapshots module COUNTS in the Patterned
/ Legacy / Other regions via pattern4. This extension adds two
rate-style metrics that the archpat SD model needs but the
snapshot-only lift cannot deliver:

  gen_pat_proxy: mean commits per patterned-module per month —
    a proxy for `gen_pat` (items shipped per patterned region per
    tick). Higher = patterned regions are actively maintained.

  gen_leg_proxy: same for the Legacy region (everything not in
    the patterned module set). The ratio gen_pat_proxy /
    gen_leg_proxy is the empirically grounded "patterned regions
    ship faster (or slower) than legacy" claim — directly usable
    when calibrating archpat.rq() in `paper/calibrate.py`.

Patterned modules per project come from the existing archpat
lift (lifts.csv: model=archpat, metric=modules). Currently
ambari + helix only — those are the two projects archpat is
lifted on.

Output: paper/outputs/lift_archpat_rates_<project>.csv with the
wide melt_lifts schema. Rows are appended to the existing
archpat_<project> roll-ups in lifts.csv via a follow-up
manual append (the prior 435-row content is preserved).

Python prototype; .Rmd / functions.R wrap is a follow-up.
"""

import csv, subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE     = Path(__file__).resolve().parents[1]
OUTPUTS  = HERE / "outputs"
DATA_DIR = HERE.parent.parent / "data"
LIFTS    = OUTPUTS / "lifts.csv"


def _resolve_repo(repo_root):
    if not repo_root.is_dir():
        return None
    if (repo_root / ".git").exists():
        return repo_root
    for child in repo_root.iterdir():
        if child.is_dir() and (child / ".git").exists():
            return child
    return None


def patterned_modules_from_lifts(project):
    """Return the comma-split list of patterned module names that
    the existing archpat lift recorded. Empty list if missing."""
    if not LIFTS.exists():
        return []
    with LIFTS.open() as f:
        for row in csv.DictReader(f):
            if (row["model"] == "archpat"
                    and row["project"] == project
                    and row["metric"] == "modules"):
                return [m.strip() for m in row["value"].split(",")
                        if m.strip()]
    return []


def commits_per_month_per_module(repo_root, modules):
    """Walk the gitlog and tally (module, year-month) -> commit
    count. A commit is credited to module M if any of its
    changed file paths starts with "<M>/". Commits that touch
    multiple modules count once per module."""
    repo = _resolve_repo(repo_root)
    if repo is None:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log",
             "--all", "--no-merges",
             "--format=COMMIT %at", "--name-only"],
            check=True, capture_output=True, text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return None
    mod_set = set(modules)
    per_pat = defaultdict(set)   # ym -> commits seen touching any patterned
    per_leg = defaultdict(set)
    cur_ts, cur_id, modules_touched_pat, modules_touched_leg = None, None, set(), set()
    for line in out.splitlines():
        if line.startswith("COMMIT "):
            cur_ts = int(line.split()[1])
            cur_id = cur_ts
            modules_touched_pat, modules_touched_leg = set(), set()
        elif line and cur_ts is not None:
            # File path's first directory segment is the module name
            # (kaiaulu's archpat lift uses module-prefix slicing). The
            # commit is patterned iff that prefix matches.
            head = line.split("/", 1)[0]
            if head in mod_set:
                modules_touched_pat.add(head)
            else:
                modules_touched_leg.add(head)
            ym = datetime.fromtimestamp(cur_ts, tz=timezone.utc).strftime("%Y-%m")
            for m in modules_touched_pat:
                per_pat[(ym, m)].add(cur_id)
            for m in modules_touched_leg:
                per_leg[(ym, m)].add(cur_id)
    return per_pat, per_leg


def project_rates(project):
    modules = patterned_modules_from_lifts(project)
    if not modules:
        return None, "no archpat row in lifts.csv"
    repo_root = DATA_DIR / project / "git_repo"
    tallies = commits_per_month_per_module(repo_root, modules)
    if tallies is None:
        return None, "git_repo unreadable"
    per_pat, per_leg = tallies
    if not per_pat and not per_leg:
        return None, "empty gitlog"

    # Aggregate to (commits-per-module-per-month). The per-region
    # mean smooths over months where one module went quiet.
    pat_counts = [len(s) for s in per_pat.values()]
    leg_counts = [len(s) for s in per_leg.values()]
    n_pat_modules = len({m for _, m in per_pat.keys()})
    n_leg_modules = len({m for _, m in per_leg.keys()})
    months_seen   = len({ym for ym, _ in (
        list(per_pat.keys()) + list(per_leg.keys()))})

    gen_pat = sum(pat_counts) / max(1, n_pat_modules * months_seen)
    gen_leg = sum(leg_counts) / max(1, n_leg_modules * months_seen)
    ratio = gen_pat / gen_leg if gen_leg > 0 else float("inf")
    return {
        "model":           "archpat",
        "project":         project,
        "gen_pat_proxy":   f"{gen_pat:.4f}",
        "gen_leg_proxy":   f"{gen_leg:.4f}",
        "gen_pat_leg_ratio": f"{ratio:.4f}",
        "n_pat_modules":   n_pat_modules,
        "n_leg_modules":   n_leg_modules,
        "months_seen":     months_seen,
        "seed":            1,
    }, ""


def main():
    n_written = 0
    for project in ("helix", "ambari", "tomcat", "camel"):
        row, note = project_rates(project)
        if row is None:
            print(f"  {project:8s} SKIP ({note})")
            continue
        out = OUTPUTS / f"lift_archpat_rates_{project}.csv"
        cols = list(row.keys())
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerow(row)
        print(f"  {project:8s} gen_pat={row['gen_pat_proxy']} "
              f"gen_leg={row['gen_leg_proxy']} "
              f"ratio={row['gen_pat_leg_ratio']} "
              f"({row['n_pat_modules']} pat / "
              f"{row['n_leg_modules']} leg, "
              f"{row['months_seen']} months)")
        n_written += 1
    print(f"\nWrote {n_written} project CSVs to {OUTPUTS}")


if __name__ == "__main__":
    main()
