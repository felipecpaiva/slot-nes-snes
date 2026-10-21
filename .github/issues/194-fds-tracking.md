---
title: "Famicom Disk System: fceumm, a yellow disk shelf of its own"
phase: 18
area: device
type: tracking
size: M
depends_on: [33-deferred-fds]
---

## Why
The maintainer asked for the Famicom Disk System as a full platform on the fceumm that already ships for the NES (ADR 0101). It closes the v1 deferral (issue 33).

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0101 and these issues.
- [x] 2. 195-platform-fds (patch 0120)
- [x] 3. 196-fds-screen (patch 0121)
- [x] 4. 197-fds-bios (patch 0122)
- [x] 5. 198-fds-disk (patch 0123, with the core tests)
- [x] 6. 199-fds-saves (patch 0124)
- [x] 7. 200-fds-tests (patch 0125)
- [x] 8. 201-fds-carts (patch 0126, tools/fetch-labels.py)
- [ ] 9. 202-fds-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 8 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1`.
- [x] README and docs/PLAN.md describe the disk shelf, the BIOS, the disk control and the saves.
- [ ] Device gate (issue 202).

## Device check (RG34XXSP)
Issue 202.

## References
- ADR 0101; docs/research/next-systems-2026-10-20.md (FDS)
