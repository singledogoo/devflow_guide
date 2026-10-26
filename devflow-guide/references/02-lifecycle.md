# Lifecycle and phase-specific exit criteria

The phases are a repeatable *small-batch loop*, not one mandatory sequential waterfall. Shared canonical identifiers: `REQ-*`, `ADR-*`, `TASK-*`, `TEST-*`, `RISK-*`, `REL-*`. Every item should have stable semantics; do not recycle IDs for different meanings.

| phase | essential activities | artifact/evidence | honest exit criterion |
|---|---|---|---|
| 0 Discover | inspect code/docs, runtime, build, owners, dependencies and risks | adoption assessment | unknowns listed, scope stated |
| 1 Need | who needs what, success metrics, out of scope, failure paths | REQ + acceptance | testable, noncontradictory |
| 2 Risk / PoC | verify uncertain performance/hardware/security assumptions | decision or investigation record | evidence or risk disposition |
| 3 Architecture | boundaries, interfaces, state/data path, capacity, deployment | architecture, critical ADR | key choices reviewed, Proposed vs Accepted clear |
| 4 Detail | contract, sequence, data layout, lifecycle and errors | design/contract | implementer and tester can derive behavior |
| 5 Task | slice vertically, dependencies, reviewers, test plan | TASK issue | task narrow and measurable |
| 6 Build | code, tests, docs same change | commits / tests | local checks reported honestly |
| 7 Integrate | automated checks, PR independent review | CI URL, review, commit | all required external checks truly complete |
| 8 Verify | hardware/end-to-end/stability/security/performance | evidence to environment+SHA | actual acceptance passed on target scope |
| 9 Release | baseline, artifacts/hash, notes, rollback, approvals | release record | approval + controlled deployment proven |
| 10 Operate | issues, incident feedback, patch prioritization | logs, issue, postmortem | next change enters loop |

## How to write verifiable REQs
BAD: `软件运行稳定且实时性很好。`
GOOD: `REQ-VIDEO-001: on RK3588 board rev B, BSP X, RAW10 1920×1080@50Hz input, after 5-min warm-up over a 2h run, 99th percentile full-frame latency <= 50 ms and dropped frames <= 0.1%, measured by timestamps of source and output within the documented capture harness.`
These values are *demonstration only* and must not be treated as product requirements without acceptance.

Minimum: identifier, scope, preconditions/inputs, measurable behavior and limits, exclusions, failure handling, method of verification, status/owner, revision link. For security and integrity requirements include adversarial/negative cases.

## Architecture decision record
An ADR is valuable when a decision is expensive to reverse or crosses team/module boundaries (e.g. shared DMA ring vs copy queue; DB schema strategy). An exploratory idea is `Proposed`, not an authoritative contract. `Accepted` decision means approved design only; code, test and release have separate statuses. On replacement use `Superseded` and link successor. Do not write ADRs for trivial naming or formatting.

## Change impact matrix
| changed | assess/update |
|---|---|
| requirement | acceptance, interfaces, architecture, affected tests, trace |
| interface / schema | consumers, compatibility, versioning, negative tests, docs |
| concurrency / timing | state machine, budgets, fault/recovery tests |
| persistent data | migration, backups, restore, rollback |
| BSP/DTS/hardware | board matrix, dependencies, HIL, flashing and release |
| security boundary | threat model, permissions, tests, deployment config |
| build / toolchain | reproducibility, CI pipeline, provenance, release manifest |

## PR cannot substitute for release
`Draft → Proposed → Accepted` (design), `Open → Reviewed → Merged` (code), and `Candidate → Approved → Released` (artifact) are separate state machines. `tests=green` is insufficient to claim acceptance when tests do not cover the target environment.
