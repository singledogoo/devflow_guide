# Documentation and directory architecture

## Principle: one source of truth
Preserve existing README, build system, source directories, architecture docs and CI. In an existing repository, `init --adopt` must map recognized documents into `.devflow.json` rather than create competing specifications; for any unrecognized canonical document, edit the map deliberately. Do not move files just for formatting conformity.

Recommended **managed** space for a new project (existing projects may map elsewhere):
```
<repo>/
  .devflow.json                         profile/assurance + document map
  README.md                             existing or new project entry
  AGENTS.md                             optional short instructions only, user-authorized
  docs/devflow/
    INDEX.md                             owner, decision states, scope
    requirements/REQUIREMENTS.md        REQ / acceptance
    architecture/ARCHITECTURE.md        contexts/components/data/quality attributes
    architecture/adr/                 accepted/proposed decisions
    interfaces/CONTRACTS.md             formats, errors, versioning
    testing/TEST_PLAN.md                levels, env, cases, CI/HIL
    testing/TRACEABILITY.csv            REQ→DESIGN→TEST→EVIDENCE
    release/RELEASE_PLAN.md             release/rollback/approval
    reviews/REVIEW_LOG.md               gate decisions and unknowns
    risk/RISK_REGISTER.md               high only
    governance/BASELINE.md              high only
    embedded/ ...                       domain docs
    web/ ...                            domain docs
    app/ ...                            domain docs
  src/, tests/, build, CI               NEVER created/changed by init
```

## Files as code
- Propose doc changes in the same PR as implementation and tests.
- Use relative links, stable IDs, machine-checked structure, reviewer/owner and revision history through Git.
- Keep human-oriented docs short; reference API schemas/tool outputs rather than duplicate them. OpenAPI/protobuf/header files may be canonical for interfaces—link instead of copying.
- One normative specification per requirement/contract. ADR records why, not parallel executable specs. Generated API docs should be generated and labeled as such.
- For regulated or high-assurance work, formal baseline and records may require tools beyond Git; this skill provides a starting structure only.

## Source tree decisions
- Maintain a runtime/module boundary: e.g. `drivers/`, `platform/`, `application/`, `tests/` for embedded; `frontend/`, `backend/`, `api/`, `infra/` for Web; `ui/`, `application/`, `domain/`, `platform/` for apps, **only when the existing build architecture supports it**.
- Do not impose one universal code layout, add fake modules, or restructure a mature repo just to match a diagram.
- Code ownership/review responsibilities may be implemented using `CODEOWNERS`/branch policies but must be enabled by authorized maintainers and checked at provider.

## Minimal document contracts
- Requirement: ID, source/owner, scenario, preconditions, stimulus and expected measurable response, failure path, constraints, test method, status.
- Architecture: context, boundaries, runtime processes/threads, data/control flows, quality budgets, trust boundaries, assumptions, decisions and open risks.
- Interface: name/version, producer/consumer, encoding/unit/endianness, errors/timeouts, concurrency, backward compatibility and conformance test.
- Test: environment and fixtures, case→REQ mapping, expected result, failure cases, artifact/log capture, actual measured outcomes and limitations.
- Release: version, SHA, artifact hashes, compatible environments, migrations, rollback, approvals, deviations, unresolved issues.

## Tool behavior
`inspect` is advisory and read-only. `init` only writes **missing** config and managed docs; emits skip messages for existing files. Run with `--dry-run` first; use `--adopt` for non-empty projects. It never modifies tracked source, existing docs, CI or Git. `audit` checks file mapping, invalid trace rows, missing file refs and placeholders but cannot know semantic correctness, test execution or compliance.
