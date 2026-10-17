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
- [x] `crates/slot/tests/ps1_common/mod.rs`: a PS-X EXE builder and an ISO9660 builder (PVD, root, `SYSTEM.CNF`, `PSX.EXE`) as `.bin` plus `.cue`, two discs and an `.m3u`, all in code. Ported from bently0602's `pcsx.rs` with credit. Done in patch 0034 (credited in its commit and in LICENSING.md).
- [ ] Tray's test card ideas (checkerboard, border, moving box) as assertions. Not done: the generated EXE fills the screen with one GPU fill command, and the tests pin every pixel of it (`red() == 640 * 480` plus both corners in `ps1_emu.rs`, red column counts per 256, 320 and 512 mode in `ps1_canvas.rs`). A checkerboard or a moving box needs more GPU commands in the EXE and would catch nothing the full-canvas count misses today (crop, offset, wrong width or a stale frame all change the count). Left for the maintainer to decide.
- [x] `require_core("pcsx_rearmed")` first in every test that opens a core (through `ps1_common::pcsx_rearmed()`), so a missing core fails under `SLOT_REQUIRE_CORES=1`. Audited all ten `ps1_*.rs` files; the tests without it open no core (pure policy, toast, serial and shelf tests), and must not skip when the dylib is missing.
- [x] `pcsx_rearmed_bios=HLE` forced. Every test that opens pcsx directly sets it (`ps1_analog.rs` was the one that did not, fixed in patch 0041). Two kinds rely on `auto` instead, on purpose: `with_no_bios_on_the_card_auto_falls_back_to_hle_and_the_disc_boots` (it proves the fallback), and the tests that seat a disc through a real `Session` (`ps1_seat`, `ps1_input`, `ps1_options`, `ps1_discs`, `ps1_card`, `ps1_then_gba`), where slot itself answers the option. Their root is a fresh temp dir with an empty `BIOS/`, so `auto` is HLE, as the fallback test proves. One behaviour per test.
- [ ] Harness leg: a PS1 game, eject, GBA, equal to the GBA-only run. Not added, as for Sega (issue 50). Covered by `ps1_then_gba.rs` instead. A leg needs the PS-X EXE and ISO9660 builders ported to Python in `harness/make_assets.py` (they exist only in Rust test code), a new `frame_dump` script and its own retry bound in `scripts/harness.sh`. The host pcsx is the interpreter build (osx sets DYNAREC 0) and its first frames after load are slow, so an H3-style bound would trip on a busy machine and fail `task check` for reasons unrelated to the patch. H3 already holds the shared eject-then-GBA path against H1 pixel for pixel; what PS1 adds (640x480 canvas, triggers to the game, Select+X picture chord, pass-through) is asserted by `ps1_then_gba.rs` against a GBA-only run.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `ps1_emu.rs` `a_generated_disc_boots_on_pcsx_with_hle_and_draws_on_the_640_by_480_canvas` | the EXE paints the expected colour in a 640x480 frame (already in patch 0034, so no `ps1_boot.rs`) |
| (new) | `ps1_card.rs` `the_128_kb_memory_card_comes_back_byte_for_byte_after_a_restart` | the 128 KB card persists across a restart: a patterned card reaches the core, comes back out on eject, and is in the core again on the next boot |
| (new) | `ps1_then_gba.rs` `a_gba_game_after_a_ps1_game_gets_the_same_input_as_a_gba_only_run` | GBA input comes back after a PS1 game (pass-through, A, B, L1, R1, L2, R2, Select+X, no `video_mode.txt`) |
| (new) | `ps1_then_gba.rs` `a_gba_game_after_a_ps1_game_gets_the_same_picture_as_a_gba_only_run` | GBA picture comes back after a PS1 game (source rect, frame width, 240x160 frame) |

Each new test was seen to fail with the code broken: skipping `load_save_ram` in `emu.rs` fails `ps1_card`; setting `set_triggers_to_game` only when a platform hands over the triggers (so it sticks after PS1) fails the input test (L2 and R2 reach mGBA), and the same for `set_video_mode_chord` (X never reaches mGBA); a canvas width that keeps the largest one seen fails the picture test (640 wide frame instead of 240x160).

## Edge cases
| Case | Expected handling |
|---|---|
| Host core built without the dynarec | Tests still pass on the interpreter. Proven by the host build itself: `core:pcsx_rearmed:host` builds with `platform=osx`, which sets DYNAREC 0, and every PS1 test runs on it |

## Acceptance
- [ ] Green on macOS CI with the host dylib. Not run from here (no push); `task check` is green locally on the M5 Max with the same host dylib, see the PR body.

## Device check (RG34XXSP)
A real-play gate, run by the maintainer (the tests above cover no frame pacing or audio on the H700).
Deploy first (`task deploy:device`), then play each title 3 minutes with the scripted input of
`scripts/auto-play.sh` (START x3, right held, A every 700 ms, B every 2.3 s, then eject):

    task perf:play PLATFORM=ps1 MINUTES=3 RUNS=1
    CORE=pcsx_rearmed PLATFORM=ps1 STEM='Spyro the Dragon (USA)' PAIR=ps1-pcsx_rearmed-light MINUTES=3 RUNS=1 sh scripts/auto-play.sh

The first runs the default pair `ps1-pcsx_rearmed-heavy` (`CTR - Crash Team Racing (USA)`), the second Spyro
(called directly because `task perf:play` does not pass `PAIR` through). Both write to the same day's folder.
Both names must match the files in `/mnt/sdcard/Games/PS1` without the extension (`.chd`, `.cue`, `.pbp` or
`.m3u`); a wrong name prints "skipped" and plays nothing. Logs land in `docs/perf/<date>/play/`, the table in
`play-eval.md`. Pass per title:
- Frame pacing: after the first 600-present window, 0 presents above 1.5x the period (`ft_max` under about
  25.2 ms) and `ft_p99_worst` at most 1.1x `ft_p50_med`.
- Audio: `starved` 0 and `dropped` 0 on the session summary line.
- No panic or crash: `crash` 0 in `play-eval.md`, and `grep -c panicked docs/perf/<date>/play/ps1-*.log`
  prints 0 (`parse_log` does not count Rust panics).
- Every session ended cleanly (the "Sessions that ended cleanly" table shows 1 of 1).

Record the rows in `docs/DEVICE-GATE.md` (PlayStation section). These are 3-minute runs, not the
10-minute success criterion 4.

## References
- ADR 0063; the 2026-10-16 code review (bently `pcsx.rs` passes against our host build)
