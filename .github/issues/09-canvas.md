---
title: "Patch 0004: Add a fixed 360x240 canvas per core via HostExtra and Compositor::set_game_canvas"
phase: 1
area: video
type: feature
size: L
depends_on: [08-core-fceumm]
---

## Why
Upstream crops every frame to 240x160 (`slot: crates/slot-retro/src/libretro.rs:321-330`) and the pipeline is fixed at `SRC_W/SRC_H`. Option A gives NES/SNES cores a 360x240 canvas (2x into the same 720x480 logical space) while GBA stays 240x160 at SCALE 3 (docs/PLAN.md Approach "Video: Option A", Build steps 11, 12, 21). Decisions: fixed per-platform 2x canvas; GBA SP bezel kept; Host field list untouched (docs/DECISIONS.md).

## Scope
`patches/0004-canvas.patch`:
- [x] New file `crates/slot-retro/src/canvas.rs`: centring copy, RGB565 conversion, hi-res 2:1 blend (activated in 14-libretro-env-and-hires), `HostExtra { canvas, av_change, av_enable }`, `ExtraGuard`. Deviations: `HostExtra` holds only `canvas`, because nothing in this patch reads the other two, so issue 14 adds `av_change` and `av_enable` (its Scope says so). The hi-res blend is written in issue 14, which already lists it. NES has its own copy of the RGB565 conversion in `canvas.rs` (`bgrx_from_rgb565`), guarded by T8 against the upstream formula for all 65,536 inputs, so `video_refresh`'s GBA branch is untouched.
- [x] `slot: crates/slot-retro/src/libretro.rs`: `HostExtra` owned by `LibretroCore`; thread-local `EXTRA` pointer set by `ExtraGuard` next to each `Active::bind` call site. `Host` fields (`:25-41`) and `Active::bind` unchanged. `Host.video` sized `canvas.w * canvas.h * 4` at open; when `EXTRA` is unbound `video_refresh` uses 240x160 exactly like upstream. New `LibretroCore::set_canvas(w, h)`.
- [x] `slot: crates/slot-retro/src/core.rs`: `RetroCore::canvas()` default method returning `(GBA_W, GBA_H)`.
- [x] `Core::canvas()` in `core_policy.rs`: Mgba/Gpsp (240, 160), Fceumm (360, 240). Also `Core::canvas_f32()` there, so the `app.rs` `picture_rect` hunk is one line.
- [x] `slot: crates/slot/src/emu.rs:151` `Frames::new` sized from `core.canvas()`; `:884` uses new `thumb::png_sized(buf, w, h)` (`slot: crates/slot/src/thumb.rs`, `png` unchanged). Done with a split: `png_sized` is in new file `crates/slot/src/thumb_sized.rs` and `thumb.rs` gains one `pub use` line, so `thumb::png_sized` still resolves.
- [x] `slot: crates/slot-retro/src/mock.rs` `MockCore::sized`; the fallback in `slot: crates/slot/src/core.rs` uses `MockCore::sized(core.canvas())`.
- [x] `slot: crates/slot-gfx/src/pipeline.rs`: `GamePass::set_canvas` (re-allocates the texture, re-sets `u_src`, scale = `OUT_W / w`); upload guard (`:122`) becomes `len == w*h*4`; `whole_scale_source` uses the pass's canvas.
- [x] `slot: crates/slot-gfx/src/fbo.rs`: `Compositor::set_game_canvas(w, h)` (owns the private `GamePass`, `:96,128-129`), exported in `slot: crates/slot-gfx/src/lib.rs`. `Compositor` is already exported there, so `lib.rs` needed no change.
- [x] `slot: crates/slot/src/frontend.rs`: call `set_game_canvas` on every core open, GBA included (GBA always (240, 160)). Deviation: it is called every frame from `Frontend::compose` and `GamePass::set_canvas` returns at once when the size is unchanged, so one call site covers every way a core appears. GBA gets (240, 160).
- [x] `slot: crates/slot/src/video_mode.rs:45-54` `source_rect` and `slot: crates/slot/src/app.rs:930` `picture_rect` take the canvas. `source_rect(platform, canvas, mode)` gains a middle parameter, its one caller is `App::source_rect`. `app.rs` totals 18 changed lines across patches 0001 to 0004 (10 added, 8 removed, budget 25); the `picture_rect` hunk is one line.
- [x] New test helpers in new file `crates/slot/tests/nes_common/mod.rs`: `require_core(name)` (skips locally, panics under `SLOT_REQUIRE_CORES=1`) and `nes_rom(battery)` (the signature is `nes_rom(name, battery)`, the name is the output file) (NROM, iNES byte 6 bit 1 for battery, fixed backdrop palette index).
- [x] Harness leg H3 in `harness/frame_dump.rs`: insert NES, eject, then H1 (patched tree only).

## Tests
| ID | File | Asserts |
|---|---|---|
| T8 | `crates/slot-retro/src/canvas.rs` `#[cfg(test)]` (new file) | 256x240 white into 360x240: lit at (52, 0) and (307, 239); dark at (51, 0) and (308, 0). Same module: RGB565 conversion equals the upstream formula for all 65,536 inputs |
| T9 | `slot/tests/nes_emu.rs` | `SLOT_REQUIRE_CORES=1`. fceumm boots `nes_rom`, 60 frames: buffer 360x240x4; picture area uniform and equal to the recorded fceumm RGB; not the mock gradient |
| T10 | `slot-gfx/tests/nes_pipeline.rs` | HeadlessSurface (macOS): `Compositor::set_game_canvas(360, 240)`, upload, draw: output (2x, 2y) equals source (x, y) at fbo scale 1; a 240x160 buffer after the switch is rejected |
| T11 | `slot/tests/nes_thumb.rs` | `png_sized` of 360x240 decodes to 360x240 with matching pixels |
| T14 | `slot/tests/nes_mock.rs` | NES cart with fceumm missing, run without `SLOT_REQUIRE_CORES`: `MockCore::sized` 360x240; no panic; upload accepted |
| T45 | harness leg H3 | NES, eject, GBA in the patched tree: hashes equal to H1 |
| added | `slot/tests/nes_window.rs` | macOS HeadlessSurface, real fceumm on `nes_rom`: a 640x480 window with a bezel lights a 456x427 box (+-1) from row 0; 720x480 lights 512x480 (+-1) centred |

Upstream tests stay unmodified, in particular the in-source `host_with()` at `slot: crates/slot-retro/src/libretro.rs:701-718`, which builds `Host` with every field listed, and `slot-gfx/tests/pipeline.rs`.

## Edge cases
| Case | Expected handling |
|---|---|
| Real-core tests skip silently because the dylib is missing | `require_core(name)` panics under `SLOT_REQUIRE_CORES=1` (set in CI and `task check`) |
| NES dylib missing on device: MockCore (240x160 buffer) uploaded into a 360x240 game texture | `MockCore::sized(core.canvas())` in the fallback; the upload guard requires `len == w*h*4`, so a mismatch is skipped rather than drawn wrong |
| After NES, GBA plays with a stale 360x240 texture | `set_game_canvas` runs on every open, GBA included; H3 (NES, eject, GBA) must equal the GBA-only H1 |

## Acceptance
- [x] T8 to T11, T14, T45 green; T9 under `SLOT_REQUIRE_CORES=1`. `task check` exit 0 (267 s, 1438 passed, 0 failed, 2 ignored). T8: 6 `canvas::tests`, including the 65,536-input RGB565 test. T9: `nes_emu` 2 passed. T10: `nes_pipeline` 4 passed. T11: `nes_thumb` 3 passed. T14: `nes_mock` 3 passed. T45: `compare: 0 diffs`, with `H3 against H1` reporting none.
- [x] GBA harness compare 0 diffs (H1, H2); H3 equals H1. `compare: 0 diffs (H1, H1G, H2, B1, H3 patched only, held against H1)`, `retries: upstream 3, patched 0, H3 (patched only, at most 1 per run) 0`. H3 has its own bound: one H3 run may retry once, a second retry fails, printed apart from the upstream-against-patched rule. In 10 `harness:control` runs H3 retried 6 times, all `the emulator was not locked 23 ms after the update at frame 338` (the first emulator step after the NES core loads); H1 retried 0 times.
- [x] `task bench:compare` within 2% (the RGB565 path is shared with gpSP). Min of 3, patched against upstream: mgba 240pee_mb.gba 98.6%, mgba gb240p.gb 101.0%, mgba cgb-acid2.gbc 97.8%, gpsp 240pee_mb.gba 98.4%.
- [x] Failure injection: delete `vendor/fceumm_libretro.dylib` and run `task test`; T9 fails with "fceumm core required (SLOT_REQUIRE_CORES=1)". `task test` stops earlier, in `scripts/run-tests.sh`, with `build/slot/vendor/fceumm_libretro.dylib is missing, run task core:host` (exit 201). Running T9 directly with `SLOT_REQUIRE_CORES=1 cargo test -p slot --test nes_emu` fails both tests with `fceumm core required (SLOT_REQUIRE_CORES=1), .../vendor/fceumm_libretro.dylib is missing`.
- [x] Failure injection: add a field to `Host` in `work/slot` and run `task check`; it fails to compile in `host_with()`. Done in `build/slot` (`cargo test -p slot-retro --no-run`): `error[E0063]: missing field `injected` in initializer of `libretro::Host`` at `libretro.rs:742`, the in-source `host_with()`, and at `:494`.
- [ ] Host smoke (needs a person at the screen, explained): `task run:4x3` shows a NES picture inside the bezel window. Needs a person at the screen; the new test `crates/slot/tests/nes_window.rs` renders it headless with real fceumm: in a 640x480 window with a bezel the lit picture is 456x427 from row 0 (box x 92 to 547, y 0 to 426), in 720x480 it is 511x480 centred (x 105 to 615). With the canvas set to 384x240 both fail (widths 426 and 478).

## Device check (RG34XXSP)
None separate. On the RG34XXSP (720x480) NES shows full height at 2x, 512x480, centred with no bezel; this is part of the phase device check in 01-phase-1-nes-boots. On 4:3 devices (RG35XXSP) it shows in the 640x427 window above the bezel, covered by harness leg B1 and nes_window.rs.

## Review notes
- Gotcha 4 (`Host` cannot grow): any new field breaks `host_with()`. New state goes only in `HostExtra`; `Active::bind`'s signature is unchanged.
- Gotcha 6 (the RG35XXSP window is 640x427): NES shows about 455x427 and SNES about 455x398, non-integer like GBA (decided). Do not "fix" this to 512x480.
- With `EXTRA` unbound, `video_refresh` and `environment` must behave exactly like upstream; review that branch line by line.
- Thumbnails: no crop, full 360x240 canvas (same 3:2 as 240x160, polaroid layout unchanged).
- `slot: crates/slot/src/app.rs:930` hunk should be one token.

## References
- docs/PLAN.md: Approach (Video: Option A), Phase 1 deliverables (0004, harness H3), Build steps 11, 12, 21, Signature impact table, Edge cases by layer (Runtime, Tests), Verification (failure injection), Test plan (Unit tests)
- `slot: crates/slot-retro/src/libretro.rs:15,25-41,321-330,701-718`; `slot: crates/slot-gfx/src/pipeline.rs:7-9,122`; `slot: crates/slot-gfx/src/fbo.rs:96,128-129`; `slot: crates/slot/src/emu.rs:151,884`; `slot: crates/slot-retro/src/mock.rs:33-47`; `slot: crates/slot/src/video_mode.rs:45-54`; `slot: crates/slot/src/app.rs:930`
