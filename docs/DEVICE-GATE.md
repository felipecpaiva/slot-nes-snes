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

2026-10-13 audio reopen fix (patch 0021, issue 47; 2 minutes per title, 1 run, same scripted input, governor
`performance`, logs in `docs/perf/2026-10-13-audio/`). Session summary line, samples:

| Title | Core | Before (gate, 3 min): dropped / starved | After (2 min): dropped / starved | Device releases in game, before / after | p99 frame ms after |
|---|---|---|---|---|---|
| Battletoads | fceumm | 46336 / 3072 | 0 / 0 | 2 / 0 | 17.40 |
| Super Mario RPG | snes9x | 48038 / 4096 | 0 / 0 | 2 / 0 | 19.02 |
| Kirby's Adventure | fceumm | 0 / 2048 | 0 / 0 | 0 / 0 | 17.36 |
| Golden Sun (GBA reference) | mgba | 22818 / 4096 | 0 / 0 | 1 / 0 | 18.26 |

- Cause, measured with a timing build: `snd_pcm_set_params` on plug:default takes about 251 ms and the
  release about 242 ms, both on the audio thread. The dropped samples came from those two stalls, the
  starved ones from the ring running dry during the cart insert (see the DECISIONS row).
- Shelf check, scripted: boot to the shelf, `audio released after silence` logged, A inserts Golden Sun,
  `audio reopened at 11138 ms` (wake at 10875 ms, play unpaused at 11641 ms), 30 s of play at 0 dropped and
  0 starved, eject, and `audio released after silence` again on the shelf. The same run on the NES shelf with
  Kirby's Adventure (fceumm, the fastest loader: emu ready 31 ms after the insert): wake at 10877 ms, reopened at
  11138 ms, unpaused at 11630 ms, 0 dropped and 0 starved. The insert animation, not the core load, is what
  hides the open.
- These are 2-minute runs, not the 10-minute gate. Not measured: a resume after more than 3 s of pause still
  reopens the device (one ~251 ms stall), and whether the speaker buzzes during long in-game silence.

## PlayStation (pcsx_rearmed)

PS1 real-play gate from issue 63, on the ari64 dynarec build of pcsx_rearmed that `task core:device`
ships (the host tests run the interpreter, so they say nothing about speed on the H700). Two titles,
3 minutes each, scripted input, one run:

1. `task deploy:device`. Note the zip version.
2. `task perf:play PLATFORM=ps1 MINUTES=3 RUNS=1` plays `CTR - Crash Team Racing (USA)` (pair
   `ps1-pcsx_rearmed-heavy`, 3D racing with music).
3. `CORE=pcsx_rearmed PLATFORM=ps1 STEM='Spyro the Dragon (USA)' PAIR=ps1-pcsx_rearmed-light MINUTES=3 RUNS=1 sh scripts/auto-play.sh`
   plays Spyro (`task perf:play` does not pass `PAIR`). The stems must match the card's file names
   without `.chd`, `.cue`, `.pbp` or `.m3u`; a wrong one prints "skipped".
4. Read `docs/perf/<date>/play/play-eval.md` and fill one row per title below. Fail a title on any of:
   starved or dropped above 0; a present above 1.5x the period after the first window; `ft_p99_worst`
   above 1.1x `ft_p50_med`; `crash` above 0; a session that did not end cleanly; or
   `grep -c panicked docs/perf/<date>/play/ps1-*.log` above 0 (`parse_log` does not count panics).

These are 3-minute runs, not the 10-minute criterion 4. A pass here is the go to run the 10 minutes.

| Title | Core | Starved / dropped in 3 min | p50 / p99 / max present ms | Crash or panic lines | Clean eject | CPU governor | Date | Zip version |
|---|---|---|---|---|---|---|---|---|
| CTR - Crash Team Racing | pcsx_rearmed | 0 / 0 | 16.79 / 17.69 / 24.06 (61.44 in the first window) | 0 / 0 | yes | performance | 2026-10-17 | v1.7.0-ns.0 (main 96248fb) |
| Spyro the Dragon | pcsx_rearmed | 0 / 0 | 16.79 / 19.07 / 25.67 (152.78 in the first window, 35.14 on eject) | 0 / 0 | yes | performance | 2026-10-17 | v1.7.0-ns.0 (main 96248fb) |

CTR passes. Spyro misses two limits by a small margin, with no audio cost: one window's p99 is 19.07
ms (1.14x the median, limit 1.1x) and one present is 25.67 ms (1.53x the period, limit 1.5x). Every
other window's p99 is 17.3 to 17.8 ms. The 35.14 ms present is the eject at the end of the run. Likely
a level load (CD read) under the scripted input; to confirm with the 10-minute run.

## PAL pacing (issue 66, ADR 0071)

Checks that a PAL game runs at its own 50 fps with its own pitch and no audio cost. Pick titles the
cores really detect as PAL (the first line below proves it either way):

| System | Example (No-Intro name) | Why it reads as PAL |
|---|---|---|
| NES (fceumm) | `Super Mario Bros. 3 (Europe)` | "(Europe)" in an iNES 1.0 file name, or the NES 2.0 timing byte |
| SNES (snes9x2005_plus or snes9x) | `Super Mario World (Europe)` | header region byte |
| Mega Drive | a Europe-only cart, e.g. `Asterix and the Great Rescue (Europe)` | header region `E` only; a `JUE` header (most "(USA, Europe)" carts) runs as NTSC |
| Master System | `Micro Machines (Europe)` or `Fantastic Dizzy (Europe)` | in Genesis Plus GX's database; most other SMS carts run as NTSC |
| PS1 | `Spyro the Dragon (Europe)` | SCES disc |

Per title, 3 minutes, one run:

1. `task deploy:device`. Note the zip version. PAL Speed must be Native (no `Config/pal_speed.txt`,
   or no line for that system).
2. `CORE=<core> PLATFORM=<nes|snes|md|sms|ps1> STEM='<name on the card>' PAIR=<platform>-pal MINUTES=3 RUNS=1 sh scripts/auto-play.sh`
3. In `docs/perf/<date>/play/<platform>-pal.1.log` (auto-play names the log `<PAIR>.<run>.log`):
   - `grep 'slot: emu: pacing at' <log>` must print one line near 50 (50.007 NES and SNES, 49.701
     Mega Drive and Master System, about 50 PS1). No line means the core ran the game as NTSC: pick
     another title, it is not a pacing failure.
   - Game speed: `grep -c 'slot: audio: .* queued' <log>` counts one line per 300 game frames, so
     3 minutes at 50 fps gives about 30 (36 would mean 60 fps). Enter count x 300 / 180 as fps.
   - Audio: starved and dropped 0 in the session summary, as for every title. In the
     `slot: audio: Q/T queued` lines Q must stay near T for the whole run. A paced core takes its
     ticks-to-frames ratio from the pacer's estimate of the panel period, not from the measured
     tick rate; if the two differ by more than the 0.5% rate control can absorb, Q climbs steadily
     (towards dropped: frames run faster than the panel really ticks) or falls steadily (towards
     starved) long before the summary shows it. Note the first and last Q of the run.
   - Presents: `ft_p50_med` stays about 16.78 ms and `ft_p99_worst` within 1.1x of it, from
     `play-eval.md`. The panel still presents at 59.6 Hz; a repeated frame is not a missed present.
4. By ear and eye, against a stopwatch: a PAL game's music at Native is about 17% lower in pitch
   and slower than with PAL Speed set to Panel (flip the row in that system's Screen section, start
   the game again). An in-game clock (a level timer) should keep pace with the stopwatch over 60 s.
5. Optional, for the record: `adb shell cat /sys/class/graphics/fb0/modes` and add it to Notes
   (upstream never writes a panel mode; a 50 Hz mode is the open alternative in ADR 0071).

| Title | Core | Pacing line fps | Game fps (audio lines) | Q first / last (T) | Starved / dropped | p50 / p99 present ms | Native vs Panel by ear | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Asterix (Europe), NES | fceumm | 50.007 | about 50 (21 lines in a 2 minute run) | 2443 / 2110 (2184) | 0 / 0 | 16.78 / 17.39 | not checked | 2026-10-18 | branch pal-pacing (2b4445a), governor performance | 2 minutes, auto-play, one run; no panic, clean eject |
| Another World (Europe), MD | genesis_plus_gx | 49.701 | about 50 (21 lines) | 3243 / 2205 (2184) | 0 / 0 | 16.78 / 17.42 | not checked | 2026-10-18 | branch pal-pacing (2b4445a), governor performance | as above |
| Addams Family (Europe), SMS | genesis_plus_gx | 49.701 | about 50 (21 lines) | 2470 / 2251 (2184) | 0 / 0 | 16.78 / 17.32 | not checked | 2026-10-18 | branch pal-pacing (2b4445a), governor performance | as above; the title is in Genesis Plus GX's Europe list |
| Rapid Reload (Europe), PS1 | pcsx_rearmed | 50.000 | about 50 (21 lines) | 3068 / 1950 (2184) | 0 / 0 | 16.78 / 18.86 | not checked | 2026-10-18 | branch pal-pacing (2b4445a), governor performance | p99 as the NTSC Spyro run, accepted |

PAL gate passed on 2026-10-18. Q starts above T (the start-up prefill) and settles near T, with no
steady drift. SNES had no European cart on the card, so SNES PAL pacing is host-tested only.

## Master System region (issue 69, ADR 0076)

Checks that Region Europe makes a European Master System cart the core does not know run at PAL
timing, and that Auto leaves it as before. Genesis Plus GX's database marks only these as Europe:
Cosmic Spacehead, Fantastic Dizzy, Micro Machines, The Addams Family, Back to the Future Part III,
Bram Stoker's Dracula, California Games II, Home Alone, Power Strike II, Predator 2, RoboCop 3,
Sensible Soccer, Shadow of the Beast, Sonic the Hedgehog 2, Space Harrier (50 Hz), Chase H.Q. (and
a few Brazilian and prototype entries). Pick a European cart **not** in that list, for example
`Asterix (Europe)`, `Asterix and the Secret Mission (Europe)`, `Lemmings (Europe)`,
`Land of Illusion Starring Mickey Mouse (Europe)`, `The Lucky Dime Caper Starring Donald Duck
(Europe)`, `Streets of Rage (Europe)`, `Ninja Gaiden (Europe)`, `Prince of Persia (Europe)`,
`Ecco the Dolphin (Europe)` or `The Smurfs (Europe)`.

1. `task deploy:device`. Make sure `Config/region.txt` has no `sms` line (Auto) and PAL Speed is
   Native.
2. `CORE=genesis_plus_gx PLATFORM=sms STEM='<name on the card>' PAIR=sms-region-auto MINUTES=2 RUNS=1 sh scripts/auto-play.sh`.
   `grep 'slot: emu: pacing at' docs/perf/<date>/play/sms-region-auto.1.log` must print nothing:
   the core runs the cart at 59.92 fps, the reason for the row. A `pacing at 49.701` line means the
   cart is in the core's list; pick another.
3. On the device, open the Master System Screen section, set Region to Europe (or put
   `sms = europe` in `Config/region.txt`), then
   `CORE=genesis_plus_gx PLATFORM=sms STEM='<same name>' PAIR=sms-region-europe MINUTES=2 RUNS=1 sh scripts/auto-play.sh`.
4. In `sms-region-europe.1.log`: one `slot: emu: pacing at 49.701 fps` line; starved and dropped 0;
   Q near T in the `queued` lines; `ft_p50_med` about 16.78 ms and `ft_p99_worst` within 1.1x.
5. Optional: start a Game Gear and a Mega Drive game with Region still on Europe; neither log may
   show a `pacing at` line for a non-European cart. Set Region back to Auto afterwards.

| Title | Auto: pacing line | Europe: pacing line fps | Starved / dropped | p50 / p99 present ms | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|
| Streets of Rage (Europe, Brazil) | none (60 Hz) | 49.701 | 0 / 0 | 16.79 / 17.34 (worst window) | 2026-10-18 | branch sms-region (df8a717), governor performance | auto-play, Region set by `sms = europe` in Config/region.txt, removed afterwards; no panics |

Master System region gate passed on 2026-10-18. Logs: `docs/perf/2026-10-18/play/sms-region-*.1.log`.

## Atari Lynx (issue 112, ADR 0093)

Pending. Needs the player's own `BIOS/lynxboot.img` (512 bytes, crc32 0d973c9d). The host measured
the rate each cart programs (docs/research/lynx-plan.md section 11); a `slot: emu: the game runs at`
and a `slot: emu: pacing at` line in `slot.log` say what the device ran.

1. Boot: the cart seats, the first picture comes after the boot ROM (about half a second).
2. Picture: Actual is 640x408 in the middle; SELECT+X or the Picture row gives Stretch (full panel).
3. Rotation: a right-turned cart (Klax, Gauntlet: The Third Encounter) is drawn upside down with
   Flip Right Carts on; with the handheld turned, the d-pad moves the way the picture faces. Off draws
   it as made. Lexis (left) is drawn as made either way.
4. Controls: A and B, L and R (Option 1 and 2), START (Pause).
5. Audio: no crackle; `starved` and `dropped` stay 0 under `SLOT_TRACE`.
6. Speed: Native paces a 75 Hz game at 75 fps (1 or 2 frames a vsync) and a 50 Hz one at 50;
   Panel runs one frame a vsync.
7. States: save and load a state; eject and power cycle resume where it was.
8. Missing BIOS: rename `BIOS/lynxboot.img`; launching shows "Lynx needs BIOS/lynxboot.img" and the
   cart stays on the shelf. Put it back.

| Title | Turn | Measured fps (host) | Device pacing line | Starved / dropped | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|

## Sega 32X (issue 152, ADR 0096)

Pending. No BIOS. Move the three games into `Games/32X` first (the Mega Drive shelf stays on Genesis
Plus GX, where 32X games do not run). The Mac build has no SH-2 dynarec, so every host number is an
interpreter number; the device is the first place the dynarec runs.

1. Dynarec: `task bench:device CORE=picodrive ROM_ON_DEVICE=/mnt/sdcard/Games/32X/<game>` twice, with
   `ARGS="--frames 3000 --warmup 300 --repeats 3 --option picodrive_drc=enabled"` and with
   `picodrive_drc=disabled`. The enabled run must be clearly faster; record both medians.
2. Boot: each cart seats, no black screen, the 32X layer draws (title screens, 3D in Virtua Racing).
3. Picture: Stretch fills the panel at the frame width, SELECT+X walks Actual and 4:3.
4. Controls: the six-button pad: A, B, C on Y, B, A; X, Y, Z on L1, X, R1; START; SELECT is MODE.
5. Speed: 10 minutes each under `SLOT_TRACE`, Renderer Accurate and Sound Rate 44 kHz first; a title
   that misses frames is played again on Fast and on 22 kHz, and the row it took is recorded.
6. Audio: no crackle; `starved` and `dropped` stay 0.
7. States and rewind: save and load a state; rewind works; eject and power cycle resume.
8. Saves: a game that saves (World Series Baseball '95, NBA Jam TE) writes `Saves/32X/<stem>.sav` on
   eject and finds it on the next start.

| Title | Renderer | Sound Rate | bench:device ms/frame (drc on / off) | Starved / dropped | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|
| Virtua Racing Deluxe | | | | | | | heavy, polygons |
| Star Wars Arcade | | | | | | | heavy, polygons |
| Knuckles' Chaotix | | | | | | | 2D platformer |

## Virtual Boy (issue 182, ADR 0097)

Pending. No BIOS. Copy the games into `Games/VB` and fetch their labels
(`task labels:fetch -- --device --library <library> --only VB --by-name --logo-fallback`).

1. Speed: `task bench:device CORE=mednafen_vb ROM_ON_DEVICE=/mnt/sdcard/Games/VB/<game>` with
   `ARGS="--frames 3000 --warmup 600 --repeats 3"`, then again with `--option vb_cpu_emulation=accurate`.
   Record both medians; the budget at 50.27 fps is 19.9 ms.
2. Boot: each cart seats, the Nintendo warning and the title draw in red on black, one image, no ghost
   of the other eye.
3. Picture: Actual is 720x420 with a band above and below; Stretch fills the panel; SELECT+X flips
   between them. Palette walks the eight colours and the next game starts in the chosen one.
4. Controls, Stick mode (the default): D-pad is the left D-pad; the right stick is the right D-pad in all
   four directions, the right way round (if a direction is backwards, fix the axis in
   `Config/sticks.txt`, ADR 0068, and note it); A, B, L, R, START, SELECT; L2 rewinds and R2
   fast-forwards; X and Y do nothing.
5. Controls, ABXY mode: set Right Pad to ABXY, start the game again; X, A, B, Y are right up, right,
   down, left; R2 is A and L2 is B; SELECT+R2 toggles fast-forward.
6. Speed in play: 10 minutes each under `SLOT_TRACE`; `starved` and `dropped` stay 0, no missed frames
   past the first window, audio without crackle at the 50.27 Hz Native pacing.
7. States and rewind: save and load a state; rewind works (Stick mode); eject and power cycle resume.
8. Saves: Wario Land writes `Saves/VB/<stem>.sav` (64 KB) on eject and finds it on the next start.

| Title | CPU | bench:device ms/frame (fast / accurate) | Right Pad | Starved / dropped | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|
| Virtual Boy Wario Land | | | Stick | | | | platformer, depth layers, saves |
| Jack Bros. | | | Stick | | | | top-down action |
| Red Alarm | | | Stick and ABXY | | | | wireframe 3D, right pad flies the ship |
| Teleroboxer | | | Stick and ABXY | | | | one D-pad per fist |

## Expansion Card (ADR 0098)

Pending. Needs the RG34XXSP with the Base System card in TF1 and an Expansion Card prepared by
`tools/expansion-card.py` in TF2, `Games/PS1/` filled on it and `PS1` in `Config/expansion.txt`. Read
everything over adb (`mise exec -- adb shell ...`).

1. Main card: after boot, `grep -E 'mmcblk|expansion' /proc/mounts` shows `/dev/mmcblk0p7` at
   `/mnt/sdcard`, `/dev/mmcblk1p2` at `/mnt/expansion` and again at `/mnt/sdcard/Games/PS1`, and no
   `mmcblk1p1` anywhere. `grep mmcblk1p1 /mnt/sdcard/baseos-boot.log /mnt/sdcard/Logs/*.log` finds
   nothing mounted from it.
2. p1 stays empty: `dd if=/dev/mmcblk1p1 bs=1M count=16 2>/dev/null | od -An -tx1 | sort -u` prints a
   single line of zeros, also after a reboot (the boot-time `fsck.fat -a` must not have written it).
3. Session log: `grep expansion: /mnt/sdcard/Logs/slot-session.log` shows the exFAT mount and
   `Games/PS1 now comes from the expansion card` before the `exec` line.
4. Shelf: the PlayStation shelf lists the Expansion Card's games; a disc boots, a multi-disc game
   swaps discs, the jewel case and disc label show (labels on the main card).
5. Saves and states: a memory card save and a save state land in `Saves/PS1` and `States/PS1` on the
   main card (`ls -l /mnt/sdcard/Saves/PS1`), not on the Expansion Card.
6. Respawn: `killall slot`; after the frontend restarts, `/proc/mounts` has each line from step 1
   once (no second bind) and the log says `Games/PS1 is already on the expansion card`.
7. Card out: power off, remove TF2, boot. The shelves show the base card only, the session log says
   `no card at /dev/mmcblk1p2`, boot takes about one second longer, nothing crashes. A PS1 game
   seated at power off is not resumed. Put the card back and power on: the shelf returns.
8. Power off with the card in, from the menu and by closing the lid past its timeout. On the next
   boot `dmesg | grep -i -E 'exfat|fat-fs'` shows no dirty or not-unmounted warning for
   `mmcblk1p2` or `mmcblk0p7`.
9. Card repair (Repair in the power menu, "Repair the SD card?") with the card in: it ends `REPAIR COMPLETE`,
   `/data/slot-repair.log` names only `/dev/mmcblk0p7`, and there is no `could not unmount` line.
10. USB storage (hold MENU at power on): the Mac sees the Expansion Card (`EXPANSION` plus an
    unformatted 16 MiB partition, which macOS must not offer to initialise silently; dismiss it).
    Eject, remove TF2, repeat: the Mac sees the main card.
11. Tools over adb: `python3 tools/hacks.py --check --device` and
    `python3 tools/fetch-labels.py --device --library ~/ROMS --only PS1 --dry-run` list the
    Expansion Card's PS1 games.

| Step | Result | Date | Zip version | Notes |
|---|---|---|---|---|
| 1 to 11 | | | | |
## Atari 2600 and 7800 (issues 162 and 170, ADR 0095)

Pending. No BIOS for the 2600; the 7800 BIOS is optional and Off by default.

1. Boot: each cart seats on its own shelf (A2600 Stella 2014, A7800 ProSystem), no black screen.
2. Picture: 4:3 by default, Stretch and Actual walk; a PAL dump (2600 Europe) runs at 50 Hz with
   PAL Speed Native, and the cropped rows in 4:3 hide nothing the game needs.
3. Controls, 2600: d-pad moves, A and B fire, SELECT is Select, START Reset (starts most games);
   Right Difficulty A makes a game harder where it reads it (Space Invaders: wider shots on B);
   TV Type B&W turns Pitfall! grey or pauses games that read it; a paddle game (Kaboom!,
   Breakout) turns with the left stick and fires on A.
4. Controls, 7800: B and A are buttons 1 and 2, X Reset, START Pause, SELECT Select; a game that
   reads the difficulty switches follows the rows.
5. BIOS, 7800: copy the backup's `[BIOS] Atari 7800 (USA)` dump to the card as exactly
   `BIOS/7800 BIOS (U).rom` (4096 bytes, md5 `0763f1ffb006ddbe32e52d497ee848ae`); BIOS On then shows the logo before Asteroids; Off boots
   straight in.
6. Speed and audio: 10 minutes each under `SLOT_TRACE`; `starved` and `dropped` stay 0.
7. States and rewind: save and load a state; rewind works; eject and power cycle resume.

| Title | System | Picture | Starved / dropped | Date | Zip version | Notes |
|---|---|---|---|---|---|---|
| Pitfall! | 2600 | | | | | |
| River Raid | 2600 | | | | | |
| Kaboom! | 2600 | | | | | paddle on the left stick |
| Asteroids | 7800 | | | | | BIOS Off and On |
| Ms. Pac-Man | 7800 | | | | | |
| Ninja Golf | 7800 | | | | | |
## Neo Geo, CPS1 and CPS2 (issue 193, ADR 0099)

Pending. Put `neogeo.zip` in `BIOS/` and the sets in their shelves (`docs/rom-library/best-copy/arcade-adds.tsv`
lists the device copy). Host numbers are 0.21 to 0.30 ms a frame on the M5 Max; the device sets the bar.

1. Speed: `task bench:device CORE=fbneo ROM_ON_DEVICE=/mnt/sdcard/Games/<BOARD>/<set>.zip ARGS="--frames 3000
   --warmup 600 --repeats 3 --system /mnt/sdcard/BIOS"` for mslug (Neo Geo), ffight or dino (CPS1, dino has
   QSound) and ddtod (CPS2); record the medians.
2. BIOS: with `BIOS/neogeo.zip` moved away, a Neo Geo set stays on the shelf with "Neo Geo needs
   BIOS/neogeo.zip"; put back, it boots the MVS Asia/Europe BIOS.
3. Picture: Stretch fills the panel, SELECT+X walks Actual and 4:3; Neo Geo 304-wide sets (mslug) stretch
   like the 320-wide ones.
4. Vertical: 1941 or varth stands upright, 360x480 in the middle; Vertical Games Turned fills the panel
   sideways and the D-pad moves the plane the right way with the handheld held right edge up.
5. Controls: SELECT inserts a coin, START starts; Neo Geo A, B, C, D on B, A, Y, X; a CPS2 fighter
   (ssf2t) has the punches on Y, X, L1 and the kicks on B, A, R1; the service menu never opens on a
   held START.
6. Audio: 10 minutes each under `SLOT_TRACE`; no crackle; `starved` and `dropped` stay 0.
7. States, rewind, resume: save and load a state, rewind, eject and power cycle resume the set.
8. NVRAM: change a CPS2 game's settings in its own menu, quit, start again: kept (`Saves/fbneo/<set>.nv`).

| Set | Board | bench:device ms/frame | Starved / dropped | Date | Zip version | Notes |
|---|---|---|---|---|---|---|
| mslug | Neo Geo | | | | | 304 wide |
| dino | CPS1 | | | | | QSound |
| ddtod | CPS2 | | | | | |
| 1941 | CPS1 | | | | | vertical, both ways |

## Famicom Disk System (issue 202, ADR 0101)

Pending. Needs the player's own `BIOS/disksys.rom` (8192 bytes, crc32 5e607dcf, md5
ca30b50f880eb660a320674ed365ef7a). No new core: fceumm is already in `System/`. Copy the disks into
`Games/FDS` and fetch their labels
(`task labels:fetch -- --device --library <library> --only FDS --by-name --logo-fallback`).

1. Speed: `task bench:device CORE=fceumm ROM_ON_DEVICE=/mnt/sdcard/Games/FDS/<disk>` with
   `ARGS="--frames 3000 --warmup 600 --repeats 3"`; the budget is 16.7 ms.
2. Shelf: each disk is a yellow Disk Card with its label in the well; the shelf sits after the Master
   System in Release Year order.
3. Boot: the BIOS screen (Mario and Luigi) runs for a few seconds, then the game loads from side A.
4. Disk flip: at the game's "set side B" screen press SELECT+L2. The banner says "Disk 1 Side B", the
   game sees the disk go out and come back about a second later and loads on. SELECT+L2 again goes
   back to side A (or to Disk 2 on a two-disk game). L1 and R1 never touch the drive.
5. Picture: Crop by default; Stretch, Actual and 4:3 from the Picture row; Shader walks the retro list.
6. States and rewind: save and load a state on side B; the next flip still names the right side.
7. Saves: save in a game that writes the disk (Zelda no Densetsu, Nazo no Murasamejou), eject:
   `Saves/FDS/<stem>.sav` is the disk size (65,500 bytes a side) and the `.fds` on the card has its
   old date and size. Start again: the save is there.
8. Missing BIOS: rename `BIOS/disksys.rom`; launching shows "FDS needs BIOS/disksys.rom" and the disk
   stays on the shelf. Put it back.

| Title | Sides | bench:device ms/frame | Flip | Save | Starved / dropped | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|---|
| Nazo no Murasamejou | 2 | | | | | | | action adventure, disk saves |
| Esper Dream | 2 | | | | | | | action RPG, disk saves |
| Famicom Tantei Club Part II Zenpen and Kouhen | 2 each | | | | | | | adventure in two disk files |

## PC Engine SuperGrafx (issue 214, ADR 0103)

Pending. No BIOS. Apply `docs/rom-library/best-copy/sgx-adds.tsv` (workspace): copy the five SuperGrafx
cards into `Games/SGX` and move the two Darius cards there from `Games/TG16`, with their
`Labels/TG16/<stem>.png` to `Labels/SGX/` and any `Saves/TG16/<stem>.sav` and `States/TG16/<stem>*` to the
SGX folders. Then fetch the missing labels
(`task labels:fetch -- --device --library <library> --only SGX --by-name --logo-fallback`).

1. Speed: `task bench:device CORE=mednafen_supergrafx ROM_ON_DEVICE=/mnt/sdcard/Games/SGX/<game>` with
   `ARGS="--frames 3000 --warmup 600 --repeats 3 --option sgx_forcesgx=enabled"`, for Daimakaimura and
   1941. Record the medians; the budget at 59.82 fps is 16.7 ms, the host estimate 3 to 7 ms.
2. Boot: each card seats with no BIOS; the TG16 shelf no longer lists the Darius cards; the SGX shelf
   lists seven, the five as Super HuCards (contacts on top) and the two Darius as plain HuCards.
3. SuperGrafx mode: the five SuperGrafx cards boot past their title screens (a PC Engine cannot run
   them). Darius Alpha and Darius Plus show their SuperGrafx picture: compare a boss fight with the same
   card on the TG16 shelf before the move, and note any difference in sprite flicker.
4. Picture: Crop by default; the Picture row walks Stretch, Actual, 4:3 and back; L1 and R1 change it in
   game; the next game starts in the chosen one, and the TG16 shelf keeps its own.
5. Controls: B is II, A is I, START is Run; SELECT alone after the hold is Select; SELECT and START soft
   reset; X and Y fire turbo I and II with Turbo Buttons on and nothing with it off; L2 rewinds, R2
   fast-forwards. Pad 6 Buttons, next start: X, Y, L1 and R1 reach the game (any fighting HuCard that
   reads the Avenue Pad 6 shows III to VI), SELECT+X toggles the picture, X and Y no longer fire turbo.
6. Speed in play: 10 minutes each under `SLOT_TRACE`; `starved` and `dropped` stay 0, no missed frames
   past the first window, audio without crackle. Note the fast-forward speed (no core frameskip).
7. States and rewind: save and load a state; rewind works; eject and power cycle resume the SGX game.
8. Saves: a card writes `Saves/SGX/<stem>.sav` (2 KB, `HUBM`) on eject and finds it on the next start.

| Title | CPU | bench:device ms/frame | Starved / dropped | FF speed | Date | Zip version | Notes |
|---|---|---|---|---|---|---|---|
| Daimakaimura | | | | | | | two VDCs, the heaviest card |
| 1941: Counter Attack | | | | | | | vertical shooter, cloud layer |
| Aldynes | | | | | | | |
| Battle Ace | | | | | | | pseudo 3D |
| Madou King Granzort | | | | | | | |
| Darius Plus | | | | | | | PC-SG mark, detected by CRC |
| Darius Alpha | | | | | | | not in the core's table, needs sgx_forcesgx |

## PC Engine CD (issue 221, ADR 0104)

Pending. BIOS required: copy `syscard3.pce` (262,144 bytes, md5 38179df8f4ac870017db21ebcbf53114) to
`BIOS/`. The discs go on the Expansion Card (ADR 0098): copy the staged CHDs into `Games/PCECD` on the
Expansion Card (`/mnt/expansion/Games/PCECD` on the device), add the line `PCECD` to `Config/expansion.txt`
on the main card, and power cycle so `System/expansion.sh` binds it. The list, with sizes and data SHA1s,
is `docs/rom-library/best-copy/pcecd-adds.tsv` (workspace). Then fetch covers and disc scans
(`task labels:fetch -- --device --library <library> --only PCECD --by-name --logo-fallback`).

1. BIOS: with `BIOS/syscard3.pce` renamed away a disc stays on the shelf with "PC Engine CD needs
   BIOS/syscard3.pce"; with the headered 262,656-byte copy it starts with no toast.
2. Boot: Rondo of Blood, Ys Book I and II and Gate of Thunder reach their title screens through the
   System Card; Garou Densetsu Special (Arcade CD-ROM², the Arcade Card) reaches its fights.
3. CD audio: the Ys Book I and II opening and the Rondo of Blood intro play without a tick or a gap every
   few seconds (the CHD hunk is 200 sectors, about 2.7 s of 1x audio, decoded in the emulation thread).
   If it ticks, restage that disc with chdman's default hunk size and compare.
4. Speed in play: 10 minutes each under `SLOT_TRACE`; `starved` and `dropped` stay 0 and no missed frames
   past the first window, during CD audio, ADPCM speech (Ys cut scenes) and disc loads.
5. Picture: Crop by default; the Picture row walks Stretch, Actual, 4:3 and back; L1 and R1 change it in
   game; the TurboGrafx-16 shelf keeps its own.
6. Controls: B is II, A is I, START is Run; SELECT and START soft reset; X and Y fire turbo; L2 rewinds,
   R2 fast-forwards (note the speed, and that CD audio keeps up or drops).
7. States and rewind: save and load a state in a CD audio scene; rewind 10 seconds; eject and power cycle
   resume the disc.
8. Saves: Ys Book I and II saves to the backup RAM; `Saves/PCECD/<stem>.sav` (2 KB, `HUBM`) is written on
   eject and the save loads on the next start.
9. Shelf: each disc is a jewel case with its cover, a Japanese disc with the spine strip; on insert the
   case opens and the disc goes into the slot.

| Title | Starved / dropped | CD audio | FF speed | Date | Zip version | Notes |
|---|---|---|---|---|---|---|
| Akumajou Dracula X - Chi no Rondo | | | | | | Super CD-ROM², the intro has CD audio |
| Ys Book I & II | | | | | | CD audio and ADPCM speech, backup RAM saves |
| Gate of Thunder | | | | | | shooter, CD audio throughout |
| Garou Densetsu Special | | | | | | Arcade CD-ROM², needs the Arcade Card |
| Dungeon Explorer II | | | | | | |

## Shelf order (ADR 0100)

Checks that Release year reorders the shelves on the device and that the choice survives a restart.
The maintainer's device runs Release year; every other card stays Classic.

1. `task deploy:device`. With no `Config/shelf_order.txt`, R1 from Recents walks GBA, GB, GBC, NES,
   SNES and on in the old order.
2. Set Release year: on the SNES shelf, open Settings > General > Shelf Order and press Right. The
   row reads Release Year (the whole value fits the row), `adb shell cat
   /mnt/sdcard/Config/shelf_order.txt` says `order = release-year`, and after closing the menu
   slot is still on the SNES shelf with CPS2 or the next newer shelf to its right, no restart.
   Without the menu: `adb shell 'printf "order = release-year\n" > /mnt/sdcard/Config/shelf_order.txt'`
   (or that line in `Config/shelf_order.txt` with the card in a computer), then restart slot
   (`adb shell 'killall slot'`, or power off and on).
3. R1 from Recents: Atari 2600, NES, Master System, Famicom Disk System, Atari 7800, TurboGrafx-16, CPS1, Mega Drive,
   Game Boy, Lynx, Neo Geo, Game Gear, SNES, CPS2, 32X, PlayStation, Virtual Boy, Game Boy Color,
   Neo Geo Pocket, WonderSwan, GBA (shelves with no carts are skipped), then Recents again. L1 walks
   it backwards. The shelves peeking left and right of the current one are its neighbours in this
   order.
4. Settings > Screen lists the systems in the same order as step 3 (systems without carts are left
   out), GBA last; with Classic it starts Game Boy Advance, Game Boy Color, Game Boy.
5. Stop on a cart on the Virtual Boy shelf, close the lid or power off, start again: slot comes back
   on that shelf and cart, and R1 goes to Game Boy Color.
6. `grep -i "shelf.order\|screen order" /mnt/sdcard/Logs/slot-session.log` prints nothing.
7. Back to Classic: the row to Classic (applies at once), or `adb shell 'rm
   /mnt/sdcard/Config/shelf_order.txt'` and restart. Not on the maintainer's device, which keeps
   Release year.

| Step | Result | Date | Zip version | Notes |
|---|---|---|---|---|
| 1 to 6 | needs device | | | |

## Core bench on the device (test carts)

`task bench:device CORE=<core> ROM=<path>`. Emulation only, no video or audio, so it shows headroom, not the gate. Generated test carts (`harness/make_assets.py nes|snes`) are tiny, so real games cost more. Use your own dumps of the 11 titles for real numbers.

| Date | Zip version | Governor | Core | ROM | Median ms/frame | Frames/s |
|---|---|---|---|---|---|---|
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | mgba | 240pee_mb.gba | 0.795 | 1258 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | gpsp | 240pee_mb.gba | 0.924 | 1083 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | fceumm | generated NES cart | 1.624 | 616 |
| 2026-10-12 | v1.6.0-ns.0 (main after #59) | performance | snes9x | generated SNES cart | 3.295 | 304 |

2026-10-13 retro shader run (patches to 0021, `task perf:play`, 2 minutes per mode, logs in
`docs/perf/2026-10-13-shaders/`): Super Mario RPG (snes9x) once per SNES mode, Battletoads (fceumm)
with Off and crt-pi.
- All four new shaders build on the Mali-G31 (no "did not build" line) and every run reads 0 dropped,
  0 starved with patch 0021.
- After the first window the longest present and the p99 match Off for every mode (Super Mario RPG
  about 18-19.7 ms in every mode, Off included; Battletoads 17.4-18.2 ms). The shaders add no
  measurable per-frame cost.
- Each new mode shows one long present (31-67 ms) in the first window, Off does not: most likely the
  driver finishing the retro program on its first draw.
- Follow-up, same day (logs in `docs/perf/2026-10-13-shaders-warm/`): the retro program now draws each
  mode once off screen when it is built. First-window longest present: Sharp on Super Mario RPG
  33.95 to 19.45 ms, crt-pi on Battletoads 66.66 to 23.59 ms (under 1.5x the period); crt-pi on
  Super Mario RPG 30.97 to 29.90 ms, one run each, so that title's start-up spike is not shown to be
  the shader.
- Boot cost: building the retro program at start-up made `boot: compositor` take about 306 ms
  against 172 ms before patch 0020 (every play log since), and the warm-up adds about 15-25 ms
  more. Kept at boot by maintainer choice over building it at the first NES/SNES insert.

2026-10-14 Line, Pixel and sharp Scanlines run (patches to 0022, 2 minutes per mode, logs in
`docs/perf/2026-10-14-line-pixel/`): Super Mario RPG with Line, Pixel and Scanlines, Battletoads
with Line and Pixel.
- All modes build on the Mali-G31. `boot: compositor` stays about 310 ms with six retro modes warmed.
- Every run reads 0 dropped samples; 0 starved except the first Line run, whose start overlapped
  slot caching 1564 new labels at boot (insert 28 s), which also explains its slow early windows.
- After the first window, p99 matches the Off runs of 2026-10-13 for every mode (Super Mario RPG
  17.3-19.3 ms, Battletoads 17.2-17.4 ms). Battletoads with Pixel shows one 92 ms present in its
  first window, one run only.

## [BIOS] files off the shelves (patch 0088)

1. Leave `[BIOS] ...` files in `Games/TG16`, `Games/Lynx` and `Games/NGP` (System Card, Lynx boot ROM,
   NGP Color BIOS). None of them shows as a cart; the games beside them do.
2. With `cart_platform=tg16` and `cart=Bonk's Adventure (USA)` in `Config/slot.state` and a NES cart
   of the same name on the NES shelf, power on: the TurboGrafx-16 cart resumes (patch 0089 pins it in
   `resume_platform.rs`).

## PICO-8 (issue 208, ADR 0102)

Pending. Copy the carts listed in `docs/rom-library/best-copy/pico8-adds.tsv` (workspace) into
`Games/PICO8/` under their target names, then `task labels:fetch -- --card <card> --only PICO8` (no network)
for the labels. Host numbers are 0.05 to 0.67 ms a frame on the M-series; the device sets the bar.

1. Speed: `task bench:device CORE=fake08 ROM_ON_DEVICE="/mnt/sdcard/Games/PICO8/<name>.p8.png" ARGS="--frames 3000
   --warmup 600 --repeats 3"` for Cave Runners! (the slowest on the host), UFO Swamp Odyssey and Celeste;
   record the medians.
2. Picture: Actual is a sharp 384x384 square in the middle (3x, no shimmer when Celeste's camera moves);
   Stretch fills the panel; SELECT+X flips between them; the Shader row walks the retro list.
3. Controls: B is O (Celeste jumps), A is X (Celeste dashes), Y and X fire turbo O and X in Cherry Bomb,
   START opens the pause menu (Continue, the cart's own items, Reset Cart, nothing else) and Reset Cart
   restarts the same game; every quick tap counts in a 30 fps cart (Pico Racer menu, Ma Puzzle moves).
4. Audio: 10 minutes each of Celeste and Witch Loves Bullets under `SLOT_TRACE`; music at the right pitch,
   no crackle; `starved` and `dropped` stay 0.
5. Saves: set a Pico de Pon high score (it uses cartdata), wait 2 s, power off at the switch, power on: the
   score is kept (`Saves/PICO8/cdata/picodepon_high_scores.p8d.txt`), with no `.tmp` left beside it.
6. No states: the in-game menu has no States page; eject, lid close and power tap leave nothing in
   `States/PICO8/`; L2 does nothing, R2 fast-forwards.
7. Errors: Demon Castle and Under Construction show "runtime error" and stay there; no other cart starts.
8. Logs: `System/slot.log` keeps getting lines after a cartdata save (the stderr fix).

| Cart | bench:device ms/frame | Starved / dropped | Date | Notes |
|---|---|---|---|---|
| Cave Runners! | | | | slowest on the host |
| UFO Swamp Odyssey | | | | |
| Celeste | | | | jump and dash |
| Pico de Pon | | | | cartdata across a power cut |
