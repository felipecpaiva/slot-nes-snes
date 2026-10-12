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
- [ ] `docs/DEVICE-GATE.md`: checklist and a per-title results table (fps, underrun count, CPU governor, p99 frame time, date, zip version) for the 11 titles:
  - SNES: Star Fox, Yoshi's Island, Kirby Super Star, Super Mario RPG, Seiken Densetsu 3.
  - NES: Super Mario Bros. 3 (MMC3), Kirby's Adventure (MMC3, heavy scenes), Castlevania III (MMC5), Akumajou Densetsu (VRC6 expansion audio), Mega Man 2 (MMC1), Battletoads (AxROM, timing-sensitive).
- [ ] `task bench:device` (core_bench on device) and the read-out steps: `grep -c underrun slot.log`; frame pacing from `SLOT_TRACE_LATENCY` (`System/trace-latency.on`).
- [ ] Note that ROMs are the maintainer's own dumps and are never committed.

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
- [ ] `docs/DEVICE-GATE.md` exists with all 11 titles and the thresholds: 0 underruns per 10 minutes, p99 frame time under 16.7 ms.
- [ ] Any governor change is backed by a recorded before/after measurement.

## Device check (RG34XXSP)
None separate. The first SNES pass is step 4 of the device check in 11-phase-2-snes; the full 11-title passes are in 18-phase-3-parity and 28-phase-5-release.

## Review notes
- Do not change the governor without a measurement in the table.
- Use `DEVICE-GATE.md` as the only file name for device results.

## References
- docs/PLAN.md: Spec success 4, Working process, Edge cases by layer (Device), Outcome verification mechanisms
- docs/QUALITY-BAR.md: Device gate
