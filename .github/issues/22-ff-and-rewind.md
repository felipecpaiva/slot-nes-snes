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
- [ ] T32 dump of `declared_options()` for all 6 cores; correct any `option_prefix()` value it disproves (frameskip and overscan keys).
- [ ] FF: frameskip set via `option_prefix()`; video off on skipped frames through `GET_AUDIO_VIDEO_ENABLE` (from 14-libretro-env-and-hires).
- [ ] Rewind: measure snes9x serialize time and size against the 2-frame cadence and the blocking `sync_channel(4)` (`slot: crates/slot/src/rewind.rs:98`). Add `Platform::rewind_every()` (default 2) only if a measurement exceeds budget. The channel stays as it is.
- [ ] New test files committed on the `nes-snes` branch and exported with the concern they exercise.

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
- [ ] T28, T29, T32 green under `SLOT_REQUIRE_CORES=1`.
- [ ] GBA harness compare 0 diffs (H1, H2); mgba/gpsp frameskip keys unchanged.
- [ ] Rewind measurement recorded in the PR description; `rewind_every()` added only if it exceeded budget.

## Device check (RG35XXSP)
None separate. Rewind and FF on Super Mario RPG are in the phase device check in 18-phase-3-parity.

## Review notes
- Gotcha 8 (rewind's blocking channel): `slot: crates/slot/src/rewind.rs:98` stalls the emu thread when the writer lags. Measure first and tune the cadence; don't redesign the channel.
- Gotcha 14 (frameskip key is not the dylib name): verify through T32. `core_bench --frameskip` knows only mgba/gpsp (`slot: crates/slot-retro/examples/core_bench.rs:104`).
- T32 confirms the fceumm overscan keys first chosen in 08-core-fceumm.

## References
- docs/PLAN.md: Phase 3 deliverables (FF, rewind), Consumer-grep evidence (frameskip key), AC-to-code coverage (Rewind, Fast-forward)
- `slot: crates/slot/src/rewind.rs:98`; `slot: crates/slot/src/core.rs:178`; `slot: crates/slot-retro/examples/core_bench.rs:104`
