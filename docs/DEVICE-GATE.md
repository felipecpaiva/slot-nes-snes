# Device gate (RG34XXSP)

Success criterion 4 in `docs/PLAN.md`: every gate title runs at full speed with no audio
underruns for 10 minutes on the reference device, an Anbernic RG34XXSP (H700, 720x480, BaseOS).
This is a manual gate run by the maintainer. This file is the only place device results live.

## Rules

- ROMs are the maintainer's own dumps. They are never committed, never pushed to a branch and
  never attached to an issue. `task bench:device` pushes one to a temp dir on the SD card and
  removes it afterwards.
- Thresholds, per title: 0 audio underruns in 10 minutes of play, and p99 frame time under
  16.7 ms. Until slot has a frame-time trace (#45) the p99 column is n/a and only the
  starved count decides pass or fail.
- Do not change the CPU governor (or add a governor line to `launch_frontend.sh`) without a
  before and after row in the table below. Measure on the default governor first. If an SA-1
  title (Super Mario RPG, Seiken Densetsu 3) underruns, add a second row for the same title
  with the `interactive` governor and the same zip version, and change nothing else.
- One row per title per zip version. A re-run adds a row, it does not overwrite one.

## What the log can and cannot tell you

Read from `work/slot` (crates `slot/src/emu.rs`, `latency.rs`) and `card/System/launch_frontend.sh`:

- Slot's stderr goes to `/mnt/sdcard/slot.log`. The previous run is moved to `slot.log.1` at
  launch, so read the log before you start the next game.
- The log never contains the word "underrun". The counter is called starved and counts samples,
  not events.
  - End of session, when dropped or starved is above 0 or `SLOT_TRACE` is set:
    `slot: audio: N samples dropped, M starved`.
  - With `SLOT_TRACE` set, every 300 paced frames:
    `slot: audio: Q/T queued, D dropped, S starved, locked ...`.
  - With `SLOT_TRACE` off, a clean session prints no summary line, so no line means 0 starved
    and 0 dropped only if the game was left through the menu. With `SLOT_TRACE` on the line always
    prints, so a missing line means the session did not end cleanly. A crash or a power-off prints
    no summary. Crash lines (`slot: crash:`) go to `slot.log`, and crash dumps are written to the
    card's `crash/` directory by `coresave.sh`. `slot-session.log` only holds the launcher's exec
    lines.
  - `grep -c underrun slot.log` is always 0 and proves nothing. Use `task readout:device`.
- `SLOT_TRACE` is not set by `launch_frontend.sh`. To get the periodic lines, add
  `export SLOT_TRACE=1` under the `export SLOT_ROOT` line on the device for the run, and remove it
  afterwards.
- Latency lines (`slot: latency: ... total X ms`) appear when `System/trace-latency.on` exists
  on the SD card (or `SLOT_TRACE_LATENCY` is set). They time one input from read to screen swap.
  That is input latency, not frame time. Do not enter it as p99 frame ms.
- Nothing in slot logs a per-frame wall time, so p99 frame time cannot be read from the device
  today. The nearest figure is `task bench:device`, which reports the core's mean ms/frame per
  repeat (median, min, max over repeats). It times the core and slot's copy and audio callbacks, not
  the GL upload. Record the bench median and max in the Notes column and leave p99 as `n/a` until
  a frame-time trace exists.
- p99 frame time cannot be measured yet because slot has no frame-time trace. Adding one belongs
  to issue #45 (performance evaluation across platforms). The gate's p99 column stays `n/a` until
  then.

## Known now

On 2026-10-12, `slot.log` from real play sessions on the RG34XXSP showed starved samples at
session level (2708, 4356, 3072, and 12288 with 6656 dropped) on GBA, NES and SNES alike. The
start-up starve also seen on GBA is tracked in #45. No title has passed the 0-underrun gate yet.

## Checklist per title

1. Deploy the zip under test: `task deploy:device`. Note the zip version (`slot-nes-snes-<tag>-<ns.N>`).
2. `adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` and note it.
3. Optional: `adb shell touch /mnt/sdcard/System/trace-latency.on` for latency lines, and the
   `SLOT_TRACE` edit above for periodic audio lines.
4. Play the title for 10 minutes, with scenes that stress it (see the table notes), then quit to
   the shelf. Do not power off.
5. `task readout:device`. Read the audio summary line (starved must be 0, or the line absent with `SLOT_TRACE` off) and the trace
   maximum.
6. Fill one row below. Fail the title if starved is above 0 (p99 is n/a until #45 adds a frame-time trace).
7. Bench: `task bench:device CORE=<core> ROM=<path to your dump>`. Record ms/frame and fps.

## Results

fps is the core_bench frames per second at idle on the device, a ceiling, not the played rate.
Underruns/10 min is the starved sample count from `slot.log`. Date is YYYY-MM-DD.

| Title | Platform | Mapper/chip | Core | fps | Underruns/10 min | CPU governor | p99 frame ms | Date | Zip version |
|---|---|---|---|---|---|---|---|---|---|
| Star Fox | SNES | Super FX (GSU) | snes9x | | | | | | |
| Yoshi's Island | SNES | Super FX 2 (GSU-2) | snes9x | | | | | | |
| Kirby Super Star | SNES | no coprocessor | snes9x | | | | | | |
| Super Mario RPG | SNES | SA-1 | snes9x | | | | | | |
| Seiken Densetsu 3 | SNES | SA-1 | snes9x | | | | | | |
| Super Mario Bros. 3 | NES | MMC3 | fceumm | | | | | | |
| Kirby's Adventure | NES | MMC3 (heavy scenes) | fceumm | | | | | | |
| Castlevania III | NES | MMC5 | fceumm | | | | | | |
| Akumajou Densetsu | NES | VRC6 (expansion audio) | fceumm | | | | | | |
| Mega Man 2 | NES | MMC1 | fceumm | | | | | | |
| Battletoads | NES | AxROM (timing sensitive) | fceumm | | | | | | |
| GBA reference (any title, same session) | GBA | n/a | mgba | | | | | | |

No device results recorded yet. The GBA row is the comparison point: measure it in the same
session as the others, on the same governor.

## Core bench on the device (test carts)

`task bench:device CORE=<core> ROM=<path>`. Emulation only, no video or audio, so it shows headroom, not the gate. Generated test carts (`harness/make_assets.py nes|snes`) are tiny, so real games cost more. Use your own dumps of the 11 titles for real numbers.

| Date | Zip version | Governor | Core | ROM | Median ms/frame | Frames/s |
|---|---|---|---|---|---|---|
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | mgba | 240pee_mb.gba | 0.795 | 1258 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | gpsp | 240pee_mb.gba | 0.924 | 1083 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | fceumm | generated NES cart | 1.624 | 616 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | snes9x | generated SNES cart | 3.295 | 304 |
