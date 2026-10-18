# suprsomething/slot.advance: quality-of-life changes vs slot-nes-snes

Read-only survey, 2026-10-18. I cloned all 20 remote branches into `~/.cache/forks/suprsomething`
(the prior summary said 14). I compared them against:

- slot-nes-snes ADRs 0001 to 0069, docs/PLAN.md and patches 0001 to 0041;
- the patched tree `~/.cache/pal/slot-nes-snes/work/slot`;
- upstream BrandonKowalski/slot at v1.7.0 (`34ac380`) and upstream `main` (`1b20432`, the unreleased 1.8.0).

**Base.** Every fork branch forks from `4ebd85a` (v1.5.0-25), which is 90 commits behind v1.7.0. The fork
then carries 114 commits on `main` (fork `main` at `3525f86`, release `advance-0.4.2`). Its app.rs is
pre-v1.7.0 (no in-game menu, no Recents shelf, old About sticker), so nothing ports as a cherry-pick.
Every item below means reimplementing it, or copying a self-contained file.

**Device.** The fork targets the **Anbernic RG SP (2026)**, a 720x480 clamshell on BaseOS 1.3.0 (Linux
4.9). Upstream lists the RG SP and the RG34XXSP as **separate devices**. The sysfs nodes the fork relies on
were all found on the RG SP (2026) and are **unverified on our RG34XXSP**:

- `axp2202-battery/os_sleep` and `hallkey`;
- `axp2101-pek.0` and `sunxi-rtc`;
- the GPIO `hall switch` line;
- the six ohci/ehci controller addresses;
- the `8821cs` driver, `rf-ctrl/scan_device` and `axp2202-cldo4`;
- the 35 mAh-per-percent gauge step.

The same applies to every power number (the 100 mA cap, ~70 mA asleep, 0.81 s wake). Section 9,
step 0 probes each of these, read-only.

**Upstream moved after v1.7.0**, and that changes the sleep verdict:

- [2c82294](https://github.com/BrandonKowalski/slot/commit/2c82294) adds `lid_off_min` (1 to 30 min) with a Lid Off menu row.
- [ad5ce8a](https://github.com/BrandonKowalski/slot/commit/ad5ce8a) unloads Wi-Fi before power-off and adds `card/System/lid.sh`, a watcher that powers off once the lid has been shut for Lid Off + 60 s.
- [0ba5370](https://github.com/BrandonKowalski/slot/commit/0ba5370) powers off on a held POWER.
- [894201d](https://github.com/BrandonKowalski/slot/commit/894201d) and [656ce7e](https://github.com/BrandonKowalski/slot/commit/656ce7e) are two save-state fixes the fork also carries.
- [b0fe199](https://github.com/BrandonKowalski/slot/commit/b0fe199) **removes run-ahead entirely** (#104).

Licence: GPL-3.0-or-later (LICENSE, README "same licence as slot"). Authors are:

- Dean Laufs (`dlaufs@gmail.com`, the owner, 28 commits);
- `suprlab` (19);
- Claude (59, at the owner's direction, per the README's AI disclosure);
- 8 cherry-picks of Brandon's and flo's upstream commits.

Credit it as "suprsomething/slot.advance (Dean Laufs), GPL-3.0" with commit links. Recents is itself
"adapted from ciscosweater/slots", so the credit chains. The GBA label photo pack is credited to its
photographers per file and is not GPL; it is not ours to take.

Link prefix: `https://github.com/suprsomething/slot.advance/commit/<sha>`

Verdict key: **adopt / adapt / already have / ours better / superseded upstream / skip**. Value H/M/L,
effort S/M/L.

## 1. Sleep, lid and power

| Change | Commits | What it does technically | Ours | Verdict | Value | Effort | Risk | Conflicts with our patches / ADRs | Upstream first? |
|---|---|---|---|---|---|---|---|---|---|
| **Suspend-to-RAM with lid wake** | [c9e5697](https://github.com/suprsomething/slot.advance/commit/c9e5697) (main feature, 2,399 lines incl. 666 lines of tests), [dbbadae](https://github.com/suprsomething/slot.advance/commit/dbbadae), [d7cb474](https://github.com/suprsomething/slot.advance/commit/d7cb474) | At lid close (or a POWER tap), upstream's `doze` still saves `resume.state` and `.sav` first. After a 400 ms settle, `slot-power/src/sleep.rs` writes `0` to `axp2202-battery/os_sleep`. BaseOS writes `16` ("Super Standby", lid not a wake source) at every boot; `0` makes the hall sensor wake the device through `axp2101-pek.0` (it checks `power/wakeup` reads `enabled`). It sets a relative alarm on the rtc named `sunxi-rtc` (found by name, never by number) and reads it back. Then it writes `mem` to `/sys/power/state`, which blocks until wake. It refuses to suspend if the lid is not armed or the alarm does not read back. Time asleep comes from `/proc/uptime` (counts suspend) minus `Instant` (does not), plus `suspend_stats` `success:`. `slot/src/sleep.rs` `SleepPlan` classifies each wake:<br>(1) lid open: resume, nothing reloaded (`wake()` relights the backlight);<br>(2) deadline reached: clean shutdown, and the next boot resumes;<br>(3) anything else (POWER with the lid shut, charger): back to sleep after 1 s.<br>Two failed suspends, or more than 20 stray wakes, fall back to software standby. POWER is ignored with the lid shut and for 3 s after a wake. Battery cap: the deadline is pulled in to leave 10%, assuming 100 mA (1,260 s per percent), with a 3-minute floor. Audio needs nothing new: the ALSA write path already calls `snd_pcm_recover` (present in v1.7.0 and in our tree, alsa.rs:275). The display driver suspends and resumes in the kernel; the GL/fbdev context survives. **Claims, measured on the RG SP (2026) with the battery gauge only:** ~70 mA asleep (70 to 75) against ~250 mA for its own 0.3.0 software standby held awake by a modified build, so "72% less" is relative to the fork's build, not upstream. Upstream's doze was never measured. Observed 2 to 3.2%/h over three overnight sleeps (all above 80%, where the gauge is nonlinear). Wake to first frame: median 0.81 s with Wi-Fi off (0.4.1), 1.25 s before the stale SDIO fix. Arming lid wake costs ~7 to 9 mA over Super Standby. **Known limitation:** deliberate rapid lid flicks left the screen dark in 9 of 20 flicks (0.4.1) and 10 of 20 (0.4.0); recovery is to close and reopen the lid | None. ADR 0033 keeps upstream's doze: backlight off, core paused, power off after 3 min | **adapt** (after the step 0 probe passes on the RG34XXSP) | H | L | High: kernel interfaces unverified on our device; the lid-flick dark screen; unattended shutdowns | Supersedes ADR 0033 (needs a new ADR). Touches `doze` and the device loop. Patch 0015 (frame-trace) edits the same `Pacer` (`resume()` is added there), and patch 0021 hooks `doze` for shelf memory. New `SlotState` fields (`sleep_minutes`, `wifi`) hit named test site (f) in durability.rs (ADR 0034), and a new Sleep row hits sites (g)/(h). **Upstream 1.8.0 conflict:** `lid.sh` measures lid-shut time with `/proc/uptime`, which counts suspend. After any non-lid wake past Lid Off + 60 s it runs `rmmod; sync; poweroff`, behind slot's back, defeating the "never shut down an unsaved game" rule. Brandon's held-POWER power-off also meets the fork's "POWER ignored while the lid is shut" | **Yes.** Device-wide, not NES/SNES specific, and Brandon is reworking lid power-off right now. Open a discussion upstream first. If we carry it, the duration must extend upstream's `lid_off_min` and Lid Off row (add longer steps only when suspend probed OK), never a parallel `sleep_minutes` key and Sleep row |
| Lid stale-"shut" check | [d7cb474](https://github.com/suprsomething/slot.advance/commit/d7cb474) | After a resume the lid driver writes `hallkey=0` first, then `1`; the second step is sometimes missed. `slot-power/src/lid.rs` cross-checks `hallkey=0` against the raw `hall switch` line in debugfs `/sys/kernel/debug/gpio`. The polarity is learnt the first time `hallkey` reads 1 | None | adapt, as part of suspend | M (only with suspend) | S | Low; needs debugfs mounted | Replaces upstream's `find_hall` in `input/device.rs` | With suspend |
| "Unsaved" doze: a running core with no state | [dbbadae](https://github.com/suprsomething/slot.advance/commit/dbbadae) | If `snapshot.state()` is `None` while the core is `Ready`, the flush is reported as failed and the `.sav` is **still written**. Then the timer never shuts the game down; it retries. A core still loading counts as saved | **Upstream bug, still in upstream `main` and in our tree:** `flush_resume` (our app.rs:4357) logs "the core gave up no state" and returns **without writing the battery save either**. The 3-minute doze power-off then drops the game held in RAM | **adopt** (the generic half: write `.sav` anyway, and report the flush failure) | M | S | Low | None (`flush_resume` is unpatched) | **Yes, upstream-first.** Stands without sleep |
| Software standby (stop drawing while dozing) | [bf810b6](https://github.com/suprsomething/slot.advance/commit/bf810b6) | Once two black frames are presented (one per swap buffer), the device loop stops ticking the core, rendering and swapping. It rests 50 ms per pass and still reads input, polls the lid (150 ms) and runs timers. `slot/src/standby.rs`, 57 lines plus a pure `Standby::step` test | None. Upstream draws a black frame at ~60 Hz for the whole doze | adapt | L on v1.7.0 (it saves at most 3 min per doze), M once upstream's Lid Off reaches 30 min | S | Low | Patch 0015 edits `Pacer` in device_app.rs, the same loop | **Yes.** Generic. Measure first (section 9, B vs B2) |
| Unused hardware off ("quiet") | in c9e5697, [4dacaf3](https://github.com/suprsomething/slot.advance/commit/4dacaf3) | At start-up it writes `0` to six `*hci*_enable` switches (`5200000.ohci1`, `5310000.ohci2/ehci2`, `5311000.ohci3/ehci3`, `5200000.ehci1`); the USB-C port is `5100000.udc` and is left alone. At uptime 20 s it `rmmod 8821cs` (which cuts rail `axp2202-cldo4`) unless `wifi=on`. 0.4.1 then writes `1` to `class/misc/sunxi-wlan/rf-ctrl/scan_device` to drop the stale `mmc2` SDIO card; otherwise every resume waits ~1.1 s for `mmc2: error -110`. Measured (one run): USB off saved ~30 mA asleep; Wi-Fi off showed no separable saving asleep | None | **skip as a default**; adapt only as opt-in options if the probe matches | L to M | M | Medium: addresses are board-specific. **Wi-Fi off by default breaks SlotLink** (the fork hides `wifi=on` and shows "Link Off") | New `SlotState` key | Upstream already unloads Wi-Fi at power-off and Restart; a "Wi-Fi off" option is upstream's call |
| Sleep setting 3 min to 8 h, default 30 | in c9e5697 | `SLEEP_MINUTES = [3, 15, 30, 60, 120, 480]`, `sleep_minutes` in slot.state, a Sleep row in Settings | Upstream 1.8.0 has `lid_off_min` [1, 3, 5, 10, 15, 30], unset by default (falls back to the platform's 3 min) | superseded upstream (the row); extend it, do not add one | n/a | S | n/a | Sites (f), (g), (h) | Extend upstream's row |
| Version and build in slot.log | [6b17f46](https://github.com/suprsomething/slot.advance/commit/6b17f46) | Semver 0.4.0, `build_info.rs` logs version and build at start-up | We have `VERSION` and our own ship stamp | already have | L | n/a | n/a | none | no |

## 2. Save states

| Change | Commits | What it does | Ours | Verdict | Value | Effort | Risk | Conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|---|---|
| Ask before deleting a state | [2fe9876](https://github.com/suprsomething/slot.advance/commit/2fe9876) | In the switcher, Y shows "Delete this state?" with B Keep / Y Delete. A second Y deletes. Any other press keeps the state and does nothing else, so A cannot load from the question | v1.7.0 deletes on **one** Y press (app.rs:2042 `delete_selected`), and undo covers only save and load, not delete | **adopt** | M (a PS1 state is 4.4 MB of progress; one mis-press loses it) | S | Low | Patch 0037 touches state load (disc trailer), not delete. Upstream render/switcher tests pin the plate, so build it upstream | **Yes, upstream-first** |
| Up / Down in the switcher | 2fe9876 | Up = newer, Down = older, besides Left/Right | Left/Right only | adopt with the above | L | S | Low | none | Yes, same PR |
| Ring of 5 instead of 10 | 2fe9876 | `RING_MAX` 10 to 5. Older states beyond one over move to `older/` instead of being deleted | Upstream's 10 | **skip as a default** (maintainer rule: never retune factory defaults). A "States kept" option is possible later | L | S | Medium: it moves user files on first run | Upstream tests use `RING_MAX` | Only as an option, upstream |
| Clock-behind save and one state-size query per game | [247aae0](https://github.com/suprsomething/slot.advance/commit/247aae0), [1176256](https://github.com/suprsomething/slot.advance/commit/1176256) | Cherry-picks of Brandon's [894201d](https://github.com/BrandonKowalski/slot/commit/894201d) and [656ce7e](https://github.com/BrandonKowalski/slot/commit/656ce7e) | Not in v1.7.0; arrive on our next rebase | superseded upstream | M | n/a | n/a | none | done |
| Lid close writes only `resume.state` | 2fe9876 (tests) | A test that lid close never touches the manual ring | Same behaviour upstream | already have | n/a | n/a | n/a | none | no |

## 3. Per-game profiles

| Change | Commits | What it does | Ours | Verdict | Value | Effort | Risk | Conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|---|---|
| Profile store | [bdf47c3](https://github.com/suprsomething/slot.advance/commit/bdf47c3) | `Config/game_profiles.txt`, one `GBA/<stem>.<field> = value` line per changed setting (shader, colour correction, FF speed, FF sound). A missing line falls back to slot.state; the last good line wins | We already ship per-game `selected_core.txt`, `video_mode.txt` (picture mode, by stem) and `cart_shell.txt`, all upstream | **adapt narrowly** (see the judgement below) | L to M | M | Low | ADR 0043 (in game, Shader follows the system), our per-system shader files (ADR 0051, PS1_SHADER_FILE) | If done, upstream-first: GBA benefits too |
| Games run on their profile; in-game changes write it | [ad1798f](https://github.com/suprsomething/slot.advance/commit/ad1798f) | SELECT+A/B (shader) and SELECT+Y (colour) in a game write that game's line; on the carousel they edit the default | In-game shader changes write the system default | adapt narrowly | L to M | M | Low | Our retro and Sega shader stores | as above |
| FF speed and FF sound chords | [f399fad](https://github.com/suprsomething/slot.advance/commit/f399fad) | SELECT+L2/R2 steps FF speed; SELECT+X toggles FF sound | none | **skip** | L | S | n/a | **Chord collisions:** SELECT+X is our picture toggle (ADR 0007, and the PS1 picture toggle in ADR 0068). SELECT+L2 is the PS1 disc swap (ADR 0067), SELECT+R2 is PS1 fast-forward (ADR 0066) | no |

**Judgement on profiles (I partly disagree with the earlier "out of scope").** The non-goal reads
"RetroArch breadth: ... per-game overrides". That fits a generic per-game override store (FF speed, sound,
colour, core options). But upstream itself already keeps per-game core and per-game picture mode in
stem-keyed ini files. A **per-game shader only**, resolved over each system's own Screen section default,
is a narrow extension of that pattern, not breadth. It has a real use on PS1 (2D sprite games want a CRT
shader, 3D games look worse with one) and on SNES. I would not build it now. If a user asks, do a
shader-only line, no new chords, and upstream-first. One more thing: the fork's `<platform>/<stem>` key
would also fix our documented stem-collision non-goal (`selected_core.txt`, `video_mode.txt`). That is
an argument for raising the key format upstream, separately.

## 4. Carousel and UI

| Change | Commits | What it does | Ours | Verdict | Value | Effort | Risk | Conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|---|---|
| Favourites (Y stars a cart) | [e761baa](https://github.com/suprsomething/slot.advance/commit/e761baa) | `Config/favourites.txt`, a Favourites shelf, gold stars, L2/R2 switch categories | v1.7.0 [42a1590](https://github.com/BrandonKowalski/slot/commit/42a1590) (favorites from #89) | superseded upstream | n/a | n/a | n/a | n/a | done |
| Recents | [4000933](https://github.com/suprsomething/slot.advance/commit/4000933) | The last 10 games, from ciscosweater/slots | v1.7.0 [18f2a41](https://github.com/BrandonKowalski/slot/commit/18f2a41) | superseded upstream | n/a | n/a | n/a | n/a | done |
| Last cartridge at boot | [bf685bd](https://github.com/suprsomething/slot.advance/commit/bf685bd) | `last_category` in slot.state; an empty slot boots on the last game played | Upstream #53 shelf memory plus our per-shelf cart memory (ADRs 0039, 0049) | superseded upstream / ours better | n/a | n/a | n/a | n/a | done |
| Game titles above the cart, with a marquee | [9127781](https://github.com/suprsomething/slot.advance/commit/9127781), [85a3f34](https://github.com/suprsomething/slot.advance/commit/85a3f34) | A title above the selected cart in a 280 px window; a long title scrolls at 28 px/s after 2 s. Its cleaner drops dump tags ((USA), (Rev 1), [!], [T-En]) but keeps meaningful groups ((Arcade), (2nd Edition)) | v1.7.0 "Game Titles" ([419b03b](https://github.com/BrandonKowalski/slot/commit/419b03b), [68fe057](https://github.com/BrandonKowalski/slot/commit/68fe057)): the rack name fades into the selected game's name. Upstream's `clean_label` strips every bracket group | superseded upstream (the feature); the smarter cleaner is a small idea | L | S | Low | Our label fetcher has its own name rules | The cleaner, if anyone asks |
| GBA shader default Off, star glyph | [6084b34](https://github.com/suprsomething/slot.advance/commit/6084b34) | GBA defaults to Off because 720x480 is exactly 3x | Upstream's default | **skip** (a factory-default retune for one device) | n/a | n/a | n/a | GBA must stay byte-identical (PLAN success 1) | no |
| Battery banners at 15% and 10% | [d495461](https://github.com/suprsomething/slot.advance/commit/d495461) | Once per discharge, in game or on the carousel. Charging re-arms them; nothing behind a shut lid; a reading past both shows only the lower; the 5% shutdown is unchanged. Two new `Toast` variants (grows `Toast::FIXED`) | v1.7.0 shows battery in the in-game menu corners and a low LED at 20% (app.rs:63). No banner | adopt | M | S | Low | If carried before upstream: follow the `disc_toast.rs` pattern (patch 0037) and do not grow `Toast::FIXED`, which upstream toast tests pin | **Yes, upstream-first** (marghost/slot_modded did the same) |
| Shorter FF sound banners | [88c3893](https://github.com/suprsomething/slot.advance/commit/88c3893) | "FF Sound On/Off" so the banner is not shrunk | Fork-era text | skip (check v1.7.0 banner sizes only if a test flags it) | L | n/a | n/a | none | no |
| About screen: version, game count, card free space | [896a578](https://github.com/suprsomething/slot.advance/commit/896a578), [6753dc1](https://github.com/suprsomething/slot.advance/commit/6753dc1) | Replaces upstream's sticker with fork branding, `card_space.rs` (free space via statvfs) and a game count | Upstream sticker | skip (branding). The card free-space line is a small upstream idea | L | S | Low | none | idea only |
| Boot logo "slot. ADVANCE" | [0d1cd49](https://github.com/suprsomething/slot.advance/commit/0d1cd49), [7c4303b](https://github.com/suprsomething/slot.advance/commit/7c4303b) | Branding | ours separate | skip | n/a | n/a | n/a | n/a | no |

## 5. Diagnostics, tests and tooling

| Change | Commits | What it does | Ours | Verdict | Value | Effort | Risk | Conflicts | Upstream first? |
|---|---|---|---|---|---|---|---|---|---|
| Keep the newest five crash logs | [590f1f1](https://github.com/suprsomething/slot.advance/commit/590f1f1) | `coresave.sh` copies slot.log into `crash/` on every crash and never prunes; now it keeps 5 | Upstream unchanged (no `KEEP_LOGS` in upstream `main`) | adopt | L | S | Low | none (card script) | **Yes** |
| Main-thread crash label | [2c4dfbb](https://github.com/suprsomething/slot.advance/commit/2c4dfbb), test [2eccd96](https://github.com/suprsomething/slot.advance/commit/2eccd96) | The crash line says "thread slot" instead of `ld-linux-aarch6` (gettid == getpid, async-signal-safe) | Upstream `crash.rs` has no `on_main_thread` | adopt | L | S | Low | none | **Yes** |
| Linux headless EGL surface for render tests | in [e761baa](https://github.com/suprsomething/slot.advance/commit/e761baa) (`slot-gfx/src/headless_egl.rs`, 209 lines) | GLES 2 pbuffer context through EGL (Mesa llvmpipe, `EGL_PLATFORM=surfaceless`), so render tests run on Linux with the **same GLSL ES dialect as the device**. Upstream's headless surface is macOS CGL desktop GL only | Render tests run on macOS only (ADRs 0010, 0035) | **adapt** | M for us: our retro shaders (ADRs 0028, 0029) are GLES programs that macOS desktop GL can let slip | S to M | Low | Our own new file, plus a cfg in slot-gfx `lib.rs` | Yes, it helps upstream CI too |
| README screenshots from the real renderer | `slot/examples/readme_screenshots.rs`, `readme_titles.rs`, [ffa1135](https://github.com/suprsomething/slot.advance/commit/ffa1135), [84b4a86](https://github.com/suprsomething/slot.advance/commit/84b4a86) | Renders shelves headless after normal animation frames, rejecting transition frames | We render with our harness | skip (we have our own) | L | n/a | n/a | n/a | no |
| Upstream cherry-picks | [fa4a461](https://github.com/suprsomething/slot.advance/commit/fa4a461), [d4cdca9](https://github.com/suprsomething/slot.advance/commit/d4cdca9), [b262fb6](https://github.com/suprsomething/slot.advance/commit/b262fb6), [44900e6](https://github.com/suprsomething/slot.advance/commit/44900e6), [e6bd5cf](https://github.com/suprsomething/slot.advance/commit/e6bd5cf), [bfa939b](https://github.com/suprsomething/slot.advance/commit/bfa939b) | Present pacing, released-audio pacing, crash cores, crash line, gpSP JIT cache, launch timing | All in v1.7.0 (ADR 0041 dropped our pacing patch for d4cdca9's upstream twin) | already have | n/a | n/a | n/a | n/a | done |
| Link test with Wi-Fi on | [03cc36f](https://github.com/suprsomething/slot.advance/commit/03cc36f) | Needed only because the fork turns Wi-Fi off | n/a | skip | n/a | n/a | n/a | n/a | no |

## 6. Release, docs, website and art

| Change | Commits | What it does | Verdict |
|---|---|---|---|
| Release workflow with a hand-started test build | [d276a84](https://github.com/suprsomething/slot.advance/commit/d276a84), [cc0616b](https://github.com/suprsomething/slot.advance/commit/cc0616b) | `workflow_dispatch` with an optional `release_tag`: empty means a test build that publishes nothing | Low value. Our release.yml is tag-only (`v*-ns.*`); a no-publish manual run is a nice-to-have. Ours, not upstream |
| Issue form, beta rule | [b612924](https://github.com/suprsomething/slot.advance/commit/b612924) | Bug form asking for version and slot.log | skip (we track issues in `.github/issues/`) |
| Battery and wake methodology docs | [ca25491](https://github.com/suprsomething/slot.advance/commit/ca25491) to [3525f86](https://github.com/suprsomething/slot.advance/commit/3525f86) (`documentation/sleep-and-battery.md`, `technical.md`, `battery-tests/calculate.py`) | Unusually careful gauge methodology: 1% = 35 mAh, nonlinear above 80%, tick timing, ratio correction | **Reuse the method** (section 9), not the numbers |
| slotadvance.com website | [5b739f3](https://github.com/suprsomething/slot.advance/commit/5b739f3) and the website branches | Replaces upstream's site | skip |
| GBA original label starter pack | [0b0cc9c](https://github.com/suprsomething/slot.advance/commit/0b0cc9c) | 12 photographed retail labels, credited per photographer, not GPL | skip (GBA, third-party photos; ADR 0037 keeps art out of code repos) |

## 7. Branches

All 20 remote branches. "In main" means 0 commits not in `main`.

| Branch | Ahead of v1.7.0 | Last commit | Status |
|---|---|---|---|
| main | 114 | 2026-10-17 0.4.2 notes | reviewed above |
| release-0.4.2 | 114 | 2026-10-17 | = main |
| docs-readme-simplification | 97 | 2026-10-16 | in main |
| docs-post-0.4.1-reorganisation | 92 | 2026-10-16 | in main |
| prep-0.4.1 | 90 | 2026-10-16 | in main |
| docs-0.4.0-accuracy | 83 | 2026-10-16 | in main |
| docs-0.4.0-standby | 81 | 2026-10-16 | in main |
| website-video-no-version | 78 | 2026-10-15 | in main |
| website-video-width | 76 | 2026-10-13 | in main |
| website-self-hosted-video | 75 | 2026-10-13 | **1 commit not in main**: [6f6987d](https://github.com/suprsomething/slot.advance/commit/6f6987d), website video width only (main has the same change as e4c67c5) |
| battery-beta3 | 71 | 2026-10-13 | in main |
| release-0.4.1 | 70 | 2026-10-14 | in main (497c8e5 merged by 81fb5ad) |
| battery-measured | 69 | 2026-10-13 | in main |
| release-0.4.0 | 67 | 2026-10-13 | in main |
| sleep-v4 | 38 | 2026-10-12 | in main (the suspend work: c9e5697, dbbadae) |
| titles-v4 | 35 | 2026-10-12 | in main |
| profiles-standby | 31 | 2026-10-10 | in main (profiles, standby, banners, last cart) |
| artwork/gba-original-labels | 6 | 2026-10-10 | in main (PR #1) |
| rgsp | 5 | 2026-10-10 | in main (favourites, recents, ring of five, README) |
| v2-baseline | 5 | 2026-10-10 | = rgsp |

## 8. Extending each candidate to our systems

| Candidate | NES / SNES | Game Gear / SMS / MD | PS1 | Per-system Screen section? |
|---|---|---|---|---|
| Suspend-to-RAM | The whole process freezes, so any core resumes with no serialize call. The lid-close save still runs first (`flush_resume`), as upstream does | Same | Same, and the biggest win: a lid close today writes a 4.4 MB `resume.state` plus PNG and then powers off after 3 min, so coming back means a full boot and a pcsx state load. Check pcsx's threaded GPU and drc threads (ADR 0064 `auto`) and CHD file reads after resume. Disc-in-state (ADR 0067) is untouched: nothing reloads | No. One global duration on upstream's Lid Off row |
| Save-safety flush (dbbadae) | fceumm and snes9x serialize reliably; `.sav` written either way | Same | Large state; a failed 4.4 MB serialize or write is more likely than on GBA, so writing `.sav` anyway matters most here | No |
| Delete confirmation | Same switcher | Same | Most valuable here: 4.4 MB of progress per state. Multi-disc states carry the `SLOTPSX1` trailer; delete removes the whole file, so no special case | No |
| Ring size option (if ever) | n/a | n/a | 10 states = ~44 MB per game plus thumbs. A "States kept" option would be global; a PS1-only cap would need its own Screen/filter section by the maintainer rule | Only if made per system |
| Battery banners | Global toast | Global | Global | No |
| Software standby | Global loop change | Global | Global | No |
| Per-game shader (idea) | Resolves over the NES or SNES section's shader | Over the Sega shader file (ADR 0051) | Over `PS1_SHADER_FILE` | Yes, it resolves through each system's existing section; the default stays the section's value |

## 9. Measurement plan for the device claims (you run it; adb from your Mac)

Rules: every battery segment runs **with USB unplugged** (adb over USB charges the device and keeps the
UDC awake). Start loggers with `nohup`, then unplug. All sysfs writes below last only until reboot
(BaseOS rewrites `os_sleep=16` at boot). To escape a stuck state, hold POWER about 10 s. Run segments
**below 80%** charge, where the fork showed the gauge is close to linear.

**Step 0. Read-only probe** (decides whether anything in section 1 applies to the RG34XXSP):

```sh
adb shell '
P=/sys/class/power_supply/axp2202-battery
ls $P
for f in os_sleep hallkey capacity charge_counter charge_full_design voltage_now current_now power_now status; do printf "%s=" $f; cat $P/$f 2>&1; done
cat /sys/power/state
for r in /sys/class/rtc/rtc*; do echo "$r $(cat $r/name) $(ls $r/wakealarm 2>&1)"; done
find /sys/devices -maxdepth 9 -name "axp2101-pek*" 2>/dev/null
cat $(find /sys/devices -maxdepth 10 -path "*axp2101-pek.0/power/wakeup" 2>/dev/null | head -1)
mount | grep debugfs; grep -i hall /sys/kernel/debug/gpio
cat /sys/kernel/debug/suspend_stats
for f in /sys/devices/platform/soc/*hci*/*_enable; do echo "$f=$(cat $f)"; done
ls -d /sys/devices/platform/soc/*udc* 2>&1
lsmod; ls /sys/class/misc/sunxi-wlan/rf-ctrl/ 2>&1
grep -i cldo /sys/kernel/debug/regulator/regulator_summary 2>/dev/null
for p in $(pgrep -f slot); do tr "\0" "\n" < /proc/$p/environ | grep BASEOS; done
'
```

Pass means: `os_sleep`, `hallkey`, `mem` in `/sys/power/state`, a `sunxi-rtc` with `wakealarm`,
`axp2101-pek.0`, and a `hall switch` GPIO line. Also record:

- whether `current_now` reads a live value (if it does, it beats 1% ticks for every awake segment);
- `charge_full_design` (the fork's 3,500 mAh and 100 mA cap are RG SP constants);
- which `*hci*` controllers exist, and the Wi-Fi module name.

**Step 1. Manual suspend smoke test** (no code change; slot on the shelf, no game seated). Push this
to `/mnt/sdcard/Logs/s1.sh`, set `RTC` to the `sunxi-rtc` from step 0, run
`adb shell nohup sh /mnt/sdcard/Logs/s1.sh &`, unplug USB within 30 s, and leave the lid open:

```sh
P=/sys/class/power_supply/axp2202-battery; RTC=/sys/class/rtc/rtc1; L=/mnt/sdcard/Logs/s1.log
sleep 30; echo 0 > $P/os_sleep; echo 0 > $RTC/wakealarm; echo +60 > $RTC/wakealarm
echo "$(date +%s) up=$(cut -d" " -f1 /proc/uptime) alarm=$(cat $RTC/wakealarm)" >> $L; sync
echo mem > /sys/power/state
echo "$(date +%s) up=$(cut -d" " -f1 /proc/uptime) woke" >> $L; dmesg | tail -60 >> $L; sync
```

Pass means:

- the screen goes dark and returns about 60 s later;
- uptime moved about 60 s more than the time the script itself took;
- dmesg shows `PM: suspend entry` and `Enabling non-boot CPUs`;
- there is no `mmc*: error -110` (if there is, that is the Wi-Fi SDIO stall the fork fixed in 4dacaf3);
- slot redraws and sound still plays.

**Step 2. Lid wake.** Repeat with `+600`, close the lid during the 30 s wait, and open it after 2 min.
Pass means it wakes on lid open (log about 120 s asleep). Do 10 rounds. Also try:

- POWER with the lid shut: it should wake, and slot will not go back to sleep, because nothing tells it to;
- plugging the charger in while asleep: note whether it wakes.

**Step 3. Wake time** (what the player sees). Film lid-open to first game frame at 240 fps, 10 trials,
for each of:

- (a) step 2's manual suspend;
- (b) today's doze within 3 min (backlight-on time);
- (c) today's path after more than 3 min: hold POWER, boot, resume.

Also take dmesg `Enabling non-boot CPUs` timestamps for (a). This puts the fork's 0.81 s against our
real alternative (ADR 0033 says about 2 s of boot, plus the POWER press).

**Step 4. Current, by segment.** Logger at `/mnt/sdcard/Logs/batt.sh`, started with nohup before each
segment:

```sh
P=/sys/class/power_supply/axp2202-battery
while :; do echo "$(date +%s) $(cut -d" " -f1 /proc/uptime) $(cat $P/capacity) $(cat $P/voltage_now) $(cat $P/current_now 2>/dev/null) $(cat $P/status)" >> /mnt/sdcard/Logs/batt.log; sync; sleep 30; done
```

The logger keeps running in segments A, B and B2, so it reads the live current there. It is frozen in
segment C and only resumes at wake. Segments:

- **A.** Awake on the shelf, backlight at your usual level, 60 min.
- **B.** Upstream doze, held for 30 min: lid closed on upstream `main` with Lid Off = 30, or a test build with `DOZE_TIMEOUT` raised. Repeat 3 times.
- **B2.** Same as B with software standby (bf810b6) applied. This puts a number on that item.
- **C.** Suspend, 90 min, by an rtc alarm (step 1 script with `+5400`, lid closed). Use the fork's tick method: start right after a 1% tick, and after waking stay awake until the next tick (it gives the awake current for the ratio correction).
- **C2.** As C, after writing `0` to the `*hci*_enable` switches step 0 found (only if they exist and the USB-C port is a different controller).

Convert as follows:

- mAh = ticks x (`charge_full_design` / 100) below 80%, or use mean `current_now` where it is live;
- report %/h as the primary figure;
- run C at least twice. The fork's own overnight runs disagree (53 vs 74 mA).

**Step 5. Our systems, once a prototype build exists.** Suspend for 5 min mid-play on fceumm (SMB3),
snes9x (Star Fox), Genesis Plus GX (MD, Sonic 2) and pcsx_rearmed. For PS1, use a game with CD audio or
XA, plus a multi-disc game on disc 2. After each wake, check:

- sound is clean, and `slot: audio reopened` appears with no repeated xrun lines;
- `SLOT_TRACE` p99 frame time for 60 s after the wake matches the 60 s before;
- for PS1, the disc index and `Saves/PS1/<stem>.disc` are unchanged.

Then a GBA RTC game (Pokemon Emerald) slept for 1 h: the in-game clock should advance about 1 h.

**Step 6. Stress, as the fork did:**

- 20 rapid lid flicks (count dark screens with the lid open; the fork saw 9 of 20);
- 10 POWER presses with the lid shut;
- 5 charger plug and unplug cycles while asleep.

**Step 7. Upstream 1.8.0 conflict check** (after rebasing onto upstream `main`): set Lid Off to 1 min,
suspend for 10 min, then wake with the charger while the lid is shut. Expected today: `lid.sh` powers the
device off (see `Logs/ags-shutdown-trace.log`). That confirms the watcher must learn about suspend before
any sleep patch ships.

## Recommended to adopt (ranked)

1. **Write the battery save even when the core gives no state, and report that flush as failed**
   (generic half of [dbbadae](https://github.com/suprsomething/slot.advance/commit/dbbadae)).
   - Why: upstream `flush_resume` (our app.rs:4357) returns before writing `.sav` when `state()` is `None`. The 3-minute doze power-off then loses the game in RAM. Riskiest on PS1's 4.4 MB states.
   - Effort: S.
   - Route: **upstream-first** PR (needs `Snapshot::running()` and a test with a silent mock core). Carry it only if Brandon is slow.
   - Verify: unit test (a mock snapshot that returns `None` while running still writes `.sav`). On the device, nothing to provoke. Check `slot.log` shows the new line only in the test.
2. **Ask before deleting a save state, plus Up/Down in the switcher** ([2fe9876](https://github.com/suprsomething/slot.advance/commit/2fe9876), without the ring-of-5 change).
   - Why: one Y press deletes a state today, with no undo.
   - Effort: S.
   - Route: **upstream-first** (it changes an upstream-tested plate).
   - Verify on the device:
     - Y then B keeps the state;
     - Y then A keeps it and does not load;
     - Y then Y deletes it;
     - repeat on a PS1 multi-disc state.
3. **Hardware sleep (suspend-to-RAM, lid wake, stale-lid check, unsaved-game guard)**
   ([c9e5697](https://github.com/suprsomething/slot.advance/commit/c9e5697), [d7cb474](https://github.com/suprsomething/slot.advance/commit/d7cb474), [dbbadae](https://github.com/suprsomething/slot.advance/commit/dbbadae)).
   - Why: the highest-value QoL item in the fork. Open the lid and the game is back in about 0.8 s, even hours later, at roughly 2 to 3%/h instead of a power-off and reboot. The PS1 gain is largest.
   - Effort: L. Reimplement on v1.7.0 / 1.8.0. Write a new ADR superseding 0033.
   - Gate: **only after section 9 steps 0 to 2 pass on the RG34XXSP**.
   - Route: **upstream-first discussion**. Brandon shipped `lid_off_min` and `lid.sh` on 2026-10-17, and `lid.sh` would power off a suspended device after any stray wake. Extend his Lid Off row; do not add a Sleep row or key. Keep Wi-Fi and USB untouched by default.
   - Verify: section 9 steps 1 to 7.
4. **Battery banners at 15% and 10%** ([d495461](https://github.com/suprsomething/slot.advance/commit/d495461)).
   - Why: today the only warning is the LED at 20%, and you cannot see it while playing.
   - Effort: S.
   - Route: **upstream-first**. If carried, use a separate toast file like `disc_toast.rs`; do not grow `Toast::FIXED`.
   - Verify: play from 17% down to 9% unplugged. You should see one banner at 15% and one at 10%. Plugging in re-arms them.
5. **Linux headless EGL render surface** (from [e761baa](https://github.com/suprsomething/slot.advance/commit/e761baa)).
   - Why: it runs our render and retro-shader tests under GLES 2 like the device, on Linux CI.
   - Effort: S to M.
   - Route: upstream-first (it helps upstream CI). Ours meanwhile, as a new file.
   - Verify: `EGL_PLATFORM=surfaceless cargo test -p slot-gfx` on Linux passes the same render tests as macOS. Then deliberately break GLES-only syntax in a retro shader: Linux should fail where macOS might not.
6. **Software standby while dozing** ([bf810b6](https://github.com/suprsomething/slot.advance/commit/bf810b6)).
   - Why: it stops ~60 Hz black-frame rendering behind a dark panel. It is worth more once Lid Off reaches 30 min.
   - Effort: S.
   - Route: upstream-first. Measure first (section 9, B vs B2).
   - Watch: it conflicts with patch 0015's `Pacer` hunks.
7. **Crash log cap and main-thread crash label** ([590f1f1](https://github.com/suprsomething/slot.advance/commit/590f1f1), [2c4dfbb](https://github.com/suprsomething/slot.advance/commit/2c4dfbb)).
   - Why: the card fills with crash logs, and the crash line names the wrong thread.
   - Effort: S.
   - Route: upstream-first, not worth carrying.
   - Verify: `card/test-coresave.sh` and `crates/slot/tests/crash.rs` from the fork.

## Skip

- **Ring of 5, GBA shader default Off, Wi-Fi off by default, Sleep default 30 min:** factory-default
  retunes for one device (maintainer rule). Wi-Fi off also breaks SlotLink. At most, offer them as options.
- **FF speed and FF sound chords (f399fad):** they collide with ADRs 0007, 0066, 0067 and 0068.
- **Generic per-game profile store:** breadth. A shader-only per-game line is the narrow version
  worth keeping in mind (section 3).
- **Favourites, Recents, last cart, titles:** superseded by v1.7.0 (titles' smarter name cleaner is a
  minor upstream idea).
- **USB and Wi-Fi quiet job as a default:** the board addresses are unverified on the RG34XXSP, and the
  gain while awake is unmeasured.
- **Branding, About screen, boot logo, website, label photo pack, README screenshot tooling, release naming.**
