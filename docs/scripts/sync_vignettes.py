#!/usr/bin/env python3
"""Extract structured content from kaiaulu-style vignettes for site use.

Each canonical vignette in `../lifts/vignettes/<topic>_<method>.Rmd`
gets parsed into Markdown sections; the result is written to
`core/docs/_data/vignette_extracts.yml`. gen_md.py reads that file and
injects Intro / Verdict / References blocks into each model page.

Section → field mapping (per TODO SS(b)):
  Introduction (+ Method outline subblock)  → intro
  Verdict on <project>                      → verdict
  Sanity Checks                             → discussion
  References / Bibliography                 → refs

Code chunks are stripped from intro/verdict/discussion. References are
preserved as a list of one citation per line where possible.

Diff policy: this script writes a YAML file. Diff vs prior commit is
the standard `git diff` — no interactive prompt. Skip-overwrite happens
only if the extracted intro is empty (vignette has no Introduction).

Run: python3 docs/scripts/sync_vignettes.py
"""
import re, sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve()
DOCS = HERE.parents[1]              # core/docs
CORE = HERE.parents[2]              # core/
SCI  = CORE.parent                  # sci4seng/
VIG  = SCI / "lifts" / "vignettes"
OUT  = DOCS / "_data" / "vignette_extracts.yml"

# Mirror gen_md.py: canonical filename per model.
MODEL_TO_VIGNETTE = {
    "archpat":    "archpat_gof_pattern_partition",
    "brooks":     "brooks_late_hire_velocity",
    "brooksq":    "brooksq_injection_leak",
    "bugs":       "bugs_goel_okumoto_fit",
    "congruence": "congruence_radio_silence_brokers",
    "debt":       "debt_refactoring_pay_rate",
    "defmap":     "defmap_bug_caught_ratio",
    "dora":       "dora_four_keys_lift",
    "learn":      "learn_cohort_transitions",
    "rework":     "rework_failrate_estimation",
}


def strip_chunks(text):
    """Drop ```{r ...} ... ``` code blocks; keep prose."""
    return re.sub(r"```\{r[^}]*\}.*?```", "", text, flags=re.S)


def parse_yaml_header(text):
    """Return {title: ...} from the leading --- ... --- block."""
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    if not m:
        return {}
    header = m.group(1)
    title_m = re.search(r'^title:\s*"?([^"\n]+)"?\s*$', header, flags=re.M)
    return {"title": title_m.group(1).strip()} if title_m else {}


def split_sections(text):
    """Return list of (heading, body) pairs split on top-level `# ` lines.
    First entry has heading=None and body=everything-before-first-#."""
    out = []
    lines = text.splitlines()
    cur_head = None
    cur_body = []
    for ln in lines:
        if re.match(r"^# [^#]", ln):
            out.append((cur_head, "\n".join(cur_body).strip()))
            cur_head = ln[2:].strip()
            cur_body = []
        else:
            cur_body.append(ln)
    out.append((cur_head, "\n".join(cur_body).strip()))
    return out


def find_section(sections, *needles):
    """Return body of the first section whose heading contains any
    of the case-insensitive needles. None if no match."""
    for head, body in sections:
        if head is None: continue
        h = head.lower()
        if any(n.lower() in h for n in needles):
            return body
    return None


def extract_refs(body):
    """Convert a References section body into a list of citation lines.
    Accepts both `1.` numbered and `-` bulleted lists; falls back to
    one citation per non-empty line."""
    if not body:
        return []
    items = []
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln: continue
        # Strip leading list markers
        ln = re.sub(r"^\s*(\d+\.|-|\*)\s*", "", ln)
        if ln:
            items.append(ln)
    return items


def yaml_quote(s):
    """Quote a YAML scalar safely as a block-literal (`|`) when it
    contains newlines or special chars."""
    if s is None:
        return "~"
    s = str(s)
    if "\n" not in s and not re.search(r"[:#&*!|>'%@`,?\[\]{}]", s):
        return s
    # Use block-literal preserving newlines, indent 4 spaces.
    indented = "\n".join("    " + ln for ln in s.splitlines())
    return "|\n" + indented


def extract_one(rmd_path):
    text = rmd_path.read_text()
    header = parse_yaml_header(text)
    body = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S)
    body = strip_chunks(body)
    sections = split_sections(body)

    intro       = find_section(sections, "Introduction", "Intro")
    verdict     = find_section(sections, "Verdict")
    discussion  = find_section(sections, "Sanity")
    refs_body   = find_section(sections, "References", "Bibliography")

    return OrderedDict([
        ("title",      header.get("title", "")),
        ("intro",      (intro or "").strip()),
        ("verdict",    (verdict or "").strip()),
        ("discussion", (discussion or "").strip()),
        ("refs",       extract_refs(refs_body)),
    ])


def write_yaml(by_model, out_path):
    lines = ["# Auto-generated by docs/scripts/sync_vignettes.py.",
             "# Do not hand-edit; rerun the script after changing a vignette.",
             ""]
    for name in sorted(by_model.keys()):
        rec = by_model[name]
        lines.append(f"{name}:")
        lines.append(f"  title:       {yaml_quote(rec['title'])}")
        lines.append(f"  intro:       {yaml_quote(rec['intro'])}")
        lines.append(f"  verdict:     {yaml_quote(rec['verdict'])}")
        lines.append(f"  discussion:  {yaml_quote(rec['discussion'])}")
        if rec["refs"]:
            lines.append("  refs:")
            for r in rec["refs"]:
                lines.append(f"    - {yaml_quote(r)}")
        else:
            lines.append("  refs:        []")
        lines.append("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines))


def main():
    by_model = {}
    missing  = []
    empty    = []
    for model, stem in MODEL_TO_VIGNETTE.items():
        rmd = VIG / f"{stem}.Rmd"
        if not rmd.exists():
            missing.append((model, rmd))
            continue
        rec = extract_one(rmd)
        if not rec["intro"]:
            empty.append((model, rmd))
        by_model[model] = rec

    write_yaml(by_model, OUT)

    n = len(by_model)
    print(f"Wrote {OUT.relative_to(CORE)} ({n} model extracts)")
    for m, path in missing:
        print(f"  MISSING vignette: {m} -> {path}")
    for m, path in empty:
        print(f"  WARN: no Introduction parsed: {m} ({path.name})")


if __name__ == "__main__":
    sys.exit(main())
