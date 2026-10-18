---
title: "Pace PAL titles at 50 Hz on NES, Master System, Mega Drive and PS1"
phase: 8
area: video
type: feature
size: M
depends_on: [56-ps1-tracking]
---

## Why
PAL titles run about 20% fast because slot paces at 60 fps. omega-zero paces each core at its own fps (`Pace`, `emu.rs:44-110`, commit 726cc34). The maintainer wants it after PS1 step 2. It replaces the deferred issue 34 and amends the PAL non-goal in docs/QUALITY-BAR.md and docs/PLAN.md.

## Scope
- [x] An ADR first: it amends the PAL non-goal and replaces our `av_rate` stretch (patch 0006). ADR 0071; the stretch stays only as the PAL Speed "Panel" choice.
- [x] Pace from the core's reported fps (`SET_SYSTEM_AV_INFO`, already in `HostExtra`) for NES, SMS, MD and PS1. GBA, GB and GBC pacing unchanged. Patch 0043; SNES too (same gate, ADR 0071).
- [x] Credit oauramos (omega-zero) in the patch and LICENSING.md, with cloudwithax/unslot and nelynes/slotPlus.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/pal_pacing.rs` | a 50 fps core runs 50 frames in 60 display ticks; a 60 fps core and Panel rate run a frame every tick; a 75 fps core runs 75 in 60 and keeps all its sound; a core that turns PAL mid-game follows; fceumm "(Europe)" and Genesis Plus GX region `E` run 50 in 60; fceumm PAL sound is one second per second of game; a Session seating a "(Europe)" NES cart runs 50 in 60, and 60 with `nes = panel` |
| (new) | `slot/tests/pal_pacing_clock.rs` | undriven, a 50 fps core runs 50 frames a second of wall clock (CI timing list) |
| (new) | `slot/tests/pal_speed.rs` | PAL Speed rows default to Native; none on Game Gear or the Game Boys; flipping MD writes `md = panel` and only MD changes; an unknown line reads as Native |
| (new) | `slot/src/av_rate.rs` (in-source) | the period gate (PAL native, Panel, NTSC and Game Boy rates), owed frames at 50 and 75 fps, a native PAL core resampled from its own rate |

## Edge cases
| Case | Expected handling |
|---|---|
| Core changes fps mid-game | Pacing follows the new rate (`a_core_that_turns_pal_mid_game_is_paced_at_50_fps_from_then_on`) |

## Acceptance
- [x] ADR recorded; GBA harness compare at 0 diffs; README and QUALITY-BAR known gaps updated.

## Device check (RG34XXSP)
A PAL NES and a PAL PS1 game at 50 fps with zero underruns. Steps and the result table: docs/DEVICE-GATE.md, "PAL pacing".

- [x] Passed 2026-10-18 (2 minutes each, auto-play): NES Asterix (Europe) 50.007 fps, MD Another World (Europe) 49.701, SMS Addams Family (Europe) 49.701, PS1 Rapid Reload (Europe) 50.000; starved and dropped 0, present p50 16.78 ms, no panics, clean ejects. SNES had no European cart on the card, so SNES is host-tested only.

## References
- issue 34 (superseded by this one); docs/QUALITY-BAR.md Known gaps
