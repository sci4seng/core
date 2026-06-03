---
title: Future-work candidates
parent: Models
nav_order: 99
---

# Future-work candidates (32)

Named in the SE literature but not yet built into `paper/sd.py`. Source-quality tiers:

- **A** = peer-reviewed archival (DOI / IEEE / ACM / journal)
- **B** = book or grey-lit anchor; partial peer-reviewed companion
- **C** = tacit / named-only / not formally modelled

Data legend:

- **have**: data on disk now, lift could run
- **partial**: would need 1–2 days of new pipeline
- **none**: structurally absent on the 8-project family

## Tier A (12)

| name | year | source | data |
|---|---|---|---|
| `cace` | 2015 | Sculley et al NeurIPS — Hidden Technical Debt in ML | none — same gap as drift |
| `collapse` | 2024 | Shumailov et al Nature — 10.1038/s41586-024-07566-y | none — no training-data provenance logs |
| `commons` | — | Hardin Science 1968 — 10.1126/science.162.3859.1243 | partial — per-team file-touches share of common modules; no CI data |
| `diffusion` | 1969 | Bass Management Science — 10.1287/mnsc.15.5.215 | partial — first-use spreading of an internal API call could be Bass-fit; needs API-usage s |
| `drift` | — | Gama et al ACM CSUR 2014 — 10.1145/2523813 | none — no project on disk is an ML system with production accuracy logs |
| `escalation` | — | Staw Org Behavior 1976 — 10.1016/0030-5073(76)90005-2 | none — sunk-cost decisions not visible in OSS git history |
| `estbias` | — | Jorgensen IEEE TSE 2004 — 10.1109/TSE.2004.108; Kahneman+Tversky '79 | none — no project on disk records estimate-vs-actual time |
| `exposure` | 2006 | Frei et al SIGCOMM LSAD — 10.1145/1162666.1162671 | partial — NVD CVE entries for openssl/tomcat exist publicly; would need NVD-to-commit mapp |
| `nosilver` | 1986 | Brooks IEEE Computer — 10.1109/MC.1987.1663532 | partial — essential vs accidental complexity is inherently judgmental; could proxy via Ref |
| `shiftburden` | — | Repenning, Sterman ASQ 2002 — 10.2307/3094847 | partial — heuristic hotfix detection from commit msg (\"hotfix\", \"urgent\") + SZZ recurr |
| `tenx` | 1968 | Sackman, Erikson, Grant CACM — 10.1145/362851.362858 | partial — per-developer LOC/commit/day as productivity proxy; not Sackman's controlled-tas |
| `wirth` | 1995 | Wirth IEEE Computer — 10.1109/2.348001 | partial — binary size per release tag computable; hardware capability is exogenous (Moore' |

## Tier B (9)

| name | year | source | data |
|---|---|---|---|
| `brokenwin` | — | Hunt &amp; Thomas, The Pragmatic Programmer (book); Wilson+Kelling 1982 (essay) | partial — could quantify TODO/FIXME density growth over time |
| `buildtrap` | — | Perri, Escaping the Build Trap (book) | none — no value-realised data in OSS git |
| `erodegoals` | — | Senge archetype (book) | partial — CI test-suite pass-rate drift would need GH Actions logs |
| `goodhart` | — | Goodhart 1975; Strathern 1997 (peer-reviewed adaptation) | none — metric-gaming signals are mostly absent in OSS |
| `patchherd` | — | SIR-shaped; no SE-specific peer-reviewed source | none — fix-uptake telemetry not in OSS git |
| `postel` | — | RFC 760/793; IAB RFC 5841 \"harmful consequences\ | none — interop ambiguity logs not in OSS git |
| `riskcomp` | — | Peltzman JPE 1975 — 10.1086/260352 | none — would need a controlled experiment (more tests → less careful code) |
| `secondsys` | 1975 | Brooks, MMM (book) | none — Apache projects don't have a clean \"system #2 attempt\" event |
| `testshape` | 2009 | Cohn, Succeeding with Agile (book; \"test pyramid\") | partial — infer test-tier from path prefix (unit/integ/system) heuristically |

## Tier C (11)

| name | year | source | data |
|---|---|---|---|
| `alertfatigue` | — | [tacit, SOC literature] | none |
| `bugage` | — | [tacit] | partial — would need issue-open-time time series |
| `configdrift` | — | [tacit] | none — environment configs are deploy-time, not git-resident |
| `deadcode` | — | [tacit] | partial — could approximate via Depends reachability (callable but never called) |
| `docdrift` | — | [tacit] | partial — README/docs/*.md git-blame age vs whole-repo touch rate |
| `flagdebt` | — | [tacit] | partial — could grep for feature-flag patterns in code, age them via git blame |
| `fwchurn` | — | [tacit] | none — cross-project framework adoption telemetry absent |
| `hyrum` | — | [named, unmodeled — Hyrum's Law] | none — would need usage telemetry of internal APIs |
| `labeldebt` | — | [tacit] | none |
| `migration` | — | [tacit] | partial — detect via parallel-API patterns in commit messages (\"deprecat\", \"migrate\") |
| `revlat` | — | [tacit] | **have** — GH PR data for Helix + kaiaulu has review wait timestamps |

