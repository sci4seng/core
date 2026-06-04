#!/usr/bin/env python3
"""Lift the aiwork SD model (GitClear + METR) partial-data params.

The aiwork ctrl `ai` is structurally unliftable on OSS without
AI-usage telemetry per developer; this script lifts the two
non-AI params we CAN ground in commit history:

  churn_base: baseline (no-AI) churn rate, measured as the
    fraction of commits whose subject matches a revert/reset/
    "fix typo"/rollback pattern. METR / GitClear treat AI churn
    as a multiplicative inflation on top of this base.

  mature_rate: Wip -> Kept transition rate. Lifted as the
    inverse of the mean commit-author cycle (a proxy: 1 / mean
    days_between_first_and_last_commit_of_a_short_author_run).
    This is rough; the kaiaulu .Rmd wrapping (TODO followup) will
    swap in proper PR-cycle lifts where issue trackers are
    available.

These two are partial-data — the model still needs `gen_boost`,
`churn_mult`, `verify_drag` from literature priors when running
the calibrated rq. Item-4-focus-aiwork follow-up: rerun
calibrate.py against the lifted churn_base.

Output: paper/outputs/lift_aiwork_<project>.csv with the wide
schema melt_lifts.py expects.
"""

import csv, re, subprocess
from pathlib import Path

HERE     = Path(__file__).resolve().parents[1]
OUTPUTS  = HERE / "outputs"
DATA_DIR = HERE.parent.parent / "data"

PROJECTS = ["helix", "tomcat", "camel"]

# Subject-line patterns flagged as "churn signal" (no-AI baseline).
# Borrowed from common revert/rollback conventions.
CHURN_RX = re.compile(
    r"\b(revert|rollback|undo|reset|fix typo|backout|"
    r"reapply|re-apply|amend|hotfix)\b", re.IGNORECASE,
)


def _resolve_repo(repo_root):
    if not repo_root.is_dir():
        return None
    if (repo_root / ".git").exists():
        return repo_root
    for child in repo_root.iterdir():
        if child.is_dir() and (child / ".git").exists():
            return child
    return None


def gitlog_summary(repo_root):
    """Return list of (subject, author, unix_time) for every
    commit. Empty if the repo can't be read."""
    repo = _resolve_repo(repo_root)
    if repo is None:
        return []
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log",
             "--all", "--no-merges", "--format=%s\t%an\t%at"],
            check=True, capture_output=True, text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        subj, author, ts = parts
        try:
            rows.append((subj, author, int(ts)))
        except ValueError:
            continue
    return rows


def lift_aiwork_for(project):
    rows = gitlog_summary(DATA_DIR / project / "git_repo")
    if not rows:
        return None
    n_commits = len(rows)
    n_churn   = sum(1 for s, _, _ in rows if CHURN_RX.search(s))
    churn_base = n_churn / n_commits if n_commits else 0.0

    # mature_rate proxy: mean per-author span (last - first commit,
    # in days). Inverse gives a Wip->Kept rate. Trim authors with
    # only one commit (span=0 distorts the inverse).
    by_author = {}
    for _, author, ts in rows:
        lo, hi = by_author.get(author, (ts, ts))
        by_author[author] = (min(lo, ts), max(hi, ts))
    spans_days = [
        (hi - lo) / 86400
        for lo, hi in by_author.values()
        if hi > lo
    ]
    if spans_days:
        mean_span = sum(spans_days) / len(spans_days)
        mature_rate = 1.0 / mean_span if mean_span > 0 else 0.0
    else:
        mean_span = 0.0
        mature_rate = 0.0

    return {
        "model":         "aiwork",
        "project":       project,
        "churn_base":    f"{churn_base:.4f}",
        "n_churn":       n_churn,
        "n_commits":     n_commits,
        "mature_rate":   f"{mature_rate:.5f}",
        "mean_span_days": f"{mean_span:.1f}",
        "n_authors":     len(by_author),
        "seed":          1,
    }


def main():
    n_written = 0
    for project in PROJECTS:
        row = lift_aiwork_for(project)
        if row is None:
            print(f"  {project:8s} SKIP (no git_repo on disk)")
            continue
        out = OUTPUTS / f"lift_aiwork_{project}.csv"
        cols = ["model", "project", "churn_base", "n_churn",
                "n_commits", "mature_rate", "mean_span_days",
                "n_authors", "seed"]
        with out.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerow(row)
        print(f"  {project:8s} churn_base={row['churn_base']} "
              f"({row['n_churn']}/{row['n_commits']}) "
              f"mature_rate={row['mature_rate']} "
              f"authors={row['n_authors']}")
        n_written += 1
    print(f"\nWrote {n_written} project CSVs to {OUTPUTS}")


if __name__ == "__main__":
    main()
