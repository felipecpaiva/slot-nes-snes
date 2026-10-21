---
title: "Test Sega CD with synthetic discs, a dummy BIOS and the real BIOS when given"
phase: 21
area: tests
type: test
size: S
depends_on: [216-segacd-tracking]
---

## Why
Step 2, and the contract later steps build on. A synthetic disc cannot boot a program: the BIOS runs a disc only with Sega's security block at 0x200, which is not in this repo and not recoverable from the BIOS. But the core checks nothing in the BIOS file, so a dummy boot ROM lets almost every fact run on CI (ADR 0104).

## Scope
- [x] `crates/slot/tests/segacd_core.rs` (patch 0135), on slot's Mega Drive open path (`open_core_for_palette`, `Platform::Md`):
  - no BIOS refused; region byte picks U, E or J; PAL at 49.70 fps;
  - cue/bin, iso and chd (when `chdman` is on PATH) at 59.92 fps on the 360x240 canvas, no `SAVE_RAM`;
  - default `scd_U.brm`, per-game `<stem>.brm`, written only at unload, read back at load, not rewritten unchanged, not in the state;
  - flush by reload writes the file and restores the state, timed;
  - `.m3u` lines relative to the playlist; the per-game name follows the m3u stem;
  - with `SLOT_SEGACD_BIOS` (US, crc32 9f6f6276): the real BIOS alone and with a synthetic disc draws its menu inside the 320-wide picture;
  - with `SLOT_SEGACD_DISC`: the reload timed on an owned disc.
- [x] Platform half: `slot-store/tests/segacd_platform.rs`, `segacd_screen.rs`, `segacd_bios.rs`, `segacd_discs.rs`, `segacd_saves.rs`, `segacd_then_gba.rs`, `slot-ui/tests/segacd_case.rs`, `tools/tests/test_fetch_labels_segacd.py`; shared helpers in `crates/slot/tests/segacd_common/mod.rs`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `segacd_core.rs` | 11 tests; 9 run everywhere, 2 print a BIOS or disc skip without their variable |

## Edge cases
| Case | Expected handling |
|---|---|
| No `chdman` | The CHD discs print a skip; the flush test falls back to a cue disc |
| `SLOT_SEGACD_BIOS` set to the wrong file | A BIOS skip naming size and crc32 |

## Acceptance
- [x] `task check` green on the groundwork branch.

## Device check (RG34XXSP)
None for the core half.

## References
- ADR 0104; Lynx issue 110 (the env-gated BIOS precedent); docs/research/segacd-plan.md section 1
