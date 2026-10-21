---
title: "PICO-8: FAKE-08, a shelf of its own, no states"
phase: 19
area: device
type: tracking
size: L
depends_on: [194-fds-tracking]
---

## Why
The maintainer asked for PICO-8 as a full platform. One core, FAKE-08 pinned at `814991a` with its z8lua submodule and `cores/fake08/slot.patch`, one shelf `Games/PICO8`, the 128x128 picture at 3x (ADR 0102). PICO-8 itself is never shipped.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0102 and these issues.
- [x] 2. 204-pico8-core-build
- [x] 3. 207-pico8-tests, core half: patch 0127
- [x] 4. 205-platform-pico8 (patch 0128)
- [x] 5. 206-pico8-carts (patch 0129 and tools/fetch-labels.py)
- [x] 6. 207-pico8-tests, platform half (patch 0130)
- [ ] 7. 208-pico8-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 6 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the FAKE-08 dylib.
- [x] A GBA game after a PICO-8 game equals a GBA only run (`pico8_then_gba.rs`).
- [x] README, docs/PLAN.md and LICENSING.md describe PICO-8.
- [ ] Device gate (issue 208).

## Device check (RG34XXSP)
Issue 208.

## References
- ADR 0102; docs/cart-art/PICO8.md; `docs/rom-library/best-copy/pico8-adds.tsv` (workspace)
