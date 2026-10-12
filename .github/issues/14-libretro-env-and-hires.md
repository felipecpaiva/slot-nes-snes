---
title: "Patch 0006: Answer SET_GEOMETRY, SET_SYSTEM_AV_INFO and GET_AUDIO_VIDEO_ENABLE, and enable the hi-res blend"
phase: 2
area: cores
type: feature
size: M
depends_on: [12-platform-snes, 13-snes9x-core-build]
---

## Why
fceumm and snes9x call env commands upstream answers with false (`slot: crates/slot-retro/src/libretro.rs:213`), so av changes are lost and FF cannot skip rendering. SNES hi-res frames (512 wide, 448 tall) must blend into the 360x240 canvas (docs/PLAN.md Phase 2 deliverables, Build steps 12, 14).

## Scope
`patches/0006-libretro-env.patch`:
- [ ] Add the fields `av_change` and `av_enable` to `HostExtra` in `slot: crates/slot-retro/src/canvas.rs` (patch 0004 ships it with `canvas` only). Env arms in `slot: crates/slot-retro/src/libretro.rs` that read `EXTRA`: `SET_GEOMETRY` returns true; `SET_SYSTEM_AV_INFO` stores the av info in `HostExtra.av_change`; `GET_AUDIO_VIDEO_ENABLE` returns 3, with the video bit clear on FF-skipped frames. All three return false when `HostExtra` is unbound.
- [ ] `RetroCore::take_av_change(&mut self) -> Option<AvInfo>` default method (returns None) in `slot: crates/slot-retro/src/core.rs`.
- [ ] `slot: crates/slot/src/emu.rs`: after `run_frame`, call `take_av_change()` and rebuild `Resampler::new` at the new rate.
- [ ] Hi-res blend in `canvas.rs` active: average 2:1 horizontally when `width > 360`, vertically when `height > 240`.
- [ ] New file `crates/slot-retro/src/env_tests.rs`, wired by one `#[cfg(test)] mod env_tests;` line.

## Tests
| ID | File | Asserts |
|---|---|---|
| T18 | `slot-retro/src/env_tests.rs` | `SET_GEOMETRY` true; `SET_SYSTEM_AV_INFO` 50.0 fps / 32040 Hz: `take_av_change()` returns it once; unbound returns false |
| T19 | `slot-retro/src/env_tests.rs` | `GET_AUDIO_VIDEO_ENABLE` returns 3 normally; video bit clear on an FF-skipped frame |
| T20 | `slot-retro/src/canvas.rs` tests | 512x224 alternating columns gives 256 wide mid-grey; 512x448 checkerboard halves 448 to 224 |
| T21 | `slot/tests/snes_emu.rs` | `SLOT_REQUIRE_CORES=1`. snes9x boots `snes_rom(Lo)`: uniform recorded RGB, not mock; `av_info().sample_rate` about 32040 |

Upstream tests stay unmodified, in particular the in-source libretro tests and `host_with()` at `slot: crates/slot-retro/src/libretro.rs:701-718`; with `HostExtra` unbound every env call behaves as upstream.

## Edge cases
| Case | Expected handling |
|---|---|
| fceumm region option or snes9x changes av mid-game; the resampler stays at the old rate and audio drifts | `HostExtra.av_change`; the emu loop calls `take_av_change()` after `run_frame` and rebuilds `Resampler::new` |

## Acceptance
- [ ] T18 to T21 green; T21 under `SLOT_REQUIRE_CORES=1`.
- [ ] GBA harness compare 0 diffs (H1, H2); H3 equals H1.
- [ ] Only one line added to `libretro.rs` for the test module.

## Device check (RG34XXSP)
None on its own. The phase device check is in 11-phase-2-snes.

## Review notes
- The `#[cfg(test)] mod env_tests;` line is the one permitted addition to an upstream src file's test surface; `scripts/check-upstream-tests.sh` must allow it by name (see 03-task-check-and-upstream-guard).
- The unbound path must return false exactly like upstream's `_ => false`; check that mgba and gpSP never see a different answer.
- Option B (true variable frames, full hi-res detail) is deferred (36-deferred-option-b-video).

## References
- docs/PLAN.md: Phase 2 deliverables (0006, hi-res), Build steps 12, 14, Signature impact table (`RetroCore`), Edge cases by layer (Runtime), Test plan (Unit tests)
- `slot: crates/slot-retro/src/libretro.rs:213,701-718`
