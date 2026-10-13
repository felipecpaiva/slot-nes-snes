---
title: "Create docs/DEVICE-GATE.md and the RG34XXSP measurement routine"
phase: 2
area: device
type: chore
size: S
depends_on: [10-dist-zip-deploy, 15-snes-input]
---

## Why
Success criterion 4 is a manual gate on the RG34XXSP: full speed and zero audio underruns over 10 minutes per title, read from `SLOT_TRACE`/`slot.log` (docs/PLAN.md Spec, Working process, Outcome verification mechanisms). Results need one place to live from the first SNES pass onward.

## Scope
- [x] `docs/DEVICE-GATE.md`: checklist and a per-title results table (fps, underrun count, CPU governor, p99 frame time, date, zip version) for the 11 titles:
  - SNES: Star Fox, Yoshi's Island, Kirby Super Star, Super Mario RPG, Seiken Densetsu 3.
  - NES: Super Mario Bros. 3 (MMC3), Kirby's Adventure (MMC3, heavy scenes), Castlevania III (MMC5), Akumajou Densetsu (VRC6 expansion audio), Mega Man 2 (MMC1), Battletoads (AxROM, timing-sensitive).
- [x] `task bench:device` (core_bench on device) and the read-out steps: `grep -c underrun slot.log`; frame pacing from `SLOT_TRACE_LATENCY` (`System/trace-latency.on`). Done as `task bench:device CORE= ROM=` (run on the RG34XXSP on 2026-10-12, all four cores, numbers in DEVICE-GATE.md) and `task readout:device` (pulls `slot.log`). The log never says "underrun": slot logs starved samples (`slot: audio: N samples dropped, M starved` at session end when dropped or starved is above 0 or `SLOT_TRACE` is set; per 300 frames with `SLOT_TRACE=1`). `SLOT_TRACE_LATENCY` is input to swap latency, not frame time, and slot has no frame-time trace, so p99 frame time cannot be measured yet. Adding a frame-time trace belongs to issue #45 (performance evaluation across platforms), and the p99 column stays n/a until then.
  Known now: on 2026-10-12 `slot.log` from real play sessions on the RG34XXSP showed starved samples at session level (2708, 4356, 3072, and 12288 with 6656 dropped) on GBA, NES and SNES alike. The start-up starve also seen on GBA is tracked in #45. No title has passed the 0-underrun gate yet.
- [x] Note that ROMs are the maintainer's own dumps and are never committed.

## Tests
| ID | File | Asserts |
|---|---|---|
| (none) | | Manual gate, no T-id |

No upstream test file is touched.

## Edge cases
| Case | Expected handling |
|---|---|
| SA-1 titles pop on the default governor | Measure first. If underruns appear, test the `interactive` governor (one muOS RG40XXH report) via a `launch_frontend.sh` line, gated on the measurement |

## Acceptance
- [x] `docs/DEVICE-GATE.md` exists with all 11 titles and the thresholds: 0 underruns per 10 minutes, p99 frame time under 16.7 ms.
- [x] Any governor change is backed by a recorded before/after measurement. No change made: the RG34XXSP already runs the `performance` governor (read by `task bench:device`).

## Device check (RG34XXSP)
None separate. The first SNES pass is step 4 of the device check in 11-phase-2-snes; the full 11-title passes are in 18-phase-3-parity and 28-phase-5-release.

## Review notes
- Do not change the governor without a measurement in the table.
- Use `DEVICE-GATE.md` as the only file name for device results.

## References
- docs/PLAN.md: Spec success 4, Working process, Edge cases by layer (Device), Outcome verification mechanisms
- docs/QUALITY-BAR.md: Device gate
