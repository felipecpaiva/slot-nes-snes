---
title: "Sega 32X: 32X on PicoDrive, a shelf of its own beside an unchanged Mega Drive"
phase: 15
area: device
type: tracking
size: L
depends_on: [70-ngp-tracking]
---

## Why
The maintainer asked for Sega 32X as a full platform. 28 32X games sit on the device's Mega Drive shelf, where Genesis Plus GX cannot run them. One core, PicoDrive pinned at `1890c29`, one shelf `Games/32X` (ADR 0096).

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0096 and these issues.
- [x] 2. 144-s32x-core-build
- [x] 3. 150-s32x-tests, core half: patch 0090
- [x] 4. 145-platform-s32x (patch 0091)
- [x] 5. 146-s32x-options (patch 0092)
- [x] 6. 147-s32x-screen (patch 0093)
- [x] 7. 148-s32x-saves (patch 0094, tests only)
- [x] 8. 149-s32x-input (patch 0095, tests only)
- [x] 9. 150-s32x-tests, platform half (patch 0096)
- [x] 10. 151-s32x-carts (patch 0097 and tools/fetch-labels.py)
- [ ] 11. 152-s32x-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [x] Steps 4 to 10 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the picodrive dylib.
- [x] A Mega Drive game after a 32X game equals a Mega Drive only run (`s32x_then_md.rs`); harness compare 0 diffs.
- [x] README, docs/PLAN.md and LICENSING.md describe 32X, with the non-commercial notice naming PicoDrive.
- [ ] Device gate (issue 152).

## Device check (RG34XXSP)
Issue 152.

## References
- ADR 0096; docs/cart-art/S32X.md
