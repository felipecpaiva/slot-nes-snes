---
title: "Test PS1 with generated PS-X EXE and ISO discs on HLE BIOS"
phase: 8
area: tests
type: test
size: M
depends_on: [57-ps1-core-build]
---

## Why
Step 10. Every PS1 behaviour needs a real-core test with no copyrighted BIOS or game (ADR 0063).

## Scope
- [ ] `crates/slot/tests/ps1_common/mod.rs`: a PS-X EXE builder and an ISO9660 builder (PVD, root, `SYSTEM.CNF`, `PSX.EXE`) as `.bin` plus `.cue`, two discs and an `.m3u`, all in code. Ported from bently0602's `pcsx.rs` with credit; tray's test card ideas (checkerboard, border, moving box) as assertions.
- [ ] `require_core("pcsx_rearmed")` first in every test, so a missing core fails under `SLOT_REQUIRE_CORES=1`, never passes silently.
- [ ] `pcsx_rearmed_bios=HLE` forced. One behaviour per test.
- [ ] Harness leg: a PS1 game, eject, GBA, equal to the GBA-only run.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `ps1_boot.rs` | the EXE paints the expected colour in a 640x480 frame |
| (new) | `ps1_card.rs` | the 128 KB card persists across a restart |
| (new) | `ps1_then_gba.rs` | GBA input and picture come back after a PS1 game |

## Edge cases
| Case | Expected handling |
|---|---|
| Host core built without the dynarec | Tests still pass on the interpreter |

## Acceptance
- [ ] Green on macOS CI with the host dylib.

## Device check (RG34XXSP)
None.

## References
- ADR 0063; the 2026-10-16 code review (bently `pcsx.rs` passes against our host build)
