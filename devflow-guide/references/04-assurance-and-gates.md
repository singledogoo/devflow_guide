# Assurance, risks and gates

## Risk escalation
Consider user impact, safety, privacy/security, availability, hardware damage, irreversibility and recovery cost. A `high` setting should impose additional evidence, but only relevant domain standards and qualified assessors can determine regulatory compliance. Standards differ: ASPICE is automotive process assessment, ISO 26262 applies to relevant road-vehicle functional safety, MISRA is a coding-guideline family; none is an automatic blanket obligation for every embedded project.

## Stage gates

### Design preflight
- Requirements testable, approved boundary/owner, assumptions and risks recorded.
- Significant architecture changes have evaluated alternatives and ADR status; proposed designs are NOT shipped contracts.
- Interface version/format/timing/error states explicit; verification strategy mapped.
- **Human authority** accepts design/risks when required.

### Merge preflight
- Scope and baseline confirmed; reviewed code + tests + impacted docs in same change.
- Reproducible automated checks with real results; test environment and SHA recorded.
- Required external CI and PR review are checked in provider; local file existence is not proof.
- No high-severity security issue unassessed; negative tests and backward compatibility considered.

### Release preflight
- Exact artifact build configuration, version/hash/SBOM as risk warrants; immutable reproducible baseline.
- Environment and target-specific verification; firmware version/hardware matrix or DB migration accordingly.
- Restore/rollback verified or explicit non-reversibility accepted; incident contacts/runbook present.
- Approval from authorized release owner, independent review where required, and external policy gates complete.

## Evidence quality hierarchy
- **Verified machine evidence:** actual CI provider/tool output or reproducible command with environment, revision and log/artifact references.
- **Verified human evidence:** reviewer or test operator sign-off with identity, date, scope and accessible test record.
- **Self-reported:** copied summary, checkbox, local JSON. Useful for tracking, not a substitute for trusted validation.
- **Unknown:** checks not run, tools unavailable, logs absent, stale revision or insufficient environment matching.

High assurance needs trace coverage in both directions: requirement→test/evidence and test/evidence→justifying requirement; include negative tests and hazard mitigations. `TRACEABILITY.csv` is a **minimal ledger**, not proof that semantic coverage is complete.

## Configuration management
Capture selected toolchain/compiler versions, dependency lockfile hashes, SDK/BSP, board rev, kernel/DT/bootloader, build options, third-party libraries, environment controls, binary hash, git SHA/tag, approval state and change request. Avoid committing credentials. Make reproducibility possible without pretending every build is bit-for-bit reproducible.

## Deviations and hotfix
When essential gates cannot be met, log missing gate, severity, accountable approver, bounded scope, compensating measures, deadline and follow-up issue. Never automatically bypass security/functional-safety requirements. In a production emergency, restore service via safe controlled action; retrospective test and documentation closure are required.

## CLI interpretation
`scripts/devflow.py audit` checks **structure and consistency**, not correctness or actual remote status. `gate` is **local readiness screening**: even a clean local screen reports external sign-offs as `UNKNOWN`. Never use its result to assert a release is approved.
