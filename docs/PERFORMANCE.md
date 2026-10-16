# Performance evaluation (issue 39, #45)

Goal: a NES or SNES cart feels like a GBA cart. This file holds the tables, the thresholds and the
routine. Raw logs live under `docs/perf/<date>/`. ROMs are the maintainer's own dumps and are never
copied into the repo; logs and tables name a cart by platform only, and `ROM_ON_DEVICE` runs print
`name withheld`.

Status: first device run done on 2026-10-13 (`docs/perf/2026-10-13/`). The automated tables below are
filled from it. The interactive part is manual and still pending.

## Device record

From `docs/perf/2026-10-13/meta.txt` (written by `task perf:eval`).

| Date | Device and firmware | Governor | Thermal zone | Idle SoC temp (C) | Run limit (C) | Power | Zip version |
|---|---|---|---|---|---|---|---|
| 2026-10-13 | RG34XXSP (H700), BaseOS, Linux 4.9.170 aarch64 | performance | `thermal_zone0` (cpu_thermal_zone) | 48.5 (first reading) | 58.5 (idle + 10) | on charger, battery Full | slot v1.6.0, VERSION ns.0, zip built from the stacked branch through patch 0013 |

The limit is idle + 10 C, not the +5 C the script defaulted to: the device idles near 54 C with slot on
screen, so +5 would have discarded runs for no reason. No run was discarded (no `discards.log`). Start
temperatures stayed under the limit; end of run readings sit around 54 C.

Baseline and candidates are measured in the same session, on the same governor, on the charger. The
baseline is GBA on mGBA (the card GBA cart, row `gba-mgba`). `core_bench` runs the stack's core, so
"patched against unpatched v1.6.0" stays the job of `task bench:compare` (2% gate); here the baseline
is the GBA row in the same session.

## Thresholds against the GBA baseline

| Metric | Threshold | Gated on |
|---|---|---|
| Frame time median | within 5% of GBA | median over runs |
| Frame time p99 | present p99 within 1.1x the median present interval, and 0 presents above 1.5x the period (see `docs/DEVICE-GATE.md`) | `slot: frametime:` lines, every session |
| Audio underruns | zero | every session |
| Insert to first frame | within 10% | median over runs |
| Save state and load state | within 20% | median over runs |
| Fast-forward | at least the GBA multiple | median over runs |

Worst cases are reported, not gated. A miss gets its own follow-up issue with the numbers attached.
SA-1 and Super FX titles are reported on their own rows against the same thresholds, not averaged in.

## Automated part: `task perf:eval`

```
task deploy:device          # cores under test must be in System/
task perf:eval              # DATE=YYYY-MM-DD RUNS=3 SD=/mnt/sdcard optional
```

What it does, per pair (GBA mGBA and gpSP, GB and GBC mGBA, NES fceumm and nestopia, SNES snes9x and
snes9x2005_plus), over adb with `core_bench` and at least 3 runs per mode:

- normal: `--frames 1800 --warmup 300 --repeats 3` (ms per frame median and worst repeat, x real time).
- serialize: `--serialize --frames 300` (rewind cost: run, serialize and unserialize per frame, median and worst).
- ff: `--steps 4` (four frames per present, no frameskip; works for every core).
- ffskip: `--steps 4 --frameskip`, mgba and gpsp only, because `core_bench` sets only the `mgba_` and
  `gpsp_` frameskip options. NES and SNES have no frameskip row, and that is a parity gap to note, not a fix.
- Governor and SoC temperature are recorded at the start and end of every run (thermal zone found under
  `/sys/class/thermal`, type cpu or soc, read only).
- Idle temperature is the first reading of the session plus 10 C (was +5 in the first script; the device idles near 54 C with slot on screen). A run that would start above it waits
  30 s and re-checks, up to 4 times, then is discarded (logged in `discards.log`) and the pair is
  reported as missing and the script exits non-zero. Start it on a rested device.
- Card carts are found by listing `Games/<PLATFORM>`; override with `ROM_GBA`, `ROM_GB`, `ROM_GBC`,
  `ROM_NES`, `ROM_SNES`. GB and GBC card pairs report "no workload" when the card has no cart, which is
  not a failure. The free harness carts (`harness/roms`) run as extra `-harness` pairs through `ROM=`.
- Output: `docs/perf/<date>/{meta.txt,*.log,runs.tsv,status.tsv,perf-eval.md}`. Paste the tables from
  `perf-eval.md` into the sections below.

Frame cost is the core plus slot's copy and audio callbacks. It is not frame time in game and does not
include the GL upload, so it is a ceiling check, not the p99 gate.

### Workloads (not the same game across platforms)

| Rows | Workload |
|---|---|
| GBA mGBA (baseline), GBA gpSP | GBA card cart (a large GBA game) |
| NES fceumm, NES nestopia | NES card cart (a NES game) |
| SNES snes9x, SNES snes9x2005_plus | SNES card cart (an SA-1 game, heavy) |
| GB mGBA, GBC mGBA | free harness carts (test patterns, light); no GB or GBC cart on the card |
| GBA mGBA and gpSP, second row | free harness GBA cart (test pattern, light) |

Caveat that governs every "vs GBA" column: the baseline and the candidates run different games, so
"vs GBA" compares workloads as much as cores. Only same-game pairs are like for like: fceumm against
nestopia (same NES cart), snes9x against snes9x2005_plus (same SA-1 cart), mGBA against gpSP (same GBA
cart). Every pair ran above 1.0x real time (full speed) with headroom.

### Frame cost (ms per frame, median and worst repeat)

| Pair | Median | Worst | vs GBA mGBA (median) |
|---|---|---|---|
| GBA mGBA (baseline, card cart) | 5.346 | 5.351 | n/a |
| GBA gpSP (card cart) | 2.097 | 2.098 | -60.8% |
| GBA mGBA (harness cart) | 0.794 | 0.796 | -85.1% |
| GBA gpSP (harness cart) | 0.924 | 0.925 | -82.7% |
| GB mGBA (harness cart) | 1.150 | 1.153 | -78.5% |
| GBC mGBA (harness cart) | 1.107 | 1.108 | -79.3% |
| NES fceumm | 5.970 | 5.981 | +11.7% |
| NES nestopia | 5.532 | 5.544 | +3.5% |
| SNES snes9x (SA-1) | 10.326 | 10.332 | +93.2% |
| SNES snes9x2005_plus (SA-1) | 4.661 | 4.662 | -12.8% |

### Speed headroom in normal play (x real time, higher is better)

| Pair | Median | Worst | vs GBA mGBA |
|---|---|---|---|
| GBA mGBA (baseline, card cart) | 3.117 | 3.115 | n/a |
| GBA gpSP (card cart) | 7.948 | 7.943 | +155.0% |
| GBA mGBA (harness cart) | 20.980 | 20.938 | +573.2% |
| GBA gpSP (harness cart) | 18.045 | 18.025 | +479.0% |
| GB mGBA (harness cart) | 14.487 | 14.455 | +364.8% |
| GBC mGBA (harness cart) | 15.060 | 15.037 | +383.2% |
| NES fceumm | 2.792 | 2.787 | -10.4% |
| NES nestopia | 3.013 | 3.007 | -3.3% |
| SNES snes9x (SA-1) | 1.613 | 1.613 | -48.2% |
| SNES snes9x2005_plus (SA-1) | 3.577 | 3.575 | +14.8% |

### Fast-forward (x real time reached, 4 frames per present)

Frameskip is applied for mgba and gpsp only: `core_bench` sets only the `mgba_` and `gpsp_` frameskip
options. NES and SNES fast-forward was therefore measured without frameskip (parity gap, noted earlier,
not a fix). Compare the no-frameskip column across pairs, since that is the only one every core has.

| Pair | No frameskip, median | No frameskip, worst | Frameskip, median | Frameskip, worst |
|---|---|---|---|---|
| GBA mGBA (baseline, card cart) | 3.112 | 3.108 | 4.430 | 4.425 |
| GBA gpSP (card cart) | 7.943 | 7.935 | 19.970 | 19.957 |
| GBA mGBA (harness cart) | 20.960 | 20.958 | 42.608 | 42.590 |
| GBA gpSP (harness cart) | 18.038 | 18.025 | 58.803 | 58.795 |
| GB mGBA (harness cart) | 14.495 | 14.490 | 29.290 | 29.275 |
| GBC mGBA (harness cart) | 15.073 | 15.068 | 31.812 | 31.773 |
| NES fceumm | 2.790 | 2.790 | not measured | not measured |
| NES nestopia | 2.998 | 2.992 | not measured | not measured |
| SNES snes9x (SA-1) | 1.615 | 1.613 | not measured | not measured |
| SNES snes9x2005_plus (SA-1) | 3.573 | 3.572 | not measured | not measured |

### Rewind cost (ms per frame, median and worst)

Rewind frame cost is run plus serialize every frame. Serialize and unserialize are the per-call costs.

| Pair | Rewind frame cost, median / worst | Serialize, median / worst | Unserialize, median / worst |
|---|---|---|---|
| GBA mGBA (baseline, card cart) | 5.074 / 5.075 | 2.027 / 2.047 | 1.035 / 1.037 |
| GBA gpSP (card cart) | 2.747 / 2.750 | 0.398 / 0.443 | 0.571 / 0.578 |
| GBA mGBA (harness cart) | 1.904 / 1.907 | 4.692 / 4.699 | 1.524 / 1.553 |
| GBA gpSP (harness cart) | 1.125 / 1.132 | 0.315 / 0.323 | 0.477 / 0.489 |
| GB mGBA (harness cart) | 1.243 / 1.244 | 0.877 / 0.898 | 0.390 / 0.403 |
| GBC mGBA (harness cart) | 1.188 / 1.189 | 0.861 / 0.876 | 0.386 / 0.387 |
| NES fceumm | 6.097 / 6.109 | 0.019 / 0.020 | 0.064 / 0.065 |
| NES nestopia | 5.497 / 5.498 | 0.068 / 0.069 | 0.039 / 0.040 |
| SNES snes9x (SA-1) | 9.942 / 9.958 | 1.297 / 1.326 | 2.328 / 2.373 |
| SNES snes9x2005_plus (SA-1) | 4.576 / 4.585 | 0.663 / 0.679 | 0.519 / 0.524 |

The slowest single serialize or unserialize call over all runs (the "worst" tables in `perf-eval.md`)
stays under 3 ms for every pair except mGBA on the GBA harness cart, which peaks at 5.5 ms serialize.
This is core cost only, not the save state UI time with thumbnail (manual, see below).

## Verdict per pair against the thresholds

Read with the caveat above: "vs GBA" mixes game and core. Only measured, automated metrics are judged;
p99, underruns, insert to first frame and UI save and load time are manual and pending.

| Pair | Frame cost (within 5%) | Fast-forward (at least GBA multiple) | Rewind and state cost (within 20%) |
|---|---|---|---|
| GBA gpSP | pass (-60.8%) | pass (7.9x vs 3.1x) | pass |
| GB mGBA, GBC mGBA (harness) | pass, light cart, not a real comparison | pass, same caveat | pass, same caveat |
| NES fceumm | miss, +11.7% (different game) | miss, 2.79x vs 3.11x | rewind frame cost +20.2% (borderline miss); serialize and unserialize far below GBA |
| NES nestopia | pass, +3.5% (different game) | miss by a hair, 3.00x vs 3.11x | pass, +8.3% |
| SNES snes9x (SA-1) | miss, +93.2% (heavy game) | miss, 1.6x vs 3.1x: x4 fast-forward cannot reach its target | miss: rewind frame cost +95.9%, unserialize +124.9% |
| SNES snes9x2005_plus (SA-1) | pass, -12.8% | pass, 3.57x vs 3.11x | pass |

- Every pair runs above 1.0x real time (full speed) with headroom. The worst is snes9x on the SA-1 game
  at 1.6x.
- snes9x2005_plus is faster than snes9x on the same SA-1 cart (4.66 against 10.33 ms). Nobody has checked
  that it emulates this game correctly, so this is a speed result only, unverified.
- Same-game comparisons: fceumm is 7.9% slower than nestopia on the NES cart (5.970 against 5.532 ms);
  gpSP is 2.5x faster than mGBA on the GBA card cart (2.097 against 5.346 ms).
- Zero audio underruns, p99 and insert to first frame are not measured here (manual, pending).

## Follow-ups proposed

Proposed, not yet filed as GitHub issues (maintainer to confirm). Each carries the numbers to attach.

1. SNES snes9x fast-forward ceiling on SA-1: 1.6x real time (1.615 median, 10.326 ms per frame, no
   frameskip available) against GBA mGBA 3.11x, so x4 fast-forward cannot reach its target on this game.
   Options include frameskip for snes9x and a lighter core for SA-1 carts.
2. NES fceumm frame cost: +11.7% against the GBA baseline (5.970 against 5.346 ms), threshold 5%, rewind
   frame cost +20.2%. The baseline is a different game, so a same-workload check is needed first (a GBA
   and a NES cart of comparable cost, or the same core family) before calling it a regression.
   nestopia is +3.5% on the same cart.
3. snes9x2005_plus on SA-1: faster (4.661 ms, 3.58x) but correctness on this game is unchecked. Run the
   SA-1 gate titles on it before offering it as the fast SNES core.
4. Frame-time trace: done by the `frame-trace` patch (see Play results). Earlier logs have no `frametime:` lines.
5. Gate titles not on the card: the DEVICE-GATE SNES and NES sets, Super FX and other mappers, and GB and
   GBC card carts were not run. A real GB and GBC cart is needed for non-harness numbers.

## Interactive part: manual routine

slot has no frame-time trace and this round adds none (a patch only if upstream's log has no
equivalent, per the issue). These cells stay "manual, pending" until someone plays. The log lines
(from `work/slot` `crates/slot/src/{boot_time,emu,latency}.rs`):

- `slot: boot: <phase> at <ms> ms`: boot phases, always printed to `slot.log`.
- `slot: audio: Q/T queued, D dropped, S starved, locked ...`: every 300 paced frames, `SLOT_TRACE` only.
- `slot: audio: N samples dropped, M starved`: once at session end if either is above 0, or always with `SLOT_TRACE`.
  "Starved" counts samples, not events. `grep underrun` proves nothing.
- `slot: latency: read>pad .. take>swapped .. total X ms`: per input, with `System/trace-latency.on` on the card
  (or `SLOT_TRACE_LATENCY`). Input to screen swap, not frame time.

Per platform and core, 3 sessions each, same governor, on the charger, device rested:

1. `adb shell cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor`, note it. Note the SoC temp
   (read the zone `perf-eval` printed in `meta.txt`) and skip a session that starts above idle + 10 C.
2. `adb shell touch /mnt/sdcard/System/trace-latency.on`. Add `export SLOT_TRACE=1` under the
   `export SLOT_ROOT` line of `System/launch_frontend.sh` on the device for the run, remove it after.
3. Power on to the shelf. Boot to shelf: read the `slot: boot:` lines in `slot.log` (first line to the
   shelf phase). Stopwatch fallback if no shelf phase is logged.
4. Insert the cart, launch it: insert to first frame is the boot lines between the launch and the first
   game phase in the same log. Note which `boot:` phase names you used.
5. Play 10 minutes with the heaviest scenes, then quit through the menu (not power off, or the summary
   line is lost). Do not pull `slot.log` before the next launch: it is rotated to `slot.log.1`.
6. `task readout:device` after each session: starved samples at session end and the trace maximum
   give underruns per 10 min. The latency summary (median, p99, max over inputs) gives input latency.
7. Shelf scroll, quick menu frame time, save state and load state UI time (with thumbnail): no log
   line exists. Record by phone slow-motion video (240 fps) of the screen, count frames from press to
   change, 5 repeats, median and worst. Mark the method in the table.
8. Save the logs as `docs/perf/<date>/manual/<pair>.<n>.log` (cart named by platform only).

| Metric | GBA mGBA | GBA gpSP | GB mGBA | GBC mGBA | NES fceumm | NES nestopia | SNES snes9x | SNES snes9x2005_plus |
|---|---|---|---|---|---|---|---|---|
| Boot to first shelf frame | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |
| Insert to first game frame | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |
| Frame time p99 in game | manual, pending (no trace) | manual, pending (no trace) | manual, pending (no trace) | manual, pending (no trace) | manual, pending (no trace) | manual, pending (no trace) | manual, pending (no trace) | manual, pending (no trace) |
| Audio underruns per 10 min | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |
| Input latency (median, p99) | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |
| Shelf scroll frame time | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |
| Save state UI time | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |
| Load state UI time | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending | manual, pending |

Known before measuring (docs/DEVICE-GATE.md): on 2026-10-12 real sessions showed starved samples on GBA,
NES and SNES alike, so the zero-underrun threshold is expected to fail everywhere until the start-up
starve is fixed.

## Sega core: Genesis Plus GX (2026-10-15, issue 50)

First step for Game Gear, Master System and Mega Drive (ADR 0053): the core alone, before any
frontend code. `core_bench` on the device through `scripts/bench-device.sh` (`CORE=genesis_plus_gx`,
the core pushed to `System/` by hand for the run and removed after), RG34XXSP, governor
`performance`, SoC 51 to 57 C, 3 runs of `--frames 3000 --warmup 300 --repeats 3` per pair, then one
`--serialize --frames 300`. Logs: `docs/perf/2026-10-15-sega/`. The carts are free test homebrew,
kept out of the repo: 240p Test Suite 1.32 for Mega Drive and 1.10 for SNES (Artemio Urbina, GPL-2.0,
itch.io), River Strike 0.10 (haroldo-ok, MIT, SMS) and Tunnel 1.0 (liamhays, GPL-3.0, GG). The card has no
Sega folders, so no owned cart was run.

**Light workload.** `core_bench` presses nothing, so each cart sits on its menu or title screen. Read
the rows as a floor for each system's cost, not as gameplay. The SNES row is the same suite on
snes9x2005_plus, measured in the same session, so MD and SNES compare like for like.

| Pair (device) | ms/frame, median of 3 runs (worst run) | x real time at 59.92 Hz (60 Hz) | State size | Serialize run / save / load, median (p95) ms |
|---|---|---|---|---|
| MD Genesis Plus GX, 240p Suite | 3.305 (3.305) | 5.05 (5.04) | 1,036,288 | 3.595 / 0.305 (0.467) / 0.421 (0.537) |
| MD Genesis Plus GX, FM `nuked (ym2612)` | 11.760 (1 run) | 1.42 (1.42) | same | not run |
| SMS Genesis Plus GX, River Strike | 1.302 (1.307) | 12.82 (12.80) | 1,036,288 | 1.643 / 0.260 (0.461) / 0.351 (0.468) |
| GG Genesis Plus GX, Tunnel | 1.013 (1.024) | 16.47 (16.45) | 1,036,288 | 1.108 / 0.252 (0.415) / 0.351 (0.479) |
| SNES snes9x2005_plus, 240p Suite | 2.696 (2.701) | 6.17 at 60.10 Hz (6.18) | 564,544 | 3.045 / 0.630 (0.887) / 0.560 (0.776) |

Host proxy (M5 Max, arm64 dylib, one run of 5 repeats): MD 0.217, SMS 0.072, GG 0.060 and SNES
snes9x2005_plus 0.134 ms/frame. The device is 15 to 22 times slower, so host numbers rank cores but
do not predict the device.

Frame hashes match between host and device for every cart, so the device build runs the same code path.

What it shows:

- MD on Genesis Plus GX costs 1.23 times snes9x2005_plus on the same suite (3.305 against 2.696 ms),
  and less than snes9x2005_plus on the 2026-10-13 SA-1 cart (4.661 ms, a different session and game).
- SMS and GG are trivial: over 12x real time.
- The Genesis Plus GX state is a fixed 1,036,288 bytes on every system, 1.8 times snes9x2005_plus.
  Rewind therefore costs the same per push on GG and SMS as on MD; serialize itself stays under
  0.5 ms at p95. The XOR and lz4 cost of a 1 MB delta in slot's rewind ring is not measured here.
- The default FM core, `mame (ym2612)`, is what the table measures. Nuked is 3.6 times slower
  (11.76 ms, 1.42x): no x4 fast-forward, so it stays off.

**Go/no-go, Genesis Plus GX against PicoDrive for MD: go for Genesis Plus GX, provisionally.** 5x
headroom on a light cart is in the same class as snes9x2005_plus, which passes every threshold above,
and Genesis Plus GX is the more accurate core (Batocera uses it as the MD default and calls PicoDrive
the lighter one for weaker hardware). PicoDrive is not built or measured. It stays the fallback if the
heavy MD gate on the maintainer's own cards misses full speed or x4 fast-forward: Virtua Racing (SVP),
Sonic 3D, Street Fighter II SCE, Thunder Force IV, Vectorman (issue 53).

## Not measured yet

- Everything in the interactive table above (needs a person at the device).
- In-game frame time p99 and dropped or late presents for the 2026-10-13 logs: they predate the `frame-trace` patch. Re-run `task perf:play` with it.
- NES and SNES fast-forward with frameskip (`core_bench` has no frameskip option for those cores).
- Fast-forward as slot itself runs it (`--steps` reproduces the emulation cost, not the real FF path with
  audio and presents).
- Rewind emu-thread stalls (the `STALL` path in `emu.rs` logs nothing), only the serialize cost is measured.
- The 11 gate titles and the NES mapper set from `docs/DEVICE-GATE.md`: not on the card. Only one NES, one
  SNES SA-1 and one GBA card cart are covered, so Super FX and other mappers are untested.
- GB and GBC on card carts (none on the card): only the free harness carts, which are test patterns and light.
- Unpatched v1.6.0 slot as a separate baseline binary (the GBA row of the same session stands in).
- Battery state other than on charger, and any governor other than the default.
- Shader, video mode and rewind-on-play cost on top of the core.

## Play results, automated (2026-10-13)

`task perf:play` (`scripts/auto-play.sh`) boots each game through `slot.state` resume, injects the same input on every core (START x3, then hold Right, tap A every 700 ms and B every 2.3 s), ejects with a held MENU, and parses `slot.log` with `SLOT_TRACE=1` and `trace-latency.on`. One run per pair, 3 minutes each, same session, governor `performance`. A heavy and a light game per platform. Full tables: `docs/perf/2026-10-13/play-eval.md`; logs: `docs/perf/2026-10-13/play/` (game names redacted).

| Pair | Work per frame, median / worst window (ms) | Input latency, median / p99 (ms) | Starved samples | Missed latches |
|---|---|---|---|---|
| GBA mGBA heavy (baseline) | 7.6 / 9.8 | 17.4 / 27.5 | 5120 | 1 |
| GBA mGBA light (baseline) | 9.4 / 11.4 | 18.9 / 27.4 | 6144 | 1 |
| GBA gpSP heavy / light | 5.4 / 7.4, 5.4 / 7.6 | 15.4 / 23.9, 15.3 / 24.6 | 4096, 5120 | 1, 1 |
| GBC mGBA | 5.2 / 5.7 | 15.7 / 23.8 | 4096 | 2 |
| NES fceumm heavy / light | 6.4 / 7.6, 8.0 / 15.8 | 15.7 / 24.1, 20.5 / 48.5 | 6202, 1024 | 0, 1 |
| NES nestopia heavy / light | 8.8 / 10.6, 8.7 / 15.9 | 17.9 / 27.2, 20.3 / 47.8 | 4096, 4096 | 0, 1 |
| SNES snes9x heavy / light | 12.8 / 15.7, 10.1 / 13.4 | 22.9 / 32.9, 18.8 / 30.3 | 5120, 3072 | 0, 1 |
| SNES snes9x2005_plus heavy / light | 10.5 / 13.2, 8.4 / 10.4 | 18.8 / 29.6, 17.7 / 26.9 | 5120, 3072 | 0, 1 |

Every session ran at the full 60 Hz present period (16.78 ms), ended cleanly and logged no crash. Starved samples appear on every platform including the GBA baseline (the known start-up starve), so they are not a NES/SNES regression; they still fail the 0-underrun gate for everyone. After the parser corrections below, snes9x on the heavy Super FX game has a latency p99 of 32.9 ms (the earlier 345 ms was volume-key lines) and a steady worst 600-frame window of 15.7 ms of work (the earlier 37 ms was the eject window), the same range as the other cores. NES light p99 latency (about 48 ms) is still above the GBA baseline (27 ms), and is the same on fceumm and nestopia. One 3-minute run per pair is noisy; treat single-run deltas as leads, not verdicts.

### Parser corrections (2026-10-13 re-parse)

The first parse of these logs mixed in two measurement artifacts. `scripts/auto-play.sh` now drops both, and `sh scripts/auto-play.sh eval 2026-10-13` was re-run on the same logs to produce the table above.

- The last `slot: pace:` window of a session is the eject window (the MENU hold and teardown), not play. It is dropped. This is what made the worst work window look like 20 to 37 ms.
- `slot: latency:` lines after a VolumeUp or VolumeDown key are not input latency. Upstream `latency::read()` stamps on any key-down (`crates/slot/src/input/device.rs`), but `latency::applied()` only fires on a pad bit (`emu.rs`), so a volume key leaves a stale stamp and the next pad press reports the gap (up to 435 ms). This is a trace-only quirk in upstream code and slot is not patched for it. The parser drops a latency line when a `slot: Volume` line appeared since the previous latency line. Before and after: snes9x heavy p99 345.3 to 32.9 ms, gpSP light max 328.2 to 26.3 ms, GBC max 135.5 to 24.4 ms.
- A real bug the same logs exposed (patch `audio-release-pace`): after 3 s of silence the audio thread released the PCM and slept a relative 512 frames per loop, which drains slower than real time. The ring filled and `push_blocking` held the emulator thread, adding 8 to 17 ms of pad to emu latency on silent NES games. It now sleeps to an absolute deadline. Since slot v1.7.0 upstream's own `audio/pacer.rs` does this and the patch is dropped (ADR 0041).
- Frame time: `slot: frametime:` lines (patch `frame-trace`, with the latency trace on) give present-to-present p50, p99 and max per 600 presents. The parser reports `ft_p50_med`, `ft_p99_worst` and `ft_max` for runs made after that patch. The 2026-10-13 logs predate it, so those rows read n/a.
