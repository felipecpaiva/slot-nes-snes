---
title: "Pace Lynx games at the rate their frames carry, with a Lynx Speed row (Native default)"
phase: 12
area: video
type: feature
size: M
depends_on: [106-lynx-canvas-screen, 66-pal-pacing]
---

## Why
Step 8. Beetle Lynx reports a constant 75 fps but each `retro_run` is one game frame of whatever length the game programmed: 59.9 Hz as the boot ROM leaves it (736 sample frames at 44.1 kHz), 75 Hz for a game that sets it (588). ADR 0071 paces from the reported fps, so it would run a 59.9 Hz game 25% fast, and its Panel choice would drop the pitch. The rule "options stay available, the player's choice becomes the default" gives a row (ADR 0093).

## Scope
- [x] Measure the content rate from the sound each frame carries: sample frames per run over the sample rate, smoothed (EMA over about 30 frames, clamped 50 to 80 fps), for cores flagged as reporting no real rate (Lynx only). nelynes 0848fcb and b264635 follow the same idea; credit them.
- [x] **Native** (default): feed that rate to ADR 0071's period and owed-frames path (1 or 2 frames a tick at 75 Hz on the 59.6 Hz panel, 0 or 1 below). The resampler is built on the measured rate, so one second of game feeds one second of sound.
- [x] **Panel**: one frame per vsync, sound resampled from what each frame carried; a 75 Hz game plays at 80%.
- [x] Stored as `lynx = panel` in `Config/pal_speed.txt` or its own file (decide with issue 106); missing line is Native.
- [x] `lynx_force_60hz` stays disabled (issue 105).
- If the maintainer picks Handy: it runs fixed cycles per run (`handy_refresh_rate`), so Native is "set 75 and pace at 75" and Panel "set 60", with no measuring.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `lynx_core.rs` rate tests | 736 per run at the boot ROM rate, 588 at 75 Hz, reported 75 both times |
| (new) | `lynx_pacing.rs` (MockCore) | a core reporting 75 but carrying 735 samples a frame runs 60 frames in 60 ticks; carrying 588 runs 75 in 60 and keeps all its sound; a game that switches rate mid-play follows within a second; Panel runs one frame a tick |
| (new) | `av_rate.rs` in-source | the smoothing and clamp |

## Edge cases
| Case | Expected handling |
|---|---|
| A frame with no sound (pause, load) | Keep the last rate |
| No display frame ends (missing BIOS, 43.75 ms cap) | Cannot happen: issue 104 refuses the launch |

## Acceptance
- [x] GBA harness compare 0 diffs; `pal_pacing.rs` unchanged.

## Status
Landed as patch 0075-lynx-pacing (2026-10-19). As built: windows of 20 frames, a rate taken once two windows agree within 0.5 fps (no EMA), clamp 50 to 80; stored as `lynx` in `Config/pal_speed.txt`. `EmuHandle::paced_fps` reports the period in use.

## Device check (RG34XXSP)
Zero underruns at Native on a 60 Hz and a 75 Hz game (issue 112 lists them once measured).

## References
- ADR 0071, 0093; issue 66; nelynes/slotPlus 0848fcb, b264635
