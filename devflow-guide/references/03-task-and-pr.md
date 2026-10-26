# Issue, implementation and PR review contract

## TASK template (copy to issue tracker)
```
TASK-ID: TASK-<SCOPE>-NNN
TYPE: feature | defect | refactor | experiment | documentation | hotfix
REQ: REQ-...
WHY / GOAL: observable outcome, not implementation guess
SCOPE: changed paths and explicitly excluded paths
CONTEXT: baseline branch / target platform / linked ADR and interface contract
APPROACH: bounded steps; alternatives if decision is material
ACCEPTANCE: verifiable happy and failure paths, measurable budgets
TESTS: name, environment, commands, required hardware / E2E / HIL
RISK: security, safety, data loss, backward compatibility, rollback
EVIDENCE: where result/logs will be stored, verified-by
DONE WHEN: code + docs + tests + review + trace are linked
```

## PR template
```
## Purpose / Requirements
REQ-..., TASK-...; expected behavioral changes
## Design impact
ADR status, public API/protocol change, migrations, hardware matrix
## Changed files and why
list of key paths, what was intentionally not touched
## Tests executed (real results)
command; environment; commit; result; evidence ref/URL
## Tests NOT run and risk
name and explanation; no implied pass
## Security / safety / backwards compatibility
threat/error states, rollback/upgrade, data and timing impact
## Docs / trace links
REQ → ADR/contract → implementation → TEST → evidence
## Gate / approval
reviewers, pending checks, explicit unverified items
```

## Review checklist
1. Implementation exactly fits scope and acceptance; no unrelated changes.
2. Contracts and consumers are compatible; input validation and errors specified.
3. Concurrency/ownership/lifecycle resource leaks and recovery considered.
4. Security boundaries, secrets and unsafe paths reviewed.
5. Necessary requirement/architecture/protocol docs changed in same PR.
6. Reproducible tests have correct assertions, not vacuous pass; target conditions accurate.
7. Regressions, performance budgets and upgrade/rollback impact covered.
8. CI/review actual results retrieved from trusted system or marked unknown.

## AI assistant result reporting
| Check | result | verified-by | evidence |
|---|---|---|---|
| format | PASS/FAIL/UNKNOWN | local command | command output/path |
| unit | PASS/FAIL/UNKNOWN | command CI system | SHA/log URL |
| target hardware | PASS/FAIL/UNKNOWN | board ID / tester | log and env |
| remote CI | PASS/FAIL/UNKNOWN | provider API | run URL/check-id |
| human approval | APPROVED/PENDING/UNKNOWN | reviewer | PR approval record |

Use a truthful `UNKNOWN` for inaccessible or unexecuted checks. Never invent timestamps, token budgets, SHA, PR numbers, server status, reviewer or hardware results.
