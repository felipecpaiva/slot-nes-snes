---
title: "PC Engine CD: CD-ROM2 and TurboGrafx-CD discs on Beetle PCE Fast, a shelf of its own"
phase: 21
area: device
type: tracking
size: L
depends_on: [209-sgx-tracking]
---

## Why
The maintainer asked for the PC Engine CD as its own platform. No new core: Beetle PCE Fast, already shipped for the TurboGrafx-16, built with its CHD reader; one shelf `Games/PCECD`; the System Card 3.0 checked, never shipped (ADR 0104). He owns 27 discs, all CHD.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0104 and these issues.
- [x] 2. 217-pcecd-core-build (HAVE_CHD=1) and the core half of the tests (patch 0135)
- [x] 3. 218-platform-pcecd (patch 0136)
- [x] 4. 219-pcecd-bios (patch 0137)
- [x] 5. 220-pcecd-cases (patch 0138 and tools/fetch-labels.py)
- [ ] 6. 221-pcecd-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 5 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1`.
- [x] README, docs/PLAN.md and LICENSING.md describe the PC Engine CD.
- [x] The library: `docs/rom-library/best-copy/pcecd-adds.tsv` (workspace), repacked CHDs staged off the Mac.
- [ ] Device gate (issue 221).

## Device check (RG34XXSP)
Issue 221.

## References
- ADR 0104; docs/cart-art/PCECD.md; docs/research/next-systems-2026-10-20.md (PC Engine CD)
