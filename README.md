# sci4seng/core

The methodology + V&V framework + site for MYTHS (Models Yielding
Testable Hypotheses in Software).

## Walk the site (no build needed)

```
docs/
├── index.md                # landing
├── findings.md             # F0–F5
├── typology.md             # 2×2 cell explanation
├── data.md                 # per-project lift coverage
└── models/
    ├── index.md            # all 35 models grouped by cell
    ├── brooks.md           # one MD per model
    ├── archpat.md
    └── ...
```

Just `cd docs && ls -R` — every page is plain markdown. Cross-links
are relative `.md` paths so `grep` and `less` work natively. No JS,
no build step required to read.

## Build the site (optional)

Jekyll + Just-the-Docs gives nav + search + dark mode:

```bash
cd docs
bundle install
bundle exec jekyll serve   # http://localhost:4000
```

Deploys automatically to GitHub Pages on push to main.

## Reproduce the audit

```bash
cd paper
python3 full_audit.py        # writes outputs/full_audit.csv
python3 boundary_check.py
python3 calibrate.py
python3 cross_project.py
python3 ../docs/scripts/gen_md.py   # refresh docs/ from CSVs
```

Or one command:
```bash
make refresh                 # from paper/Makefile
```

## Sibling repos

- **[sci4seng/lifts](https://github.com/sci4seng/lifts)** — vignettes
  (`.Rmd` + `.R` + sample `conf/`). PR'd into `sailuh/kaiaulu` for
  external review. NO HTML, NO data per SME's PR-hygiene rule.
- **[sci4seng/data](https://github.com/sci4seng/data)** — drop-zone
  + manifest. Raw bundles live on Drive; this repo tracks only the
  ingest contract.

## Roles

- **coder** drives the framework.
- **SME** reviews lift vignettes via kaiaulu PRs.
- **DBmang** reviews downstream.
