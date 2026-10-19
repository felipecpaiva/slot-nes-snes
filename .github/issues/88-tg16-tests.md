---
title: "Test TG16 with a generated HuCard"
phase: 10
area: tests
type: test
size: S
depends_on: [82-tg16-core-build]
---

## Why
Real-core tests from the start, the NES, SNES and NGP way: no game ROM in the repo, so the HuCard is generated. The core half lands with the groundwork; each platform step adds its own tests.

## Scope
- [x] Patch 0057 adds `crates/slot/tests/tg16_core.rs` (new file only, no upstream test edited). The HuCard is 8 KB: the reset vector at $1FFE points at $E000, the code maps the I/O page (`tam #$01`), writes red into VCE colours 0 and 0x100, and spins (`bra *`). Recipe after nelynes/slotPlus 92b7022 (`pce_core.rs`) and cloudwithax/unslot 00296a5 (`systems.rs`), credited in the patch.
- [x] Four tests on the host dylib:
  - boots with no BIOS, 59.80 to 59.85 fps, 44100 Hz, sound, frame width 256, and every pixel of the 360x240 canvas: red at x 52 to 307 and y 0 to 239, black elsewhere (scanline options answered);
  - unanswered scanline options: 243 lines halved to 121 rows (y 59 to 179), the contract issue 84 must meet;
  - a state round-trips byte for byte;
  - save RAM is the 2 KB BRAM with the `HUBM` header, and `load_save_ram` round-trips.
- [x] Platform half, per step: `tg16_platform.rs` (83), `core_option_keys.rs` rows (84), `tg16_canvas.rs` and `tg16_screen.rs` (85), `tg16_saves.rs` (86), `tg16_input.rs` (87), cart and label tests (89), and a `tg16_then_gba.rs` eject test (the PS1 precedent).

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `tg16_core.rs` | the four tests above, all green on 2026-10-18 |

## Edge cases
| Case | Expected handling |
|---|---|
| The dylib is missing | Skip locally; fail under `SLOT_REQUIRE_CORES=1` (`core_common::require_core`) |
| A pin bump changes the scanline fallback | The unanswered-options test fails and says why |

## Acceptance
- [x] `cargo test -p slot --test tg16_core` green with the pinned dylib.
- [ ] `task check` green with each platform step.

## Device check (RG34XXSP)
None.

## References
- ADR 0091; patch 0057; docs/research/tg16-plan.md section 2

## Outcome (2026-10-19)
Patches 0057 (core) and 0058 to 0063 (one test file per step). Patch `0063-tg16-tests` adds `slot/tests/tg16_then_gba.rs`: a GBA game after a TG16 game gets the same input and picture as a GBA-only run. Shared helper `slot/tests/tg16_common/mod.rs`.
