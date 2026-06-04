#!/usr/bin/env python3
"""Lift the ownership SD model (Bird et al. 2011) on each project
with a git_repo bundle. For every project: walk the full commit
history, tally commits-per-author-per-file, identify each file's
majority contributor, and compute `minor_share` = 1 - max_author /
total_commits at the file level. Aggregate across files (mean) to
get the project-level minor_share lift value. Also emits the file
count (Modules) and the mean major_quality proxy
(1 - mean(file_minor_share) is the inverse: high major-fraction =
high implied major_quality, so we leave both metrics raw).

This is a Python prototype; an .Rmd vignette mirroring the kaiaulu
convention is item-4-lift-1 of the deferred lift rollout.

Output: paper/outputs/lift_ownership_<project>.csv with the wide
schema melt_lifts.py expects (one row, one column per metric).

Note: skipped if subprocess `git log` returns nothing (no
git_repo bundle on disk).
"""

import csv, subprocess, sys
from collections import defaultdict
from pathlib import Path

HERE     = Path(__file__).resolve().parents[1]
OUTPUTS  = HERE / "outputs"
DATA_DIR = HERE.parent.parent / "data"

PROJECTS = ["helix", "tomcat", "camel"]


def _resolve_repo(repo_root):
    """Project bundles sometimes nest the actual repo one level
    down (data/helix/git_repo/helix/.git rather than
    data/helix/git_repo/.git). Find whichever directory has the
    .git inside."""
    if not repo_root.is_dir():
        return None
    if (repo_root / ".git").exists():
        return repo_root
    for child in repo_root.iterdir():
        if child.is_dir() and (child / ".git").exists():
            return child
    return None


def gitlog_author_files(repo_root):
    """Yield (author, file_path) per (commit, file) in the repo's
    full history. Empty if the repo can't be read."""
    repo = _resolve_repo(repo_root)
    if repo is None:
        return
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log",
             "--all", "--no-merges",
             "--format=%H\t%an", "--name-only"],
            check=True, capture_output=True, text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return
    author = None
    for line in out.splitlines():
        if "\t" in line:
            _, author = line.split("\t", 1)
        elif line and author is not None:
            yield author, line


def lift_ownership_for(project):
    repo = DATA_DIR / project / "git_repo"
    by_file = defaultdict(lambda: defaultdict(int))
    n_commits = 0
    for author, fpath in gitlog_author_files(repo):
        by_file[fpath][author] += 1
        n_commits += 1
    if not by_file:
        return None
    minor_shares = []
    for fpath, authors in by_file.items():
        total = sum(authors.values())
        if total < 2:
            continue
        major = max(authors.values())
        minor_shares.append(1 - major / total)
    if not minor_shares:
        return None
    mean_minor = sum(minor_shares) / len(minor_shares)
    return {
        "model":            "ownership",
        "project":          project,
        "modules":          len(minor_shares),
        "minor_share_mean": f"{mean_minor:.4f}",
        "n_commits_seen":   n_commits,
        "seed":             1,
    }


def main():
    n_written = 0
    for project in PROJECTS:
        row = lift_ownership_for(project)
        if row is None:
            print(f"  {project:8s} SKIP (no git_repo on disk)")
            continue
        out = OUTPUTS / f"lift_ownership_{project}.csv"
        cols = ["model", "project", "modules",
                "minor_share_mean", "n_commits_seen", "seed"]
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerow(row)
        print(f"  {project:8s} modules={row['modules']:6d} "
              f"minor_share_mean={row['minor_share_mean']} "
              f"n_commits={row['n_commits_seen']}")
        n_written += 1
    print(f"\nWrote {n_written} project CSVs to {OUTPUTS}")


if __name__ == "__main__":
    main()
