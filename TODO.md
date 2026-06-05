# TODO.md — handoff for next session (post-compaction)

Snapshot 2026-05-25. Repo `github.com/sci4seng/core` @ `main`.

## DECIDED

- **Paper**: ICSE 2027 NIER (4pp) first, EMSE follow-up. Topic:
  falsification-based testing of SE system-dynamics models, paired
  with kaiaulu real-data calibration. Anonymous double-blind.
- **Site name**: MYTHS = Models Yielding Testable Hypotheses in Software.
- **Family**: 8 Apache-style OSS projects — Helix, junit5, Ambari,
  kaiaulu, airflow, openssl, tomcat, camel. (cleaned Helix bundle on
  disk now too.)
- **Deliverable format** (SME's §3): kaiaulu-vignette-style
  `.Rmd` + companion R helpers in `lifts/functions.R`. Each lift is
  PR-reviewable into kaiaulu as student-style code review.
- **Card ordering**: diapers first, then year-desc. Years are on
  both cards + page titles.
- **Source tiers for the 47-candidate "other" inventory**:
  - **A** = peer-reviewed archival (DOI/IEEE/ACM/journal) — 21 models
  - **B** = book / grey-lit anchor; partial peer-reviewed companion — 15
  - **C** = tacit / named-only / not formally modelled — 11
- **brooks.html is hand-tuned** (`manual=True` in `scripts/gen_rich.py`);
  the other 17 model pages regenerate from gen_rich.py.

## DONE

### Framework
- 33 SD models in `paper/sd.py` (was 17 → +1 congruence on 2026-05-24
  → +15 buildable-today on 2026-05-25).
- `paper/tests.py` 9-test V&V bank intact.
- `paper/outputs/full_audit.csv` — 33 models × stress matrix + 8-test
  bank (~91% PASS overall on the 18 original; new 15 mostly clean).

### Lifts (10 informable models × 8 projects, ~63 CSVs in `outputs/`)
- Helix: 10/10 informable lifted (brooks, brooksq, bugs, debt,
  rework, learn, defmap, dora, archpat, congruence).
- Ambari: 8/10.
- tomcat: 8/10.
- camel: 7/10 (archpat blocked by mvn-on-Java-26 dep issues).
- junit5: 7/10 (archpat blocked by Gradle JDK 25 toolchain).
- airflow: 6/10 (Python — no archpat / debt).
- openssl: 6/10 (C — no Java tools).
- kaiaulu: 7/10 (R — no archpat / debt; bugs lifted via GH issues).

### Analyses (S13–S16 in TIMETABLE schema)
- `outputs/boundary_check.csv` — 8 models × 8 projects. **17
  out_of_range cells, 8 at_boundary, 78 in_range.**
- `outputs/calibrated_verdicts.csv` — 9 models recalibrated; all
  retain CONFIRM; gap magnitudes shift meaningfully.
- `outputs/cross_project.csv` — 9 models × 8 projects key-metric grid.
- `findings.md` — 5 F-findings (F0 boundary failures, F1 leak_rate
  7/8, F2 pay_rate convergence, F3 Brooks 11× spread, F4 brooksq
  split verdict).

### Tools installed (no further sudo needed)
- PyDriller 2.9 (`.venv`), Perceval 1.4.7
- R 4.6 + kaiaulu pkg + igraph + jsonlite
- Temurin OpenJDK 26 (user-sudo'd)
- Maven 3.9.16
- RefactoringMiner 3.0.10
- pattern4.jar (Concordia)
- Depends 0.9.7
- scc 3.7.0
- networkx + python-louvain (mbox graph)
- git-filter-repo 2.47.0

### SME's §4 sanity checks
- 3/5 kaiaulu wrappers verified: `parse_gitlog`, `parse_line_metrics`,
  `parse_gof_patterns`. 2 have **kaiaulu source bugs** documented in
  `kaiaulu_notes/known_bugs.md` (one-line patches suggested):
  - `parse_dependencies` — reads `<name>.json` but Depends
    `--granularity=file` writes `<name>-file.json`.
  - `parse_java_code_refactoring_json` — (a) `regex=".git"` matches
    `_git` in `git_repo`; (b) parses RefMiner stdout mixed with
    INFO log lines.

### Site (`/docs`)
- GitHub Pages enabled on `/docs`. `.nojekyll` present.
- `docs/index.html` — 18 model cards + "+47 more" card linking to
  other.html. Diapers first, year-desc.
- 18 model pages with 6 panes each (Summary / Model / Lift / Inputs /
  Scorecard / Results) + peer-reviewed References table per page.
- `brooks.html` hand-tuned (~630 lines); the rest regenerate from
  `scripts/gen_rich.py`'s `M` dict.
- `docs/other.html` — 47-candidate inventory + per-candidate tier +
  data-on-disk verdict.
- Site anonymised: no team names. `Anonymous submission · ICSE 2027`
  footer.

### Data
- `~/Downloads/helix/` (pre-cleanup) + `data/helix_clean/`
  (SME cleaned, from his Drive bundle). radio_silence reproduces
  identically on both — cleaning didn't affect comm graph.
- 6 dataset zips extracted from `/Users/timm/tmp/Claude SE Models-…zip`.

## LEFT (priority order)

### OPEN — USER-SIDE (user's actions, not coder's)

These five items block on user (email, Drive op, decision call); no
amount of coder work can move them. Re-emphasised here per the
2026-06-03 session request to track them explicitly.

1. **Send DBmang/intern status email** — draft already in
   `diary/2026-05-25_status_to_rick_umar.md`. user's send.
2. **Ping DBmang on `archpat.pat_strength`** — the param is declared
   in `paper/sd.py` archpat init but never referenced in `step()`.
   Either dead code (delete) or a missing equation in the
   pattern-decay branch (add). Need DBmang's call.
3. **Anonymous mirror for ICSE 2027 submission** —
   `github.com/sci4seng/...` URL identifies the lab. Options:
   anonymous.4open.science, or zip `docs/` + push as a separate
   anonymised repo before the submission deadline.
B5. **5 missing project bundles from Drive** — junit5, ambari,
    kaiaulu, airflow, openssl. user must rsync/extract them under
    `sci4seng/data/<project>/{git_repo,jira,mbox,github}/` to
    unblock further family-member lifts. Tomcat / helix / camel
    already in place locally.
B6. **Inventory + cleanup of the existing Drive bundle** — pair
    with B5; SME's cleaned-helix bundle established the layout
    convention, but the rest haven't been audited against it.
    user's call on whether to ingest other Drive folders.

### OPEN — BLOCKED ON USER DATA (coder-ready otherwise)

10. **Behavior reproduction (S17) + behavior prediction (S18)** for
    each model — never attempted. Requires monthly historical CSVs
    per project (release-month -> observed-metric pairs) so the
    sim trajectory can be compared to ground truth. user has to
    pull or generate those before the coder side can wire them in.
    Once the CSVs land in `sci4seng/data/<project>/observed_*.csv`,
    we can add a `paper/scripts/behavior_check.py` that reads them
    + the corresponding sim trajectory and emits a fit-quality
    row per (model, project) into a new
    `outputs/behavior_check.csv`.

11. **Surface R lift helpers on every model page** (2026-06-04).
    Today every `docs/models/<name>.md` shows the SD model + lift
    Rmd link but not the actual R helper functions the Rmd calls
    from `sci4seng/lifts/R/functions.R`. brooks.md got the helpers
    inlined by hand on 2026-06-04 as a sample
    (`detect_late_hires` + `compute_velocity_changes`); next
    `gen_md.py` run will clobber that edit.

    Proper fix: add a per-model sidecar dir (e.g.
    `docs/_notes/<name>.md` — plain markdown, no frontmatter) +
    teach gen_md.py to inline the sidecar under a `## Notes` or
    `## R lift helpers` section when present. Sidecars are
    READ-only from gen_md's perspective, so hand-written notes
    survive regen forever. Then back-fill the helper bodies for
    the other 35 models (brooksq's SZZ helpers, debt's pay/born
    rate helpers, etc.) from `lifts/R/functions.R` roxygen
    blocks. Should also surface the helper's `#' @export`
    docstring as the body, not paraphrased prose, so the page
    stays a faithful mirror of the R source.

### Buildable today (15 candidates ranked in `docs/other.html`)
4. **9 A-tier with HAVE-data** (ordered by paper impact):
   ownership, orgchurn, pareto, mirroring, little, entropy,
   costchange, deprot, ossfail.

   **SCOPE SHRUNK 2026-06-03**: per a mid-session redirect, focus
   is now **brooks, aiwork, archpat ONLY**. The other A-tier
   candidates are deferred; their SD models + docs pages are
   already shipped (paper/sd.py + docs/models/*.md), only the
   lift pipelines (per-project metric extraction) remain. Each
   lift is ~4-8h of kaiaulu-vignette work, so the deferred
   inventory below is roughly 60-100h of follow-up.

   **In-focus follow-ups (2026-06-03 status, deepened pass)**:
   - **aiwork** lift PROTOTYPE shipped (`paper/scripts/lift_aiwork.py`)
     -> helix/tomcat/camel CSVs. `churn_base` observed 0.01-0.03
     (model default 0.05). Now ALSO wired into
     `paper/calibrate.py` as `calibrate_aiwork()`: helix-lifted
     `churn_base` + `mature_rate` shrink the rq gap from -51.7 to
     -1.52 (97% drop, verdict stays CONFIRM but right at the
     neutral threshold). Methodology paper finding: AI-quality
     concern nearly disappears once the no-AI baseline is
     ground-truthed. Also wrapped as kaiaulu-style .Rmd:
     `../lifts/vignettes/aiwork_churn_baseline.Rmd` +
     `detect_churn_commits()` / `compute_author_span_rate()` in
     `../lifts/R/functions.R`. PR-ready for kaiaulu.
   - **brooks** lift already at 8 projects, 5 metrics. Saturated
     for now — no obvious next column without an SME request.
     `calibrate_brooks` notes that brooks_tax_median is a derived
     metric and the model's comm_coef / train_coef stay at
     defaults; an inverse-fit would need item 8 sd.opt() style
     search over those.
   - **archpat** lift extended on helix with two new metrics
     (`paper/scripts/lift_archpat_rates.py`):
     `gen_pat_proxy = 7.69` commits/patterned-module/month vs
     `gen_leg_proxy = 0.47` for the legacy region — ratio ~16.4x.
     The model's default ratio was 2.5x; under the lifted helix
     values archpat's CONFIRM verdict FLIPS to **neutral**
     (gap +229 -> -1.41). Patterned regions already ship so fast
     on helix that aggressive migration adds little. `sd.py`
     `gen_pat` hi widened 3 -> 10 to absorb the observed value
     (lift was clipping at 3; same shape as the 7/7a F0/F1
     boundary widens). Ambari rate lift skipped — git_repo not
     on disk (B5). Tomcat / camel: NOT archpat targets per the
     current lifts.csv coverage, would need a pattern4 build
     first.
     `pat_strength` dead-param finding (declared in init,
     propagated, never read in step()) confirmed — recommend
     deletion from init + setattr loop. Concrete info for
     user-side item 2 ping to DBmang.

   **Out-of-focus but already shipped (out-of-band on 2026-06-03)**:
   - `ownership` lift on helix/tomcat/camel —
     `paper/scripts/lift_ownership.py`. user committed it
     directly (commit 4d495cb); preserved in lifts.csv but
     out of focus going forward.

   **Deferred** (SD + docs shipped; lifts pending, ~half-day each):
   orgchurn, pareto, mirroring, little, entropy, costchange,
   deprot, ossfail. Pick up after brooks/aiwork/archpat are
   exhausted.
5. **6 B-tier with HAVE-data**: coordn2, scope, ctxswitch, limits,
   successful, linus.

   **SCOPE SHRUNK 2026-06-03** — same redirect as item 4. All
   six SD models + docs pages already shipped; lifts deferred.

   Net coverage if all 15 deferred lifts ever land: **33 models
   with full lifts** (vs 12 today: brooks, brooksq, bugs, debt,
   rework, learn, defmap, dora, archpat, congruence, ownership,
   aiwork).

### Needs new pipeline (~1-2 days each)
6. **15 partial-data candidates** in `other.html`. Most leverage:
   `exposure` (NVD CVE-to-commit pipeline), `flaky` (GH Actions
   retry-pattern parser), `testshape` (path-prefix-based test-tier
   classifier).

### Site / docs UX

XX. **DONE 2026-06-02.** Hyperlink scorecard terms to definitions.
    Shipped under the Jekyll Markdown site (not the old icse27theories
    HTML rollout):
    - `docs/glossary.md` — 32 anchors covering 8 F&S/Chen tests,
      rq/verdict family, stress/cell typology, stats primitives
      (Cliff's δ / KS / median ε), 5 data-tier checks. Each entry:
      one-line def + literature citation + line-link into
      `paper/tests.py` / `paper/sd.py` / `paper/stats.py`.
    - `docs/scripts/gen_md.py` — added `GLOSS` dict + `gloss()` helper;
      `render_model()` wraps 14 scorecard terms with markdown links
      `[term](../glossary.md#anchor "tooltip")`. Just-the-Docs renders
      the tooltip as a hover title.
    - `render_glossary()` emits `docs/glossary.md` (nav_order=6).
    - Verified: each model page has 22 glossary links; `make regen`
      runs clean; `make verify-k-anon` clean.

XX-jira. **DONE 2026-06-02.** Jira lift for Helix + Camel.
    - `../lifts/conf/camel.yml`: added `issue_tracker.jira` block
      (helix.yml already had it).
    - `../lifts/R/functions.R`: appended `lift_project_jira()` helper
      that stages `*.json` into a tempdir before calling
      `kaiaulu::parse_jira` (the installed pkg crashes on `.DS_Store`).
    - `../lifts/vignettes/lift_jira.Rmd`: new vignette; knits cleanly.
      Extracts helix (97 issues, 152 comments) and camel (500 issues,
      2142 comments). Outputs written to
      `paper/outputs/lift_jira_{helix,camel}_{issues,comments}.csv`.
    - `../lifts/kaiaulu_notes/known_bugs.md`: documented three new
      `parse_jira()` gotchas — installed-vs-source signature mismatch
      (DIRECTORY vs FILE), base_info/ext_info → JIRA REST `[["issues"]]`
      schema shift, `.DS_Store` crash. The metric.R `"Closed"/"Resolved"`
      filter matches nothing under the installed schema — use
      `issue_status == "Done"`.

### New model: motif-based congruence (SME GH #3, DONE 2026-05-25)

UU. **DONE.** Shipped `congruence_motif()` SD model + `M[]` entry +
    `docs/models/congruence_motif.html` page + index card +
    `extract/lifts/lift_congruence_motif.Rmd` + MODELS_README +
    STATE.md update. Audit profile: CONFIRM gap=-68.78, cell=universal
    (174/154 of 200). Cataldo's 3 matrix-form variants remain
    queued as a separate future model `congruence_cataldo`
    (still needs paper-pull).

    Original entry preserved below for reference.

UU. **Add a second congruence model to the bucket — motif-based STC
    (socio-technical congruence) per Cataldo + kaiaulu motif.R.**
    Current `congruence` in `paper/sd.py:839` is the **smells-based**
    variant (Catolino 2019, R/smells.R, radio_silence). SME's
    GitHub issue #3 asks for the motif-based variant as a separate
    model, with reference to Cataldo's 3 versions.

    **References (all 4 from SME's issue)**:
    1. Catolino 2019 (smells): IEEE 8651329 — already implemented as
       current `congruence`
    2. Paradis/Kazman 2014 → Mauerer et al. 2021 (motif): IEEE 9436025
       and TSE 48(8) 2022 doi:10.1109/TSE.2021.3082074 — the basis for
       the new model
    3. Paradis 2024 comparison paper: sciencedirect S0164121224000104
       — compares both approaches + related literature
    4. Cataldo (multiple, 2008+): 3 distinct congruence variants
       (matrix-based, graph-weighted, task-dependency-graph). Reviewer-
       requested in 2022 submission. Need paper-pull to enumerate.

    **Motif structure** (from local kaiaulu R/motif.R):
    - Triangle: 2 devs communicate when changing same file (+)
    - Anti-triangle: 2 devs DON'T communicate when changing same file (−)
    - Square: 2 devs communicate when changing 2 dep-linked files (+)
    - Anti-square: 2 devs DON'T communicate across dep-linked files (−)

    Congruence_motif = (Triangles + Squares) / (Triangles + AntiTri
    + Squares + AntiSq).

    **SD model sketch** (working name `congruence_motif`):
    - Stocks: `Triangles`, `AntiTri`, `Squares`, `AntiSq`, `Bugs`
    - Inputs (UPPER): `Devs`, `Files`, `DepLinks` — project scale
    - Params (lower):
      - `comm_rate` — ctrl, probability a dev-pair on the same file
        communicates (0=no comm, 1=full comm)
      - `dep_density` — fraction of file-pairs with cross-file deps
      - `bug_rate_per_antimotif` — bugs born per anti-motif event
      - `bug_repair_rate` — bugs paid down per tick
    - Flow logic per tick: enumerate co-touch events → classify into
      4 motifs → AntiTri + AntiSq increment Bugs.
    - y = Bugs at tmax (success = low bugs).
    - rq = "raising comm_rate from 0.2 → 0.8 lowers final Bugs".
      Cataldo's thesis: congruence gap predicts defects.

    **3 Cataldo variants** map to different update rules:
    a. **Matrix-form** (Cataldo 2006): coordination_requirement matrix
       CR = TD ∩ TA, congruence = |CR ∩ CA| / |CR|. Simplest.
    b. **Weighted** (Cataldo 2008): edge weights by frequency.
    c. **Task-graph-based** (Cataldo 2014?): uses task dependency
       graph directly. Need paper-pull.

    For SD: variants collapse into 3 different formulas for the
    `congruence` derived metric in step(). Each gives a different y()
    if Bugs born differently. Could ship as one model with a
    `variant` param ∈ {1,2,3} ctrl switch, OR as 3 separate models.
    SME preference TBD.

    **Lift recipe** (confirmed against kaiaulu vignette
    `motif_analysis.html` fetched 2026-05-25):
    ```r
    git_network    <- transform_gitlog_to_bipartite_network(gitlog,
                                                            mode="author-file")
    reply_network  <- transform_reply_to_bipartite_network(replies)
    reply_network  <- bipartite_graph_projection(reply_network,
                          mode = TRUE,
                          weight_scheme_function = weight_scheme_sum_edges)
    file_network   <- transform_r_dependencies_to_network(deps,
                                                          dependency_type="file")
    # merge networks into single combined graph
    g_all <- list(nodes = unique(rbind(...)),
                  edgelist = rbind(git_network$edgelist,
                                   reply_network$edgelist,
                                   file_network$edgelist))
    i_all <- igraph::graph_from_data_frame(d=g_all$edgelist,
                                           directed=FALSE,
                                           vertices=g_all$nodes)
    V(i_all)$color <- ifelse(V(i_all)$color == "black", 1, 2)
    # Count each motif type via subgraph isomorphism (VF2)
    counts <- list()
    for (mt in c("triangle","anti_triangle","square","anti_square")) {
      mg <- motif_factory(mt)
      img <- igraph::graph_from_data_frame(d=mg$edgelist,
                                           directed=FALSE,
                                           vertices=mg$nodes)
      V(img)$color <- ifelse(V(img)$color == "black", 1, 2)
      counts[[mt]] <- igraph::count_subgraph_isomorphisms(
        img, i_all, method="vf2",
        edge.color1=NULL, edge.color2=NULL)
    }
    ```
    Emit `paper/outputs/lift_congruence_motif_<project>.csv` with
    columns: Triangle, AntiTriangle, Square, AntiSquare,
    n_devs, n_files, n_deps. Vignette example on kaiaulu itself
    gave triangle=34, square=32 (anti variants not demonstrated
    there but available via `motif_factory("anti_triangle")` etc.).

    **Congruence formula**: vignette is counts-only; the ratio
    comes from Mauerer 2022 consumer side. Most natural:
    `congruence = (Triangle + Square) / (Triangle + AntiTri + Square + AntiSq)`.
    Verify against Mauerer TSE 2022 §formal definition before
    committing.

    **Cataldo's 3 variants are a SEPARATE track**: matrix-form
    CR ∩ CA / |CR|, NOT graph-motif counts. Vignette doesn't
    reference Cataldo at all. Including the Cataldo variants
    means a second lift pipeline (task-dependency × people-task
    matrices, not igraph motifs). Could ship as a third model
    `congruence_cataldo` distinct from `congruence_motif`. SME
    expectation needs clarification: does he want ONE model with
    formula switches, or THREE distinct models
    (smells / motif / cataldo)?

    **Implementation checklist**:
    - [ ] Pull Cataldo's 3 papers; enumerate the variants
    - [ ] Update current `congruence` docstring to say "smells-based
          (Catolino 2019)"; rename internal vars if helpful
    - [ ] Add `congruence_motif()` to sd.py
    - [ ] Add `M["congruence_motif"]` entry to gen_rich.py with rich
          intro1/intro2/rq_text/cell_para/refs (4-paper citation list)
    - [ ] Add to MODELS_README.md table (34→35 models)
    - [ ] Add to full_audit.py MODELS list
    - [ ] Write extract/lifts/lift_congruence_motif.Rmd using kaiaulu
          motif wrappers
    - [ ] Run pipeline: full_audit → melt_lifts → boundary_check →
          calibrate → gen_rich → gates
    - [ ] Note for paper: this model + the existing `congruence` give
          a methodological contrast — same SE thesis (coordination
          gap → defects), two different operationalizations, can the
          framework triage which is the better measurement target?

    **Open questions for SME/DBmang**:
    - One model with variant=1/2/3 ctrl, or 3 separate models?
    - Should the smells-based `congruence` be renamed
      `congruence_smells` for symmetry?
    - Does the paper want both shipped as the worked-example trio
      (replacing one of brooks/archpat/dora)?

    Big-ticket effort: estimate 1 day of paper-reading + 1 day of
    SD model drafting + 1 day of lift Rmd + audit pass. Wait for
    SME prioritisation before starting.

### Model-derived findings re-validation (deferred 2026-05-25)

VV. **DONE 2026-06-03 (claim REFUTED).** Re-validated the May 11
    aidebt regime-crossover claim against current sd.py. Built
    `paper/scripts/grid_aidebt.py`: 10x10 sweep over
    (pay_rate, born_ai_mult), repeated at tmax ∈ {10, 20, 30, 50, 80}.
    Outputs: 5 `outputs/grid_aidebt_tmax{T}.csv`, one
    `outputs/grid_aidebt_summary.csv`, one
    `outputs/figs/grid_aidebt.svg` (faceted heatmap).

    **Key finding: the regime flip is TEMPORAL, not parametric.**

    Verdict distribution by tmax (100 cells/grid):
    - tmax= 10: 25 CONFIRM /  70 REFUTE /  5 neutral
    - tmax= 20: 22 CONFIRM /  78 REFUTE
    - tmax= 30: 29 CONFIRM /  71 REFUTE
    - tmax= 50: 99 CONFIRM /   1 REFUTE
    - tmax= 80: 99 CONFIRM /   1 REFUTE

    Median crossover ratio at tmax 10/20/30 is 0.27 / 0.20 / 0.25
    (range 0.0–0.33). NOT near 1.5x anywhere in the grid. At tmax
    50/80 there is essentially no verdict-flip surface — the
    long-run cumulative-debt effect dominates and AI uniformly hurts.

    The May 11 leverage-ratio framing does not survive contact with
    sd.py — the regime boundary lives in the tmax axis, not the
    `pay_rate / (born_base × (1 + born_ai_mult))` axis. The
    methodology paper should NOT cite the 1.5x crossover as a
    finding; use the temporal regime flip instead.

    **Prudence caveat unresolved (VV step 6)**: aidebt still has
    `boundary_adq=FAIL`, `extreme_eqn=ERR`, `mr_scale=ERR`. Grid
    numbers above are tentative until those three rows resolve.
    The temporal-regime finding is qualitative-robust to those
    prudence rows (the sign-flip is large; not a near-threshold
    call).

    **VV step 6 DONE 2026-06-03 (second pass).** Root cause was a
    framework-wide `tests.py` bug, not aidebt-specific:
    `extreme_eqn` (L75) and `mr_scale` (L183) unpacked 3-tuples but
    init specs became 4-tuples after the dim_check / S4 work (item 9
    shipped today). Every model has hit `ERR:ValueError` on those
    two rows since 9 landed; the failure was just most visible on
    aidebt because the VV write-up highlighted it.

    Fix: switched both rows + `mr_zero_input` (L105) + `mr_monotone`
    (L129) to the index-based `spec[1], spec[2]` pattern that
    `sd.py` already uses, preserving units (`spec[3]`) when
    rebuilding test specs. After fix:
    - aidebt `extreme_eqn=PASS`, `mr_scale=PASS`.
    - aidebt `boundary_adq=FAIL` stays — that's the real VV
      temporal-regime finding (t=20:REFUTE → t=80:CONFIRM); the
      F&S test is correctly detecting the regime flip, not a bug.

    **Side effect / new follow-up items.** Re-running full_audit
    with the fix unmasked real model FAILs that were previously
    hidden behind ERR. Pre-existing — not introduced today, just
    newly visible:
    - `mr_monotone=FAIL` on learn, defmap, coordn2, entropy,
      costchange, pareto, linus, mirroring, burnout, ossfail,
      deprot, maturity (y not monotone in ctrl across the 5-grid;
      may be expected for some, suspect for others).
      **TRIAGED 2026-06-03 (12 -> 2).** Root cause was a second
      tests.py bug: `mr_monotone` set `expect_down = (rq.gap < 0)`
      but rq()s typically compare two named regime points (not
      lo vs hi), so the sweep direction across the full [lo,hi]
      doesn't agree with rq's signed gap. Fix: derive sweep
      direction from the sweep endpoints themselves (Chen MR1:
      output predictable in input). After fix, 10 of the 12 are
      strictly monotone and now PASS. Remaining 2 are real
      single-hump shapes:
      * **coordn2** — was a model bug: `tax = min(0.9, ...)` cap
        produced a non-physical back-end where output rose linearly
        with Devs once tax saturated (rise-fall-rise). Replaced
        with `factor = max(0, 1 - ...)` so throughput decays
        cleanly past the Brooks-inflection point. New shape
        [200, 5100, 100, 0, 0] = one peak — Brooks's law clean.
        Still FAILs strict mr_monotone (hump), but the FAIL now
        documents the model thesis, not a bug.
      * **burnout** — legitimate hump: 0 work delivers 0; moderate
        work optimal; chronic overload erodes Capacity via Stress.
        rq() compares workload=40 vs 60 inside the past-peak
        decline region, hence CONFIRM. mr_monotone over the full
        [0,100] range crosses the inflection; FAIL documents the
        peaking thesis. No fix needed.
    - `mr_bound_consist=FAIL` on diapers, brooks, brooksq, defmap
      (clamping is load-bearing).
      **TRIAGED 2026-06-03 (4 -> 0).** Three model fixes:
      * brooks/brooksq: `prod*dt` could overshoot remaining Todo,
        making Done saturate against its bound. Cap delta at
        remaining Todo (conservation: Done + Todo = constant).
      * defmap: `Caught` accumulates `detect` per tick with no
        decay; the [0,100] bound was too tight to hold the integral
        across a sweep (~440 hits). Widened to 2000.
      * diapers: already PASS; not affected.
    - `mr_scale=FAIL` on diapers, brooks (sign-flip / nonlinearity
      large enough to trip the < 0 guard).
      **DOCUMENTED 2026-06-03.** Both are real model theses, not
      bugs:
      * brooks: doubling Vet flips the sign of net progress
        because quadratic comm overhead outpaces linear productivity
        gain. THAT IS Brooks's law. Annotated in sd.py docstring.
      * diapers: hi-stressed Use drains the fixed Clean supply;
        y goes negative. Stress-collapse is what the toy
        demonstrates. Annotated in sd.py docstring.
    - `mr_scale=SKIP` on defmap (y=0 baseline).
      **DOCUMENTED 2026-06-03.** Parameter-balance artefact: at
      default tst=2.5, detect_coef=0.4, `leak = Injected * (1 -
      tst*detect_coef) = 0`, so Latent and Prod stay 0 and
      y = -Prod - 0.5*Latent = 0. mr_scale can't compute a ratio.
      The model still meaningfully responds to ctrl (tst sweep);
      mr_scale just happens to be ill-defined at the default
      operating point. Annotated in sd.py docstring.
    - `anomaly_check=FAIL` on diapers, flaky (sign reversal under
      stress).
      **DOCUMENTED 2026-06-03.** Both are stress-collapse theses:
      * diapers: same demand-overrun-supply story above.
      * flaky: hi-stressed Tests+Flakes+Bugs sends `cover` low
        enough that leak overwhelms invest_base; the spiral to
        the all-Flakes attractor flips y = Tests - Bugs sign.
        That is the model's documented hypothesis. Annotated.
    - `mr_dt_halving=FAIL` on diapers (uncovered after the bound
      fixes ran clean — was hidden by the prior FAIL set).
      **DOCUMENTED 2026-06-03.** `int(t) % 7 == 6` and `t == 13`
      event triggers are dt-dependent (Saturday fires twice at
      dt=0.5). Sterman dt-halving is misapplied to a discrete-event
      toy. Annotated.

    All non-PASS rows in `outputs/full_audit.csv` now document
    real model theses (sign-flip, hump, temporal regime,
    stress-collapse, toy artefact) or are SKIPs for ill-defined
    metrics. There are no remaining V&V table bugs as of
    2026-06-03. The 18-model methodology paper table can read
    directly off `full_audit.csv` once the model docstrings are
    rolled into the per-model HTML page footnotes.

    Outputs touched: `paper/tests.py`,
    `paper/outputs/full_audit.csv`. `audit_staleness.py` reports
    clean — site numbers in sync with the new audit.

    Original deferral spec preserved below for reference.

VV (original spec). **Re-validate the May 11 aidebt regime-crossover
    claim against current sd.py.** Claim: leverage measurement = ratio
    `pay_rate / (born_base × (1 + born_ai_mult))`, crossover ≈ 1.5×,
    teams above benefit from AI, teams below degrade. Source: May 11
    chat — model-based reasoning, never grid-validated.

    Status today (2026-05-25):
    - Structurally still valid: aidebt step() line 746-749 retains
      both params; only rename `born_rate` → `born_base`.
    - Quantitatively suspect: default ratio = 0.15/(0.3×2.5) = 0.2,
      well below claimed 1.5× threshold. Default `rq()` reports
      REFUTE +6.50 at tmax=20, CONFIRM at tmax≥30 (per
      MODELS_README.md line 107-108). Regime appears in TIME, not
      param-ratio, as currently configured.
    - Stress matrix backs the "params matter" framing:
      `inp_cnt=183/200` vs `par_cnt=74/200` (37%), cell =
      world-conditional.
    - Prudence dirty: `boundary_adq=FAIL`, `extreme_eqn=ERR`,
      `mr_scale=ERR`. Verdicts should carry that caveat.

    Build `paper/scripts/grid_aidebt.py`:
    1. Sweep `(pay_rate, born_ai_mult)` over their declared `[lo, hi]`
       on a 10×10 grid.
    2. For each cell: run `rq()` at tmax ∈ {10, 20, 30, 50, 80}.
    3. Output 2D verdict heatmap CSV per tmax.
    4. Compute the contour where verdict flips (CONFIRM ↔ REFUTE).
    5. Compare to 1.5× ratio claim.
    6. Fix the 3 prudence FAIL/ERR rows before publishing the
       contour as evidence.

    Output: `paper/outputs/grid_aidebt_tmax<T>.csv` + a figure spec
    for the NIER paper (regime boundary in (pay_rate, born_ai_mult)
    space at chosen tmax). This is publishable — directly anchors
    the methodology paper's "model-based triage of what to measure"
    pitch.

    Parallel: same exercise for `aiwork` via `grid_aiwork.py` sweeping
    `(gen_boost, churn_mult)` — the May 11 chat already produced
    a 6×6 sensitivity table for that pair. Re-derive against current
    sd.py to check numbers reproduce.

### Vignette ↔ docs/models alignment (SME GH #1, deferred 2026-05-25)

SS. **DONE 2026-06-03.** Both parts shipped.

    **(a) DONE** — renamed 10 vignettes to canonical kaiaulu
    `<topic>_<method>.Rmd` naming via `git mv` in
    `sci4seng/lifts/vignettes/`. Downstream refs updated:
    - `core/paper/Makefile` RmdFiles wildcard now points at
      `../../lifts/vignettes/*.Rmd` (was `../extract/lifts/`).
    - `core/docs/scripts/gen_md.py` resolves the canonical name via
      `MODEL_TO_VIGNETTE`, falling back to `lift_<name>` for models
      without a SME-blessed kaiaulu name (currently:
      `congruence_motif`, `jira`).

    **(b) DONE** — built `core/docs/scripts/sync_vignettes.py` and
    wired it into `gen_md.py`. The extractor reads each canonical
    `<topic>_<method>.Rmd`, parses the YAML header, strips R chunks,
    and pulls Introduction / Verdict / Sanity Checks / References
    sections by header-name match. Outputs two artifacts on each run:
    - `core/docs/_data/vignette_extracts.yml` (one block per model;
      stable target for future Jekyll Liquid templates if needed).
    - At regen time, `gen_md.py` imports `extract_one()` from
      `sync_vignettes.py` and inlines four new sections into every
      model page that has a kaiaulu-mapped vignette: "Lift
      methodology", "Lift verdict on the project", "Sanity checks",
      and "References". 10 model pages now carry vignette excerpts.

    Diff policy: each `make regen` rewrites the model pages, so
    `git diff docs/models/*.md` is the standard review path. No
    interactive prompt. Conflict policy is "vignette wins" — manual
    edits to the four inlined sections survive only if also added to
    the upstream Rmd.

    Original deferral spec preserved below for reference.

SS (original spec). **Two related fixes for the Rmd-vignette ↔
    docs/models drift that SME flagged in GH issue #1**:

    **(a) Restructure `../lifts/vignettes/` to match kaiaulu vignette
    naming convention**. Today our lifts are named
    `lift_<model>.Rmd`. Kaiaulu's vignettes are named
    `<topic>_<method>.Rmd` (descriptive, kaiaulu's house style).
    SME's PR fork already renames them. Proposed map:

    | current name (../lifts/vignettes/) | kaiaulu vignette name (SME's fork) |
    |---|---|
    | `lift_archpat.Rmd` | `archpat_gof_pattern_partition.Rmd` |
    | `lift_brooks.Rmd` | `brooks_late_hire_velocity.Rmd` |
    | `lift_brooksq.Rmd` | `brooksq_injection_leak.Rmd` |
    | `lift_bugs.Rmd` | `bugs_goel_okumoto_fit.Rmd` |
    | `lift_congruence.Rmd` | `congruence_radio_silence_brokers.Rmd` |
    | `lift_debt.Rmd` | `debt_refactoring_pay_rate.Rmd` |
    | `lift_defmap.Rmd` | `defmap_bug_caught_ratio.Rmd` |
    | `lift_dora.Rmd` | `dora_four_keys_lift.Rmd` |
    | `lift_learn.Rmd` | `learn_cohort_transitions.Rmd` |
    | `lift_rework.Rmd` | `rework_failrate_estimation.Rmd` |

    Need git mv to preserve history (in the sibling `sci4seng/lifts`
    repo). Cross-link to TODO ZZ (data drop-zone) since ingest tool
    needs to know the canonical Rmd locations.

    **(b) Build `docs/scripts/sync_vignettes.py` to extract Rmd
    content into `gen_md.py` per-model fields.** Pattern proven on
    archpat 2026-05-25 by hand-editing M["archpat"] to mirror
    SME's vignette: 6-step method outline, flow diagram,
    pattern4 invocation gotcha, Verdict-on-Helix prose,
    family-comparison table, expanded refs (Gamma, Tsantalis 2006,
    Arcan, MacCormack). The icse27theories implementation lived in
    `gen_rich.py` against HTML output; sci4seng's equivalent target
    is `gen_md.py` against Markdown (`docs/models/<name>.md`).

    Generalise the manual archpat exercise into a script:
    1. For each model in {archpat, brooks, brooksq, bugs,
       congruence, debt, defmap, dora, learn, rework}:
    2. Pull the kaiaulu vignette via `gh api repos/timm/kaiaulu/...`
       or `curl` to the raw URL.
    3. Parse Rmd sections: YAML header → metadata; `#` headers →
       sub-sections; ```{r}``` blocks → code chunks; prose
       between chunks → narrative.
    4. Auto-update gen_md.py per-model fields:
       - `lift_intro` ← Intro section + method outline
       - `attrs_table` ← derived from code chunks' fread/parse calls
       - `tools_table` ← detected from require() + system() calls
       - `results_intro` ← Verdict section
       - `results_discussion` ← Sanity Checks + Boundary findings
       - `refs` ← Bibliography section
    5. Diff old vs new before write; ask before overwriting
       manual edits.
    6. Run after each docs regen (or as a pre-commit hook).

    Open questions:
    - Source of truth for vignette URLs: hard-code the SME
      fork URLs, OR have a `vignette_urls.yml` per model.
    - Conflict policy when vignette + manual M[] differ: prefer
      vignette, prefer M[], or interactive?
    - Should rename in (a) happen FIRST so script in (b) can
      use the canonical names?

    Recommended sequence: rename Rmd files (a), update Makefile
    + symlinks for backward compat, build extractor (b),
    one-time backfill, then ongoing sync via pre-commit hook.

### Lift function documentation (deferred 2026-05-25)

TT. **DONE 2026-06-03.** Inline WHY comments on `../lifts/R/functions.R`
    body. 9 priority helpers (detect_late_hires, compute_velocity_changes,
    parse_szz_bugfixes, compute_injection_changes, estimate_leak_rate,
    parse_mbox_dir, build_reply_edges, detect_radio_silence, plus
    compute_file_churn and assign_file_partition) already had inline
    comments from an earlier pass that survived the port. Today filled
    the gap on 10 more (compute_cohorts, estimate_transition_rates,
    compute_failrate_per_window, compute_per_phase_defects,
    compute_dora_metrics, get_tag_dates, compute_pay_rate,
    compute_born_rate_proxy, flatten_refactoring_json,
    compute_file_bug_frequency). Source-check passes (R 4.6, 32
    functions exported). Commit `2483667` in sibling sci4seng/lifts.

    Original deferral spec preserved below for reference.

TT (original spec). **Add inline WHY comments to every function in
    `../lifts/R/functions.R`.** Today each function carries a
    roxygen header (param/return/export) but the function BODY has
    no inline comments explaining the mechanism. Reader can see
    WHAT each line does from the code, but not WHY.

    (Distinct from `TT-jira` above — that's a different lift task
    redefined under the same code on 2026-06-02.)

    Reference pattern: `detect_late_hires()` lines 31-46
    (`../lifts/R/functions.R`). Roxygen header is sufficient.
    Body would benefit from comments like:
    - on `first_commits` line: "first commit per identity =
      individual's join date"
    - on `project_start` line: "earliest commit across whole repo
      = project birth"
    - on filter line: "drop founders + early hires; keep only late
      arrivals whose first commit is >365 days after birth"

    Per coder's instruction 2026-05-25 (review of the rendered
    `lift_congruence` notebook): "there are no comments in the lift
    functions. these need to be added." File is ~900 lines after
    2026-06-02 jira-helper append; ~13 exported functions.

    **Scope**: every `# ---- <Section> ----` block in functions.R.
    Highest priority (consumed by most lifts):
    - `detect_late_hires()` (used by brooks, brooksq, defmap, rework)
    - `compute_velocity_changes()` (used by brooks)
    - `compute_injection_changes()` (used by brooksq, defmap, rework)
    - `compute_file_churn()` (used by archpat)
    - `assign_file_partition()` (used by archpat)
    - `parse_szz_bugfixes()` (used by all SZZ-based lifts)
    - `parse_mbox_dir()` (used by congruence)
    - `build_reply_edges()` (used by congruence)
    - `detect_radio_silence()` (used by congruence)

    Pattern follows the aiwork docstring + inline-comment exercise
    on 2026-05-25 (see WW). Each non-obvious line gets one short
    WHY. Comments NOT added on lines whose identifier already
    explains intent (CLAUDE.md rule). Run length: budget ~2 min
    per function × 12 = 25 min.

    Audit fail mode: reviewer reading `functions.R` should be able
    to write the lift's prose description without consulting the
    Rmd notebook. Today that's only possible for `detect_late_hires`
    (the most-cited function with prose context elsewhere).

### Model documentation (deferred 2026-05-25)

WW. **DONE 2026-06-03.** All 34 models in `paper/sd.py` now meet the
    aiwork standard:
    - extended docstring (citation + stocks + control + RQ + hypothesis
      basis)
    - inline unit comments on non-obvious init params
    - WHY comments per non-obvious line in step()
    - comment on y() choice
    - comment on rq() control-arm semantics

    Before/after density (comment lines per model in `paper/sd.py`):

    | model | before | after |
    |---|---|---|
    | brooks    | 0  | 17 |
    | brooksq   | 0  | 15 |
    | bugs      | 0  |  8 |
    | debt      | 0  | 10 |
    | sir       | 0  |  8 |
    | rework    | 0  |  7 |
    | learn     | 0  |  8 |
    | defmap    | 0  | 10 |
    | flaky     | 0  |  7 |
    | dora      | 0  | 11 |
    | micro     | 0  |  8 |
    | teamtopo  | 0  |  6 |
    | burnout   | 0  |  7 |
    | aidebt    | 0  |  9 |
    | congruence| 2  | 13 |

    Models that already met the standard (left untouched): aiwork (10),
    congruence_motif (14), deprot (10), and the 13 buildable-today
    candidates each with 3-5 inline comments that already explain their
    nontrivial mechanisms. Diapers (toy) skipped per CLAUDE.md "don't
    over-comment trivial code" rule.

    Smoke-checks: `python3 paper/full_audit.py` runs to completion
    against the modified models; pre-existing prudence FAILs unchanged.
    Pyright pre-existing warnings unchanged.

    Original deferral spec preserved below for reference.

WW (original spec). **Ensure all 34 models in `paper/sd.py` are
    commented to the same standard.** Today most model defs carry only
    a 1-line docstring (citation + RQ). Inline mechanism comments are
    absent on the vast majority. `aiwork` got the canonical treatment
    on 2026-05-25 as the reference pattern: extended docstring
    (citation + stocks + control + RQ + hypothesis basis), inline
    `# unit comment` per init param explaining the meaning, brief
    `# why` comments per non-obvious line in `step()`, comment on
    the `y()` choice, comment on the rq() control-arm semantics.
    Replicate for the other 33 models.

    Priority order (clean first since they get the most page traffic):
    1. **Headline 3**: brooks, brooksq, archpat
    2. **Lifted (10)**: bugs, debt, sir, rework, learn, defmap,
       dora, congruence (already comment-dense in step), plus
       brooks/brooksq above
    3. **Pipeline-ready 15**: ownership, orgchurn, pareto, mirroring,
       little, entropy, costchange, deprot, ossfail, coordn2, scope,
       ctxswitch, limits, successful, linus
    4. **Dark 6**: aidebt, flaky, micro, teamtopo, burnout (sister
       of aiwork)
    5. **Toy**: diapers (trivial, skip)

    Pattern reference: see `aiwork()` after 2026-05-25 edit. Don't
    over-comment (CLAUDE.md says: WHY only, not WHAT). Skip lines
    where identifier name already explains. Focus on:
    - Init param units + meaning when not obvious from name
    - Multiplicative factors in step() (what does `1 + x*y` represent?)
    - Bounds / caps (`min(...)`, `max(...)`) — why?
    - Choice of y() — why this stock as success measure?
    - rq() control-arm interpretation (what does ctrl=0 vs ctrl=1 mean?)

    Audit fail mode: a reviewer reading the .py should be able to
    write the model's RQ description without consulting the docs/
    pages. Today that's only possible for ~3 models.

### Data drop-zone + one-command rebuild (PARTIAL DONE 2026-05-25)

ZZ. **PARTIAL DONE.** Built `data/dropzone/` + `scripts/refresh.py`
    + Makefile targets `refresh` / `refresh-lifts` / `refresh-dry`.
    Lift-CSV path works end-to-end:
    ```
    cp lift_<m>_<p>.csv data/dropzone/
    make refresh-lifts
    ```
    Pipeline: ingest → melt_lifts (guarded — skipped when no source
    CSVs to avoid wiping the frozen lifts.csv) → boundary_check →
    calibrate → cross_project → full_audit → gen_rich → both gates,
    then prints a per-model before/after diff of (cell, verdict,
    verdict_n, gap).

    **Raw-data render path: DONE 2026-06-03.** Wired
    `scripts/refresh.py` to call `make -C paper render` after moving
    project subdirs from `data/dropzone/<p>/` to
    `data/<p>/`. The Makefile's `render` target already uses make's
    dep tracking, so up-to-date `.html` outputs are skipped (no waste).
    Vignettes write per-project lift CSVs straight into
    `paper/outputs/`, where `melt_lifts.py` finds them on the next
    pipeline step.

    Toolchain check via `shutil.which("Rscript")`: if R is not
    installed, the render step prints a warning and continues with
    whatever CSVs already exist. This keeps the lift-CSV-only flow
    (the original PARTIAL-DONE path) working even on machines
    without an R toolchain.

    Dry-run verified: `python3 scripts/refresh.py --dry-run` shows the
    correct sequence (move → render → melt_lifts → ... → gen_md).

    Original entry preserved below for reference.

ZZ. **Single command to ingest new/updated project data and rebuild
    the entire pipeline.** Today the flow is implicit and manual:
    `data/<project>/` → `extract/lifts/*.Rmd` → `paper/outputs/lift_*.csv`
    → `melt_lifts.py` → `lifts.csv` → `boundary_check.csv` +
    `calibrated_verdicts.csv` → `full_audit.csv` (via gen_rich) →
    `docs/models/*.html`. No documented entry point. No watcher.
    Re-running each stage by hand is error-prone, and the
    `extract/lifts/*.html` already drifted (Rmd newer than html on
    all 9 lifts).

    Build a `data/dropzone/` directory + a `make ingest <project>`
    target that:
    1. Detect new or updated project under `data/<project>/` (or
       symlink from `dropzone/`).
    2. Verify `extract/conf/<project>.yml` exists; if not, generate
       a skeleton + flag for hand-edit (git_repo path, branch, JIRA
       paths).
    3. Render the 9 (or however many) `extract/lifts/*.Rmd`
       notebooks for that project — produces per-project lift CSVs
       in `paper/outputs/`.
    4. Run inference chain: `make inference` (already exists) →
       `lifts.csv`, `boundary_check.csv`, `calibrated_verdicts.csv`,
       `cross_project.csv`, `full_audit.csv`.
    5. Regenerate docs: `python3 docs/scripts/gen_rich.py`.
    6. Run gates: `audit_staleness.py` + `check_pages.py`.
    7. Print diff summary: which scorecard rows changed, which
       findings (F0–F4) shifted.

    Open questions before implementing:
    - One project at a time, or batch all projects under `data/`?
    - Detect change by mtime, content hash, or explicit list?
    - For NEW projects: which conf-yml fields are auto-detectable
      (git_repo, branch via `git symbolic-ref`) vs hand-edit
      (JIRA project key, mbox path)?
    - For schema changes (new metric in lift): does gen_rich.py
      need to learn the new column, or does melt_lifts.py auto-melt?
    - Render needs `Rscript` + working `data/<project>/git_repo/`.
      Currently broken (data/ is empty); ingest tool must verify
      preconditions before rendering.
    - Should ingest auto-update `paper/MODELS_README.md` lift-status
      column ("8/8" → "8/8 + tomcat-v2") or leave manual?

    Smaller scope to start: just a `make refresh` target that
    re-runs steps 4–6 assuming per-project lift CSVs are already
    in place. That covers the "updated audit / new gen_rich logic"
    case without solving the upstream lift-rendering blocker
    (which needs data/ repopulated first).

### Audit coverage gaps (deferred 2026-05-25)

YY. **DONE 2026-06-03.** Rewrote `paper/scripts/audit_staleness.py`
    for sci4seng's Jekyll Markdown site (was icse27theories-flavored
    and crashing on missing `gen_rich.py` / `index.html`). Now does
    three passes:

    1. **Structured numerics**: model-count and per-cell totals in
       `paper/MODELS_README.md` + `docs/models/index.md` cross-checked
       against `full_audit.csv`.
    2. **Prose-pattern sweep (the YY ask)**: scans every
       `docs/models/*.md` and `../lifts/vignettes/*.Rmd` for
       `N/M (positive|negative|noisy|projects|cases|show|of|signal|
       confirm|lifted)` and `N of M ...` patterns. Markdown table
       rows are skipped because their numbers come straight from
       the CSV (by-construction-correct). Hits print to stderr with
       `file:line: snippet` so reviewers can verify each one against
       `lifts.csv`.
    3. **Per-model lift recap**: prints per-model project count +
       row count from `lifts.csv` to stderr — the reference table
       reviewers compare prose hits against.

    Run output today: 0 prose hits (no stale prose in either site or
    vignettes), structured checks PASS.

    Note: the YY brief mentioned a concrete drift on the OLD
    icse27theories `brooks.html` (`5/8 positive` vs lifts.csv 6/8).
    That HTML file does not exist in sci4seng — `docs/models/brooks.md`
    is auto-regenerated. The drift mechanism now is the SS-inlined
    vignette content; the prose sweep catches it if it appears there.

    Original deferral spec preserved below for reference.

YY (original spec). **audit_staleness.py misses prose-embedded lift
    stats**. Currently checks: cell label, inp_cnt/par_cnt, badge
    counts, typology totals, model count. Does NOT check summary
    statistics in page prose that are computed from `lifts.csv`.
    Concrete miss: `brooks.html` Panel 5 row `family_member_coherence`
    says "5/8 positive sign with n_hires ≥ 50; 3/8 noisy with small
    samples". Current lifts.csv gives 6/8 + 2/8 (tomcat n_hires=50
    crosses the threshold). Same drift on Panel 6 line 636
    ("5 of 8 cases, all five").
    Extend `paper/scripts/audit_staleness.py` to:
    - parse prose patterns like `N/M positive sign`, `N of M cases`,
      `N/M show <X>`
    - recompute from lifts.csv per-model
    - flag mismatch
    Also similar prose-embedded counts on other model pages — sweep
    all 34 docs/models/*.html for `\d+/\d+` and `\d+ of \d+` patterns
    that reference lift quantities (sign, threshold, magnitude).

### Methodology gaps
7. **DONE 2026-06-03.** All bounds widened per the recipe:
   - `brooksq.leak_rate hi 0.5 -> 1.0` ✓
   - `brooksq.inj_rate hi 0.5 -> 5.0` ✓
   - `archpat.Patterned hi 200 -> 1000` ✓ (previously applied)
   - `archpat.Legacy hi 200 -> 3000` ✓ (previously applied)
   - `learn.Jr hi 100 -> 2000` ✓
   - `congruence.Brokers hi 20 -> 100` ✓
   - `congruence.Clusters hi 20 -> 100` ✓

   F0 boundary violations resolved: **0 out_of_range** across all
   lifted cells (was 17 before). 7 at_boundary, 98 in_range across
   105 total.

   **Side effects**:
   - brooksq: cell stable (fragile); minor inp_cnt drift 6 -> 6.
   - **learn: cell flipped `universal -> process-conditional`**
     (inp_cnt 159 -> 13). Widening Jr to 2000 expanded the input
     sampling space far past the small Sr/Tr defaults; the thesis
     does not survive realistic-scale workforce perturbation. This
     is a publishable methodology finding: small-project bounds
     were inflating the input axis CONFIRM count.
   - congruence: cell stable (universal); inp_cnt 196 -> 177.
   - archpat: unchanged (already widened).

   Pipeline reran clean: full_audit + boundary_check + calibrate +
   cross_project + gen_md + audit_staleness + verify-k-anon.

   **7a. archpat sub-entry (added 2026-05-25)**: empirical anchor
   from `paper/outputs/boundary_check.csv`:
   - helix: Patterned=149 (in_range), Legacy=384 (1.9× over hi=200)
   - ambari: Patterned=381 (1.9× over), Legacy=1890 (9.5× over)
   Proposed bounds derive from "1.5× max observed":
   - `Patterned hi 200 → 1000` (covers ambari 381 + 2.6× headroom)
   - `Legacy hi 200 → 3000` (covers ambari 1890 + 1.6× headroom)
   Files to edit: `paper/sd.py:789` init dict (only the 2 hi
   values change; lo + default unchanged).
   **Side effects to verify post-edit**:
   - `stress()` redraws over the new range. Triangular sampler
     still peaks at default=10 (Patterned) / 90 (Legacy) so most
     draws stay near defaults; high-end tail now reachable. Cell
     typology may shift from `universal` (currently 129/200 inputs,
     122/200 params CONFIRM) toward `world-conditional` or
     `process-conditional` if Migration can't keep up with much
     larger Legacy stocks. Re-run `full_audit.py` to check.
   - `verdict_n` currently `neutral` with `gap_n=+59`, `eps=185`.
     Wider variance grows sd → eps grows → likely stays neutral.
   - `param_plausibility` row in scorecard should flip
     `FAIL → PASS` for archpat (rows for ambari Patterned + Legacy
     + helix Legacy now in_range).
   - `boundary_adq_data` row may flip `PASS → warn` (no lifted
     values reach the new wider edges).
   - F0 boundary-violation callout in archpat.html
     `scorecard_extras` (gen_rich.py:727) needs rewording or
     removal — currently quotes the old hi=200 + 384/1890/381.

   **Commit sequence** (atomic, gate-checked):
   1. Edit `paper/sd.py:789` two `hi` values.
   2. Run `python3 paper/full_audit.py` → refresh full_audit.csv.
   3. Run `python3 paper/boundary_check.py` → refresh
      boundary_check.csv (status fields will flip).
   4. Run `python3 paper/calibrate.py` → calibrated_verdicts.csv
      may shift (clipping behavior different).
   5. Update `scorecard_extras` for archpat in gen_rich.py:727 to
      reflect new bounds (or remove if all lifts now in_range).
   6. Run `python3 docs/scripts/gen_rich.py` → regenerate 32 pages.
   7. Run `paper/scripts/audit_staleness.py` + `check_pages.py`.
   8. Update `findings.md` F0 row: archpat resolved, remaining
      violations on brooksq + learn + congruence.

   (Sub-entries 7b–7e for the other 5 params follow the same
   recipe; not enumerated until authorization.)
8. **DONE 2026-06-03.** sd.opt() calibration pass shipped as
   `paper/scripts/calibrate_opt.py` ->
   `paper/outputs/calibration_opt.csv`. Per model: freeze ctrl at
   default, run `opt(n=1000, narrow=0.6)` over middle 60% of every
   other param's declared [lo, hi], record (default_y, opt_best_y,
   default_verdict, opt_verdict, top 3 fractional-shifted params).
   Runs all 35 models in ~1.4s.

   **Headline finding for the methodology paper.** Of 35 models:
   - **16 retain verdict** at the opt-best parameterisation
     (thesis robust across middle 60% of param space).
   - **17 flip CONFIRM -> neutral**: at the opt-discovered max-y
     parameterisation, the ctrl flip no longer separates y enough
     for the 5%-of-y0 verdict threshold. The default-state CONFIRM
     was parameter-sensitive.
   - **aidebt** flips REFUTE -> CONFIRM: there exists a param
     region (high pay_rate, etc.) where the AI-debt thesis DOES
     confirm — consistent with the VV grid finding that the
     thesis lives in a specific subregion, not the whole space.
   - **coordn2** flips REFUTE -> neutral: post-cap-fix from the
     V&V triage, opt finds settings where the Brooks superlinear
     tax claim sits at the verdict threshold rather than the
     declared default's REFUTE.

   This is *forward-search* calibration (find params that maximise
   the model's success metric, then test the thesis there) — NOT
   inverse-fit calibration against project-level time-series data.
   Inverse-fit needs monthly historical CSVs (see item 10,
   blocked) and is a separate pass.

   The `top_shifts` column flags the three params that moved the
   most in proportion to their declared range — useful for the
   paper's "which dial most controls each model" sidebar.

   `audit_staleness` clean; `verify-k-anon` clean. ALL_MODELS in
   sd.py widened from 34 to 35 to include `congruence_motif`
   (it was already in full_audit's MODELS — drift fix).

   Original deferral spec preserved: "currently rq() reruns at
   default; actual fitting of intr_rate etc not done."
9. **DONE 2026-06-03.** S4 dim_check built in `paper/tests.py` and
   wired into `paper/full_audit.py` ALL_TESTS + the scorecard via
   `docs/scripts/gen_md.py` + `docs/glossary.md`. Pragmatic
   per-param unit-string probe (atom or `/`-separated atoms; allows
   `$`, `%`, `-` in atoms for cost / fraction / hyphenated units like
   `debt-items`). All 34 models PASS. Does NOT do full symbolic-unit
   propagation through step() — that would need a CAS pass.
10. **Behavior reproduction (S17)** + **behavior prediction (S18)** —
    never attempted. Need monthly historical CSVs to compare against
    sim trajectories. **See the "OPEN — BLOCKED ON USER DATA"
    section near the top of this file for the expanded entry; this
    line is the original placeholder kept for cross-reference.**

### Blocked
11. **Pattern4 on junit5** — Gradle pins JDK 25; we have 26. Skip
    or install JDK 25 alongside.
12. **Pattern4 on camel** — Maven dep resolution fails on Java 26
    even with `-Dcheckstyle.skip=true`.
13. **Full Helix JIRA dump** — SME's bundle has 50 issues, 0 of
    type Bug. Need full pull or his cleaned JIRA. Until then, `bugs`
    on Helix uses GH issues route.
14. **`drift` / `cace` / `collapse` / `aiwork` / `aidebt`** — no ML
    or AI-authored data on disk. Structurally absent on the family.

## GOTCHAS

1. **macOS HFS+ case-insensitive**: `TIMETABLE.md` and `timetable.md`
   are the SAME file. Don't write to both expecting separate.
2. **Perceval date format**: `"Tue Jun 21 18:56:46 2011 -0700"`
   (git default), NOT `"%Y-%m-%d %H:%M:%S"`. Use
   `format = "%a %b %d %H:%M:%S %Y %z"` everywhere.
3. **kaiaulu `identity_match` signature**: now requires
   `label = "identity_id"` (or `"raw_name"`). Without it: "argument
   'label' is missing". Older templates omit it.
4. **kaiaulu `parse_dependencies` bug**: reads `<name>.json` not
   `<name>-file.json`. One-line patch documented in
   `kaiaulu_notes/known_bugs.md`. Until patched, call Depends
   directly via `java -jar tools/depends/...`.
5. **kaiaulu `parse_java_code_refactoring_json` bugs**: (a) the
   `.git`-strip regex eats `_git_` in path. (b) parses RefMiner
   stdout that contains INFO log lines. Until patched, call
   RefMiner directly via `tools/RefactoringMiner-…/bin/RefactoringMiner`.
6. **pattern4 CLI**: `java -jar pattern4.jar -target <classes-dir>
   -output <xml>` (NOT GUI-only despite Main-Class). Earlier session
   memory had this wrong; corrected in
   `~/.claude/projects/.../memory/reference_pattern4_gotcha.md`.
7. **learn methodology fix**: 365-day slice + 365-day Jr cutoff
   saturated `train_rate` at 1.0 for all 8 projects. **Use 90-day
   slices (annualised)** —
   `estimate_transition_rates(slice_days = 90)`. Already wired.
8. **camel detached HEAD on tag camel-1.6.0**: `git -C
   data/camel/git_repo log` shows 2,994 commits. RefMiner on `main`
   branch finds 65,803 commits — full history. Always specify
   `main` for camel ops.
9. **camel mvn fails on Java 26** — even with `-Dcheckstyle.skip=true`.
   archpat lift on camel deferred.
10. **junit5 Gradle pins JDK 25** via toolchains. Skip archpat lift
    on junit5 unless you install JDK 25.
11. **GitHub 100MB hard limit** — `data/tomcat/mbox/tomcat-dev.mbox`
    (1.6GB) and 5 zips (160–770MB) were blocked. `.gitignore`
    now covers `data/*/mbox/*.mbox`, `data/_zips/`,
    `data/*/mod_mbox/`, `data/*/bk_mod_mbox/`, `data/*/pipermail/`,
    `data/*/jira/`, `data/*/github/`, `data/*/derived/refminer*.json`,
    `data/helix_clean/`, `data/*/git_repo/`. If push ever fails on
    100MB again, run `scripts/fix_gh_push.sh` (uses git-filter-repo;
    destructive history rewrite — user must authorize).
12. **Anonymous URL still reveals identity**: `github.com/sci4seng/…`
    contains username. Don't share the repo URL as supplementary
    material; use anonymous.4open.science mirror.
13. **Congruence model defaults match Helix's measured values**
    (Brokers=3, Clusters=5). Partly circular — model was tuned to
    a prior radio_silence run. Treat airflow (4/7) + tomcat (39/33)
    as the real falsification test bed for congruence.
14. **Bugs lift R port uses grid-search Goel-Okumoto** (6×6 = 36
    candidates). Replace with `nls()` or `optim()` for publication.
15. **`scripts/gen_rich.py` is the source of truth** for 17 model
    pages. Edits to `docs/models/<name>.html` will be overwritten
    on next regen. To preserve hand-tuning, set `manual=True` in
    the `M[<name>]` dict — generator skips. (`brooks` already is.)
16. **The `docs/index.html` is HAND-edited**, not generated.
    Regenerating model pages won't touch the index. If you add a
    new model, update both `gen_rich.py` and the index by hand.
17. **diary/ vs NOTES.md**: `NOTES.md` is coder's personal session
    diary (his own writing). `diary/` is shared correspondence
    archive (collaborator emails + prompt drafts). Don't write
    Claude-generated content into `NOTES.md`.

## KEY DOCS POINTERS

- `findings.md` — 5 F-findings, paper-prose.
- `TIMETABLE.md` — per-model wall-clock log, S0–S20 schema.
- `sanity.md` — per-cell bug-count + identity-bridge status (SME §1+§2).
- `STATE.md` — original framing + 2026-05-24/25 session update.
- `NOTES.md` — coder's personal session diary (don't auto-edit).
- `diary/` — emails, prompts, status drafts.
- `kaiaulu_notes/known_bugs.md` — kaiaulu source bugs (5 total).
- `docs/index.html` — site root.
- `docs/other.html` — 47-candidate inventory.
- `scripts/gen_rich.py` — site regeneration. `M[<name>]` dict is
  single edit-point per model.
- `outputs/` — 63+ CSVs (lifts, audits, comparisons).

## ONE-LINE NEXT STEP

Pick one of the 15 buildable candidates from `docs/other.html`
(ownership recommended — Bird et al's regression is the cleanest
paper anchor) and write `lifts/lift_ownership.Rmd` + add the entry
to `gen_rich.py`'s `M["ownership"]` block.
