---
title: "Verify fast-forward and rewind on every new core, with per-core option keys"
phase: 3
area: cores
type: test
size: M
depends_on: [20-core-picker-pairs]
---

## Why
FF depends on each core declaring a `*_frameskip` option whose prefix is not always the dylib name, and rewind serializes every 2 frames through a blocking `sync_channel(4)` that snes9x may outrun (docs/PLAN.md Phase 3 deliverables (FF, rewind), docs/RESEARCH.md "Performance watch-points").

## Scope
- [x] T32 dump of `declared_options()` for all 6 cores; correct any `option_prefix()` value it disproves (frameskip and overscan keys). Disproved: `snes9x2005_plus` declares `snes9x_2005_frameskip`, so `Core::Snes9x2005Plus.option_prefix()` is now `snes9x_2005`.
- [x] FF: frameskip set via `option_prefix()`; video off on skipped frames through `GET_AUDIO_VIDEO_ENABLE` (from 14-libretro-env-and-hires). Only mgba, gpsp and snes9x2005_plus declare a frameskip key; fceumm, snes9x and nestopia declare none and rely on the video-off bit alone (see Findings).
- [x] Rewind: measure snes9x serialize time and size against the 2-frame cadence and the blocking `sync_channel(4)` (`slot: crates/slot/src/rewind.rs:98`). Add `Platform::rewind_every()` (default 2) only if a measurement exceeds budget. The channel stays as it is. Nothing exceeded budget, so `rewind_every()` is not added.
- [x] New test files committed on the `nes-snes` branch and exported with the concern they exercise. Committed as `ff-and-rewind` in `work/slot`; export with `scripts/export-patches.sh`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T28 | `slot/tests/snes_rewind.rs` | `SLOT_REQUIRE_CORES=1`. Rewind on snes9x for 300 frames: `rewind_fill` rises; L2 restores an earlier frame; serialize time logged under budget |
| T29 | `slot/tests/snes_ff.rs` | `SLOT_REQUIRE_CORES=1`. FF on snes9x and fceumm: frameskip key declared; observed speed at least `ff_speed` minus 1 |
| T32 | `slot/tests/core_option_keys.rs` | `SLOT_REQUIRE_CORES=1`. Dump `declared_options()` for all 6 cores: `option_prefix()` frameskip and overscan keys exist, or are documented absent |

Upstream tests stay unmodified, in particular `slot: crates/slot/tests/core_options.rs` and any rewind tests.

## Edge cases
| Case | Expected handling |
|---|---|
| (none specific) | Rewind overrun is handled by cadence, never by redesigning the channel |

## Acceptance
- [x] T28, T29, T32 green under `SLOT_REQUIRE_CORES=1`.
- [x] GBA harness compare 0 diffs (H1, H2); mgba/gpsp frameskip keys unchanged. `task check` 2026-10-13: compare 0 diffs (H1, H1G, H2, B1, H3); T32 shows `mgba_frameskip` and `gpsp_frameskip` unchanged.
- [x] Rewind measurement recorded in the PR description (numbers under Findings); `rewind_every()` added only if it exceeded budget (it did not).

## Device check (RG34XXSP)
None separate. Rewind and FF on Super Mario RPG are in the phase device check in 18-phase-3-parity.

## Review notes
- Gotcha 8 (rewind's blocking channel): `slot: crates/slot/src/rewind.rs:98` stalls the emu thread when the writer lags. Measure first and tune the cadence; don't redesign the channel.
- Gotcha 14 (frameskip key is not the dylib name): verify through T32. `core_bench --frameskip` knows only mgba/gpsp (`slot: crates/slot-retro/examples/core_bench.rs:104`).
- T32 confirms the fceumm overscan keys first chosen in 08-core-fceumm.

## References
- docs/PLAN.md: Phase 3 deliverables (FF, rewind), Consumer-grep evidence (frameskip key), AC-to-code coverage (Rewind, Fast-forward)
- `slot: crates/slot/src/rewind.rs:98`; `slot: crates/slot/src/core.rs:178`; `slot: crates/slot-retro/examples/core_bench.rs:104`

## Findings (T32 dump, 2026-10-13, macOS arm64, vendor cores)
T29 as first written asserted "frameskip key declared" for snes9x and fceumm. The dump disproves that, so T29 asserts the real behaviour instead (below).

| Core | Frameskip key | Overscan keys | `option_prefix()` |
|---|---|---|---|
| mgba | `mgba_frameskip` (disabled, auto, auto_threshold, fixed_interval) | none | `mgba` ok |
| gpsp | `gpsp_frameskip` (same values) | none | `gpsp` ok |
| fceumm | none | `fceumm_overscan_h_left`, `_h_right`, `_v_top`, `_v_bottom` (confirms 08-core-fceumm) | `fceumm` ok |
| snes9x | none | `snes9x_overscan` (enabled, 12_pixels, 16_pixels, auto, disabled) | `snes9x` ok |
| nestopia | none | `nestopia_overscan_h_left`, `_h_right`, `_v_top`, `_v_bottom` | `nestopia` ok |
| snes9x2005_plus | `snes9x_2005_frameskip` (disabled, auto, manual) | none | was `snes9x2005_plus`, disproved, now `snes9x_2005` |

- fceumm declares its options only after a cart is loaded (0 at open, 43 after). `apply_policy_options` runs before load, so its frameskip check sees no declarations for fceumm. Harmless today because fceumm has no frameskip key, but a future core that declares late and has one would be skipped. Not changed here. `fceumm_declares_its_options_only_once_a_cart_is_loaded` pins the fact.
- nestopia defaults `nestopia_overscan_v_top` and `_v_bottom` to 8, which crops 240 rows to 224. Policy only sets fceumm's overscan keys. Whether nestopia should be set to 0 is a decision for the maintainer, not made here.
- FF without a frameskip key: the emu loop runs `fast_steps` core frames per present and calls `set_frame_skip(true)` on all but the last, which clears the video bit of `GET_AUDIO_VIDEO_ENABLE`. Measured at x4 on all four cores: 4.0 to 4.2x the frames of normal speed, skipped frames only in Fast.
- Rewind measurements (300 frames, idle generated ROM, debug test profile; release in brackets). Budget from the code: `core.serialize()` runs inline on the emu thread, so p95 must stay under one present (16.67 ms, `PRESENT`); the writer thread gets one push per 2 presents (33.3 ms), so its per-push cost must stay under that or `sync_channel(4)` fills and blocks the emu thread.

| Core | State bytes | serialize median / p95 / max ms | writer push median / p95 ms | Ring after 300 states |
|---|---|---|---|---|
| snes9x | 823407 | 0.058 / 0.075 / 0.107 | 8.0 / 8.5 (0.055 / 0.061) | 4% |
| snes9x2005_plus | 564544 | 0.013 / 0.017 / 0.064 | 5.5 / 5.7 (0.035 / 0.039) | 3% |
| nestopia | 5420 | 0.003 / 0.005 / 0.013 | 0.056 / 0.064 | 0% |
| fceumm | 13758 | 0.002 / 0.004 / 0.050 | 0.135 / 0.148 | 0% |

  Worst case with incompressible random deltas on snes9x: writer p95 6.6 ms debug, 0.10 ms release. All under budget by more than 3x even in the debug profile, so no `Platform::rewind_every()`.
- On the device: `core_bench CORE ROM --serialize --frames 300` prints state size and run, save and load median, p95 and max in ms. It does not time the writer (XOR plus LZ4 in `Rewind::push`) and has no `SLOT_TRACE` line either. Scale the writer cost by the device to host ratio of the `run` median.

## Device measurement (RG34XXSP, 2026-10-13)
`task bench:device CORE=<core> ROM=<generated cart> "ARGS=--serialize --frames 300 --warmup 300"`, governor `performance`. ms per frame, median / p95.

| Core | State bytes | run | save (serialize) | load |
|---|---|---|---|---|
| snes9x | 823407 | 3.790 / 4.103 | 1.257 / 1.573 | 2.292 / 2.806 |
| snes9x2005_plus | 564544 | 2.364 / 2.471 | 0.540 / 0.768 | 0.426 / 0.519 |
| fceumm | 13758 | 1.616 / 1.715 | 0.015 / 0.019 | 0.059 / 0.062 |
| nestopia | 5420 | 1.080 / 1.119 | 0.058 / 0.063 | 0.034 / 0.036 |

snes9x run plus save stays under 6 ms of the 16.7 ms frame. The rewind writer (XOR plus LZ4) is not timed by core_bench; the host release figure (0.06 ms p95) scaled by the device to host `run` ratio stays far under the 33 ms push budget. Generated test carts are idle, real games cost more: re-measure on the 11 gate titles (docs/DEVICE-GATE.md).

Fix after review: core options policy now also sets the four `nestopia_overscan_*` keys to "0" like fceumm. Probing showed nestopia already emits 256x240 here (the host answers GET_VARIABLE false for unset keys), so this pins the behaviour rather than fixing a visible crop. The fceumm "declares no frameskip option" warning no longer fires before the core has declared its options.
