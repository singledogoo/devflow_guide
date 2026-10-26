# Profile and assurance selection

Choose project type by *runtime and deliverable*, not the programming language. C++ web server is `web`; Qt desktop player is `app`; Linux V4L2 driver is `embedded`. Combined projects are `hybrid`: apply one primary profile to each subproject/scope and document boundary contracts.

| type | distinguishing outputs | dominant risk | mandatory focus |
|---|---|---|---|
| embedded | flashed image/firmware, driver, DSP/MCU binary | physical I/O, timing, recovery, device compatibility | board matrix, boot/power, memory/interrupt/DMA, real hardware tests |
| web | browser client, API, backend service | network exposure, data migrations, concurrency, availability | OpenAPI/contracts, authn/authz, migrations, monitoring/rollback |
| app | desktop/mobile installer/application | UI, lifecycle, OS compatibility, update/data loss | UI state, packaging, OS/device test matrix, recovery |

Assurance:
- `lite`: individual/prototype/low impact; essential readme, verifiable acceptance, design rationale and a reproducible check. Keep records inline where practical.
- `standard`: team/project exposed to real users; tracked requirements, interfaces, key ADRs, peer review, CI, test matrix and versioned release.
- `high`: safety/security/mission-critical, contractual traceability or costly recovery; add approved baseline, hazard/risk assessment, bidirectional traceability, independence, configuration management, controlled changes, substantiated test evidence and rollback evidence. Not an assertion of regulatory compliance.

## Embedded overlay

**Before coding**: SoC and board revision, schematic/TRM, boot chain/OS/BSP, power rails, clock/reset/pinmux, DTS, bus wiring, video path, DMA ownership, cache coherency, concurrency and worst-case budgets.

**Runtime model**: init/probe, suspend/resume, stream on/off, IRQ contexts, buffer lifecycle, error propagation, backpressure and shutdown. Contract includes buffer format/stride/endianness/alignment/ownership, timeout and retry semantics. Distinguish MIPI/CSI receiver errors from CIF/ISP/DMA/buffer problems.

**Verify**: compile and host unit tests; target board sanity; real inputs, long-run/thermal, abnormal stop-start, malformed frames, power interruptions; compatibility matrix per hardware/firmware revision; HIL when justified. Record exactly which board and BSP were used. Never infer board test from simulator pass.

**Release**: signed/checksummed artifacts where applicable, bootloader/kernel/DT/app version pairing, flashing instructions, known limitations, recovery image/procedure, power-loss interrupted upgrade testing.

## Web overlay

**Before coding**: user journey, domain boundaries, request/response and error schemas, security trust boundaries, authn vs authz, data classification, concurrency, idempotency, compatibility and migration plan.

**Verify**: unit, integration, contract, E2E, negative authorization, input validation, migration/rollback, load and dependency/security scans according to risk. Keep secrets out of source/reports.

**Release**: immutable image/build, deployment parameters, health checks, rollout and rollback; carefully assess non-reversible data migrations, backups, observability and incident response.

## Application overlay

**Before coding**: supported OS/CPU versions, UI/navigation/state model, permissions, threading/main-loop, local persistence, offline behavior, file format compatibility, package/signing requirements.

**Verify**: UI unit/integration/e2e, clean install/upgrade/uninstall, OS/graphics hardware matrix, resource leaks, crashes/recovery, accessibility, import/export consistency. Media app also tests codec, buffers, A/V synchronization and rendering.

**Release**: signed installers/store artifacts as applicable, install/update/rollback, local data migration/backups, release notes and crash diagnostics.

## Multi-project rule
A repo containing `drivers/`, `server/`, `frontend/`, and `desktop/` is not safely classified by counting extensions. Create one governing issue/architecture describing interface boundary plus profile-specific controls for each subproject. Do not bootstrap unrelated subprojects on the assumption that all need the same templates.
