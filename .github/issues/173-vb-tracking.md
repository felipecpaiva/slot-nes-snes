---
title: "Virtual Boy: Beetle VB, one eye on the flat panel, a shelf of its own"
phase: 16
area: device
type: tracking
size: L
depends_on: [143-s32x-tracking]
---

## Why
The maintainer asked for the Virtual Boy as a full platform. One core, Beetle VB pinned at `d5ae54c`, one shelf `Games/VB`, the left eye in the palette colour on the flat panel (ADR 0097).

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0097 and these issues.
- [x] 2. 174-vb-core-build
- [x] 3. 180-vb-tests, core half: patch 0102
- [x] 4. 175-platform-vb (patch 0103)
- [x] 5. 176-vb-options (patch 0104)
- [x] 6. 177-vb-screen (patch 0105)
- [x] 7. 179-vb-input (patch 0106)
- [x] 8. 178-vb-saves (patch 0107, tests only)
- [x] 9. 180-vb-tests, platform half (patch 0108)
- [x] 10. 181-vb-carts (patch 0109 and tools/fetch-labels.py)
- [ ] 11. 182-vb-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 2 to 10 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the Beetle VB dylib.
- [x] A GBA game after a Virtual Boy game equals a GBA only run (`vb_then_gba.rs`).
- [x] README, docs/PLAN.md and LICENSING.md describe the Virtual Boy.
- [ ] Device gate (issue 182).

## Device check (RG34XXSP)
Issue 182.

## References
- ADR 0097; docs/cart-art/VB.md
