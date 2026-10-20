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
- [x] 2. 154-vb-core-build
- [x] 3. 160-vb-tests, core half: patch 0099
- [x] 4. 155-platform-vb (patch 0100)
- [x] 5. 156-vb-options (patch 0101)
- [x] 6. 157-vb-screen (patch 0102)
- [x] 7. 159-vb-input (patch 0103)
- [x] 8. 158-vb-saves (patch 0104, tests only)
- [x] 9. 160-vb-tests, platform half (patch 0105)
- [x] 10. 161-vb-carts (patch 0106 and tools/fetch-labels.py)
- [ ] 11. 162-vb-device-gate

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
- [ ] Device gate (issue 162).

## Device check (RG34XXSP)
Issue 162.

## References
- ADR 0097; docs/cart-art/VB.md
