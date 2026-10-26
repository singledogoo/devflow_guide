# Short worked examples and glossary

## Embedded: RK3588 video pipeline
`REQ-VID-001` defines frames/s and latency on named board/BSP and environment. Design notes describe PCIe receive buffer ownership, DMA/Cache coherency, ring size, producer/consumer rate, drops and recovery. `ADR-0001` records why bounded ring buffer over unbounded queue. `TEST-VID-001` validates 2-hour capture with actual logs per board revision. CI cross-compile passing is NOT equivalent to target board validation. Firmware manifest pins kernel, DTB, user program, toolchain, board revision and checksums.

## Web: login and session
`REQ-AUTH-001` specifies authenticating users and rejecting unauthorized calls (not just 'login works'). API schema defines inputs, error codes and token renewal. Threat notes include credential leaks, brute force, privilege escalation and logout revocation. Unit, contract, E2E and negative access tests linked. Rolling deployment must account for session compatibility and DB migration reversibility.

## Application: Qt media player
`REQ-PLAY-001` defines supported H.265 content variants, start latency and failure behavior on OS/version/decoder combinations. Architecture separates UI event loop, decoder worker and rendering queue; ownership/threading documented. Tests cover malformed input, close/open loops, device loss, installer repair, update/rollback and codec compatibility. Local unit tests cannot certify GPU driver coverage.

## Terms
- **SRS**: Software Requirements Specification, the agreed description of required behavior and constraints.
- **PRD**: Product Requirements Document, usually business/user need framing.
- **ADR**: Architecture Decision Record, what was chosen, why and status (Proposed/Accepted/Superseded).
- **C4**: layered architecture diagrams (context/container/component/code when useful), not a compulsory file format.
- **Docs as Code**: version, review and validate docs alongside code.
- **Traceability**: ability to navigate requirement ↔ design/code ↔ test ↔ evidence.
- **CI**: Continuous Integration, automated checks triggered by integration, not a promise of deployment.
- **CD**: Continuous Delivery/Deployment depending on context; delivery means releasable, deployment means automated release to users.
- **HIL**: Hardware-in-the-Loop, automated tests involving real hardware/system interfaces.
- **BSP**: Board Support Package, the OS/driver/startup board integration layer.
- **DTS/DTB**: Device Tree Source/Binary describing hardware topology/resources to kernels that use device tree.
- **DMA**: Direct Memory Access, transfers without the CPU copying every byte; cache ownership still matters.
- **IOMMU**: memory mapping/protection used by I/O devices.
- **E2E**: End-to-End, tests an observable user/business flow across components.
- **SAST/SCA**: static application security testing / software composition analysis.
- **SBOM**: Software Bill of Materials, inventory of software components and dependencies.
- **Gate**: a controlled checkpoint; local checklist and official approval are not the same thing.
- **Baseline**: identified approved versions of documents/configuration/software used as reference for changes.
- **DoD**: Definition of Done, agreed completion conditions.
