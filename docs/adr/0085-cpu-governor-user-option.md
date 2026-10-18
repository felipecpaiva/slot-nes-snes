# 0085. Offer the CPU governor as a General row, Performance by default

- Status: Proposed. Needs the device measurement below, and maintainer approval of upstream test
  site (j) (the CPU label in `the_rows_run_in_the_order_the_user_chose`)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: patches/0053-cpu-governor.patch, [fork-pvaibhav.md](../research/fork-pvaibhav.md) section 2
  and 8, [fork-review-2026-10-18.md](../research/fork-review-2026-10-18.md) item 13,
  [DEVICE-GATE.md](../DEVICE-GATE.md) (governor rule)

## Context

pvaibhav/slot (ad7ce10, 320ac44) writes `schedutil` into every
`/sys/devices/system/cpu/cpufreq/policy*/scaling_governor` from `launch_frontend.sh`. It saves battery
(their only figure is CPU MHz, 480 to 1,512 MHz under schedutil), but every perf and gate row we have
was measured on BaseOS's `performance`. Our heaviest titles are close to the period on `performance`:
Super Mario RPG (SA-1) has a 19.24 ms p99 against 18.46 ms in DEVICE-GATE.md, and PS1 CTR is heavier.
A ramping governor can miss periods where `performance` does not.

Maintainer rules: a speed against battery trade is always a user option, never forced; the user's
choice becomes the default; factory defaults stay.

Upstream 1.8.0 puts device-wide settings on the General page (2c82294 adds Lid Power Off there, just
above Date & Time).

## Decision

- General gains a **CPU** row just above Date & Time: Performance or Balanced. Left or Right flips it.
- Stored as `mode = balanced` in `Config/cpu.txt` through upstream's `ini::write`, like `region.txt`.
  A missing file or line is Performance; an unknown value is logged and read as Performance.
- Balanced writes `schedutil` to every `cpufreq/policy*`, Performance writes `performance`. It runs
  at start (from `device_app.rs`, so a slot restart without a reboot still gets the saved mode) and at
  once when the row changes. Before writing, each policy's `scaling_available_governors` must list the
  governor; if one does not, nothing is written and the refusal is logged.
- Every attempt logs one line, with what each policy reads back:
  `slot: cpu: balanced mode, governor schedutil (policy0 schedutil)`.
- `launch_frontend.sh` is unchanged. On the host and in tests nothing is written unless a test
  points the module at a fake cpufreq directory.
- Upstream test site (j): `crates/slot-ui/tests/quick_menu.rs` gains the line `"CPU",` between
  `"Lid Power Off",` and `"Date & Time"` in the General labels, because `QuickRow::GENERAL` is pinned
  there. `scripts/check-upstream-tests.sh` removes exactly that line before comparing, and accepts
  the file without it. This is a new kind of site (a list entry, like (g)), so it needs the
  maintainer's approval; until then the patch is a proposal.

## Consequences

- Default behaviour is unchanged: Performance writes the governor BaseOS already runs.
- A Balanced user gets schedutil until they flip back; the row says which mode is on.
- New hunks in upstream `quick_menu.rs` (one row), `app.rs` (the row arms) and `device_app.rs` (one
  line). Ported onto upstream main 1b20432 (ADR 0083): General has 7 upstream rows there, CPU sits
  between Lid Power Off and Date & Time, and site (j) moved with it.
- The BaseOS kernel must offer schedutil. If the probe below shows it does not, the row stays at
  Performance in effect and logs the refusal; the row should then be dropped.

## Device measurement (maintainer)

Build and deploy: `task deploy:device`. Rested device (idle, SoC within 10 C of idle as in
PERFORMANCE.md), on the charger for the performance runs.

1. Probe, read only:
   `adb shell 'cat /sys/devices/system/cpu/cpufreq/policy*/scaling_available_governors /sys/devices/system/cpu/cpufreq/policy*/scaling_governor; ls /sys/devices/system/cpu/cpufreq/'`.
   Pass: `schedutil` is listed. Note how many policies there are (the H700 should have one, policy0).
2. Performance baseline (no `Config/cpu.txt`, or `mode = performance`):
   - `task perf:play CORE=snes9x PLATFORM=snes PAIR=snes-snes9x-sa1 STEM='<Super Mario RPG as named on the card>' MINUTES=3 RUNS=3 DATE=2026-10-19-performance`
   - `task perf:play CORE=snes9x PLATFORM=snes PAIR=snes-snes9x-superfx STEM='<Star Fox as named on the card>' MINUTES=3 RUNS=3 DATE=2026-10-19-performance`
   - `task perf:play CORE=snes9x PLATFORM=snes MINUTES=3 RUNS=3 DATE=2026-10-19-performance` (the default
     pairs include Yoshi's Island, Super FX 2)
   - `task perf:play PLATFORM=md MINUTES=3 RUNS=3 DATE=2026-10-19-performance` (Virtua Racing, SVP)
   - `task perf:play PLATFORM=ps1 MINUTES=3 RUNS=3 DATE=2026-10-19-performance` (CTR)
3. Switch to Balanced: Settings > General > CPU > Right on the device, or
   `adb shell 'printf "mode = balanced\n" > /mnt/sdcard/Config/cpu.txt'`. auto-play restarts slot for
   every run and does not touch `cpu.txt`, so each run starts in Balanced.
4. Confirm it took: `adb shell cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor` says
   `schedutil`, and `grep -h 'slot: cpu:' docs/perf/2026-10-19-balanced/play/*` (after step 5) shows
   `balanced mode, governor schedutil (policy0 schedutil)` in every run.
5. Repeat every command of step 2 with `DATE=2026-10-19-balanced`. Alternate the order if time allows
   (Balanced first on a second day), since temperature drifts.
6. Compare `docs/perf/2026-10-19-performance/play-eval.md` with `docs/perf/2026-10-19-balanced/play-eval.md`
   per title, median and worst over the 3 runs:
   - Presents that missed a latch (`pace_missed`),
   - audio starved and dropped samples (`starved`, `dropped`),
   - present interval p99, worst window (`ft_p99_worst`) and longest (`ft_max`).
   Optionally `task perf:eval` once per mode (it records the governor) for core ms/frame.
7. Decision rule: Balanced is fit to offer only if every heavy title has 0 starved, 0 dropped, no more
   missed latches than Performance, and `ft_p99_worst` within 1.1x the period. Either way the row stays
   Performance by default. Add before and after rows to DEVICE-GATE.md, as its governor rule requires.
8. Put it back: `adb shell 'rm /mnt/sdcard/Config/cpu.txt'` and restart slot (or flip the row).

Battery (current cannot be read while USB is attached, so measure discharge unplugged):

1. Charge to at least 95%, then start a logger that keeps running without adb (read-only on sysfs,
   writes one file on the card):
   `adb shell 'b=$(for d in /sys/class/power_supply/*; do [ "$(cat $d/type)" = Battery ] && echo $d; done); nohup sh -c "while :; do echo \$(date +%s) \$(cat $b/capacity) \$(cat $b/voltage_now); sleep 60; done" >> /mnt/sdcard/Logs/battery-performance.log 2>&1 & echo $! > /mnt/sdcard/Logs/battery-logger.pid'`
   Check it writes a line a minute (`adb shell tail -2 /mnt/sdcard/Logs/battery-performance.log`).
   If the file stops growing once the cable is out, start it again with `setsid` before `nohup`.
2. Unplug. Seat the same cart in the same mode each time (a GBA game left in its attract loop, or the
   SNES heavy title in its demo), brightness and volume fixed, lid open, no input, 60 minutes.
3. Plug back in, `adb shell 'kill $(cat /mnt/sdcard/Logs/battery-logger.pid); cat /mnt/sdcard/Logs/battery-performance.log'`.
   Discharge rate = (first % minus last %) per hour; use `voltage_now` to break ties within 1%.
4. Recharge to 95% and repeat with Balanced, logging to `battery-balanced.log`. Two runs per mode,
   alternating. Report %/hour per mode; Balanced is worth offering only with a clear gap (more than
   the 1% gauge step per hour).
