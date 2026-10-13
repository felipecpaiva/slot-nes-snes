# Device gate (RG34XXSP)

Success criterion 4 in `docs/PLAN.md`: every gate title runs at full speed with no audio
underruns for 10 minutes on the reference device, an Anbernic RG34XXSP (H700, 720x480, BaseOS).
This is a manual gate run by the maintainer. This file is the only place device results live.

## Rules

- ROMs are the maintainer's own dumps. They are never committed, never pushed to a branch and
  never attached to an issue. `task bench:device` pushes one to a temp dir on the SD card and
  removes it afterwards.
- Thresholds, per title: 0 audio underruns in 10 minutes of play, 0 dropped frames, and a steady
  present interval. Dropped frames means 0 presents above 1.5x the panel period in the run.
  Steady means p99 present interval is at most 1.1x the median present interval. Both come from
  the `slot: frametime:` and `slot: pace:` trace lines.
- Why not "p99 frame time under 16.7 ms": the RG34XXSP panel refreshes at about 59.6 Hz, a period of
  16.78 ms (the median present period in every `docs/perf/2026-10-13/play/` log). A present can
  never be shorter than the period, so the p50 is already above 16.7 ms and that gate cannot
  pass on healthy hardware. The two rules above compare against the real period instead.
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
- With the latency trace on, the `frame-trace` patch logs `slot: frametime: 600 presents, p50 X p99 Y max Z ms`
  (present to present, per 600 presents). Enter the worst p99 and the longest max of the run, and
  count presents above 1.5x the period from the `missed a latch` figures of the `pace:` lines.
  `scripts/auto-play.sh` reports them as `ft_p99_worst` and `ft_max`. The last window of a session
  is the eject and is dropped. `task bench:device` still gives the core's ms/frame (core and copy
  only, not the GL upload) for the Notes column.

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
6. Fill one row below. Fail the title if starved is above 0 (also fail it on a dropped frame or a p99 present interval above 1.1x the median).
7. Bench: `task bench:device CORE=<core> ROM=<path to your dump>`. Record ms/frame and fps.

## Results

fps is the core_bench frames per second at idle on the device, a ceiling, not the played rate.
Underruns/10 min is the starved sample count from `slot.log`. Date is YYYY-MM-DD.

| Title | Platform | Mapper/chip | Core | fps | Underruns/10 min | CPU governor | p99 frame ms | Date | Zip version |
|---|---|---|---|---|---|---|---|---|---|
| Star Fox | SNES | Super FX (GSU) | snes9x | | 4096 in 3 min | performance | 18.14 | 2026-10-13 | ns.0 (patches to 0018) |
| Yoshi's Island | SNES | Super FX 2 (GSU-2) | snes9x | | 5120 in 3 min | performance | 18.44 | 2026-10-13 | ns.0 (patches to 0018) |
| Kirby Super Star | SNES | no coprocessor | snes9x | | 4096 in 3 min | performance | 17.99 | 2026-10-13 | ns.0 (patches to 0018) |
| Super Mario RPG | SNES | SA-1 | snes9x | | 4096 in 3 min | performance | 19.24 (fail) | 2026-10-13 | ns.0 (patches to 0018) |
| Seiken Densetsu 3 | SNES | SA-1 | snes9x | | | | | | |
| Super Mario Bros. 3 | NES | MMC3 | fceumm | | 2048 in 3 min | performance | 17.35 | 2026-10-13 | ns.0 (patches to 0018) |
| Kirby's Adventure | NES | MMC3 (heavy scenes) | fceumm | | 2048 in 3 min | performance | 17.41 | 2026-10-13 | ns.0 (patches to 0018) |
| Castlevania III | NES | MMC5 | fceumm | | 3072 in 3 min | performance | 17.35 | 2026-10-13 | ns.0 (patches to 0018) |
| Akumajou Densetsu | NES | VRC6 (expansion audio) | fceumm | | | | | | |
| Mega Man 2 | NES | MMC1 | fceumm | | 5120 (Rockman 2 (J)) in 3 min | performance | 17.36 | 2026-10-13 | ns.0 (patches to 0018) |
| Battletoads | NES | AxROM (timing sensitive) | fceumm | | 3072 in 3 min | performance | 17.34 | 2026-10-13 | ns.0 (patches to 0018) |
| GBA reference (any title, same session) | GBA | n/a | mgba | | 4096 (Golden Sun) in 3 min | performance | 18.28 | 2026-10-13 | ns.0 (patches to 0018) |

The GBA row is the comparison point: measure it in the same
session as the others, on the same governor.

2026-10-13 run (`task perf:play`, 3 minutes per title, 1 run, logs in `docs/perf/2026-10-13-gate/`):
- Every title, the GBA reference included, fails the 0-underrun rule. All starved samples, and most
  dropped ones, come from slot releasing the ALSA device after 3 s of silence and reopening it:
  once at game start, and again mid-game in Battletoads and Super Mario RPG after a silent stretch.
  This is upstream behaviour (GBA shows it too) and is the next fix.
- After the first 600-present window, every title has 0 presents above 1.5x the period (longest
  23.7 ms against 25.2 ms) and p99 within 1.1x the median, except Super Mario RPG (SA-1) at 19.24 ms
  against 18.46 ms. The governor was already `performance`, so the SA-1 governor retry does not apply.
- Seiken Densetsu 3 and Akumajou Densetsu are not on the test card and were not run.

## Core bench on the device (test carts)

`task bench:device CORE=<core> ROM=<path>`. Emulation only, no video or audio, so it shows headroom, not the gate. Generated test carts (`harness/make_assets.py nes|snes`) are tiny, so real games cost more. Use your own dumps of the 11 titles for real numbers.

| Date | Zip version | Governor | Core | ROM | Median ms/frame | Frames/s |
|---|---|---|---|---|---|---|
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | mgba | 240pee_mb.gba | 0.795 | 1258 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | gpsp | 240pee_mb.gba | 0.924 | 1083 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | fceumm | generated NES cart | 1.624 | 616 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | snes9x | generated SNES cart | 3.295 | 304 |
