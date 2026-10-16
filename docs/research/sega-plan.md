# Sega Game Gear, Master System and Mega Drive for slot-nes-snes: research and plan

Date: 2026-10-15. Read-only research. Base: v1.7.0 port, branch `rebase-v1.7.0`
(` patched tree `work/slot`, 20 patches, 46 ADRs).
Sources cloned into `$TMPDIR`: nelynes/slotPlus (all 4 branches), libretro/Genesis-Plus-GX (393f70c,
2026-10-09), libretro/picodrive (1890c29), drhelius/Gearsystem (e54b9fa), libretro/blastem (ab74365).

Markers: **verified** = read in source or a page opened today. **unverified** = recalled or inferred,
must be checked before it goes into an ADR or a colour table.

---

## 1. nelynes/slotPlus

### 1.1 What it is

| Branch | vs upstream main | Content |
|---|---|---|
| `main` | 52 ahead / 0 behind | WonderSwan (Beetle Cygne), Atari Lynx (Beetle Lynx), WS/Lynx shaders, Transparent GB shader, merged with v1.7.0 ("Merge upstream-1.7", a6a80e7) |
| `upstream-1.7` | 49 / 0 | same minus the release changelogs |
| `transparent-shader` | 47 / 81 | v1.6.0 based |
| `slotPlusUltra` | 49 / 81 | **the only branch with Game Gear**, v1.6.0 based, not ported to v1.7.0 |

Game Gear commits (all on `slotPlusUltra`, verified):
- [f0e9318](https://github.com/nelynes/slotPlus/commit/f0e9318d33c172204eb9509edac0715b86d4395a) Add Sega Game Gear support (Gearsystem core, shelf, cart). 29 files, +1315/-48.
- [4f0b477](https://github.com/nelynes/slotPlus/commit/4f0b4774201cd6b0837c84d98303af1d612ebb67) reshape the pak to the real cart (squarish, label about 1.31:1, 260x198 label art).
- [77164f3](https://github.com/nelynes/slotPlus/commit/77164f32adddef08706483f74f5628726e3eccc1) GG gets its own shader (`shader_gg` in `slot.state`, a "GG Shader" quick-menu row; edits `durability.rs` and `quick_menu.rs` tests).
- Related WS plumbing: [ceed887](https://github.com/nelynes/slotPlus/commit/ceed8874a8d385a8c34c5eba681fee93066afa67) per-platform video buffer (`Platform::source_size`, 360x240 for WS).

### 1.2 How it adds a platform (verified from the diffs)

- **A git fork, not a patch set.** It commits on top of upstream and merges upstream releases. No
  `patches/`, no `SLOT_PIN`, no `.meta` provenance for the frontend (cores do get slot-style
  `cores/<core>/build.sh` with a stamp).
- **No generic hook.** Each platform is a new arm in every match: `Platform::ALL` grows (3 to 6),
  `Core::ALL` grows (2 to 5), app.rs arms (`slot_owns_the_shoulders`, `screen_shader`, shader cycle,
  link refuse), `core.rs` (`colour_option`, `has_frameskip`, `apply_core_options`), `session.rs` input
  masks per core.
- **Edits upstream tests freely.** `main` vs upstream touches 17 test files (+873/-16), including
  `slot-store/tests/platform.rs` (rewrites the `ALL` assertions), `durability.rs` (+55), `quick_menu.rs`,
  `render_shelf.rs`, `chrome.rs`, `gpsp.rs`, `toast.rs`.
- **Adds fields to `Host`** (ceed887: `video_w`, `video_h`, `shown_w`, `shown_h`), which breaks the
  in-source `host_with()` helper. That is exactly what our ADR 0009 forbids.
- **Canvas:** `Platform::source_size()` per platform (240x160 for GBA/GB/Lynx/GG, 360x240 for WS),
  same idea as our ADR 0004 canvas but keyed by platform and stored in `Host`.
- **Game Gear specifics:** Gearsystem 3.9.22 (GPL-3.0) built `make -C platforms/libretro platform=unix
  LTO=1` with `-mcpu=cortex-a53`; options `gearsystem_bios_gg/sms=Disabled`, `gearsystem_overscan=Disabled`,
  `gearsystem_aspect_ratio=1:1 PAR`, `gearsystem_link_enable=Disabled`; no frameskip option; picture
  160x144 on the Game Boy path (3x, GB shader list, L1/R1 owned by slot); **SELECT masked out because
  Gearsystem treats SELECT as a console reset**; no colour correction; black GG cart from a new SVG
  (`gg_cart.svg`, the v1.6.0 silhouette path, which v1.7.0 deleted, ADR 0042).
- **Tests:** `slot/tests/gg_core.rs` (real core), scan, platform, cart tests; plus edits to upstream ones.
- **Licence:** GPL-3.0 (LICENSE file is GPL-3). Code may be borrowed with credit.

### 1.3 Compatibility with our rules

| Our rule | slotPlus | Verdict |
|---|---|---|
| Patch set over pinned release (ADR 0001) | git fork with merges | incompatible as a delivery model |
| Exhaustive policy methods, `ALL` untouched, `SHELVES` parallel (PLAN Approach) | grows `ALL`, scattered arms | incompatible |
| Upstream tests unmodified except named sites (ADR 0013/0044) | edits 17 test files | incompatible |
| `Host` untouched (ADR 0009) | adds 4 fields | incompatible |
| Touch-point map (ADR 0024) | none | n/a |

Reusable, with credit (GPL-3.0): the Gearsystem `build.sh` recipe, the Gearsystem option keys above,
the SELECT-reset mask, and the GG cart proportions as a starting point for research (not as cited
values). Their GG code itself cannot be cherry-picked: it sits on v1.6.0 and on the deleted SVG cart path.

### 1.4 Shared "add a platform" hook and upstream-first

- The seam worth proposing is ours, not theirs: `Platform::SHELVES` beside an unchanged `ALL`, plus
  per-platform policy methods in their own file (`owns_shoulders`, `passes_xy_through`, `picker_cores`,
  `stretch_crops_height`, `shader_choices`, `Core::canvas`, `option_prefix`), and `HostExtra` for new
  libretro state. With it upstream, each new system becomes new files plus one token per remaining
  upstream match, for us and for slotPlus alike.
- Upstream-first reality: slot#30 says "slot will not be adding support for more systems", and our
  only frontend PR (#75 lazy shelf) was closed, then reimplemented by the owner in v1.7.0. A
  behaviour-neutral refactor PR is the only thing that could land, and it would still be a
  maintenance cost the owner did not ask for. **Likely declined.** The right first move is a
  comment on discussion #64 asking whether he would take a zero-behaviour "platform policy" refactor,
  optionally co-signed with nelynes. Do not open a PR unasked.
- Collaborating with nelynes: worth a note (they would gain the most from the seam), but our rules
  would require them to drop the test edits and the `Host` fields. Treat as an invitation, not a dependency.

---

## 2. Cores, licences, performance

### 2.1 Candidates (verified from the cloned sources)

| Core | Systems | Licence | aarch64 build | Notes |
|---|---|---|---|---|
| **Genesis Plus GX** | MD, SMS, GG, SG-1000, Mega-CD, Pico | Custom **non-commercial** (Charles MacDonald, Eke-Eke, MAME portions): "Redistributions may not be sold, nor may they be used in a commercial product or activity"; modified redistributions must ship complete source. LICENSE.txt also carries Nuked OPN2 (LGPL-2.1) and other notices | plain C, no JIT | 1 core covers all three; `STATE_SIZE 0xfd000` (~1 MB, fixed, `retro_serialize_size` returns it) |
| **PicoDrive** | MD, SMS, GG, 32X, Mega-CD, Pico | **Same non-commercial text** as GPGX (MAME-style) in `COPYING` | on aarch64 the Makefile selects the C cores FAME (68k) and CZ80 (`use_fame ?= 1`, `use_cz80 ?= 1`); Cyclone/DrZ80 ARM asm are ARM32 only; SH2 DRC exists for aarch64 (32X), SVP DRC is ARM32 only (Virtua Racing interpreted, unverified speed) | the speed-first core |
| **Gearsystem** | SMS, GG, SG-1000 | **GPL-3.0** | plain C++ | only GPL-clean SMS/GG option; slotPlus uses it |
| **BlastEm** | MD (+ some SMS) | **GPL-3.0** | Makefile: anything not x86 sets `NEW_CORE:=1` (generated interpreter 68k and Z80, no JIT); `Makefile.libretro` notes Android/aarch64 "take the generated cores" | treat as unviable on H700 until measured |

Not checked: clownmdemu (licence and speed unverified). Leave out of v1.

### 2.2 Licence fit

- slot is GPL-3.0-or-later. GPGX and PicoDrive are not GPL-compatible, exactly like snes9x. The same
  stance applies (LICENSING.md, ADR 0002): a separately loaded `.so` across the libretro C ABI,
  licence and full corresponding source shipped in `System/licenses/`, non-commercial only. Ship
  the whole `LICENSE.txt` (it holds the LGPL Nuked OPN2 and other notices), not a summary.
- Gearsystem is GPL-3 and fits without any stance.
- No fast GPL-clean MD core exists (BlastEm is interpreted on ARM). So MD is non-commercial either way.
- Consequence: no change to our release terms (already non-commercial because of snes9x).

### 2.3 Performance on the H700

What is sourced:
- Batocera (Knulli is Batocera-based) uses Genesis Plus GX as the primary MD core and says "Picodrive
  is a lighter emulator which although not as accurate as GenesisPlusGX, can be run on much weaker
  hardware" ([Batocera wiki: megadrive](https://wiki.batocera.org/systems:megadrive)).
- ROCKNIX ships Genesis Plus GX, GPGX Wide and PicoDrive for MD, default not stated on the page
  ([ROCKNIX: genesis](https://rocknix.org/systems/genesis)).
- BlastEm: interpreter-only on aarch64, from its own Makefile (above).

What is **not** sourced: an H700 measurement of any of these. Do not write "full speed" yet.
Primary sources still to read: the per-device default core in Knulli's and ROCKNIX's board configs
(es_systems / device overrides for H700), and muOS's core assignment files (the muos.dev MD page 404'd).
Our own evidence path: host `core_bench --serialize` on legal homebrew carts (proxy, labelled as
host), then `task perf:play` and the DEVICE-GATE checklist on the RG34XXSP.

Expected (unverified): MD on GPGX is the heaviest of the three, roughly SNES snes9x2005_plus class;
SMS and GG on any core are trivial. Heavy MD gate candidates: Virtua Racing (SVP), Sonic 3D
(fast scroll), Street Fighter II SCE (6-button), Sonic 2 two-player (interlace mode 2), Thunder
Force IV, Vectorman.

### 2.4 Core options to set (verified keys)

Genesis Plus GX (prefix `genesis_plus_gx`): `_bios` (leave disabled, no BIOS), `_overscan`
(`disabled` default; options top/bottom, left/right, full), `_left_border` (SMS left column blank,
"left border" hides it), `_gg_extra` (disabled = 160x144 GG window), `_render` (Interlaced Mode 2:
`single field` default, `double field` gives 320x448), `_lcd_filter` (GG ghosting), `_frameskip`
(disabled/auto/manual; our `{prefix}_frameskip` setter only fires if declared, fine), `_region_detect`,
`_aspect_ratio`, `_ym2612`, `_audio_filter`, `_no_sprite_limit` (leave off by default).
Gearsystem: as slotPlus above.

### 2.5 Saves (verified in GPGX source)

- SRAM and the I2C/93C EEPROMs all live in `sram.sram`, exposed as `RETRO_MEMORY_SAVE_RAM`
  (`eeprom_93c.c`, `libretro.c:3750`). One `.sav` covers both.
- Quirk: `retro_get_memory_size(SAVE_RAM)` returns `0x10000` while `is_running` is false (set false in
  `retro_load_game`, true in `retro_run`, lines 3672/3877), and the trimmed "modified length" once
  running. slot loads save RAM after `load()` and before the first `run` (`emu.rs:535`), so load gets the
  full 64 KB window. **Correct.** On save, a never-written SRAM trims to 0 and `memory()` returns None,
  so no `.sav` is written; a game whose SRAM ends in 0xFF bytes writes a shorter file. Both are safe
  for slot's copy-min load; add a round-trip test anyway (write, eject, reinsert, compare).
- `sram.on` false (no SRAM in header) gives NULL: no save, as expected.

### 2.6 FF and rewind cost

- GPGX state is ~1 MB fixed (vs snes9x2005_plus well under that, see PERFORMANCE.md rewind table).
  slot's rewind keeps XOR deltas compressed with lz4 inside a 20 MB budget (`rewind.rs`), and the emu
  thread serializes each push. Cost per push = 1 MB serialize + 1 MB XOR + lz4. Must be measured
  (`core_bench --serialize --frames 300`) before claiming rewind parity; MD deltas should compress well.
- PicoDrive's state is smaller (size not checked) and is the fallback if GPGX rewind misses budget.
- FF: same `GET_AUDIO_VIDEO_ENABLE` path as NES/SNES (patch 0006); GPGX honours video-skip
  (unverified, check `retro_run` for the `AUDIO_VIDEO_ENABLE` query).

### 2.7 Video and the fixed canvas (ADR 0004)

| System | Native output (verified from GPGX options unless marked) | Fit |
|---|---|---|
| GG | 160x144 (gg_extra off); 256x192 with gg_extra | Game Boy size: 240x160 canvas at 3x (480x432) like GB, or 320x288 at 2x in the 360x240 canvas |
| SMS | 256x192; 256x224 and 256x240 extended modes exist on SMS2 VDP (unverified which games; few) | 360x240 canvas at 2x (512x384) |
| MD | H40 320x224, H32 256x224 (NTSC); 320x240 / 256x240 PAL V30; Interlace Mode 2 320x448 (`double field`) | 360x240 canvas at 2x (640x448); 448-line frames use our existing vertical 2:1 blend; or keep `single field` |

Problems for our ADRs:
1. **ADR 0004 canvas is per core.** A multi-system core (GPGX, Gearsystem) serves GG at 160x144 and
   MD/SMS at 2x. Options: (a) accept GG at 2x in 360x240 (320x288, small, no ADR change), or
   (b) amend ADR 0004 so canvas truth is `(core, platform)` (one extra arg to `Core::canvas`, set at
   open; `HostExtra` already carries the canvas). **Recommend (b)** for GG parity with GB (3x), as a
   new ADR "canvas follows the seated platform". Small: canvas is already set at open.
2. **MD switches H32/H40 mid-game.** Our centring copy must clear the borders when the frame width
   changes (upstream clears when the frame is smaller than the buffer; check `canvas.rs` does the same
   on a width change, add a test that alternates 320 and 256 frames).
3. **Stretch crop** (ADR 0022/0046) uses the static `Platform::picture()`. MD is 320 or 256 wide per
   game. With picture (320,224) an H32 game stretched shows black side bars. Needs `picture` to follow
   the last frame size (an M change in our `video_mode` code, no new upstream file) or MD defaults to
   Actual. Decision for the maintainer.
4. PAL (50 Hz): out of scope as for NES/SNES (PLAN non-goals); `SET_SYSTEM_AV_INFO` handling (patch 0006)
   already rebuilds the resampler if a core changes rate.

### 2.8 Input on the RG34XXSP (verified in GPGX `libretro.c` and `input.c`)

- slot already calls `retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD)`. In GPGX that means
  "auto": 6-button if the ROM header lists it, else 3-button (MD) or 2-button (SMS/GG). No change needed.
- GPGX map: Y→A, B→B, A→C, **L→X, X→Y, R→Z, SELECT→MODE**, START→START (SMS: Pause).
- So MD needs the SNES policy: `passes_xy_through` true, `owns_shoulders` false, picture toggle on the
  SELECT+X chord (ADR 0007), Turbo row a no-op. 3-button games ignore X/Y/Z/MODE, harmless.
- SMS/GG: 2 buttons (B=1, A=2 in GPGX). They can keep the NES/GB policy (slot owns L1/R1, X/Y turbo).
- SELECT: on GPGX SMS/GG it is unmapped (fine). If Gearsystem is added, mask SELECT (console reset, per slotPlus).
- MD MODE on SELECT conflicts with slot's SELECT hold-back (600 ms) and chords: MODE is rarely needed
  (only to force 3-button mode at power-on). Accept, document.

---

## 3. Cart art, labels, region (research needed; nothing below is cited yet)

Same depth as VARIANTS.md: every outline and colour needs a cited or photo-sampled source, renders in
our own procedural renderer (`retro_mould.rs`, `retro_face.rs`, ADR 0042), no invented bitmaps.

| System | Variants to research (unverified) | Region auto-pick signal |
|---|---|---|
| MD | US Genesis cart vs Japanese Mega Drive cart vs PAL Mega Drive cart (shape and top grip differ); black plastic; EA carts with the yellow tab; Sonic & Knuckles lock-on; Codemasters J-Cart | header region field at 0x1F0 (`J`/`U`/`E` or the new-style hex code), verify on plutiedev.com ROM header page |
| SMS | Sega Card (My Card) vs cartridge; Western black cart vs Japanese Mark III / SMS carts | header `TMR SEGA` at 0x7FF0, region nibble at 0x7FFF (SMS JP / export / GG JP / export / intl), verify on smspower.org |
| GG | one main shell (black), JP vs Western label differences | same SMS-style header (GG codes) |

Labels: same pipeline as ADR 0037 (our own public art repo, CC BY-NC-SA 4.0 from ScreenScraper, our
developer ID exists). ScreenScraper system ids for MD, SMS, GG must be looked up (unverified). Cart Studio
fork (ADR 0032) gains outline words. Never commit art to the code repo.

---

## 4. Effort and patch list

Count from the current set: SNES tokens appear on 53 added lines across 13 upstream files. Expect
about 40 to 55 token lines per Sega system, mostly widening existing hunks, not new ones. New logic
goes in new files (policy, canvas, header readers, mould code).

### 4.1 Shared Sega foundation

| Patch | Content | Size | Upstream touch |
|---|---|---|---|
| 0021-core-genesis-plus-gx | `cores/genesis_plus_gx/build.sh` (pinned commit, sha256 in `SLOT_PIN`, `Makefile.libretro platform=unix -mcpu=cortex-a53`), full LICENSE.txt, `Core::GenesisPlusGx` (appended, `EVERY`), `option_prefix`, options in a new file; host dylib build | S | `slot-store/core.rs` tokens, `slot/core.rs` `colour_option` token, test site (e) `gpsp.rs` token (allowed by ADR 0013, append-only) |
| 0022-canvas-per-platform | ADR amending 0004: canvas from (core, platform); width-change border clear test | S/M | `slot-retro/core.rs` or our `canvas.rs` only, if done right |

### 4.2 Per system

| Patch | Content | Size | Upstream touch |
|---|---|---|---|
| 0023-platform-gg | `Platform::Gg`, `SHELVES`, `Games/GG` dirs, ext `gg`, picture 160x144, canvas 240x160 at 3x, GB-like policy, `picker_cores` None (single core like GB/GBC), title from stem, region from header, placeholder cart | M | ~13 files of tokens, test site (b) `chrome.rs` token |
| 0024-platform-sms | `Platform::Sms`, ext `sms` (`sg` later), 256x192 at 2x, NES-like policy, left-border option | M | same files, tokens |
| 0025-platform-md | `Platform::Md`, ext `md`, `gen`, `bin` (folder-scoped, `.smd` later), 2x canvas, SNES-like input policy, interlace handling, H32/H40 picture follow or Actual default | L | tokens plus `video_mode.rs` if picture follows frames |
| 0026-sega-shaders | Sega shelves on the retro shader list and the in-game/shelf pages (ADR 0043 pattern) | S, **blocked** | `SlotState` fields would change test site (f) (ADR 0034 says avoid). Options: store `shader_gg/sms/md` outside `slot.state` (like ADR 0025 did), or ask the maintainer to extend site (f). Stop-and-ask item |
| 0027-sega-cart-art | research doc like VARIANTS.md, moulds, colour table, region auto-pick, `cart_shell.txt` words | L | `cart_shell.rs`, `cart.rs`, `shell.rs` tokens |
| later: core-picodrive | MD alternative (picker pair GPGX/PicoDrive) | S | tokens, site (e) |
| later: core-gearsystem | SMS/GG GPL-clean alternative; SELECT mask | S | tokens, site (e) |

Tests per system (the NES/SNES T-list pattern): scan and extension test, real-core boot under
`SLOT_REQUIRE_CORES=1`, canvas/window size (`unsafe` allowed by ADR 0020), input mask test (MD XYZ),
save RAM round trip (GPGX size quirk), downgrade test (`cart_platform=md` on upstream boots to shelf),
harness leg "Sega cart, eject, GBA" equals GBA-only (H3 pattern), `bench:compare` GBA within 2%,
`core_bench --serialize` for rewind, DEVICE-GATE rows on the RG34XXSP.

What goes upstream: nothing system-specific (slot#30). At most the behaviour-neutral platform-policy
refactor (section 1.4), asked first on discussion #64.

### 4.3 Order

1. GPGX core build plus host bench (proves speed and rewind cost before any frontend code).
2. Game Gear (smallest: GB-sized picture, 2 buttons, single core, one cart shell).
3. Master System (2x canvas like NES, 2 buttons).
4. Mega Drive (6-button, H32/H40, interlace, the heaviest core path).
5. Cart art for all three after a VARIANTS-style research pass.
6. Second cores (PicoDrive for MD, Gearsystem for SMS/GG) as picker pairs.

One shared core first is right: one build script, one licence stance (same as snes9x), one set of
option and save tests serving three shelves.

---

## 5. Recommendation and smallest first step

Recommendation: Genesis Plus GX as the single core for all three systems in v1. Each system ships as
its own `Platform` behind our existing policy seam, single core per shelf, no picker until a second core
is added. Order: GG, then SMS, then MD. Gearsystem (GPL-3) and PicoDrive come later as picker alternatives.
Do not adopt slotPlus's code or model. Credit it for the Gearsystem recipe if we use that.

Before any frontend code, the maintainer has to decide three things:
1. Canvas per (core, platform), which amends ADR 0004 and gives GG 3x like GB, or GG at 2x.
2. Where Sega shader settings live (test site (f), ADR 0034).
3. MD stretch with variable width: follow the frame, or default MD to Actual.

**Smallest first step (S, no upstream touch):** add `cores/genesis_plus_gx/build.sh` and its pin. Build
the host dylib and the device `.so`. Run `core_bench` with `--serialize --frames 300` on legal MD, SMS and GG
homebrew next to snes9x2005_plus on the M5 Max (a host proxy, labelled as such). Then the maintainer
runs the existing device bench task (`taskfile.yml:290`, `core_bench` over adb, `CORE=` gains
`genesis_plus_gx`; `ROM_ON_DEVICE=` for an owned MD dump) on the RG34XXSP. The output is a PERFORMANCE.md
row and a go/no-go for GPGX vs PicoDrive on MD. Nothing in slot's tree changes yet.
