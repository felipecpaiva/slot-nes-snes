# nelynes/slotPlus: new platforms vs slot-nes-snes

Read-only survey, 2026-10-18. Cloned every branch into `~/.cache/forks/nelynes`. Compared with
slot-nes-snes: ADRs 0001 to 0069 (the Sega ADRs 0050 to 0062 and the PS1 ADRs 0063 to 0069 in
particular), docs/PLAN.md, docs/design/modular-platforms.md, LICENSING.md, SLOT_PIN, `cores/`,
patches 0001 to 0041 and issue 66 (#129, PAL pacing). Upstream base is BrandonKowalski/slot v1.7.0
(34ac380), the same as ours. I also downloaded the five pinned core tarballs and read their
licence headers and their libretro glue.

**Nothing ports as a cherry-pick.** The fork adds fields to `Host` (`video_w`, `rotation`,
`handheld_turn`), edits upstream tests and grows `Platform::ALL`, `Core::ALL` and `SlotState`.
ADRs 0009, 0013 and 0015 forbid all three, and ADR 0053 already says we take no slotPlus code.
So every "adopt" below really means "reimplement through `HostExtra` and our policy files, using
the fork as reference, and credit nelynes". Copying a block verbatim (an input table, a pak drawing)
is allowed by the licence but would amend ADR 0053's no-code line; this doc assumes reimplementation. The fork is GPL-3.0-or-later (a fork of slot after 2026-09-17), so copying any of
it is allowed with credit. Its commits are co-authored by nelynes (robledo.gt@gmail.com).

Branches:

| Branch | Ahead of v1.7.0 | Head | What it adds |
|---|---|---|---|
| `main` | 57 commits (52 of them not merges) | [4afc8f3](https://github.com/nelynes/slotPlus/commit/4afc8f3) (tag v1.7.0-plus1.2) | WonderSwan/Color, Atari Lynx, Transparent GB shader |
| `slotPlusUltra` | main + 20 | [92b7022](https://github.com/nelynes/slotPlus/commit/92b7022) (2026-10-17, untagged) | Game Gear (Gearsystem), NeoGeo Pocket/Color, TurboGrafx-16 |

**Correction to the earlier summary:** Game Gear on Gearsystem, NeoGeo Pocket and TG16 exist
**only on `slotPlusUltra`**. `main` and its releases ship just WonderSwan and Lynx.

Link prefix: `https://github.com/nelynes/slotPlus/commit/<sha>`

## 0. Findings that hold across platforms

| Topic | Fork | What I found | Effect on us |
|---|---|---|---|
| Core licences | `licenses/<core>-GPL-2.0.txt`, source tarball and `.meta` per core, release check in `release.yml` | Re-counted in the pinned tarballs, leaving out libretro-common, deps and intl. **No GPL-2.0-only file in any of them.** Cygne: 12 of 35 files say "or any later version", 23 have no header (readme has no licence line). Lynx: 9 GPL-2.0-or-later (Mednafen glue) plus **20 zlib files (Handy, K. Wilkins)** and 20 with no header. NeoPop: 49 of 70 or-later, 20 with no header. PCE Fast: 38 of 100 or-later, 29 with no header, plus the bundled `deps/` (zlib, lzma, zstd, libchdr) and Xiph BSD `mednafen/tremor`. Gearsystem: GPL-3.0-or-later (204 of 250 files, LICENSE is GPLv3) | All five combine with GPL-3.0-or-later, so these are **cleaner than our snes9x and Genesis Plus GX stance** (non-commercial). We can call each one a combined GPL-3.0-or-later work, as we do for fceumm, and keep the separate-program stance as a fallback. Each needs a LICENSING.md section in the fceumm style (count commands, headerless list, permissive parts named). The fork's `lynx-GPL-2.0.txt` hides the zlib Handy terms. Its `pce-GPL-2.0.txt` is the GPLv2 text **twice** plus the Xiph BSD text, with no zlib, lzma or zstd notice |
| Pinning | Taskfile pins the commit only. No tarball sha256 | I computed them (GitHub archives, 2026-10-18), listed in full under the table | Ours is stricter: SLOT_PIN holds the tarball sha256, and we build for host and device. Use these as the first SLOT_PIN values and re-check them at build time |
| Pacing for cores not at 60 Hz | `Owed` in `emu.rs` ([b264635](https://github.com/nelynes/slotPlus/commit/b264635), [0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb)) carries a fractional count of frames owed per present. Above 62 fps it follows the rate the audio implies (EMA, clamped to 50 to 85 fps) and keeps the resampler ratio at the nominal rate. It also stops trimming frames at normal speed | Upstream and our `av_rate` (patch 0006) both run one frame per present, so a 75 Hz core plays at 80% speed with its pitch dropped. The audio maths checks out: `core_hz` is built on the nominal fps, so a fixed ratio passes 44.1 kHz through 1:1 while the frame count adapts. **But `Owed::new` hard-codes `nominal = 1.0` below 62 fps, so it does nothing for 50 Hz PAL.** "Never drop owed frames" changes pacing for every core, GBA included | This is issue 66 (#129) work, not a Lynx item. Adapt the accumulator so it works in both directions (50 fps owes 0 or 1 frame per present), and compare it with omega-zero's `Pace` already cited in #129. Keep upstream's frame trimming at or below 60 fps (the PS1 Spyro frames need it). Credit nelynes and oauramos |
| Rotation (`SET_ROTATION`) | Host answers `SET_ROTATION` and rotates on the CPU, one pixel at a time with a format branch per pixel, inside `video_refresh` on the core thread ([749523c](https://github.com/nelynes/slotPlus/commit/749523c), [185257a](https://github.com/nelynes/slotPlus/commit/185257a)). It also turns the pad when the handheld is held turned | Upstream v1.7.0's env handler has no `SET_ROTATION` arm (catch-all `_ => false`) and none of our 41 patches adds one. **Cygne then rotates in software itself** (`hw_rotate_enabled` false, `rotate_buf`), and its `wswan_rotate_display` = landscape / portrait / manual picks the layout. **Beetle Lynx has no software fallback**: refused, it just draws the raw frame, which is the "hold the handheld turned" layout. Upstream's compositor already has a GPU `Turn` (`set_panel_turn`), but it turns the whole output, not the game quad | See the three options in section 2.3. WonderSwan needs **no** host rotation code. Lynx needs a 180 degree flip at most, unless we want its upright "tall" view |
| Frame shape changes mid-game | `Frames` carries a `shown` size and the texture is reallocated when the buffer size changes | ADR 0050 says the canvas is chosen once at open (ADR 0015). A 360x240 canvas holds both 224x144 and 144x224, so the canvas stays fixed and only the source rect (ADR 0018) changes per frame shape | One `source_rect` hunk keyed on the frame shape. No canvas change |
| Menu freeze after a system with no colour row | [36a4029](https://github.com/nelynes/slotPlus/commit/36a4029), [e7a4807](https://github.com/nelynes/slotPlus/commit/e7a4807): `quick_value` recursed forever when `playing_row` handed the row back | Already have it: patch 0016 rewrote the same arm as `Some(self.playing_row(row)).filter(\|own\| *own != row)` | Already have. It is latent upstream (only a fourth platform triggers it), so it can ride along as a one-line hunk in modular PR 1 or 2 (ADR 0058) |
| Option key prefix | [3ca1660](https://github.com/nelynes/slotPlus/commit/3ca1660): `cygne_frameskip` was silently dropped. Fixed with `option_prefix()` | Ours has `option_prefix()` plus a declared-key check and test (patch 0003, `core_option_keys.rs`) | Already have, ours better. New prefixes: `wswan`, `lynx`, `ngp`, `pce_fast` |

Tarball sha256 at the fork's pins (`https://github.com/<org>/<repo>/archive/<commit>.tar.gz`, fetched 2026-10-18):

| Core | Commit | sha256 |
|---|---|---|
| beetle-wswan-libretro | `4b01295838ea89e3f1355bbe4cb5cf98aa6108cd` | `bce15c0e2505e15b7b55fa1d51b4a12219d07a67be62bbca5c26678d0d89c659` |
| beetle-lynx-libretro | `fcdefcfb3c11d6d2e71be076a5d3df2e88ab73ed` | `3dd45a6f6585c444a415cb097996c572467754748e7163eca466d89b31bd8b37` |
| beetle-ngp-libretro | `a50d5ac288a81f2104ddf43195a4efdd15c72227` | `ffeabf2a357548f3a55423d542c31bb1e08571d81d7104f8213df3bfa2eb9c9f` |
| beetle-pce-fast-libretro | `3f946f277aef3aa99a95551618bbcd1dd2bda0d9` | `1bc1d96f2a0957e97d50c009d25ae5725d60e80eada679dafbb214afa84cda29` |
| drhelius/Gearsystem | `517ddaaafbab1af7a312c2b6b6f6043275f58500` | `d06ce7669a18e6b137547d2799c1a3edddec6e7de191d7f38404070954d3c56c` |

## 1. NeoGeo Pocket / Pocket Color (Beetle NeoPop), `slotPlusUltra` only

Commits: [a8eae4c](https://github.com/nelynes/slotPlus/commit/a8eae4c) (core, shelf, cart, Screen
page), [1ef7226](https://github.com/nelynes/slotPlus/commit/1ef7226) (stretch both ways),
[ceb7052](https://github.com/nelynes/slotPlus/commit/ceb7052) (bezel).

| Area | Fork | Ours would be | Notes |
|---|---|---|---|
| Core, licence | libretro/beetle-ngp-libretro `a50d5ac`, `make platform=unix`, `-mcpu=cortex-a53`. Says GPL-2.0 | Same core, pinned with sha256, host and device builds. Combined GPL-3.0-or-later (no v2-only file) | RACE is the other libretro NGP core; not checked |
| BIOS | None. NeoPop's HLE stands in | Same | No BIOS work at all |
| Extensions, shelf | `.ngp .ngc .ngpc` on one `NGP` shelf | Same, one shelf | Header byte 0x23 (0x10 = colour) can pick the shell instead of the extension |
| Canvas | 160x152 in the 240x160 buffer at 3x = 480x456, 12 px bars | 240x160 canvas at 3x (ADR 0050 path, like GG). **Fills the 480-line panel almost exactly** | Best fit of any new system |
| Input | Left face = A, right face = B, Start = Option | Same via our input policy | Nothing to remap beyond that |
| Pacing | Core reports 60.25 fps, 44.1 kHz | One frame a present, as now | No pacing work |
| Saves | **NeoPop has no `SAVE_RAM`.** `retro_get_memory_data` returns only system RAM. It writes `<name>.flash` itself when the game unloads. The fork points the core's save dir at `Saves/NGP` and stops the core before power-off | Our persist path reads `SAVE_RAM` and writes atomically. With NeoPop the flash only reaches the card on unload. Flash **is** inside save states (`FLASH_StateAction`), so the resume state covers a power cut | Real durability risk (ADR 0012, 0034). It needs its own work item and a lid-close / battery-pull device test |
| Shaders | Own `shader_ngp` in `slot.state`: Off, LCD3x, Grid, Simpletex | Own Screen section (the maintainer rule), settings outside `slot.state` (ADR 0051): Off, LCD3x, Grid, Dot, plus a Transparent look (section 5): the NGP screen is an unlit reflective LCD, which is what that shader draws | LCD3x is tuned for exact 3x, which NGP is |
| Cart and art | Bitmap pak from `assets/src/carts.py`: ridged cap, wide 246x133 label, SNK/NGP plaques | Retro bitmap cart (ADR 0054), label from ScreenScraper `ngp` **25** / `ngpc` **82** (Skyscraper `platforms_idmap.csv` at ccd49ae, the commit `fetch-labels.py` already cites). Dats `SNK - Neo Geo Pocket`, `SNK - Neo Geo Pocket Color` (libretro-database `metadat/no-intro`). Title from the header (0x24, 12 bytes) | Their pak drawing is a usable reference (GPL-3.0, credit) |
| Tests | `ngp_core.rs`: a synthetic 64 KB ROM (SNK header, `jr t,-2` at the start address) boots with no BIOS, draws 160x152, states round-trip | Same recipe, in our own test files (ADR 0020, 0013) | Recipe is directly reusable as an idea |
| Device cost | Not measured in the fork | **Estimate, unmeasured:** 1 to 2 ms a frame on the H700. Mednafen-family handheld cores run full speed on Cortex-A7 handhelds, and Genesis Plus GX on GG measured 1.0 ms here (ADR 0053) | Measure at step 1 |

Work items (PS1 issue shape, #119 to #128):
1. Build beetle-ngp from a pinned commit for host and device; SLOT_PIN commit and sha256; licence record in LICENSING.md (count, headerless list). S
2. `Platform::Ngp`, shelf `Games/NGP`, scan `.ngp .ngc .ngpc`, header title and colour flag, platform policy. M
3. Core options: `ngp_language=english`, answer declared defaults (ADR 0064). S
4. Canvas 240x160 at 3x, own Screen section (Shader, Picture), Stretch/Actual (ADR 0061). S
5. **Flash save durability:** route the core's save dir into `Saves/NGP`, unload (or reload) the core on eject, lid close and power-off so `.flash` is written, and test that it survives a lid close. M
6. Input map (A, B, Option). S
7. Tests with the synthetic SNK-header ROM. S
8. Cart: NGP pak in the retro bitmap renderer, two shells (mono grey, colour), labels via `fetch-labels.py` ids 25/82. M
9. Device gate: SNK vs Capcom Match of the Millennium, Metal Slug 2nd Mission, Sonic Pocket Adventure for 10 minutes each, zero underruns; lid-close flash test. S

Effort: **M overall**. Value: **high** (strong library, perfect 3x fit, no BIOS, no rotation).
Risks: flash durability (medium); everything else low.

## 2. WonderSwan / WonderSwan Color (Beetle Cygne), `main`

Commits: [65e0508](https://github.com/nelynes/slotPlus/commit/65e0508),
[273ded9](https://github.com/nelynes/slotPlus/commit/273ded9) (core build),
[63df039](https://github.com/nelynes/slotPlus/commit/63df039) (source tarball),
[69b8379](https://github.com/nelynes/slotPlus/commit/69b8379) (shoulder modifiers for the Y pad),
[77fd357](https://github.com/nelynes/slotPlus/commit/77fd357) (cart),
[ceed887](https://github.com/nelynes/slotPlus/commit/ceed887) (360x240 buffer for vertical games),
[0f895d3](https://github.com/nelynes/slotPlus/commit/0f895d3) (vertical controls),
[2ab147a](https://github.com/nelynes/slotPlus/commit/2ab147a) (SELECT inert on horizontal games),
[3ca1660](https://github.com/nelynes/slotPlus/commit/3ca1660) (frameskip prefix),
[eabb24e](https://github.com/nelynes/slotPlus/commit/eabb24e) (own shader),
[21cc4b0](https://github.com/nelynes/slotPlus/commit/21cc4b0) (black cart for `.ws`, clear for `.wsc`).

### 2.1 What they built

| Area | Fork | Ours would be | Notes |
|---|---|---|---|
| Core, licence | libretro/beetle-wswan-libretro `4b01295`. Says GPL-2.0 | Same core with sha256. Combined GPL-3.0-or-later; 23 of 35 files have no header, so a headerless list like fceumm's | Cygne by Dox, files that carry a header are GPL-2.0-or-later |
| BIOS | None | Same | |
| Pacing | Not set, so the fork's `Owed` handles it | `wswan_60hz_mode` is **declared** `enabled`, but `libretro.c:105` starts it `false` and only a GET_VARIABLE answer turns it on. Our host answers declared defaults for pcsx only (ADR 0064), so **in our tree WonderSwan would run at 75.47 Hz**. Set `wswan_60hz_mode=enabled` explicitly: the core drops every fifth frame itself and reports `4/5 x 75.47 = 60.38` fps (`check_variables` runs in `retro_load_game`, before av info is read). Then `Owed` is not needed for WonderSwan | A host test asserts av fps 60.38. Video judder is the core's 5:4 drop, as on any 60 Hz panel |
| Canvas | 360x240 buffer. Horizontal 224x144 is shown through a 240x160 window at 3x = 672x432; a vertical 144x224 frame shows the whole buffer at 2x = 288x448 | 360x240 canvas at 2x, chosen once (ADR 0050), with a per-frame-shape source rect: horizontal uses the 240x160 centre window (3x), vertical the whole canvas (2x) | Matches the fork's geometry without touching `Host` |
| Rotation | Host rotation via `SET_ROTATION`, CPU copy | **None needed.** We do not answer `SET_ROTATION`, so Cygne rotates in software. Set `wswan_rotate_display=portrait` for an upright tall view, or `landscape` for the turned-handheld view at 3x | Zero video code. The core option is the rotation |
| Vertical detection | ROM footer byte 6, bit 0 (`ws.rs`, 21 lines) | Same probe in our `ws.rs` | Footer byte 1 is the minimum system (colour required), so a mono-compatible WSC title reads as mono: it complements the extension for the shell choice, check against the dat |
| Input | Horizontal: X pad on the D-pad; L held = D-pad drives the Y pad; R held = face diamond drives the Y pad. Vertical: D-pad is Y pad, face diamond is X pad, L/R are A/B, turned with the view. `wswan_rotate_keymap=disabled` so the host is the only mapper. SELECT is inert on horizontal games | Same scheme in our input policy (the `snes_input.rs` pattern). SELECT flips portrait/landscape on vertical games through the core option | Their mapping tables are the hard part; reimplement from them as reference, with credit |
| Shaders | Own `shader_ws` in `slot.state` from the GB list (Off, Grid, Simpletex) | Own Screen section outside `slot.state`: Off, LCD3x, Grid, Dot, Transparent (unlit reflective LCD, like NGP) | |
| Cart and art | Bitmap cart, black for `.ws`, smoke-clear for `.wsc`, `Config/cart_shell.txt` overrides | Retro bitmap cart (ADR 0054), shell from the extension plus the footer system byte. ScreenScraper `wonderswan` **45** / `wonderswancolor` **46**; dats `Bandai - WonderSwan`, `Bandai - WonderSwan Color` | WS ROMs have no title field; names come from the file and the dat |
| Tests | `crates/slot-retro/tests/wonderswan.rs` (191 lines), `ws_video.rs`, scan tests | Synthetic ROM with a valid footer, horizontal and vertical, in our own files | |
| Device cost | Not measured | **Estimate:** 1 to 2 ms a frame. Core-side software rotation adds one 32,256-pixel 16-bit copy (about 0.1 to 0.3 ms) | Measure |

### 2.2 Work items

1. Build beetle-wswan pinned, host and device, SLOT_PIN sha256, licence record with headerless list. S
2. `Platform::Ws` (one shelf for WS and WSC), scan `.ws .wsc`, footer probe (vertical, colour), policy. M
3. Core options: `wswan_frameskip` via the prefix, `wswan_rotate_keymap=disabled`, `wswan_rotate_display` per game, `wswan_60hz_mode=enabled` set explicitly (not a declared default we answer; test av fps = 60.38). S
4. Canvas 360x240 at 2x, frame-shape source rect (3x window when landscape), own Screen section. M
5. Input: modifier scheme for horizontal games, vertical maps for portrait and landscape, SELECT flips the layout only on vertical games. M
6. Tests: synthetic ROMs (horizontal, vertical), source rect per shape, input tables. M
7. Cart: WS shell black and clear, labels via ids 45/46. M
8. Device gate: Gunpey (vertical), Klonoa: Moonlight Museum, Final Fantasy (WSC), Judgement Silversword (vertical shmup), zero underruns, both layouts. S

Effort: **M to L** (input is the work, video is small). Value: **medium** (mostly a Japanese library,
but distinctive). Risks: input ergonomics on the SP's button set (low to medium); none on licence or
speed.

### 2.3 Rotation: three ways compared (applies to Lynx too)

| Option | How | CPU cost on the H700 | Shaders | Upstream touch |
|---|---|---|---|---|
| A. Core rotates (WonderSwan only) | Do not answer `SET_ROTATION`; Cygne uses `rotate_buf` | One 16-bit copy in the core, about 0.1 to 0.3 ms | Masks stay in panel axes | None |
| B. Host CPU copy (the fork) | Answer `SET_ROTATION`, rotate in `video_refresh` | Fork's per-pixel loop with a format branch: estimate 0.2 to 0.6 ms (WS 32,256 px), 0.15 to 0.3 ms (Lynx 16,320 px). An XRGB fast path in our `canvas.rs` would halve it | Masks stay in panel axes | `video_refresh` via `canvas.rs` (already ours), env arm via `HostExtra` |
| C. GPU, quad UV swap | Rotate texture coordinates in the game pass | Zero | LCD3x and Grid masks follow texture axes, so their axes must swap too | `GAME_FRAG` / `pipeline.rs`, upstream files |

Choice: A for WonderSwan. For Lynx, the raw frame already is the turned-handheld view, so only
carts flagged "right" (rotation 3) need a 180 degree flip. That is option B restricted to a flip,
which is a reversed row copy. The upright tall Lynx view needs full B; defer it until someone asks.

## 3. Atari Lynx (Beetle Lynx), `main`

Commits: [749523c](https://github.com/nelynes/slotPlus/commit/749523c) (core, shelf, rotation),
[98419f4](https://github.com/nelynes/slotPlus/commit/98419f4) (flat card cart),
[0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb) and
[b264635](https://github.com/nelynes/slotPlus/commit/b264635) (audio rate and pacing),
[d7d0e74](https://github.com/nelynes/slotPlus/commit/d7d0e74) (rotation by title),
[185257a](https://github.com/nelynes/slotPlus/commit/185257a) (play turned ccw),
[747cf1d](https://github.com/nelynes/slotPlus/commit/747cf1d) (SELECT flips turned/upright),
[d49990b](https://github.com/nelynes/slotPlus/commit/d49990b) (rotation file, real refresh rate).

| Area | Fork | Ours would be | Notes |
|---|---|---|---|
| Core, licence | libretro/beetle-lynx-libretro `fcdefcf`. Says GPL-2.0 | Same core with sha256. Combined GPL-3.0-or-later; LICENSING.md must name the **20 zlib Handy files** and the 20 with no header | Fork's licence record misses zlib |
| BIOS | `lynxboot.img` in `BIOS/`, not shipped | Same; never shipped | **Missing BIOS fails silently:** `CRom` fills the ROM with a default byte and returns, so the game loads and shows black. We need a check before launch and a toast |
| Tests | `lynx_video.rs` (geometry only) | **Real-core tests cannot run on CI**: no BIOS can be committed. Real-core tests run only when `BIOS/lynxboot.img` is present (an env-gated skip like `SLOT_REQUIRE_CORES`); CI covers geometry, input and pacing with `MockCore` | Changes the effort and risk |
| Pacing, audio | Core reports 75 fps; each game sets its own refresh. `Owed` follows the audio-implied rate and runs 1 or 2 frames a present (5 frames per 4 presents at 75 Hz) | Section 0 pacing, done as #129: fractional accumulator, audio-implied rate only for cores that declare a variable rate. `lynx_force_60hz` **only changes the reported fps** (line 483, one Lynx frame per `retro_run` regardless), so it is a 20% slowdown, not a fix | 75 Hz on a 60 Hz panel shows a 5:4 cadence judder either way  **Correction (2026-10-18, ADR 0093, `lynx_core.rs`):** the reported 75 is a constant, but the boot ROM leaves the timers at 59.9 Hz (736 sample frames a run); only a game that sets 75 Hz runs at 75. So `lynx_force_60hz` is a slowdown only for such a game, and pacing must follow the measured rate, not the reported one (issue 107) |
| Canvas | 160x102 shown through a 180x120 window at 4x = 640x408. Turned (upright view) 102x160 at 3x = 306x480 | 240x160 canvas, 180x120 source window for 4x | Only system where 4x fits |
| Rotation | Host rotation, handheld assumed turned ccw: rotation 1 drawn raw, rotation 3 drawn flipped 180; pad turned by the host. A by-title list (Klax, Gauntlet III, Lexis, NFL Football) catches dumps whose header lacks the flag; `Config/lynx_rotation.txt` overrides; SELECT flips turned/upright | Refuse `SET_ROTATION` (raw frame = turned view), 180 flip for rotation 3, keep the by-title list and the override file. `lynx.rotateinput` is hard-wired to 0 in `mednafen/settings.cpp`, **but the libretro glue turns the pad itself** (`update_input`, `map[rotate_screen]`) whenever `lynx_rot_screen` turns the screen; its default `auto` turns LEFT carts 90 and RIGHT carts 270 (corrected 2026-10-18, ADR 0093, pinned by `lynx_core.rs`). The fork leaves `auto` on and adds a host quarter turn of picture and pad for the handheld held ccw (185257a). Which turn each rotation flag needs is a device check (Klax is flagged right in the core's list, Lexis left). Read the LNX header rotation byte (0x3A) ourselves so the shelf knows before launch | Upright tall view deferred (needs option B) |
| Input | A, B; Option 1/2 on L/R; Pause on Start; SELECT reserved for the layout flip | Same | |
| Saves | Core exposes no `SAVE_RAM` (states only) | States only; say so in the README | Few Lynx carts saved anyway |
| Shaders | Own `shader_lynx` from the GBA list (Off, LCD3x, Grid, Dot) | Own Screen section: Off, Grid, Dot, retro list. LCD3x is tuned for 3x and Lynx sits at 4x | Backlit screen, so no Transparent |
| Cart and art | Flat card with contacts ([98419f4](https://github.com/nelynes/slotPlus/commit/98419f4)) | Retro bitmap card, ScreenScraper `atarilynx` **28**, dat `Atari - Lynx`; title from the LNX header (0x0A, 32 bytes) | Fork skips the header title |
| Device cost | Not measured | **Estimate:** 1 to 2.5 ms a Lynx frame, x1.25 frames a present at 75 Hz | Measure |

Work items:
1. Build beetle-lynx pinned, host and device, sha256, licence record including zlib. S
2. `Platform::Lynx`, scan `.lnx .lyx`, LNX header (title, rotation byte), policy. M
3. BIOS check before launch with a toast, README line. S
4. Pacing: lands with #129 (fractional accumulator, audio-implied rate for this core). M (shared)
5. Canvas 240x160, 4x window, own Screen section. S
6. Rotation: refuse `SET_ROTATION`, flip for rotation 3, pad turn per rotation flag (settled on the device with a left and a right cart, since the core does none), by-title list, override file. M
7. Tests: `MockCore` for pacing and input; real core only with a BIOS present. M
8. Cart: flat card, labels via id 28. M
9. Device gate (needs the maintainer's own BIOS): California Games, Chip's Challenge, Klax (turned), Blue Lightning, zero underruns at the audio-implied rate. S

Effort: **L** (BIOS, pacing, rotation, untestable on CI). Value: **low to medium** (small library,
smallest picture). Risks: medium (silent black screen without BIOS, cadence judder, CI blind spot).

## 4. TurboGrafx-16 / PC Engine HuCard (Beetle PCE Fast), `slotPlusUltra` only

Commit: [92b7022](https://github.com/nelynes/slotPlus/commit/92b7022).

| Area | Fork | Ours would be | Notes |
|---|---|---|---|
| Core, licence | libretro/beetle-pce-fast-libretro `3f946f2`. Says GPL-2.0 (the file is GPLv2 twice plus Xiph BSD) | Same core with sha256. Combined GPL-3.0-or-later; LICENSING.md names tremor (BSD), zlib, lzma, zstd and libchdr in `deps/` | CD support is compiled in but out of scope |
| BIOS | None for HuCards; CD and SuperGrafx unsupported | Same scope | |
| Extensions | `.pce` on a `TG16` shelf | Same | |
| Canvas | 720x240 buffer; up to 352 wide at 2x in a 360x240 window; 512-wide across the whole buffer | **360x240 canvas at 2x, our SNES path.** 256x240 at 2x = 512x480 fills all 480 lines exactly; 320/336/352 fit 360 at 2x; 512 wide uses the 2:1 blend that SNES hi-res uses (`copy_centred` halves any frame wider than the canvas, patch 0006, not keyed to the SNES core) | No new canvas code; overscan crop (ADR 0062) applies |
| Input | Two-button pad (`pce_fast_default_joypad_type_p1=2 Buttons`), II left, I right, Run = Start, Select reaches the game | Same; SELECT goes to the game after the chord hold (upstream c2a27a6), as on SNES | Six-button games are rare; skip |
| Pacing | 59.82 Hz | One frame a present (no change) | |
| Saves | Saves in `Saves/TG16` | Standard path (BRAM only matters for CD) | |
| Shaders | Off, LCD3x, Grid, Dot | `Shader::RETRO` list (CRT looks), own Screen section | Mostly TV games |
| Cart and art | White HuCard with gold contacts, square label | Retro bitmap HuCard, ScreenScraper `pcengine` **31**, dat `NEC - PC Engine - TurboGrafx 16`. No header title | US TurboChip vs JP HuCard variants are a later nicety |
| Tests | `pce_core.rs`, `tg16_video.rs` | Synthetic HuCard (reset vector to a spin loop) | |
| Device cost | Not measured | **Estimate:** 1.5 to 3 ms a frame | Measure; heavy titles are few on HuCard |

Work items: (1) build pinned with licence record, S; (2) `Platform::Tg16`, scan, policy, M;
(3) options, S; (4) canvas on the SNES path plus own Screen section, S; (5) input, S; (6) tests,
S; (7) HuCard cart and labels via id 31, M; (8) device gate (Bonk's Adventure, R-Type, Air Zonk,
Bomberman '93 at 512 wide modes if any), S.

Effort: **M** (it reuses our SNES canvas). Value: **high** (large, well-loved library, exact 2x fit).
Risks: low.

## 5. Everything else in the fork

| Change | Commits | What it does | Verdict | Value | Effort |
|---|---|---|---|---|---|
| Game Gear on Gearsystem | [f0e9318](https://github.com/nelynes/slotPlus/commit/f0e9318), [4f0b477](https://github.com/nelynes/slotPlus/commit/4f0b477), [77164f3](https://github.com/nelynes/slotPlus/commit/77164f3), [529d76e](https://github.com/nelynes/slotPlus/commit/529d76e), [bb68f47](https://github.com/nelynes/slotPlus/commit/bb68f47) | Gearsystem 3.9.22 (`517ddaa`, LTO, cortex-a53), no BIOS, overscan off, 1:1 PAR, 160x144 at 3x, own shader, black pak, link off | **ours better / already have.** We ship GG on Genesis Plus GX (ADR 0053, measured 1.0 ms), at 3x (ADR 0050) with LCD3x (ADR 0060) and a box per platform. Gearsystem's one real advantage is GPL-3.0-or-later, a clean licence; ADR 0053 already names it as the candidate second core for SMS and GG in the picker | low | S if ever wanted as a picker entry |
| GG bundled bezel with green power light | [5e33605](https://github.com/nelynes/slotPlus/commit/5e33605) (`assets/src/bezels.py`) | A black GG face over the 3x picture | **adapt** (art idea, optional) | low | S |
| NGP bundled bezel | [ceb7052](https://github.com/nelynes/slotPlus/commit/ceb7052) | nelynes' own NGP face | **adapt** with NGP | low | S |
| Transparent screen shader | [9201b8a](https://github.com/nelynes/slotPlus/commit/9201b8a), [0009e2c](https://github.com/nelynes/slotPlus/commit/0009e2c) | `GAME_FRAG` mode 5: LCD3x, a grainy backing showing through light pixels, a 5-tap drop shadow 2 canvas pixels down-right. Written from scratch, idea from Matt Akins' Pixel Transparency | **skip for GB/GBC** (upstream's platforms: nelynes' PR to send, not ours to carry). **adapt for NGP and WonderSwan**, which also had unlit reflective screens. Add it as a retro mode in our `RETRO_FRAG` (7th warm-up draw, ADR 0031), not as a new `GAME_FRAG` hunk | medium for NGP/WS | S to M |
| Shader per new system in `slot.state` | [eabb24e](https://github.com/nelynes/slotPlus/commit/eabb24e), [77164f3](https://github.com/nelynes/slotPlus/commit/77164f3) | `shader_ws`, `shader_lynx`, `shader_gg` fields | **ours better**: settings outside `slot.state` (ADR 0051), so older builds read the card unchanged | n/a | n/a |
| `Mould` table for cart shapes | `crates/slot-ui/src/shelf.rs`, `bitmaps.rs`, `assets/src/carts.py` | One shadow and backing per mould, PNGs generated by a Python script | **already have** the equivalent (retro renderer ADR 0042, bitmap carts ADR 0054). Their `carts.py` shapes are a drawing reference for NGP, WS, Lynx and HuCard | medium (reference) | n/a |
| WS cart colour by extension | [21cc4b0](https://github.com/nelynes/slotPlus/commit/21cc4b0) | `.ws` black, `.wsc` clear | **adapt:** extension plus the footer system byte | low | S |
| Lynx rotation by title, override file | [d7d0e74](https://github.com/nelynes/slotPlus/commit/d7d0e74) | Four titles turned regardless of dump; `Config/lynx_rotation.txt` | **adopt** with Lynx | medium for Lynx | S |
| Stretch fills both ways for new systems | [1ef7226](https://github.com/nelynes/slotPlus/commit/1ef7226) | Every new platform's stretch fills the screen | **already have** our own per-system Picture row (ADR 0061, 0046, 0052) | n/a | n/a |
| Stretch fills a 4:3 panel | [73f62b2](https://github.com/nelynes/slotPlus/commit/73f62b2) | Compositor draws over the whole 4:3 panel | **skip**: we target the 3:2 RG34XXSP (ADR 0021) | n/a | n/a |
| Owed pacing | see section 0 | Fractional frames per present | **adapt into #129** (works for 50 Hz once the 62 fps gate is lifted) | high | M |
| "Never drop owed frames at normal speed" | [0848fcb](https://github.com/nelynes/slotPlus/commit/0848fcb) | Normal speed never trims a frame on budget | **skip**: it changes GBA and PS1 pacing; keep upstream's trim at 60 Hz or below | n/a | n/a |
| Frame-shape log line | `frontend.rs` `note_frame_shape` | Logs buffer and picture size on change | **adapt** into our frame trace (patch 0015) for WS and Lynx | low | S |
| Content folders created on first boot | [1dc74aa](https://github.com/nelynes/slotPlus/commit/1dc74aa) | `Games/WS` etc. | **already have** (root.rs per platform) | n/a | n/a |
| README, site, banner, release workflow | many | Docs and a release check for the core tarballs | **skip** (ours has `zip-check.sh`) | n/a | n/a |

## 6. Upstream first?

- **Not new systems** (slot#30). None of the platforms go upstream.
- **`SET_ROTATION` and non-60 Hz pacing** are generic libretro seams. They fit ADR 0058's
  `PlayPolicy` (rotation, frames-per-present) and modular PR 4 ("Canvas and AV info from the
  core"). Do not post them alone: upstream has no core that needs them. Fold them into the
  modular proposal, and name nelynes as the fork that gains most (modular-platforms.md section 6
  already plans to).
- **Menu-freeze guard:** a one-line defensive hunk for modular PR 1 or 2.
- **Transparent shader:** nelynes' to offer Brandon for GB/GBC; we only borrow the idea for NGP/WS.

## Recommended to adopt (ranked)

1. **NeoGeo Pocket / Color on Beetle NeoPop.** Fits 3x on the 480-line panel, no BIOS, no
   rotation, light core, GPL-2.0-or-later. Plan: issue set as in section 1 (9 items). The one new
   thing is flash durability: point the core at `Saves/NGP`, unload on eject, lid close and
   power-off, and device-test a lid close. Own Screen section with a Transparent retro mode. Labels
   via ScreenScraper 25/82. Effort M, value high, risk medium (saves only). Credit nelynes for the
   synthetic-ROM recipe and the pak reference (a8eae4c).
2. **TurboGrafx-16 / PC Engine HuCard on Beetle PCE Fast.** Rides our SNES 360x240 canvas,
   including the 2:1 blend for 512-wide modes; 256x240 at 2x fills the panel exactly. Plan: section
   4 (8 items), `Shader::RETRO` list, HuCard cart, labels via 31, LICENSING.md naming the bundled
   BSD, zlib, lzma and zstd parts. Effort M, value high, risk low.
3. **Pacing for cores not at 60 Hz, as #129.** Take `Owed`'s accumulator and audio-implied rate,
   lift the 62 fps gate so 50 Hz PAL owes 0 or 1 frame per present, keep upstream's frame trim at
   or below 60 Hz, compare with omega-zero `Pace`, and record it in an ADR that amends the PAL
   non-goal. It is a prerequisite for Lynx and fixes PAL NES, SMS, MD and PS1. Effort M, value
   high, risk medium (touches the emu loop; GBA harness compare must stay at 0 diffs). Credit
   nelynes (b264635, 0848fcb) and oauramos.
4. **WonderSwan / Color on Beetle Cygne.** No host rotation: leave `SET_ROTATION` unanswered and
   drive `wswan_rotate_display`; set `wswan_60hz_mode=enabled` explicitly (our host does not answer Cygne's declared defaults, so it would otherwise run at 75.47 Hz). 360x240 canvas with a frame-shape source
   rect (3x landscape, 2x portrait). The work is the input remap; borrow the fork's tables with
   credit (69b8379, 0f895d3, 2ab147a). Footer probe for vertical and colour. Labels via 45/46.
   Effort M to L, value medium, risk low.
5. **Atari Lynx on Beetle Lynx, last.** Only after item 3. BIOS check with a toast (it otherwise
   fails to a black screen), raw-frame turned view plus a 180 degree flip for "right" carts, the
   by-title list and override file (d7d0e74), 4x window. Real-core tests run only when a BIOS is
   present. Labels via 28. Effort L, value low to medium, risk medium.

Skip: Game Gear on Gearsystem (ours is shipped and measured; keep Gearsystem as the future picker
candidate ADR 0053 names), Transparent on GB/GBC, per-system fields in `slot.state`, the 4:3 panel
fill, and "never drop owed frames".
