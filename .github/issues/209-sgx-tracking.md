---
title: "PC Engine SuperGrafx: Beetle SuperGrafx, a shelf of its own beside the TurboGrafx-16"
phase: 20
area: device
type: tracking
size: L
depends_on: [203-pico8-tracking]
---

## Why
The maintainer asked for the PC Engine SuperGrafx as its own platform. One core, Beetle SuperGrafx pinned at `9c11dcd`, one shelf `Games/SGX`, every card run on the SuperGrafx hardware (ADR 0103). He owns the five SuperGrafx cards and the two SG Enhanced Darius cards.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0103 and these issues.
- [x] 2. 210-sgx-core-build
- [x] 3. 213-sgx-tests, core half: patch 0131
- [x] 4. 211-platform-sgx (patch 0132)
- [x] 5. 212-sgx-carts (patch 0133 and tools/fetch-labels.py)
- [x] 6. 213-sgx-tests, platform half (patches 0132 and 0133)
- [x] 7. 215-sgx-pad (patch 0134)
- [ ] 8. 214-sgx-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 7 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the Beetle SuperGrafx dylib.
- [x] A GBA game after a SuperGrafx game equals a GBA only run (`sgx_then_gba.rs`).
- [x] README, docs/PLAN.md and LICENSING.md describe the SuperGrafx.
- [ ] Device gate (issue 214).

## Device check (RG34XXSP)
Issue 214.

## References
- ADR 0103; docs/cart-art/SGX.md
