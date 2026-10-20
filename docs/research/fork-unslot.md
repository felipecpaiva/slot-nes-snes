# cloudwithax/unslot vs slot-nes-snes

Read-only survey, 2026-10-18. Clone of every branch of https://github.com/cloudwithax/unslot (`main`
and `multi-system`, which are the same commit, 6339c18) in `~/.cache/forks/unslot`, compared with
upstream BrandonKowalski/slot (`~/.cache/forks/slot-upstream`, head 1b20432, 2026-10-17) and with our
patched tree (patches 0001 to 0041, `~/.cache/pal/slot-nes-snes/work/slot`, slot v1.7.0 `34ac380`).
I read docs/PLAN.md (non-goals), DECISIONS.md and ADRs 0001 to 0069, PERFORMANCE.md,
research/slot-forks.md, research/fork-savethefails-snes.md, research/n64-feasibility.md and
design/modular-platforms.md. Nothing was run on the device.

Link prefix: `https://github.com/cloudwithax/unslot/commit/<sha>`

## 0. What unslot is

- **A fork, not a rewrite.** The history is upstream's: 534 of its 574 commits are Brandon's. It
  branches at upstream [0ba5370](https://github.com/BrandonKowalski/slot/commit/0ba5370) ("Power off
  on a held POWER", 2026-10-15). That is v1.7.0 plus 14 upstream commits, including the windowed sinc
  resampler (5dc5b83) and the mGBA state-size fix (656ce7e). **Those 14 are upstream's work, not
  unslot's.** Our "Ours" column is v1.7.0, so anything in that range is marked "upstream post-1.7.0".
- **Divergence:** 25 commits ahead, 10 behind upstream. Diff: 280 files, +45,381/-1,273. About 30k of
  that is assets, licence texts and a 9,357-line arcade name table. Rust is +16,236/-1,178 across 123
  files, of which crate sources are +13,860/-920 in 72 files. The heaviest are `app.rs` (+2,189),
  `scrape.rs` (+953, new), `wifi.rs` (+893, new), `platform.rs` (+828) and `libretro.rs` (+750).
- **Same crate layout as upstream.** No crate was replaced. The new modules are `slot-retro/src/hw.rs`,
  `slot-gfx/src/{offscreen,headless_egl}.rs`, `slot/src/{scrape,update,pak,wifi,bluetooth,services,
  wireguard,search,gpu}.rs`, `slot/src/input/stick.rs`, and `slot-ui/src/{media,scraped,keyboard,
  list_page,page,qr_page}.rs`. The one structural change is that upstream's per-platform matches became
  a `Spec` table (`slot-store/src/platform.rs`), and per-platform settings became an array indexed by
  platform.
- **Speed and quality caveat.** The 25 commits landed in about 25 hours (2026-10-15 22:35 to
  2026-10-16 23:10 -0400), and 24 of the 25 carry a Claude Opus 5.5 co-author line. In that time it went from
  3 systems to 55. It edits 44 upstream test files and adds 6. The repo has no CI test workflow, only
  `release.yml`, `images.yml` and `pages.yml`. The README names one tested device ("has been run on
  the RG34XX SP"), and there are no performance numbers anywhere. "Very ambitious" is fair. Every item
  below that we adopt needs our own test and a device check. None of it is proven.
- **Licence:** GPL-3.0 (upstream's LICENSE, unchanged). See section 10.

## 1. Upstream since our pin (context for every verdict)

These are upstream commits, not unslot's. They decide what is "superseded upstream", and they are a
bigger rebase risk for us than anything unslot does.

| Upstream commit | What | Effect on us |
|---|---|---|
| [5dc5b83](https://github.com/BrandonKowalski/slot/commit/5dc5b83) | Game audio resampled to 48 kHz through a windowed sinc (was linear to 32768) | Touches `resample.rs` and the audio path that patch 0018 (audio reopen, ADR 0030) and our `av_rate` stretch (patch 0006) sit on. unslot inherits it. |
| [b0fe199](https://github.com/BrandonKowalski/slot/commit/b0fe199) (v1.8.0) | **Run-ahead removed** ("scrambled saves in games with a 128 KB flash chip", #104); `tests/runahead.rs` deleted | savethefails Adopt items 1 to 3 (SNES run-ahead, the 12 ms budget guard as an upstream PR, the audio comparison tool) lose their base. The guard can no longer go upstream. unslot forked before this, so it still carries `RunAhead` in `emu.rs`: that part is superseded upstream (removed). |
| [e1bfb2b](https://github.com/BrandonKowalski/slot/commit/e1bfb2b), [2c82294](https://github.com/BrandonKowalski/slot/commit/2c82294) | Global button remapping (`slot-store/src/bindings.rs`), shortcuts and shelf keys; L2/R2 are default Rewind/FF bindings | Rewrites `gesture.rs` and `input/mask.rs` (patch 0007 TurboMode, and patches 0038/0040 `owns_triggers`). It supersedes the "per-shelf remap" idea in slot-forks.md. It does **not** hand L2/R2 to the game per system, so unslot's `game_triggers` and our `owns_triggers` are still needed. |
| [bfb8bb2](https://github.com/BrandonKowalski/slot/commit/bfb8bb2) | Left stick steers menus on Anbernics that have one: fixed codes ABS 0x02/0x03, deadzone 2048, a target list (`rg34xxsp`, ...) | Rewrites `input/evdev.rs` and `input/device.rs`, the files patch 0040 (ps1-analog) changes. Certain conflict on the next rebase. |
| [a1c3314](https://github.com/BrandonKowalski/slot/commit/a1c3314) | Core opened off the frame loop; screen lit while a ROM loads | `session.rs` and `app.rs` launch path (patches 0030 need-fullpath, 0037 discs). Helps PS1 load time for free. |

## 2. Platforms and cores

Columns: V/E/R = value (H/M/L) / effort (S/M/L) / risk.

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| One `Spec` table per system | [0c34d25](https://github.com/cloudwithax/unslot/commit/0c34d25), [00296a5](https://github.com/cloudwithax/unslot/commit/00296a5), [3da2bc3](https://github.com/cloudwithax/unslot/commit/3da2bc3) (`slot-store/src/platform.rs`) | `Spec { name, short, dir, extensions, native, picture, header, cores, shaders, shader, colour_correction, palettes, bezels, shoulders, triggers, turbo, rewind, link, bios }`, one row each, built from const bases `CONSOLE` and `HANDHELD` with `..CONSOLE`. `Platform::ALL` becomes 55 entries. Invariant tests: `every_spec_is_complete`, `dir_names_are_unique_and_round_trip`, `turbo_stays_off_a_pad_whose_x_and_y_are_its_own` | Policy methods in our own files (`platform_policy.rs`, `core_policy.rs`), plus the ADR 0058 proposal (`PlatformSpec`, `CoreSpec`, `CartLook`) | Theirs is Option A of our design, done as a hard fork. The struct-update bases give up our "a forgotten field fails to compile" rule (design 3, no `Default`). Changing `Platform::ALL` breaks upstream's pinned tests, which is why 44 test files were edited | Architectural reference only (section 8) | M/-/- | n/a (not portable) | Contradicts ADR 0013 and QUALITY-BAR (zero hunks in upstream tests) if copied | Evidence for our ADR 0058 discussion: a table scales to 55 systems |
| Core list per platform, picker from a list | 3da2bc3 (`app.rs` `Phase::Cores`, `slot-store/src/core.rs` `core_for_platform`, `runs`, `default_for`) | START on a cart whose system has 2+ cores opens a list page (Default marked, "Use This Core"). GBA keeps upstream's socket picker. `core_for_platform` drops a stored core that cannot run the platform | Pair-relative socket picker (patch 0009, ADR 0002), 2 cores per system | Ours keeps the board-and-socket look for our pairs. A list only wins for 3+ cores, which we do not have | Skip | L/M/low | 0009 | none | Fits ADR 0058 PR 3 ("picker from the platform's cores") |
| BIOS check before launch | [da1c857](https://github.com/cloudwithax/unslot/commit/da1c857) (`app.rs` `missing_bios`, `Spec::bios`, `Toast::NoBios`) | A game whose required BIOS is missing stays on the shelf. Insert is refused with a toast and a log line | PS1 falls back to HLE when the BIOS is missing (ADR 0063), so it never blocks. NES, SNES and Sega need none | Not needed by our systems | Skip, but take `bios` as a spec field idea (section 8) | L/S/low | none | none | Only with a core that needs a BIOS |
| Cores fetched from the libretro buildbot | [ed46743](https://github.com/cloudwithax/unslot/commit/ed46743) (`taskfile.yml` `FETCHED`, `vendor/cores.manifest`) | 42 cores downloaded as `nightly/linux/aarch64/latest/<core>_libretro.so.zip`. The sha256, date and URL are written down *after* download | Built from pinned source: tarball sha256, `.meta` stamp, patched source tarball shipped (ADR 0002, 0063, SUPPLY-CHAIN.md) | **Ours is better.** "latest" is unpinned, so two builds a day apart ship different cores. There is no source commit to offer under GPL §6. Buildbot builds are generic aarch64, not our `-mcpu=cortex-a53` (pcsx) flags | Skip; use only as a benchmark comparison (section 9 A) | -/-/- | none | Contradicts ADR 0002/0063 supply chain | no |
| GPU cores built from pinned source | 3da2bc3 (`cores/gles/build.sh`, `GLES_CORES` vecx, parallel_n64, flycast, ppsspp by commit) | GLES builds in a Docker box, pinned by commit | We pin the same way for our cores | Same discipline | Already have (the method) | -/-/- | none | none | no |
| Systems smoke test with hand-written ROMs | 00296a5 (`slot-retro/tests/systems.rs`) | A few bytes of machine code per system (NES NROM `JMP $C000`, SNES LoROM `BRA -2` with a valid checksum, MD, SMS, GG, PCE, NGP, WS, a PS-X EXE). Boots each real core, checks picture size range, fps, audio and a state round trip. Skips when `SLOT_SYSTEM_CORES` is unset | Per-system real-core tests already exist (`nes_fceumm.rs`, `snes_rom.rs`, `md_emu.rs`, `gg_emu.rs`, `ps1_emu.rs`, synthesized ROMs in `snes_common`) | Ours is deeper per system. Theirs is one table across all cores | Already have | L/S/none | none | none | no |
| need_fullpath load, core's valid extensions | [4cf8468](https://github.com/cloudwithax/unslot/commit/4cf8468) (`libretro.rs` `need_fullpath`, `valid_extensions`) | Path with data NULL for need_fullpath cores; reads `valid_extensions` from `retro_get_system_info` | Patch 0030, ADR 0059 (same behaviour, "drop when the upstream PR lands") | Equal | Already have | -/-/- | 0030 | none | Yes, already our upstream-first item |
| Arcade set names | 3da2bc3 (`slot-store/src/arcade.rs`, `assets/arcade_names.tsv`) | Zip name to game name from the FBNeo and MAME dats | n/a | n/a | Skip (non-goal: systems by ADR only) | -/-/- | none | PLAN non-goals | no |
| 45 further systems | 3da2bc3 | N64, Dreamcast, PSP, arcade, computers and more | NES, SNES, GG, SMS, MD, PS1 by ADR | n/a | Skip (non-goal) | -/-/- | none | PLAN "systems are added one at a time by ADR" | no |

## 3. Libretro host and rendering

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| Native canvas (frames at the core's own size) | 4cf8468 (`libretro.rs` `Canvas::{Fixed, Native}`, `slot-gfx/src/pipeline.rs` `GamePass::upload(.., size)`) | The host buffer takes each frame's size. The game texture is reallocated when the size changes. `fit_aspect` places it by the core's geometry aspect. Grid's whole-scale source uses the real texel size | Option A: fixed 360x240 canvas, SNES hi-res blended 2:1 (ADR 0004, patch 0004, 0036 for the PS1 640x480 canvas) | This is our deferred Option B (issue 36). Theirs keeps true 512x448 detail. Ours is byte-identical for GBA and has our shaders tuned to the canvas. Risk in theirs: a `glTexImage2D` reallocation on every 256/512 width switch (SNES hi-res scenes), and NEAREST sampling at non-integer scale with only Off, Grid and LCD3x for NES and SNES (shimmer) | Design reference for issue 36 only | M/L/high | 0004, 0006, 0014, 0017, 0033, 0036 | Contradicts ADR 0004 and PLAN out-of-scope "Option B" | Only if upstream ever wants variable frames |
| 4:3 picture from the core's geometry | 4cf8468, 0c34d25 (`frontend.rs`: `set_game_aspect(aspect.filter(|_| !stretched))`) | Actual places the picture at the aspect the core reports. For snes9x that is 4:3 (640x480 pillarboxed on 720x480). Stretch fills the rect | Actual (2x, 8:7 square pixels), Stretch, Crop (ADRs 0022, 0046, 0061, 0062) | Theirs gives the "TV aspect" that the savethefails review found missing in ours. On our canvas the same thing is a source rect plus a 4:3 dest rect, with no Option B | **Adapt** as a 4th picture mode, "4:3", in each system's own Picture row | M/M/low | 0032 (system-picture), 0033 (crop), `video_mode.rs` | Extends ADR 0061; the user's last pick stays the default (no factory default change) | no |
| 0RGB1555 pixel format, and as the default | 4cf8468 (`libretro.rs` `PixelFormat::Rgb1555`, default `Rgb1555`) | libretro.h says a core that never calls SET_PIXEL_FORMAT is 0RGB1555. Upstream defaults to XRGB8888 and refuses 1555 | Same as upstream | Theirs follows the spec. None of our 6 cores depend on it (all set RGB565 or XRGB8888) | Upstream-first PR (tiny) | L/S/low | 0006 (`libretro.rs` hunks) | none | **Yes, generic** |
| SET_ROTATION, quarter turns in the shader | da1c857 (`shaders.rs` `turned()`, `u_rot`) | A core can turn its picture (WonderSwan vertical, arcade) | None | Not needed by our systems | Skip | -/-/- | `shaders.rs` (0014, 0017 retro shaders use their own program, ADR 0028) | none | Generic, but upstream has no user for it |
| SET_GEOMETRY / SET_SYSTEM_AV_INFO, disk control, sticks in the host | 4cf8468 | Aspect and timing kept in `Host`; disk control 13/57/58; analog sticks per port | `HostExtra` side struct (ADR 0009, 0015), disk control with rollback and state trailer (ADR 0067), sticks (ADR 0068, patch 0040) | Ours keeps upstream's `Host` field list unchanged (upstream test helper `host_with`). Theirs edits it, and the upstream test with it | Already have | -/-/- | 0006, 0037, 0040 | ADR 0009 if copied | Part of ADR 0058 PR 4 |
| GLES hardware rendering for GPU cores | 3da2bc3 (`slot-retro/src/hw.rs`, `slot-gfx/src/offscreen.rs`, `slot/src/gpu.rs`, `slot-retro/build.rs` + `csrc/log.c`) | SET_HW_RENDER (GLES2/3 only), a GL context of the core's own on the emu thread (surfaceless/offscreen EGL), `get_current_framebuffer` from a global atomic, the GLES and EGL libraries dlopen'd `RTLD_GLOBAL`, `glReadPixels` read back every frame into the software frame buffer | None. n64-feasibility.md calls this "the single big item" | Answers our N64 spike's question (a). Cost: a synchronous readback every frame (640x480x4 = 1.2 MB) on the Mali-G31, unmeasured. There is no device fps claim anywhere | Reference for an N64 spike only; skip now | H (if N64)/L/high | none today | N64 not in scope (no ADR) | Would be upstream's call; Brandon says no new systems |
| Grid uses real texels | 4cf8468 (`whole_scale_source(.., texels)`) | Grid's whole-scale fit uses the texture size, not the GBA constants | Our retro shaders run in their own program (ADR 0028) with the canvas size | n/a for us | Already have | -/-/- | none | none | Only with variable frames |

## 4. Input and latency

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| Stick axes found from the node's capabilities | [3a8cfd0](https://github.com/cloudwithax/unslot/commit/3a8cfd0) (`input/stick.rs` `layout()`) | Reads `/sys/class/input/eventN/device/capabilities/abs`. X/Y/RX/RY is a gamepad (Bluetooth). Z/RX/RY/RZ is Anbernic stock. Y/Z/RY/RZ without X or RX is muOS. Otherwise no sticks | Fixed codes 0x02 to 0x05 with `Config/sticks.txt` overrides, found by `scripts/stick-check.sh` (patch 0040, issue 65) | Theirs needs no per-device file and covers BT pads. Ours is proven on our RG34XXSP | **Adapt**, upstream first: bfb8bb2 hard-codes 0x02/0x03 and a target list, and capability detection would replace both | M/S/low | 0040 (`sticks.rs`, `device.rs`); bfb8bb2 conflicts with it anyway | none (ADR 0068 v2 keeps its codes as the fallback) | **Yes** (to bfb8bb2's stick path), then our analog-to-core part rebases on it |
| Axis range from the kernel, centre from the resting reading | 3a8cfd0 (`stick.rs` `Range::new`, `abs_range` via EVIOCGABS) | min and max from the kernel. The centre is the value read when the node opens, unless it is more than 1/8 of the throw off (stick held), then the middle. Deadzone 7% of the throw | Range 4096 and deadzone 32 fixed, overridable in `Config/sticks.txt` | Theirs adapts to each unit's drift. Ours needs a file for a unit that differs. Keep the user's file as the override, per the "user's choice becomes the default" rule | **Adapt** with the item above | M/S/low | 0040 | none | Yes, same PR |
| Device subclass mask, analog button index | 4cf8468 (`input_state`: `device & 0xff`, `DEVICE_INDEX_ANALOG_BUTTON`) | Subclassed device ids map to the base device; analog face/shoulder buttons answer full scale | `input_state` compares `device == DEVICE_ANALOG` exactly | **Not a bug for us:** pcsx_rearmed (pinned `c8816799`, `frontend/libretro.c:3115,3261`) calls the base `RETRO_DEVICE_ANALOG`, and `get_analog_button` falls back to the digital bit when the answer is 0. Hardening only | Upstream-first, optional | L/S/none | 0040 | none | Yes, generic |
| GET_INPUT_BITMASKS answered | 4cf8468 (`ffi.rs` `51 \| 0x10000`, answered true) | Cores read the whole pad in one call instead of 16. Upstream already answers `JOYPAD_MASK` but never says so | Same as upstream | Small per-frame saving, generic | Upstream-first PR | L/S/none | 0006 (`environment` arms) | none | **Yes, generic** |
| L2/R2 to the game per system | 00296a5 (`gesture.rs` `set_game_triggers`) | Rewind and FF give up L2/R2 when the system's pad has them | `owns_triggers` (ADR 0068, patch 0038) | Equal | Already have | -/-/- | 0007, 0038; upstream e1bfb2b moves this code | none | Upstream's bindings (e1bfb2b) do not cover it |
| Sticks rest while a menu is open | 3a8cfd0 (`session.rs` `set_sticks`) | The game gets `[0; 4]` while the in-game menu is over it | Patch 0040 publishes sticks straight from the input thread (`input/device.rs:144`) | No gap in practice: the in-game menu pauses the core (upstream v1.7.0), so no frame reads the sticks while it is open | Already have (in effect) | -/-/- | 0040 | none | no |
| Pads that connect later | [75e4276](https://github.com/cloudwithax/unslot/commit/75e4276) | Input nodes opened after boot (Bluetooth pads) | Nodes picked at start (upstream) | Needs Bluetooth | Skip (non-goal) | -/-/- | `device.rs` | none | Generic, upstream's call |

## 5. Audio and pacing

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Pace at the core's own fps when it is far from 60** | 4cf8468 (`emu.rs` `frame_period`, `core_hz`, `NEAR_PANEL_HZ = 2.0`) | A core within 2 Hz of 60 runs at exactly the panel's 16.667 ms, and the resampler soaks up the difference (GBA 59.73 is unchanged). Any other rate (PAL 50, WonderSwan 75.47) keeps its own period: the deadline steps by `period`, the FF budget uses it, and `core_hz` stops stretching audio. The clock lock (`driven`) is off when `period != PRESENT`. On a mid-game `SET_SYSTEM_AV_INFO` the period and resampler are rebuilt. Tested: `a_core_near_sixty_hertz_runs_at_the_panels_rate`, `a_pal_or_75_hz_core_keeps_its_own_clock`, `audio_is_stretched_only_for_a_core_run_at_the_panels_rate` | Always paced at 60 (PRESENT). `av_rate::rebuilt_resampler(av, PRESENT, ..)` stretches audio, so PAL runs 20% fast (PLAN out-of-scope, issue 66 planned, omega-zero's `Pace` is the named reference) | Theirs is the issue 66 feature in about 30 lines, and keeps GBA identical by the 2 Hz window. A 50 Hz picture on a 60 Hz panel judders (frame repeat pattern) because the lock is off. That is unavoidable without a 50 Hz panel mode, and must be written in the ADR | **Adapt** into issue 66, as a second reference next to omega-zero 726cc34 | H/S-M/medium (judder, FF budget at 20 ms, rewind cadence) | 0006 (`av_rate`), 0010 (FF/rewind), 0015 (frame trace) | Amends the PLAN PAL non-goal (issue 66 already plans the ADR) | Ours. Upstream has no non-60 Hz core, but it is zero-behaviour for upstream, so it can ride along with ADR 0058 PR 4 |
| Bluetooth audio route | 75e4276 (`audio/alsa.rs` `set_route`, `ROUTE_CHANGES`) | A preferred ALSA device first. The output thread releases and reopens when the route changes | ADR 0030 keeps ALSA open while fed (patch 0018) | Needs Bluetooth. **Flag:** it edits the same `Playback::run` loop as patch 0018 | Skip (non-goal); track for rebase if upstream takes jgraving's Bluetooth PR | -/-/- | 0018 | ADR 0030 | Upstream's call |
| Recorded menu sounds | [f514169](https://github.com/cloudwithax/unslot/commit/f514169) (`audio/sfx.rs`, CC0 Freesound recordings) | Move, open, back, toggle, shelf and error sounds, each with a switch | None | Product choice | Skip (not ours) | -/-/- | none | none | Generic, upstream's call |
| Sinc resampler to 48 kHz | upstream 5dc5b83 | (upstream post-1.7.0) | Linear (v1.7.0) | n/a | Superseded upstream: arrives on our next rebase | -/-/- | 0006, 0018 | ADR 0030 re-check | already upstream |
| Run-ahead | upstream 4a4ba92, carried by unslot | 1-frame run-ahead, GBA on mGBA | Inherited from v1.7.0, gated `(Mgba, Gba)` | n/a | **Superseded upstream (removed in b0fe199, v1.8.0)** | -/-/- | none | savethefails adopt items 1 to 3 need a new plan | removed upstream |

## 6. UI, UX and quality of life

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| Per-platform Screen settings as an array, rows parameterised by platform | 0c34d25 (`slot_state.rs` `screens: [Screen; COUNT]`, `Screen { shader, colour_correction, bezel }`, `settings_parent` (GBC falls back to GB); `quick_menu.rs` `QuickRow::{ScreenOf, ShaderOf, ColourCorrectionOf, BezelOf}(Platform)`) | Every system has its own Screen section. Keys are written as `<setting>_<dir>`, so upstream's `shader_gba` and `bezel_gb` keep their names | Our own Screen section per system (ADR 0048, 0061), Sega shaders in `Config/sega_shaders.txt` (ADR 0051), named test sites (f), (g), (h) | Theirs meets the maintainer's "own Screen section per system" rule. The keys still read on upstream, but the write order changes (interleaved per platform), so `slot.state` bytes differ. That breaks our "same slot.state bytes" design goal and upstream's `durability.rs` | Architectural reference (section 8): option (a) of our design 3.5, without the consts | M/-/- | 0016, 0023, 0027, 0032 (all quick-menu hunks) | ADR 0013, 0034, 0051 if copied | Feeds ADR 0058 PR 7 |
| Disc row in the in-game menu | da1c857 (`QuickRow::Disc`, hidden for one-disc games) | Left/right swaps the disc; the core's count and index are mirrored through an atomic | SELECT+L2 on PS1 (ADR 0067 amendment), rollback on refusal, `Saves/PS1/<stem>.disc`, `SLOTPSX1` state trailer | **Ours is better** on mechanics: theirs has no rollback, no disc memory and no disc in states. Theirs is easier to discover | Already have; keep the chord until the maintainer adds a test site for a row (ADR 0067 says so) | L/S/low | 0037 | ADR 0067 (a row needs a named test site) | no |
| Search every shelf by name | 3da2bc3 (`slot/src/search.rs`, X on the shelf, d-pad keyboard `slot-ui/src/keyboard.rs`) | Word-prefix ranking (`rank`, 3 tiers), at most 300 results with each game's media; A turns to its shelf | Letter jump (upstream) | Generic QoL. It needs the 550-line keyboard | Skip for us; upstream idea | L/M/low | none | none | Generic: upstream's call |
| Button legends on every page | f514169, [05c4e2b](https://github.com/cloudwithax/unslot/commit/05c4e2b) | Each page shows its buttons and what they do for the current row | Upstream carousel footer (6f5eca1, post-1.7.0) | Generic | Skip (upstream's design) | -/-/- | none | none | Generic |
| 12-hour clock | [988bcca](https://github.com/cloudwithax/unslot/commit/988bcca) | A Clock setting | None | Generic | Skip | -/-/- | none | none | Generic |
| Haptics on menu events | f514169 | Rumble motor nudge for eject, setting change, refusal | None | Product choice | Skip | -/-/- | none | none | Generic |
| Bundled JPG wallpapers | [d0bbfd2](https://github.com/cloudwithax/unslot/commit/d0bbfd2) | 12 wallpapers, JPG decoding | None | Product choice | Skip | -/-/- | none | none | Generic |
| Labels appear on the shelf as soon as they are scraped | f514169 | Label cache refreshed live | Restart slot after `fetch-labels.py` pushes | Needs the on-device scraper | Skip | -/-/- | 0020, `label_cache.rs` | none | no |
| Wi-Fi, Bluetooth, SSH/SMB/Tailscale/WireGuard, QR sign-in | [d0c17b1](https://github.com/cloudwithax/unslot/commit/d0c17b1), 75e4276, [d501dd8](https://github.com/cloudwithax/unslot/commit/d501dd8) | About 4,000 lines plus vendored Tailscale, wireguard-go and Samba | None | Product choice | Skip (non-goal) | -/-/- | none | PLAN Spec "who it's NOT for" | Upstream's call (jgraving's Bluetooth branch is the likely PR) |

## 7. Power, sleep and updates

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| Held POWER powers off; Restart on About's X | upstream 0ba5370 | (upstream post-1.7.0, unslot's base) | Upstream lid doze (ADR 0033) | n/a | Superseded upstream: arrives on rebase | -/-/- | none | none | already upstream |
| Signed `.pak` updates, OTA, rollback after 3 failed starts | [01b46fc](https://github.com/cloudwithax/unslot/commit/01b46fc), 3da2bc3 (`pak.rs` ed25519 `verify_strict`, `card/System/launch_frontend.sh` trial counter, `System.old`) | The release key signs the version and the zip's checksum. A pak that fails the check is renamed `.bad`. After a swap the new System has 3 starts to draw a frame, or the old one comes back | Manual install: unzip, replace `System/` (PLAN success item 5) | The rollback is a nice safety net, but it only works with an installer that keeps `System.old`. Ours has none | Skip | L/M/low | none | none | Upstream's call (needs OTA) |
| SSH left to BaseOS | [edc0fc7](https://github.com/cloudwithax/unslot/commit/edc0fc7) | Stops a second dropbear racing for the port | n/a | n/a | Skip | -/-/- | none | none | no |

## 8. Art

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Logo Only label renderer** | [0b0f3a3](https://github.com/cloudwithax/unslot/commit/0b0f3a3) (`slot-ui/src/scraped.rs`, 313 lines) | A Rust port of Cart Studio's "Logo Only" style (its gradient, brightness split, logo box, olive-to-amber rule, box-art hue), from Cart Studio's `label.rs` and `hue.rs`, on resvg/tiny_skia (already in slot-ui). Falls back to covering the box art when there is no logo | ADR 0014: "With no label texture the fallback is Logo Only (a logo on a generated ground)". `fetch-labels.py` says this fallback **is not implemented** ("needs image code beyond the standard library") | Theirs is exactly our missing fallback, in our language and on our dependencies. Its box-art fallback goes beyond ADR 0014 (only SMS and PS1 use box art, ADRs 0057, 0069); drop it | **Adopt** as a Rust example (like `retro_neutrals.rs`, ADR 0054) that `fetch-labels.py --by-name` calls for ROMs left without a label scan, fed by libretro-thumbnails `Named_Logos` | M/S-M/low | none (new files) | none; it implements ADR 0014's fallback | Cart Studio already has Logo Only; the gap is ours |
| On-device scraper | 0b0f3a3, [cc292c0](https://github.com/cloudwithax/unslot/commit/cc292c0), 988bcca (`slot/src/scrape.rs`) | libretro-database dats (CRC and name), libretro-thumbnails logos and box art, ScreenScraper `jeuInfos` first when a devid is present; runs while you play | `tools/fetch-labels.py`: real label scans (art.slot-cfw.fyi, ScreenScraper support-texture), header-aware CRCs, siblings, aliases, review list (#136) | **Ours is better on quality.** Theirs: (1) `crc_of` hashes the whole file, so an SNES `.smc` with a 512-byte copier header or an MD `.smd` interleaved dump never matches by CRC (ours, `fetch-labels.py` `crcs()`, tries SNES without the copier header, MD de-interleaved, NES with and without the iNES header); (2) it makes logo labels, not real label art (ADR 0014); (3) it needs Wi-Fi. Its ScreenScraper call (CRC, size and name in one request, as ES-DE does) matches ours | Skip | -/-/- | none | ADR 0014, 0032 | no |
| ScreenScraper developer id compiled in | 988bcca (`option_env!("UNSLOT_SS_DEVID")`, from release secrets) | The release binary carries the devid and password | We wait for our own devid; the user supplies `SS_DEVID` (ADR 0032) | A compiled-in credential can be pulled out of the binary; check ScreenScraper's terms before anyone does this | **Never copy** | -/-/- | none | ADR 0032 | no |
| Neutral shells modelled in Blender | [afcb637](https://github.com/cloudwithax/unslot/commit/afcb637), f514169, 3da2bc3 (`tools/media/render_media.py`, `assets/*_neutral.png`, `slot-ui/src/media.rs`) | Each medium modelled at real size in mm, lit from the upper left, orthographic, 50% grey with a moulded stipple, scaled so the flat face is 128 for upstream's Overlay. The script prints the label box | ADR 0054: generated 50% grey bitmaps lit from measurements of `gba_neutral.png` (`retro_neutrals.rs`); NES, Famicom, SNES, SFC variants (ADR 0006); Sega one box per platform (ADR 0056); PS1 jewel cases (ADR 0069) | Same idea, different tool. Theirs has real depth from a 3D model. Ours is byte-reproducible in Rust with no Blender, and has the regional variants theirs lacks (one NES, one SNES shape) | Skip the assets. Keep the Blender pipeline as an option if a shape ever needs real depth (3D disc, ADR 0069 "deferred") | L/M/low | 0023, 0028, 0039 | ADR 0054 | no |

## 9. Tooling and CI

| Change | Commits | What it does | Ours | Better/worse | Verdict | V/E/R | Conflicts with our patches | ADR conflict | Upstream? |
|---|---|---|---|---|---|---|---|---|---|
| **Render tests on Linux through surfaceless Mesa EGL** | [42ef0f8](https://github.com/cloudwithax/unslot/commit/42ef0f8) (`slot-gfx/src/headless_egl.rs`, 179 lines; `#![cfg(any(target_os = "macos", target_os = "linux"))]` on 10 render test files) | `HeadlessSurface` on `EGL_PLATFORM_SURFACELESS_MESA` with a GLES2 pbuffer, so `render*.rs` run on a Linux box with no display | macOS is the only render host (ADR 0010); GPU pixel tests run as information on CI (ADR 0035) | llvmpipe is software and deterministic, so our Linux job could gate render tests, not just build. Its hashes will not equal macOS's, so the layout hash tests (ADR 0045) need their own expected values per OS | **Adopt, upstream first** | M/S/low | none (new file, cfg lines in test files are upstream's) | Amends ADR 0035 once upstream has it | **Yes, generic** |
| Flashable BaseOS card images per model | [49efd0e](https://github.com/cloudwithax/unslot/commit/49efd0e), [9cc4b8b](https://github.com/cloudwithax/unslot/commit/9cc4b8b), [6339c18](https://github.com/cloudwithax/unslot/commit/6339c18), [e4e5b7a](https://github.com/cloudwithax/unslot/commit/e4e5b7a) (`tools/image`, `images.yml`) | BaseOS TF1 image with the frontend on the card partition, kept through first-boot format | Zip plus source tarball | Convenience. We are H700-only and install by copy | Skip | L/M/low | none | none | Brandon's call |
| No CI test job | (absence) | Only release, images and pages workflows | macOS test job, Linux arm device build (ADR 0010) | Ours is better | n/a | -/-/- | n/a | n/a | n/a |

## 10. Architectural ideas worth borrowing (code not portable)

Compared with design/modular-platforms.md and ADR 0058:

1. **Proof that a table scales.** unslot runs 55 systems off one `Spec` row each, with 47 cores in
   one `Core` list. That is the strongest evidence yet for our discussion #64 draft. It also shows
   what we must avoid: 44 upstream test files edited, because `Platform::ALL` changed shape. Our
   `SHELVES`/`ALL` split and the extension stub (design 3.6, option C) are what keep upstream's tests
   unedited.
2. **Fields our `PlatformSpec` lacks:**
   - `rewind: bool`, so the PS1 no-rewind rule (ADR 0066) becomes data, not a match;
   - `bios: &[&str]`, with `a|b` alternatives;
   - `native: bool`, if Option B ever lands;
   - `short` names for narrow columns.

   Our `Caps.runahead` field is moot now that upstream removed run-ahead (b0fe199); drop it from the
   design.
3. **Invariant tests on the table:** "every spec is complete", "default shader is in the offered
   list", "dir names round-trip". These are cheap, and they replace the exhaustive matches as the
   safety net. Add them to PR 2 of the plan.
4. **Do not copy `..CONSOLE` defaults.** They give up "a forgotten field fails to compile", which
   is design section 3's main argument for a table over a trait.
5. **Settings keyed `<setting>_<dir>` in `slot.state`.** It is simpler than our proposed
   `Config/platform_settings.txt`, and upstream's three keys keep their names. The cost is that the
   write order changes for upstream's own keys (`durability.rs`). A middle path for PR 7: upstream
   writes its own keys first in today's order, then appends `<setting>_<dir>` for any other
   platform. One file, upstream's bytes unchanged.
6. **`QuickRow::ScreenOf(Platform)`, `ShaderOf(Platform)`.** This is our design 3.5 option (a)
   without the compatibility consts. It confirms the payload-variant shape works across about 220
   rows.
7. **`frame_period` belongs in PR 4** ("canvas and AV info from the core"): zero behaviour for
   upstream's cores, and it lets a module bring a 50 or 75 Hz system.

## 11. Device measurement plan (for you to run; I ran nothing)

unslot makes no performance claims. These runs check the two things it does differently that could
matter to us: buildbot nightly cores, and pacing. Our scripts do the device transport themselves. Do
file swaps by mounting the card on the Mac. The log lines our parser reads are the same in unslot
(`slot: boot: first frame at`, `device_app.rs:181`; `slot: launch: first frame shown at`,
`session.rs:313`; the `slot: audio: .. queued, .. dropped, .. starved` line, `emu.rs:892`), so
`auto-play.sh eval` parses an unslot log as it is.

**A. Core cost: our pinned builds vs buildbot nightly** (decides whether "buildbot is fine" is a
real argument).

1. On the Mac, download `https://buildbot.libretro.com/nightly/linux/aarch64/latest/<core>_libretro.so.zip`
   for fceumm, snes9x, genesis_plus_gx and pcsx_rearmed. Note each sha256 and the date (it is
   "latest").
2. Mount the card. For one core at a time, rename `System/<core>_libretro.so` to `.ours`, then copy
   the buildbot file in under the real name.
3. Run `BENCH_NO_BUILD=1 CORE=snes9x ROM_ON_DEVICE='/mnt/sdcard/Games/SNES/<heavy title>' sh scripts/bench-device.sh`
   with the device on the charger and rested. Run it 3 times interleaved with ours (swap back
   between runs). Use the PERFORMANCE.md workloads: Super Mario RPG for snes9x, Kirby's Adventure
   for fceumm, the MD heavy title, CTR for pcsx_rearmed.
4. Compare the minimum repeat median frames/s. A gap under 2% is noise (bench-compare.sh rule).
   Put the original file back.

**B. Whole frontend, unslot vs ours, same ROMs** (optional, a second card).

1. Flash or copy unslot v2.2.0 to a spare card with the same NES and SNES ROMs.
2. Do not use our PS1 pair: unslot's folder is `PS`, ours is `PS1`.
3. Run `task perf:play PLATFORM=snes CORE=snes9x STEM='<card name>' MINUTES=10 RUNS=3` against each
   card, then `sh scripts/auto-play.sh eval`.
4. Read "Boot to first frame", "Insert or resume to first game frame", starved and dropped samples,
   and "Present interval p99, worst window".
5. Caveat: unslot's base is upstream 14 commits past ours (sinc resampler), so a difference in audio
   lines is not unslot's own work.

**C. PAL pacing, after the issue 66 patch** (verifies the adapt).

1. Use a PAL NES title and a PAL MD title you own.
2. Run `task perf:play PLATFORM=nes CORE=fceumm STEM='<PAL title>' MINUTES=10 RUNS=1` with
   `SLOT_TRACE` on.
3. Pass if all of these hold:
   - emulated frames per second is 50 ± 0.5 (from the trace lines);
   - starved is 0 and dropped is 0;
   - "Present period, median" stays 16.7 ms (the panel);
   - an NTSC title in the same session is unchanged;
   - the GBA harness compare is still 0 diffs.
4. Watch for judder by eye on scrolling (expected; it goes in the ADR).

**D. Stick detection, after the 0040 adapt.**

1. Run `sh scripts/stick-check.sh live` on the device itself (it reads the node directly, no adb).
2. Confirm that the capability bitmap gives Z/RX/RY/RZ.
3. Confirm that the centre read at open sits within the deadzone with the stick at rest.
4. Delete `Config/sticks.txt` and check that a PS1 analog game still steers.

## 12. Licence and credit

- **unslot is GPL-3.0** (upstream's LICENSE, unchanged; its base is after upstream's 2026-09-17
  move to GPL-3.0-or-later). That is compatible with us. Credit "cloudwithax/unslot" with commit
  links in the patch header and LICENSING.md for anything taken:
  - `scraped.rs` (0b0f3a3) is itself a port of Brandon's Cart Studio (GPL-3.0-or-later), so credit
    both;
  - `frame_period` (4cf8468);
  - `stick.rs` `layout`/`Range` (3a8cfd0);
  - `headless_egl.rs` (42ef0f8).
- 24 of the 25 commits carry a Claude Opus 5.5 co-author line. That changes nothing legally for us; it is a reason
  to test, not trust.
- **Do not copy unslot's distribution model.** It ships 42 buildbot "latest" GPL binaries with
  licence texts but no corresponding source or source commit. It also ships spruceOS's prebuilt
  Samba (GPL-3.0) with no source. Our pinned-source, source-tarball model (ADR 0002, SUPPLY-CHAIN.md)
  is the one that complies.
- snes9x, fmsx, mame2003_plus and picodrive are non-commercial, as ours is (ADR 0002).
- FinalBurn Neo's licence made unslot drop its Ko-fi link. It applies to us since ADR 0099 (FBNeo for Neo Geo, CPS1 and CPS2): this project asks for no donations anywhere.
- Assets:
  - menu sounds are CC0 Freesound recordings (`licenses/sounds.txt`);
  - wallpapers are listed in `licenses/wallpapers.txt`;
  - the Blender neutrals are GPL-3.0 with the repo.

  We take none of them.

## Skipped

**Skip** (one line each):

- native canvas (our deferred Option B, ADR 0004);
- GLES HW render (reference for an N64 spike only, no ADR);
- the 45 extra systems, arcade names, Wi-Fi, Bluetooth, services, OTA and signed paks, card images
  (non-goals or product choices);
- the on-device scraper (logo labels and whole-file CRC, needs Wi-Fi);
- the compiled-in ScreenScraper devid (ADR 0032);
- buildbot nightly cores (supply chain, GPL source gap);
- the Disc row (ours is safer, a row needs a test site);
- search, button legends, 12-hour clock, sounds, haptics, wallpapers (generic, upstream's call);
- the list core picker (we have 2 cores per system);
- the Blender neutrals (ADR 0054, no regional variants).

**Separate from unslot, raised by this survey:** upstream v1.8.0 removed run-ahead (b0fe199). That
retires savethefails Adopt items 1 to 3, and those docs should say so. The rebase onto current
upstream also conflicts with patches 0007, 0038 and 0040, through e1bfb2b, 2c82294 and bfb8bb2.

## Recommended to adopt (ranked)

1. **PAL pacing from `frame_period` (issue 66).**
   - **What:** pace a core at its own period when its fps is more than 2 Hz from 60, keep 60 Hz
     locking and audio stretch inside the window, rebuild on `SET_SYSTEM_AV_INFO`. This replaces
     `av_rate`'s always-PRESENT stretch in patch 0006.
   - **Why:** PAL titles run 20% fast today. It is the planned issue 66, and this is a tested,
     30-line reference next to omega-zero's `Pace`.
   - **Effort:** S-M. Needs an ADR amending the PAL non-goal, `tests/pal_pacing.rs` (issue 66 table),
     and a check of FF and rewind budgets at 20 ms.
   - **Upstream-first or ours:** ours, offered as part of ADR 0058 PR 4.
   - **Verify:** plan C, plus the GBA harness compare at 0 diffs.
2. **Logo Only label fallback (ADR 0014) from `scraped.rs`.**
   - **What:** a Rust example (`slot-ui/examples`, like `retro_neutrals.rs`) that renders a
     `Named_Logos` PNG onto Cart Studio's Logo Only ground. `fetch-labels.py --by-name` calls it for
     ROMs left without a label scan. Drop unslot's box-art fallback.
   - **Why:** ADR 0014 promises this fallback, and our fetcher says it is missing. This is the
     missing piece, in Rust, on deps slot-ui already has.
   - **Effort:** S-M.
   - **Upstream-first or ours:** ours (Cart Studio already has the style).
   - **Verify:** run `fetch-labels.py --card` on a card with a hack or translation that has no scan.
     Judge the label side by side with Cart Studio's Logo Only output, then on the device shelf in
     both themes.
3. **Stick detection by capability, kernel range and rest centre (patch 0040).**
   - **What:** `layout()` from `capabilities/abs`, the range from EVIOCGABS, the centre from the
     resting value. `Config/sticks.txt` stays as the user's override.
   - **Why:** the next rebase onto bfb8bb2 rewrites `evdev.rs` and `device.rs` anyway. Detection
     removes the per-unit file and covers BT pads.
   - **Effort:** S.
   - **Upstream-first or ours:** **upstream first** (it improves bfb8bb2's hard-coded codes and
     target list); our analog-to-core part rebases on it.
   - **Verify:** plan D.
4. **Surfaceless Mesa EGL for render tests on Linux.**
   - **What:** `headless_egl.rs` plus the cfg widening.
   - **Why:** our Linux job could gate the render tests that ADR 0035 now runs as information only.
   - **Effort:** S.
   - **Upstream-first or ours:** **upstream first**; amend ADR 0035 and 0045 (per-OS expected
     hashes) when it lands.
   - **Verify:** `task check` on macOS unchanged; the Linux job runs `render*.rs` green twice in a
     row with the same hashes. No device needed.
5. **A 4:3 picture mode in each system's Picture row.**
   - **What:** the "TV aspect" unslot gets from the core geometry, done on our canvas: a dest rect at
     the core's reported aspect (4:3 for snes9x, NES by fceumm's aspect option) inside the screen
     rect. It sits after Actual, Stretch and Crop, and the user's last pick stays the default.
   - **Why:** the savethefails review also found it missing, and it needs no Option B.
   - **Effort:** M (ADR amending 0061, our own test site rules).
   - **Upstream-first or ours:** ours.
   - **Verify:** `render_picture_modes`-style frame test, then device check of SNES and NES at 4:3
     with Line and Sharp shaders (no shimmer).
6. **Two small libretro environment fixes.**
   - **What:** answer GET_INPUT_BITMASKS (`51 | 0x10000`), and default to and accept 0RGB1555 per
     libretro.h.
   - **Why:** spec conformance and fewer input calls. Low value to our 6 cores.
   - **Effort:** S.
   - **Upstream-first or ours:** **upstream first**; carry nothing until it lands.
   - **Verify:** upstream suite plus our `core_bench` within 2% (bench-compare.sh).
7. **Design notes into ADR 0058's plan (no code).**
   - **What:**
     - add `rewind`, `bios` and `short` to `PlatformSpec`;
     - add the table invariant tests to PR 2;
     - drop `Caps.runahead` (upstream removed run-ahead);
     - in PR 7, write upstream's keys first, then `<setting>_<dir>`;
     - cite unslot as the 55-system proof in the discussion draft.
   - **Effort:** S.
   - **Verify:** n/a.
