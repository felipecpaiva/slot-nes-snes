# pvaibhav/slot vs slot-nes-snes: what is worth adopting

Read-only review, 2026-10-18. Fork cloned to `~/.cache/forks/pvaibhav` (all branches), with
`upstream` (BrandonKowalski/slot) and `bph` (bphenriques/slot) as extra remotes. Compared against
slot-nes-snes `main` at da67dd2 (patches 0001 to 0041, ADRs 0001 to 0069, docs/PLAN.md,
docs/PERFORMANCE.md, docs/DEVICE-GATE.md) and the patched tree `~/.cache/pal/slot-nes-snes/work/slot` (patches through 0041 plus the in-progress
issue 66 commit cadd65c).

Base: branch `pvaibhav-improvements` at 6411a22 (tag `v1.7.0-pvaibhav.1`, 2026-10-15) is v1.7.0 plus 36
commits (33 by Prashant Vaibhav, 3 machine-authored). `main` (a54157c, 2026-10-07) has 0 commits
that are not in upstream `main` or v1.7.0: a stale mirror with no fork work. Diff against v1.7.0: 191 files, +37,591 / -813, most of it RetroAchievements, Wi-Fi and the
`tools/refresh` measurement data. The input-lag and performance work is one commit,
[e8ff757](https://github.com/pvaibhav/slot/commit/e8ff757) (2026-10-15), plus a few small ones. The
fork has opened **no PRs** upstream.

Upstream moved since v1.7.0 (24 commits on `main`, unreleased, CHANGELOG heading 1.8.0). Four of them
overlap this fork and change verdicts below:

- [b0fe199](https://github.com/BrandonKowalski/slot/commit/b0fe199) **removes run-ahead entirely**
  (#104: it scrambled 128 KB flash saves, e.g. Super Mario Advance 4). It cuts 117 lines from `emu.rs`.
- [656ce7e](https://github.com/BrandonKowalski/slot/commit/656ce7e) caches mGBA's state size (the fork's
  826a4e9).
- [0ba5370](https://github.com/BrandonKowalski/slot/commit/0ba5370) powers off on a held POWER (the
  fork's 90e7d9c).
- [5dc5b83](https://github.com/BrandonKowalski/slot/commit/5dc5b83) replaces the linear resampler with a
  48 kHz windowed sinc, the same block e8ff757 rewrites.

So any port of e8ff757 has to be planned against upstream `main`, not v1.7.0.

Side note for our own docs: the top recommendations in `docs/research/fork-savethefails-snes.md` (SNES
run-ahead, the budget guard, the audio comparison) build on upstream run-ahead, which 1.8.0 deletes.
Those items need a re-think before anyone starts them (this review does not edit that file).

Link prefix: `https://github.com/pvaibhav/slot/commit/<sha>`; bphenriques:
`https://github.com/bphenriques/slot/commit/<sha>`.

Verdict key: **adopt / adapt / already have / ours better / skip**. V/E/R = value (H/M/L), effort (S/M/L),
risk (H/M/L).

## 1. Frame pacing, 120 Hz and input lag (the interesting part)

How upstream v1.7.0 (and so ours) paces, from `work/slot/crates/slot/src/device_app.rs` and `emu.rs`:
the frontend `Pacer` learns the swap period (starts at 16.76 ms, EMA of blocked swaps) and the worst
frontend work of the last 32 frames. Each loop it sleeps until `last_swap + period - (work + 1.5 ms)`,
then reads input, ticks the emulator (the worker is **locked** to that tick and runs one game frame per
present), renders and swaps. That is a late latch: input is read as close to the vsync as the measured
work allows. Game speed is therefore the **panel** rate (about 59.58 Hz on the RG SP family). Audio is
kept in sync by scaling the resampler with the measured present rate (`TickRate`, 300-tick windows) plus
DRC. Result: perfectly even cadence, but every core runs at 59.58 fps. GBA is 0.25% slow, NES and SNES
(60.0988) are 0.86% slow, and PAL (50) is 19% fast, which is our issue 66. Our patch 0006 `av_rate.rs`
only stretches the resampler for a `SET_SYSTEM_AV_INFO` change; it does not change pacing.

| Change | Commits | What it does (technically) | Ours | Better/worse | ADR conflict | Upstream? | Verdict, V/E/R |
|---|---|---|---|---|---|---|---|
| **(a) Native-rate pacing** | [e8ff757](https://github.com/pvaibhav/slot/commit/e8ff757) (`pacing.rs` new, `emu.rs` 314 lines changed, `device_app.rs`, `frontend.rs`, `session.rs`) | Replaces the late-latch `Pacer` with `FramePacer`: absolute deadlines every `1/av.fps` (`native_period`, falls back to 16.667 ms on bad fps). Each loop sleeps to the deadline, reads input, runs `due` frames (1, or 2 if behind by one or two periods; a debt above 2 periods is dropped and counted), renders, swaps. The swap no longer sets game speed. Worker: `tick()` loses its present argument, `TickRate` and the measured `scale` are deleted, the resampler runs at the core's real rate (`Resampler::new(av.sample_rate, device_hz)`) with DRC only; fast-forward uses a duration ratio. A late frame becomes a "fallback" frame the worker runs by itself, and the pacer rebases so the time is not committed twice. Mode changes (`set_driven`, `set_speed`, `set_rewinding`, drop) now wake the worker through the condvar instead of letting it finish a sleep (`wait_until` replaces `thread::sleep`). `MIN_FRAME` (12 ms floor) is removed | Not present. Our pacing is upstream's lock. Issue 66 asked for PAL pacing; it is now being done another way (row a1) | Right speed for every core, and it retires our `av_rate` stretch. **But at 60 Hz it trades even cadence for speed**: one present carries two game frames every 1/(fps - 59.58) s. That is every ~6.9 s for GBA, **every ~1.9 s for NES and SNES**, every ~3 s for MD, SMS, GG and PS1, and a 6:5 cadence for PAL. On NES/SNES scrolling that is visible judder. The fork only tested 59.7275 fps cores. It reads `av.fps` once per session; our 0006 handles a mid-game `SET_SYSTEM_AV_INFO`, so `native_ns` must be updated there too. It also drops upstream's late latch (see the latency notes below) | Changes `tick(present)` to `tick()` and `step_emulator(present, timeout)` to `step_emulator(timeout)`. Upstream tests call `emu.tick(PANEL)` (`tests/emu.rs:1016,1020,1040,1096`, `tests/runahead.rs:152,479`) and the fork edits both files, which breaks **PLAN success criterion 1** (zero hunks in upstream test code). It deletes the `Pacer` that **0015-frame-trace** hooks into (5 touch points in `device_app.rs`) and rewrites the resampler lines that **0006** and **0018-audio-reopen** touch. DEVICE-GATE's present thresholds (p99 within 1.1x the 16.78 ms period, 0 presents above 1.5x) would need re-basing on the game period. Issue 66 says "GBA, GB and GBC pacing unchanged" | Generic. Upstream-first under ADR 0047 if it goes anywhere. Brandon deliberately chose the lock in 1.7.0, so ask before sending. Contact Vaibhav first: it is his code, and he has not proposed it | **upstream-first only** (issue 66 is covered by cadd65c). V: M alone (correct NTSC speed at the cost of 60 Hz judder); H together with (b). E: L (5 files, conflicts with 0006/0015/0018, against upstream main). R: M (judder at 60 Hz, audio path rewrite) |
| **(a1) Native pacing, PAL-only variant** | idea from e8ff757 | Keep the lock (and upstream's signatures and tests) for cores near the panel rate, pace only PAL-rate cores at their own fps | **Already in progress**: issue 66 is implemented in `~/.cache/pal/slot-nes-snes/work/slot` commit cadd65c ("pal-pacing", 2026-10-18, not yet exported as a patch). It keeps the lock and `tick(present)`, runs `owed_frames` (0 or 1 frames a tick at 50 fps, a fractional carry), uses a 2 fps window around 60, resamples from the core's own rate, and adds a per-system PAL Speed choice. Credits omega-zero, cloudwithax/unslot and nelynes/slotPlus | Ours is better for our constraints: no upstream test hunks, the late latch stays, no 0015 conflict, GBA untouched. One idea worth checking from `FramePacer.due`: it caps catch-up at 2 frames and drops debt above 2 periods. Check that `owed_frames` cannot run a burst of frames after a long tick (a stall or a resume) | none | Ours | **already have (in progress)**. Only borrow the debt cap if a test shows a burst. V: L. E: S. R: L |
| **(b) 120 Hz panel mode** | e8ff757 (`slot-power/src/refresh.rs`, `device.rs`, `app.rs::set_power`, `slot_state.rs` `high_refresh` default true) | Doubles the LCD pixel clock through Allwinner's `sunxi_dump` sysfs: writes divider `0x06511044 <- 0xf000000a` then PLL `0x03001040 <- 0x88002b03` (60 Hz restore is PLL `0x88001703` then divider `0xf000000b`). Reads both back and rolls back to 60 Hz on any failure. Only if the BaseOS target is `rgsp`/`rg34xxsp` with DT `lcd_driver_name` = `rg34xxsp_v1`, or `rg34xx` with `fog_fj035fhd05_v1`, and `lcd_x/y/ht/vt/dclk` = 720/480/820/536/26. Applied at start and before the backlight on wake. On by default, no menu row. The frontend still renders about 60 times a second (one loop per native deadline); only the vsync wait shrinks | None | Their own data: 32.8 ms median against 41.3 ms at their 60 Hz, game fps unchanged, CPU +1.6 to +4.3 points. At 120.13 Hz the native cadence is almost even: GBA holds one frame 3 vsyncs instead of 2 every ~1.5 s (8.3 ms), NES/SNES skip one vsync every ~15 s, PAL 50 runs 2-3-2-3 like halved pulldown. **The fork never ran it without (a)**: under upstream's lock the game follows the frontend loop, which `MIN_FRAME` (12 ms) caps at about 83 Hz and whose `Pacer` only learns periods between 12 and 22 ms. At 120 Hz that most likely lands on a 2-vsync cadence (about 60.07 fps, so GBA 0.6% fast) or an uneven mix of 1 and 2 vsyncs. Untested either way. ROCKNIX lists `rg34xx-sp-v2-panel` as 60 Hz only, so a v2 RG34XXSP gets nothing (the probe fails closed) | Needs (a), so it inherits (a)'s criterion 1 conflict. Writing PLL registers from the frontend is new hardware policy, an ADR on its own. ADR 0021 (reference device) is fine if our unit is a v1 panel | Generic for H700. Upstream-first only; we should not carry PLL writes alone | **adapt, upstream-first, after the device A/B**. V: H if the A/B confirms it. E: M on top of (a). R: M (hardware writes, wake path, panel variants) |
| Response trace `SLOT_TRACE_RESPONSE` | e8ff757 (`latency.rs` `ResponseTrace`, `frontend.rs:528` `latency::picture`) | Writes `monotonic_ns,r,g,b` of the first pixel of the image selected for composition, after each swap where it changed. With the response ROM and probe it gives evdev injection to swap of the first changed image | Our `latency.rs` lines time read to swap (upstream's), and `scripts/auto-play.sh` injects input but has no image-side stamp | Theirs measures end to end from injection; ours misses the poll wait before the read | none if kept out of the shipped patch set (measurement-only build) | Could go upstream as a trace, low priority | **adopt as a throwaway measurement hook** for the A/B below, not as a patch. V: M. E: S. R: L |
| `emu_frame` stamp moved to where a frame really runs | e8ff757 (`emu.rs`) | Calls `latency::emu_frame(input)` inside each run branch (normal, run-ahead, linked) instead of once per loop, so a loop that runs no frame no longer closes a latency sample | Upstream behaviour; our parser already drops the volume-key artefact | Small trace accuracy fix | none (trace only, but it is upstream code: criterion 1 counts only test code, fine) | Generic: a one-line upstream PR | **adopt via upstream PR only** if we touch latency tracing anyway. V: L. E: S. R: L |
| Measurement harness `tools/refresh/` | e8ff757 (`profile.py`, `probe.rs`, `response.s`, `make_response_rom.py`, `summarize.py`) | `probe` reads mGBA's or gpSP's committed frame counter from `/proc/PID/mem` (ELF symbol lookup), CPU ticks, shared-policy MHz, SoC temp and LCD IRQ 293 every 100 ms. `profile.py` runs each mode in a fresh process on a temp card root (saves untouched), rotates mode order, fails a run whose IRQ slope is off by more than 3 Hz. The response ROM shows the previous frame's A state as red/green | `scripts/bench-device.sh` (core only), `scripts/auto-play.sh` (pace, frametime, starve, latency lines) | Theirs is the better instrument for game speed (real committed frames, not presents) and end-to-end latency. Ours covers NES/SNES/Sega/PS1, which theirs does not (GBA/GB/GBC scenes hardcoded) | none (tooling) | no | **adopt as a tool to run, not to vendor**. Use it from the fork clone for the A/B. V: M. E: S. R: L |
| Run-ahead kept as a setting | e8ff757 keeps 1.7.0's mGBA run-ahead, off by default | One speculative frame, serialize and restore | Inherited from 1.7.0, mGBA GBA only; ADR 0066 keeps it off on PS1 | Upstream 1.8.0 deletes run-ahead (b0fe199, flash save corruption). The fork's own data: +27 CPU points, governor pinned near 1.5 GHz, +4 to 5 C, game fps down to 59.3, audio starvation in 3 of 5 runs, worse p95 than 120 Hz | none | Upstream removed it | **skip** (follow upstream 1.8.0 on the next rebase) |

## 2. Governor, CPU and small performance items

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? | Verdict, V/E/R |
|---|---|---|---|---|---|---|---|
| schedutil governor at start | [ad7ce10](https://github.com/pvaibhav/slot/commit/ad7ce10), [320ac44](https://github.com/pvaibhav/slot/commit/320ac44) | `launch_frontend.sh` writes `schedutil` into every `cpufreq/policy*/scaling_governor` | We run on BaseOS's `performance` (every perf and gate row says so) | Battery gain, no published battery number (their CPU MHz is a proxy only). Risk for us: SA-1 snes9x is 10.3 ms a frame and PS1 pcsx is heavier still. A ramping governor can miss periods where `performance` does not. Their 120 Hz matrix ran under schedutil with GBA only | **DEVICE-GATE rule**: no governor change without a before and after row; PLAN risk row names `interactive`, not schedutil | Generic, upstream could take it, but it is policy | **skip for now; measure as build D** (plan below). Adopt only if SA-1, Super FX and PS1 heavy titles stay at 0 missed periods and 0 starved. V: M (battery). E: S. R: M |
| Recycle audio buffers | [777730c](https://github.com/pvaibhav/slot/commit/777730c) | New `RetroCore::recycle_audio(buf)`; the worker hands the `take_audio` Vec back so `Host.audio` stops allocating every frame batch | Not present | Saves one Vec allocation per present. Unmeasured; jemalloc/glibc likely make it noise against 5 to 10 ms frames | Adds a trait method in `slot-retro` (upstream code, not tests). Touches emu.rs lines near 0018 | Generic: upstream PR if anyone wants it | **skip** unless a profile shows allocator time. V: L. E: S. R: L |
| RGB565 widen in one u32 store | 777730c | Upstream `video_refresh` RGB565 branch writes one LE word instead of four bytes | Our NES, SNES, Sega and PS1 frames go through `slot-retro/src/canvas.rs` (`bgrx_from_rgb565` + `copy_from_slice`), not that branch. The branch is GBA (and GB/GBC), which we keep byte-identical | No gain for our systems unless re-done in `canvas.rs`. PS1 convert is 0.06 to 0.09 ms on host and the spike ceiling was 0.80 ms on device, well inside the 2 ms budget (PERFORMANCE.md) | Changing the GBA path is upstream's code; output is identical, but it is churn | Generic, upstream PR if anyone cares | **skip**. V: L. E: S. R: L |
| Frame handoff counters | 777730c, removed again in [1ea92af](https://github.com/pvaibhav/slot/commit/1ea92af) | `emulated/published/shown/overwritten/repeated` trace counters | Our 0015 frame-trace gives present p50/p99/max | Gone from the fork's tip | n/a | n/a | **skip** (not in the fork any more) |
| State size cache | [826a4e9](https://github.com/pvaibhav/slot/commit/826a4e9) | Keeps `retro_serialize_size` until load, option or link change (mGBA's costs nearly a full serialize) | Not in v1.7.0; **upstream main 656ce7e does the same** | Same job | none | Already upstream | **already have on the next rebase** (upstream 1.8.0). It helps our rewind cost too, since the cache sits in `LibretroCore` for every core |
| FF recovery test | [cab01b1](https://github.com/pvaibhav/slot/commit/cab01b1) | Test only: fast-forward recovers after one stalled skipped frame | Upstream's cost model already recovers (their message says so) | Test only | Adding it would be a hunk in upstream test code (criterion 1) | Could be an upstream test PR | **skip** |

## 3. Picture

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? | Verdict, V/E/R |
|---|---|---|---|---|---|---|---|
| Panel calibration LUT | [c00669f](https://github.com/pvaibhav/slot/commit/c00669f), [cf22ead](https://github.com/pvaibhav/slot/commit/cf22ead) | `slot-gfx/src/displaycal.rs`: picks an embedded 3x1D 256-entry `.cube` by BaseOS target (`rgsp`, `rg34xxsp`), loads it into the display engine with `/dev/disp` ioctls `0x10b` (SET_GAMMA_TABLE) and `0x10c` (ENABLE_GAMMA). Zero per-frame cost; applies to UI and games | None | It is not an identity table despite the `rg34xxsp.cube` header "Checkpoint: Uncalibrated": white goes to R 1.00, G 0.918, B 0.922 and mid-grey is lifted (max deviation 26 of 255 steps). `rgsp.cube` is Vaibhav's own unit (33 steps, bluer white pulled further). Panels vary per unit, so a LUT measured on someone else's RG34XXSP may be wrong for ours. Changes nothing a frame hash sees (applied after scan-out composition) | PLAN out of scope: "colour correction on NES/SNES" (that line means the GBA-LCD style core option, but a panel LUT is colour work too). Also changes GBA's look on the device | Generic, H700-wide: upstream's call | **skip** (out of scope). If anyone revives it, it is an upstream PR, and see Licence for provenance. V: M. E: S. R: M |
| GBA colour correction and ghosting defaults | [818901a](https://github.com/pvaibhav/slot/commit/818901a), [484bf46](https://github.com/pvaibhav/slot/commit/484bf46) | Turned colour correction and LCD ghosting on, then went back to upstream's settings | Upstream defaults | Net zero after 484bf46 | none | n/a | **skip** |
| mGBA "mix" frame blending | [cb4fc31](https://github.com/pvaibhav/slot/commit/cb4fc31) | Sets `mgba_interframe_blending=mix` for every mGBA game (v1.7.0 leaves it at the core default OFF). The commit says "cheaper than the accurate filter", but against upstream it **adds** blending | Upstream (OFF) | Changes GBA, GB and GBC output, which breaks criterion 1 (byte-identical GBA) | Criterion 1 | Upstream's call | **skip** |

## 4. Power and UI

| Change | Commits | What it does | Ours | Better/worse | ADR conflict | Upstream? | Verdict, V/E/R |
|---|---|---|---|---|---|---|---|
| Held POWER shuts down | [90e7d9c](https://github.com/pvaibhav/slot/commit/90e7d9c) | Removes the power menu; a hold powers off | v1.7.0 power menu | **Upstream main 0ba5370** does the same and moves Restart to About on X | none | Already upstream | **already have on the next rebase** |
| About sticker credit | [abe4dcf](https://github.com/pvaibhav/slot/commit/abe4dcf) | "Seasoned in Berlin" on the About sticker | n/a | n/a | n/a | n/a | **skip** |

## 5. Out of scope by PLAN.md non-goals (one row each)

| Change | Commits | What it does | Verdict and reason |
|---|---|---|---|
| RetroAchievements (background, offline cache, sync icon, rich presence) | [d6f13c7](https://github.com/pvaibhav/slot/commit/d6f13c7), [7b5a143](https://github.com/pvaibhav/slot/commit/7b5a143), [dcf2a5b](https://github.com/pvaibhav/slot/commit/dcf2a5b), [42f22dd](https://github.com/pvaibhav/slot/commit/42f22dd), [b871b6a](https://github.com/pvaibhav/slot/commit/b871b6a), [0387313](https://github.com/pvaibhav/slot/commit/0387313) | rcheevos (MIT) through a `slot-services` daemon, `SET_MEMORY_MAPS` in `libretro.rs`, GBA memory only | **skip**: RetroArch-breadth feature (PLAN "Not for": people who want RetroArch breadth); GBA only, and it touches `libretro.rs`, which our 0006 patches |
| Home Wi-Fi and time sync | [92f812e](https://github.com/pvaibhav/slot/commit/92f812e), [a388c4c](https://github.com/pvaibhav/slot/commit/a388c4c), [3487939](https://github.com/pvaibhav/slot/commit/3487939) | A home network profile, NTP, a quick-menu row | **skip**: networking is not in our scope; ADRs 0008/0023/0043 keep quick-menu rows to the ones we chose |
| Link over the home network | [8700a56](https://github.com/pvaibhav/slot/commit/8700a56), [b977d34](https://github.com/pvaibhav/slot/commit/b977d34) | GBA link via mDNS on the LAN | **skip**: GBA link is upstream's feature; we add no link work |
| On-device label fetch (LaunchBox GamesDB scrape) | [12f500a](https://github.com/pvaibhav/slot/commit/12f500a), [375b61a](https://github.com/pvaibhav/slot/commit/375b61a) | Background HTTP scraping of `gamesdb.launchbox-app.com` on the device | **skip, ours better**: our host-side `tools/fetch-labels.py` (Brandon's art set, then ScreenScraper, sibling and name matching, all 9 systems) needs no Wi-Fi on the device. Scraping LaunchBox's site has terms-of-use risk |
| Release notes, README, funding, version scheme | [2a04b6a](https://github.com/pvaibhav/slot/commit/2a04b6a), [bcb49bc](https://github.com/pvaibhav/slot/commit/bcb49bc), [4ac92f7](https://github.com/pvaibhav/slot/commit/4ac92f7), [39e8c02](https://github.com/pvaibhav/slot/commit/39e8c02), [98843c4](https://github.com/pvaibhav/slot/commit/98843c4), [5fdc339](https://github.com/pvaibhav/slot/commit/5fdc339), [99cdc29](https://github.com/pvaibhav/slot/commit/99cdc29) | Fork housekeeping | **skip** |

## 6. bphenriques/slot (only what pvaibhav lacks)

bphenriques' `pvaibhav-improvements` (876c104, 2026-10-17) is pvaibhav's tag plus 5 commits, so it is now
**ahead** of pvaibhav, not an older copy as `slot-forks.md` says. Nothing in it is about input lag or
performance.

| Change | Commits | What it does | Verdict and reason |
|---|---|---|---|
| Music player through plorpOS's Muse | [37e0e48](https://github.com/bphenriques/slot/commit/37e0e48), [ee182c2](https://github.com/bphenriques/slot/commit/ee182c2), [64ad018](https://github.com/bphenriques/slot/commit/64ad018), [876c104](https://github.com/bphenriques/slot/commit/876c104) | Bundles plorpOS's Muse daemon and FFmpeg, a `slot-music` crate, and a SoundTouch-based `slot-player` experiment | **skip**: not an emulator feature; adds FFmpeg and SoundTouch (LGPL) to the zip |
| ROMs one folder down | [1c83280](https://github.com/bphenriques/slot/commit/1c83280) | `slot_store::rom_files` also lists one subfolder level (hidden folders skipped); labels and saves still key on the name | **skip**: generic shelf behaviour, upstream's call; `scripts/push-roms.py` already lays the card out flat. V: L |

## 7. Published measurements and how to read them

The fork publishes real data (`tools/refresh/RESULTS.md`, `results/rgsp-2026-10-15/`), on an **RG SP**
(target `rgsp`, panel `rg34xxsp_v1`, BaseOS 1.4.0), governor **schedutil** (480 to 1,512 MHz), GBA/GB/GBC
only:

- Game speed (committed core frames): 59.705 to 59.741 fps at both 60 and 120 Hz; LCD IRQ 59.50 to 59.58
  Hz at 60 Hz and 120.08 to 120.17 Hz at 120 Hz. One live IRQ check on an RG34XXSP: 120.14 Hz
  (`rg34xxsp-2026-10-15/probe.json`, NextUI running, temporary until reboot).
- CPU: +1.6 to +4.3 percentage points at 120 Hz; MHz and temperature differences inside the noise.
- Response, 120 trials per mode: 60 Hz median 41.26 ms (p95 48.99), 120 Hz 32.76 ms (p95 40.64),
  60 Hz with run-ahead 30.73 ms (p95 46.42).

Caveats that matter for us:

1. **All three latency modes ran the same fork binary** (one `binary_sha256`; `profile.py` only flips
   `high_refresh` and `runahead`). Their "60 Hz" is their new native pacer at 60 Hz, **not** upstream's
   late-latch `Pacer`. So the 8.5 ms is 120 Hz against their own 60 Hz, never against v1.7.0. The native
   pacer reads input at a deadline whose phase drifts against vsync, so its input to vsync wait ranges
   over a whole period. Upstream reads input about `work + 1.5 ms` before the expected vsync. It is
   plausible that upstream at 60 Hz is already well below their 41 ms, and that 120 Hz with native pacing
   only wins back what native pacing lost. Only an A/B can tell.
2. Their figure runs from evdev injection to the first changed image's swap, on a ROM with a deliberate
   one-frame delay. Our auto-play figure (15 to 23 ms median, PERFORMANCE.md) runs from upstream's read
   stamp to swap. **Never compare the two sets of numbers.**
3. Different governor (schedutil against our performance), different device (RG SP against RG34XXSP),
   and no NES, SNES, Sega or PS1 cases.

## 8. A/B plan on our RG34XXSP (you run it; nothing here touches adb)

### Step 0: does our panel qualify at all (read-only, 2 minutes)

```sh
adb shell 'echo $BASEOS_TARGET; grep BASEOS_TARGET /etc/baseos-release'
adb shell 'n=/sys/firmware/devicetree/base$(tr -d "\000" < /sys/firmware/devicetree/base/aliases/lcd0); echo $n; tr -d "\000" < $n/lcd_driver_name; echo; for f in lcd_x lcd_y lcd_ht lcd_vt lcd_dclk_freq; do printf "%s " $f; od -An -tu1 $n/$f; done'
adb shell 'ls -l /sys/class/sunxi_dump/; cat /sys/class/disp/disp/attr/sys | grep -i fps'
adb shell 'a=$(grep "^ *293:" /proc/interrupts); sleep 10; b=$(grep "^ *293:" /proc/interrupts); echo "$a"; echo "$b"'
```

(This resolves the node the way `refresh.rs` does, through `aliases/lcd0`; the fork's `profile.py` hardcodes
`/proc/device-tree/soc@03000000/lcd0@01c0c000`.) Pass: target `rg34xxsp`, driver `rg34xxsp_v1`, and the
big-endian bytes `0 0 2 208` (720), `0 0 1 224` (480), `0 0 3 52` (820), `0 0 2 24` (536), `0 0 0 26` (26), `sunxi_dump/dump` and
`write` present and writable, IRQ 293 slope about 59.6 Hz. If the driver is anything else (for example a
v2 panel), **stop the 120 Hz track**; only issue 66 (its own track) remains.

### Builds (all GBA-comparable; same card, same cores in `System/`)

| Build | What | How |
|---|---|---|
| U | Unpatched upstream (v1.7.0, or `main` if the PR targets it) plus the same throwaway response hook. The control any upstream PR must quote: A has 41 patches, U has none | `task upstream:build`, apply the hook, upstream's own `task dist:device` in `rust:1-bullseye`, push `System/slot` only, GBA carts only |
| A | Our current dist (upstream lock + late latch, 60 Hz) plus the fork's `SLOT_TRACE_RESPONSE` hook as a **throwaway local diff** (`latency.rs` `ResponseTrace` + the one `latency::picture(&frame)` call in `frontend.rs`), never exported as a patch | `task build`, apply the diff in `work/slot`, `task dist:device`, push `System/slot` only |
| F60 | Fork tag `v1.7.0-pvaibhav.1`, `high_refresh=0` (native pacer, 60 Hz) | In `~/.cache/forks/pvaibhav`, run upstream's own `task dist:device` the same way `scripts/dist-device.sh` does (inside `rust:1-bullseye`), or per `tools/refresh/README.md` on aarch64 Linux. Swap only `System/slot` (back up ours as `System/slot.ours`). Keep **our** `launch_frontend.sh` so the governor stays `performance` |
| F120 | Same binary, `high_refresh=1` | Settings toggle only |
| A120 (optional, no code) | Build A with the panel switched to 120 Hz by hand, temporary until reboot (the same two `sunxi_dump/write` lines the fork's RG34XXSP probe used under NextUI: divider `0x06511044 0xf000000a`, then PLL `0x03001040 0x88002b03`; reboot restores 60 Hz) | Tells whether 120 Hz helps upstream's lock at all, and shows the cadence `MIN_FRAME` produces. Only after Step 0 passes |
| D | Build A under schedutil | A, plus the fork's 5-line governor loop in `launch_frontend.sh` for the run only |

Phase 2, only if F120 beats A: port (a) onto a branch of our tree (call it B and C at 60/120 Hz) so NES,
SNES, Sega and PS1 can be measured. The fork binary cannot run them. For our own decision A is the
baseline; for the upstream PR, quote U against F120.

### Runs

Conditions: on the charger, rested device (idle + 10 C rule from PERFORMANCE.md), `performance` governor
except D, 3 runs per build, rotate the build order between repeats, fresh process per run.

1. **End to end latency (GBA):** build the response ROM (`python3 -B tools/refresh/make_response_rom.py
   /tmp/slot-response.gba`, needs clang with `armv4t-none-eabi`), then for each of A, F60, F120 run the
   fork's `profile.py --serial <adb serial> --binary <build> --probe <probe> --latency-rom /tmp/slot-response.gba
   --latency-count 60 --repeats 3 --skip-profile --modes 60` (use `--modes 120` for F120, and a fresh
   `--output` per build; check `profile.py --help` first, the flags are from its README and argparse).
   Run U the same way. Note that `profile.py` refuses any panel other than `rg34xxsp_v1`: that is Step
   0 again.
2. **Game speed and CPU (GBA):** same tool without `--skip-profile`, scenes `gba-mgba`, `gba-heavy-mgba`,
   `gba-gpsp` (the ROM file names are hardcoded in `SCENES`; edit them to carts on our card, or copy
   theirs under those names). Read committed fps, CPU %, MHz, temp, IRQ slope.
3. **Cadence and audio (our tools):** `task perf:play CORE=mgba PLATFORM=gba MINUTES=3 RUNS=3` on A, F60
   and F120. For A, read `ft_p99_worst`, `ft_max` and the missed-latch count from `pace:` lines. For F60
   and F120 the fork's `slot: pace:` line reports presents/s, steps and "missed game periods", so count
   `steps - presents` (double-commit presents) per 600. Expected: about 1 per 7 s at F60, about 0 at F120.
   Starved samples from `task readout:device` for all.
4. **Governor (D against A):** `task perf:play` on the SA-1 and Super FX pairs (snes9x heavy, Yoshi's
   Island), MD Virtua Racing and PS1 CTR, 3 runs each, plus `task perf:eval` once under each governor.
   Add before and after rows to DEVICE-GATE.md as its rule requires. Optional battery check: 60 minutes of
   the same GBA cart off the charger, battery % drop, A against D.
5. **Phase 2 only (B/C):** NES and SNES auto-play pairs (judder count, present p99, starve). PAL is
   measured on the issue 66 build (cadd65c), not here.

### Decision rules

- 120 Hz goes upstream (with (a)) only if F120's pooled median latency is at least 6 ms below **A** (not
  F60), its p95 is not worse than A's, and it has 0 starved samples, 0 missed game periods and committed
  fps within 0.06% of native.
- If A is already at or below F120, drop the 120 Hz track and keep the lock: upstream's late latch is
  doing the job. Issue 66 (cadd65c) already covers PAL.
- If F60 is worse than A (expected), native pacing must never ship alone at 60 Hz for NTSC cores, which is
  what cadd65c's 2 fps window already guarantees.
- schedutil (D) only with 0 missed periods and 0 starved on every heavy title.

## 9. Licence and credit

- The fork is **GPL-3.0** (`LICENSE`, same as slot). Anything taken (code or a close re-implementation of
  `pacing.rs`, `refresh.rs` or the trace) carries Prashant Vaibhav's copyright. Credit him in the patch
  header and `LICENSING.md` with commit links (e8ff757 and the file names). Issue 66 already plans to
  credit oauramos (omega-zero), and cadd65c credits omega-zero, unslot and slotPlus; add Vaibhav only if the
  debt cap or other fork code is borrowed.
- `tools/refresh/` is in the same GPL-3.0 tree. Running it needs no credit; vendoring it would.
- `displaycal.rs` says "ported from NextUI's common/displaycal.c". NextUI switched from GPL-3.0 to
  **PolyForm Noncommercial 1.0.0 on 2026-08-15**. `displaycal.c` landed there on 2026-06-28 (GPL era),
  but Vaibhav's H700 support in NextUI (fb6a411, #807) landed on 2026-10-03, after the switch. He can
  license his own code to slot under GPL; anyone reviving the LUT must ask him which version it came from
  and where `rg34xxsp.cube` was measured (its header says "Warm2 Display Calibrator, Uncalibrated").
  Moot while the row is "skip".
- Three fork commits are machine co-authored (fork metadata); this has no licence effect.
- bphenriques: GPL-3.0 (same tree); Muse, FFmpeg and SoundTouch have their own licences, irrelevant
  since skipped.
- Upstream etiquette: Vaibhav has not proposed any of this to Brandon. Under ADR 0047, talk to him first
  and offer to co-author or review his own PR rather than sending his work as ours.

## Recommended to adopt (ranked)

1. **Measure before deciding: Step 0 + the A/F60/F120 latency A/B.**
   - What: the panel check, then the fork's `profile.py` latency mode on A (ours with the throwaway
     response hook), F60 and F120.
   - Why: the fork's 8.5 ms claim is against its own 60 Hz pacer, never against upstream's late latch.
     This one run decides whether items 2 and 3 are worth any code.
   - Effort: S (half a day: two builds, a ROM, about an hour on the device).
   - Upstream or ours: neither, it is measurement.
   - Verify: Step 0 output plus decision rules in section 8.
2. **Issue 66 stays on its own track; take one check from the fork.**
   - What: issue 66 is already implemented in `~/.cache/pal` (cadd65c, owed frames under the lock, 2 fps
     window, PAL Speed choice). The fork adds nothing for PAL. Borrow only the `FramePacer` debt rule
     (at most 2 frames per present, drop debt above 2 periods) if a test shows `owed_frames` bursting
     after a stall or a resume.
   - Why: native pacing for every core at 60 Hz would add NTSC judder (about every 1.9 s on NES and
     SNES) and break criterion 1; cadd65c avoids both.
   - Effort: S (one test: a 500 ms tick into `owed_frames` must not run more than 2 frames).
   - Upstream or ours: ours.
   - Verify: issue 66's own device check (a PAL NES and a PAL PS1 game at 50 fps, 0 starved).
3. **120 Hz with full native pacing, upstream-first, only if item 1 says so.**
   - What: (a) + (b) as one upstream PR against slot `main` (after b0fe199 and 5dc5b83), co-ordinated with
     Vaibhav. Carry nothing ourselves until Brandon accepts. Then rebase, fold issue 66's PAL
     path into the upstream pacer, and re-base the DEVICE-GATE present thresholds on the game period.
   - Why: at 120 Hz, native pacing gives right speed and near-even cadence for every core (NES/SNES
     hiccup every ~15 s instead of ~1.9 s), plus whatever latency item 1 proves.
   - Effort: L (pacing rewrite, PLL policy, wake path; upstream review).
   - Upstream or ours: upstream-first (ADR 0047).
   - Verify: decision rules, then auto-play NES/SNES/PS1 pairs on the rebased tree with 0 starved, and
     the DEVICE-GATE titles re-run.
4. **schedutil governor, only on evidence.**
   - What: the 5-line `launch_frontend.sh` loop.
   - Why: battery, if heavy titles survive it.
   - Effort: S.
   - Upstream or ours: ours (a launcher line), with DEVICE-GATE before and after rows.
   - Verify: run 4 (D against A) on SA-1, Super FX, Virtua Racing and CTR: 0 missed periods, 0 starved.
5. **Nothing else.** The state size cache and held-POWER shutdown arrive with upstream 1.8.0. Run-ahead
   leaves upstream in 1.8.0. The LUT, blending, RetroAchievements, Wi-Fi, label scraping and the music
   player are out of scope or worse than what we have.
