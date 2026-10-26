---
name: devflow-guide
description: Govern software engineering workflow, project structure, requirements, architecture, ADR decisions, interface contracts, task breakdown, code changes, traceability, reviews, tests, CI and release gates. Use for new or existing embedded Linux/MCU/DSP/ISP software, Web/API services, and desktop/mobile/Qt applications; adapt rigor to risk and never overwrite existing code or documents.
compatibility: Works with Codex and Agent Skills-compatible agents. Optional offline management CLI needs Python 3.9+; Git is optional for inspection/diff. No third-party Python packages or network access required.
metadata:
  display-name: devflow_guide
  version: "1.0.0"
---

# devflow_guide — software engineering governance skill

## Objective and boundaries
Manage the **entire change lifecycle** from verified requirement to traceable release, while maintaining one coherent source of truth between documents, code and tests. This is a *process assistant*, not an auto-approval authority, project generator, or safety-certification substitute. Select the **smallest defensible process** according to project risks. Preserve existing working practices when they meet the same controls.

## Activation conditions
Invoke when the user asks to (a) start or standardize a software project, (b) plan/implement/review a feature, (c) design or audit architecture and directories, (d) govern docs↔code↔tests, (e) assess integration/release readiness, or (f) recover a drifted or undocumented project. Do **not** run initialization on simple conceptual Q&A.

## Required startup sequence (read-only first)
1. Read `README.md`, local `AGENTS.md`, `.devflow.json` (if present), repository state, actual code tree, build/test/CI files, and relevant design docs. Honor higher-priority instructions and existing repo conventions.
2. Run `python <skill-root>/scripts/devflow.py inspect --root <repo>` where Python is available, or inspect manually. Detection is **advisory**: report embedded/web/app/hybrid candidates with evidence; do not silently force ambiguous projects into one category. For a monorepo operate on the chosen subproject scope.
3. Determine `project_type` = embedded | web | app; `assurance` = lite | standard | high. Choose on **consequence of failure and assurance obligations**, not code size. High-risk contexts require appropriate safety/security/domain specialists and standards; this skill alone does not certify compliance. Read `references/01-profiles.md`.
4. Identify current phase, existing authoritative docs, open changes, available test environments and missing evidence. Produce a **short adoption assessment** (existing / missing / conflicting / suggested, planned files). Ask before destructive, contractual or materially irreversible operations.
5. For a **new or explicitly approved adoption**, show a dry run: `python <skill-root>/scripts/devflow.py init --root <repo> --profile <type> --assurance <level> --dry-run` (add `--adopt` when existing). Only then execute `init` if the user authorized setup. `init` does not overwrite existing files, source, Git or CI.

## Continuous development loop (repeat per independently testable change)
1. **Request**: Write verifiable requirement ID `REQ-*`, acceptance conditions, target hardware/environment, measurable non-functional budgets, out-of-scope and failure scenarios; decide whether it is a bugfix, feature, refactor, hotfix, or design-only change.
2. **Risk-first design**: Evaluate risk, alternatives, boundaries and interfaces; maintain `ARCHITECTURE.md`, contracts and an ADR **only if an enduring decision is being made**. For a small isolated change, concise issue-level design is enough. Do not introduce architectural abstractions without a demonstrated need.
3. **Task contract**: For each issue define parent requirements, scope, dependencies, touched modules, expected artifacts, tests, negative tests, review criteria, stop conditions and owner. Use `references/03-task-and-pr.md`.
4. **Implementation**: Work in a narrow change-set; respect repository coding/build conventions. Prefer tests at the appropriate level. Never silently refactor unrelated subsystems. Keep requirements, architecture, interface specs, configuration, source and tests coherent **within the same PR**.
5. **Verification**: Execute actual available tests or explicitly state which were not run and why. Evaluate unit, integration, target/HIL or E2E according to the profile. Record command, environment, result, commit/revision and evidence location; **never hallucinate CI or hardware test results**.
6. **Review**: Run the read-only local audit `python <skill-root>/scripts/devflow.py audit --root <repo> [--base <git-ref>] [--strict]`. Review architectural compatibility, failure and rollback paths, security, traceability and unintended scope drift. Missing proof is `UNKNOWN`/`BLOCKED`, not `PASS`.
7. **Gate**: Run `python <skill-root>/scripts/devflow.py gate --root <repo> --stage design|merge|release`. This is a **local preflight**; external PR reviews/branch rules/CI, deployment permission, hardware sign-off and regulatory compliance MUST be verified by their actual systems/humans. `gate` must not be reported as production approval.
8. **Close**: Record issue→requirement→design/contract→PR/commit→test→evidence→version. Update changelog/release notes when externally observable behavior changes. Explicitly distinguish `design accepted`, `PR merged`, `build verified`, `release approved`, and `released`.

## Stage transitions and required honesty
- Design: verifiable requirements, known risks, interfaces, architecture impact, named verification strategy. No premature claim of 'contract released' for a Proposed ADR.
- Merge: relevant docs+code+tests changed together, reproducible local results, real remote CI/review check where required. The CLI cannot authenticate remote results.
- Release: tested immutable artifact/configuration, version+hash, compatible hardware/runtime and migration/rollback plan, recorded approvals. A green unit-test run is not release approval.
- Mark evidence `verified`, `self-reported` or `not-available` and document who/what verified it. Never turn samples or unchecked files into proof.
- Escalate when requirements conflict, tests are unavailable, a security/functional-safety issue arises, Git state is unexpected, or a change cannot be safely reversed.

## Project-type overlays
- **Embedded**: board/SoC/BSP/bootloader/firmware compatibility matrix; clock/reset/power/DT and I/O; DMA/cache/IOMMU/buffer contracts; real-time and memory budgets; host+target+HIL tests; fault injection, power interruption, flashing/recovery, binary provenance. See `references/01-profiles.md`.
- **Web**: API/schema/migration compatibility, authn/authz, privacy, dependency security, contract/E2E/load tests, observability, progressive delivery, database restore and rollback. See `references/01-profiles.md`.
- **App**: UI states/accessibility, lifecycle/threading, OS/device compatibility, offline/persistence, installers/signing, app upgrade/downgrade/data migration, crash handling and support rollback. See `references/01-profiles.md`.
- **High assurance** adds bidirectional requirement traceability, configuration baselines, independent/risk-based review, risk register, controlled deviations, immutable test evidence and explicit approvals. See `references/04-assurance-and-gates.md`.

## Files, references and tooling
- Lifecycle, artifacts and definitions of done: `references/02-lifecycle.md`.
- Task contract, PR reviews and agent report format: `references/03-task-and-pr.md`.
- High-reliability controls, test strategy, evidence classification: `references/04-assurance-and-gates.md`.
- Directory/document design, anti-duplication, change-impact matrix: `references/05-docs-and-layout.md`.
- Domain examples and terminology: `references/06-examples-and-glossary.md`.
- Reusable Markdown/CSV templates: `assets/templates/`.
- Non-destructive CLI: `scripts/devflow.py` (subcommands: `inspect`, `init`, `audit`, `gate`; `--help`).
- Human-readable detailed offline manuals: `../manual/zh/devflow_guide.html` (Chinese) and `../manual/en/devflow_guide.html` (English).

## Mandatory agent response format on actual project work
1. **Context**: profile, assurance, scope, branch/baseline, inspected artifacts and unknowns.
2. **Decision**: what changes, why, effects, risk, alternatives only if material.
3. **Plan**: small tasks, target files, test/evidence and gate.
4. **Execution**: changed and untouched files, requirement/ADR status, commands and outcomes; do not claim unexecuted actions.
5. **Review**: PASS/FAIL/UNKNOWN per check, remaining risks, explicit approvals required.
6. **Next action**: the smallest clear actionable step; no invented commit SHA, PR, CI or acceptance sign-off.

## Safety and compatibility
- Read-only by default. Do not create files without user-approved initialization/change request; scripts have no remote access, deletion, overwrite or execution of project build scripts.
- Never mutate `.git`, secrets, user source files, CI, existing docs, or branch settings during scaffold initialization.
- If existing docs are authoritative, map them; do not create shadow specifications. Diagnose conflicts before edits.
- If a project mixes types, select a **scope** and additional overlays; do not merge incompatible quality gates into a misleading average.
- For emergency fixes allow a short risk-accepted path **only with recorded rationale, minimum regression and later documentation closure**; do not silently skip essential safety gates.
