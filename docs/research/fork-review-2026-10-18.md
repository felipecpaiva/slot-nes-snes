# Fork review, 2026-10-18: what to adopt and in what order

Six forks of BrandonKowalski/slot were reviewed in depth, one report each:

| Fork | Report | Focus |
|---|---|---|
| pvaibhav/slot | [fork-pvaibhav.md](fork-pvaibhav.md) | input lag, 120 Hz, pacing, governor |
| marghost/slot_modded | [fork-marghost.md](fork-marghost.md) | small UI and power fixes |
| nelynes/slotPlus | [fork-nelynes.md](fork-nelynes.md) | new platforms (WonderSwan, Lynx, NGP, TG16) |
| jgraving/slot | [fork-jgraving.md](fork-jgraving.md) | quality of life, Bluetooth, sleep |
| suprsomething/slot.advance | [fork-suprsomething.md](fork-suprsomething.md) | sleep, save states, battery |
| cloudwithax/unslot | [fork-unslot.md](fork-unslot.md) | 55 systems, label fallback, pacing |

Every fork is GPL-3.0 (or later). Nothing cherry-picks cleanly onto our patch set (ADR 0009, 0013, 0015
rule out edits to upstream tests and `Host`), so "adopt" means reimplement with the fork as reference and
credit it in the patch header and LICENSING.md. Generic fixes go upstream first (ADR 0047); we carry a
patch only until upstream ships it.

Claims below marked **verified** were checked by the maintainer's orchestrator against our tree or the
device, not only by the reviewer.

## Findings about our own tree

| Finding | Source | Status |
|---|---|---|
| Settings > Screen has 9 rows (468 px) against the 427 px legend line: the top row is off screen and the bottom row sits on the legend | marghost, jgraving (independently) | **verified** on the device by the maintainer; fix in progress (backport of upstream e1bfb2b's scroll window, extended to SCREEN) |
| `flush_resume` returns before writing `.sav` when the core gives no state, so the doze power-off can lose in-RAM progress | suprsomething (dbbadae) | **verified** in `app.rs:4357`; upstream bug |
| The lowest backlight step leaves the RG34XX panel black (upstream #100, fixed in 3b6349c after v1.7.0) | jgraving | **verified**: our tree has `BACKLIGHT_FLOOR = 1.0` |
| Upstream main (1.8.0) removes run-ahead (b0fe199, flash-save corruption) | suprsomething, pvaibhav, unslot | **verified**; retires the run-ahead items in fork-savethefails-snes.md |
| The panel is `rg34xxsp_v1`, 720x480, ht 820, vt 536, dclk 26 MHz, 59.8 fps, `sunxi_dump` present | pvaibhav step 0 | **verified** on the device: the 120 Hz track is possible |
| Rebasing onto upstream main conflicts with patches 0007, 0038 and 0040 (e1bfb2b, 2c82294 remapping, bfb8bb2 left stick) | unslot | to plan with the 1.8.0 rebase |

## Plan

### Tier 1: bugs, now

1. Screen page scroll (in progress, own patch, dropped when the 1.8.0 rebase lands; ADR proposes "any long page scrolls" upstream).
2. Carry upstream 3b6349c (backlight floor), two lines, drop on rebase.
3. Write `.sav` when the core gives no state (upstream PR first, carry if slow).
4. Cart face and restock race: stale face on the wrong cart after a favourite toggle, faces rebuilt on every restock (marghost 88af60a). Upstream first.
5. Confirm before deleting a save state, Up/Down in the switcher (suprsomething 2fe9876, without its ring-of-five default). Upstream first.

### Tier 2: small quality of life, upstream first

6. Battery Low banners at 15% and 10% (marghost 1706a16, suprsomething d495461). Separate toast file if carried.
7. Stop drawing while dozing (marghost b1f9e24, suprsomething bf810b6). Measure current first; collides with patch 0015's `Pacer`.
8. Confirm favourite removal with a second Y (jgraving e2dc0cb).
9. Show the volume HUD when a game starts muted (jgraving 12f7b3a).
10. START closes the core picker it opened (jgraving e047d17).
11. Logo Only label fallback for games with no scan (ADR 0014 promise), as a Rust example called by `fetch-labels.py --by-name` (unslot `scraped.rs`). Ours.

### Tier 3: measure, then decide

12. 120 Hz with native pacing (pvaibhav e8ff757). The fork's "8.5 ms less" is against its own 60 Hz pacer, not upstream's late latch. Run the A / F60 / F120 latency A/B in fork-pvaibhav.md section 8. Adopt only as an upstream PR, only if 120 Hz beats our build by at least 6 ms with no worse p95 and no audio starvation.
13. schedutil governor: only with before and after DEVICE-GATE rows on SA-1, Super FX, Virtua Racing and CTR.
14. Fast shelf scroll (marghost): only if SNES and PS1 frametime p99 stays in the gate.
15. Suspend-to-RAM with lid wake (suprsomething c9e5697, jgraving f2aa20d). Largest QoL gain (PS1 most), large and risky; found on a different Anbernic model. Upstream discussion first, extend Brandon's `lid_off_min` and teach `lid.sh` about suspend; new ADR superseding 0033.

### Tier 4: new platforms (nelynes reference, credit nelynes)

16. NeoGeo Pocket / Color on Beetle NeoPop: 3x fills the panel, no BIOS, no rotation; flash-save durability is the new item.
17. TurboGrafx-16 HuCard on Beetle PCE Fast: rides the SNES 360x240 canvas.
18. WonderSwan / Color on Beetle Cygne: rotation via core option, set `wswan_60hz_mode=enabled`; the work is the input remap.
19. Atari Lynx on Beetle Lynx, last: needs PAL-style non-60 Hz pacing (issue #129) and a BIOS check.

All five cores' sources combine with GPL-3.0-or-later; pinned tarball hashes are in fork-nelynes.md.

### Tier 5: tooling and later

20. Linux headless EGL for render tests (suprsomething e761baa, unslot `headless_egl.rs`), upstream first; lets the Linux job gate render tests (amend ADR 0035).
21. Stick detection from capabilities and kernel range (unslot), upstream first on top of bfb8bb2; `Config/sticks.txt` stays the override.
22. A 4:3 option in each system's Picture row (unslot), the user's pick stays the default.
23. Rebase onto upstream 1.8.0: drops the scroll and backlight patches, retires run-ahead, resolves 0007 / 0038 / 0040.

### PAL pacing (#129)

In progress on its own branch. Prior art fed to it: nelynes `Owed` (gate lifted below 62 fps), unslot `frame_period` / `core_hz` (cores within 2 Hz of 60 stay locked), pvaibhav's catch-up cap (at most 2 frames per present). Designed so 75 Hz cores (Lynx, WonderSwan) can use the same path.

## Skipped

- Bluetooth, USB audio, Sound menu (jgraving; Brandon declined Bluetooth on upstream #109), Wi-Fi, OTA, RetroAchievements, parent controls, network services (non-goals).
- Panel colour LUT (pvaibhav; measured on one unit, NextUI licence question), mGBA frame blending (changes GBA output).
- 4:3-panel-only work in marghost (integer scale, bezels, fullscreen menus) and nelynes' 4:3 fill.
- Game Gear on Gearsystem (ours on Genesis Plus GX is shipped and measured; Gearsystem stays the picker candidate in ADR 0053).
- Save-state ring of five, Wi-Fi off by default, shader default changes: they retune factory defaults (maintainer rule: keep options, the user's choice is the default).
- unslot's distribution model (unpinned nightly cores, no corresponding source, a compiled-in ScreenScraper dev id).
- Button cheat sheet, startup screen, branding.

## Corrections to slot-forks.md

- jgraving has 63 branches, not 36; its Bluetooth branch is not an upcoming upstream PR (declined on #109).
- nelynes' Game Gear, NeoGeo Pocket and TG16 live on `slotPlusUltra` only; `main` has WonderSwan, Lynx and the Transparent shader.
- suprsomething has 20 branches and branches off v1.5.0-25.
- bphenriques is 5 commits ahead of pvaibhav, not an older copy.

## 120 Hz latency A/B result (2026-10-18, RG34XXSP, rg34xxsp_v1 panel)

pvaibhav's `profile.py` latency mode with its response ROM, GBA on mGBA, 3 rounds x 60 presses per build,
build order rotated, governor performance, on USB power. Display interrupt 298 confirmed the panel rate
(about 59 Hz, and 120 Hz during the 120 Hz runs). Every trial passed; 0 starved, 0 dropped in every run.

| Build | Median ms | p95 ms | Per-round medians |
|---|---|---|---|
| A: ours (main 5214076), 60 Hz | 30.99 | 38.72 | 32.8, 31.4, 29.7 |
| A120: ours, panel set to 120 Hz by hand | 25.16 | 42.40 | 25.5, 25.0, 25.5 |
| F60: pvaibhav, 60 Hz | 41.61 | 49.26 | 41.3, 41.8, 42.1 |
| F120: pvaibhav, 120 Hz | 29.38 | 36.16 | 30.1, 29.9, 28.9 |
| U: upstream v1.7.0 unpatched, 60 Hz | 73.23 | 88.23 | 73.1, 76.1, 72.7 |

- Decision rule (F120 at least 6 ms below A, no worse p95): F120 is only 1.6 ms below A. **NO-GO** for the fork's 120 Hz with native pacing.
- Our 60 Hz build is 10.6 ms faster than the fork at 60 Hz, which confirms the review: the fork's "8.5 ms less" was measured against its own slower 60 Hz pacer.
- A120 (our pacing, panel at 120 Hz, no code) is 5.8 ms faster at the median but 3.7 ms worse at p95 (uneven cadence under the upstream lock). Not adopted; a 120 Hz option would need its own pacing work and a battery measurement first, and would ship only as a user setting.
- **Upstream's 73 ms was not reproducible.** Its own counters showed the frame loop presenting at 30 Hz (about 540 of 600 frames missed a latch) after it released the audio device in a silent scene. A day-later rerun of the same binary, freshly rebooted, measured 30.8 ms with the same audio release. Most likely the 30 Hz state followed the repeated panel clock writes of the 120 Hz runs, not normal use. Recorded as not reproducible; no upstream PR. A prepared branch (`keep-audio-open-while-fed`, 26456de in ~/contrib/slot) stays local in case it reappears.
- Panel registers were restored to the 60 Hz values after every run and the device was rebooted at the end.
