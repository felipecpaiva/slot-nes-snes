# Decisions

Binding decisions now live as Architecture Decision Records in [docs/adr/](adr/README.md), one
file each with its context and consequences. To record a new one, add an ADR (see the
[ADR README](adr/README.md)) and a row below. This table is the short index, oldest first.

| Date | ADR | Decision |
|---|---|---|
| 2026-10-11 | [0001](adr/0001-patch-set-over-pinned-slot.md) | Patch set over pinned slot releases, not a fork and not a shim core |
| 2026-10-11 | [0002](adr/0002-cores.md) | Cores: fceumm (NES default), nestopia (alt), snes9x (SNES default), snes9x2005_plus (alt) |
| 2026-10-11 | [0003](adr/0003-reference-device-rg35xxsp.md) | Reference device: Anbernic RG35XXSP (superseded by 0021) |
| 2026-10-11 | [0004](adr/0004-fixed-2x-canvas.md) | Video: fixed per-platform 2x canvas (360x240 logical), SNES hi-res blended 2:1 |
| 2026-10-11 | [0005](adr/0005-gba-sp-bezel-on-rg35xxsp.md) | NES and SNES keep the GBA SP bezel on the RG35XXSP (640x427 window) |
| 2026-10-11 | [0006](adr/0006-real-cart-art-with-variants.md) | Real NES, Famicom, SNES and Super Famicom cart art with variants in v1 |
| 2026-10-11 | [0007](adr/0007-snes-select-x-picture-mode.md) | SNES picture mode toggles with SELECT+X |
| 2026-10-11 | [0008](adr/0008-no-new-quick-menu-rows.md) | No new quick menu rows; NES/SNES shaders via SELECT+B/A (superseded by 0023) |
| 2026-10-11 | [0009](adr/0009-host-struct-untouched.md) | Host struct field list untouched; new state in a side struct |
| 2026-10-11 | [0010](adr/0010-macos-primary-ci.md) | macOS is the primary test job; Linux arm builds device artefacts |
| 2026-10-12 | [0011](adr/0011-one-token-in-two-test-files.md) | Two upstream test files get one Platform::Nes token each (Snes later) |
| 2026-10-12 | [0012](adr/0012-durability-value-pce.md) | durability.rs example value cart_platform=nes becomes cart_platform=pce |
| 2026-10-12 | [0013](adr/0013-five-named-test-sites.md) | Upstream test edits happen only at five named sites, each checked exactly by the guard |
| 2026-10-12 | [0014](adr/0014-real-label-art.md) | Carts show real label art, never a screenshot; NES and SNES get a Cart Studio equivalent |
| 2026-10-12 | [0015](adr/0015-hostextra-canvas-only.md) | HostExtra holds only canvas in patch 0004; issue 14 adds av_change and av_enable |
| 2026-10-12 | [0016](adr/0016-set-game-canvas-every-frame.md) | Compositor::set_game_canvas is called every frame from Frontend::compose |
| 2026-10-12 | [0017](adr/0017-thumb-sized-new-file.md) | thumb::png_sized lives in new file thumb_sized.rs, re-exported from thumb.rs |
| 2026-10-12 | [0018](adr/0018-source-rect-takes-canvas.md) | source_rect(platform, canvas, mode); Core::canvas_f32 keeps the app.rs hunk to one line |
| 2026-10-12 | [0019](adr/0019-unsafe-gamepass-set-canvas.md) | Named unsafe exception: GL texture re-allocation in GamePass::set_canvas |
| 2026-10-12 | [0020](adr/0020-unsafe-in-own-test-files.md) | unsafe is allowed in our own new test files nes_window.rs and nes_fceumm.rs |
| 2026-10-12 | [0021](adr/0021-reference-device-rg34xxsp.md) | Reference and test device is the RG34XXSP (720x480, 3:2), not the RG35XXSP |
| 2026-10-12 | [0022](adr/0022-nes-snes-default-stretch.md) | NES and SNES default to Stretch; GBA, GB, GBC keep upstream's Actual |
| 2026-10-13 | [0023](adr/0023-quick-menu-shader-rows.md) | The quick menu Screen page lists a NES or SNES shader row on its own shelf |
| 2026-10-13 | [0024](adr/0024-upstream-touch-point-map.md) | No fixed app.rs line limit; every upstream touch point is mapped with a reason |
| 2026-10-13 | [0025](adr/0025-shelf-memory.md) | slot remembers the last shelf and each shelf's cart (by stem) in Config/shelf.state |
| 2026-10-13 | [0026](adr/0026-four-more-retro-shaders.md) | NES and SNES get Sharp, Scanlines, crt-pi and crt-1tap after Off, Grid, Dot |
| 2026-10-13 | [0027](adr/0027-retro-shaders-pay-once.md) | Retro shaders are added pay once: one payload variant per enum, list and GLSL in our own files |
| 2026-10-13 | [0028](adr/0028-retro-shaders-own-gl-program.md) | Retro shaders run in their own GL program, not as new branches in GAME_FRAG |
| 2026-10-13 | [0029](adr/0029-manual-bilinear-sampling.md) | Sharp, crt-pi and crt-1tap sample bilinearly by hand (4 reads), not via GL_LINEAR |
| 2026-10-13 | [0030](adr/0030-keep-alsa-open-while-fed.md) | Keep ALSA open while a game feeds the ring, reopen on cart load, prefill silence when the game's sound starts (amended 2026-10-15) |
| 2026-10-13 | [0031](adr/0031-warm-retro-shaders-at-boot.md) | Retro shader program built and warmed at start-up, about 150 ms more boot for every user |
| 2026-10-13 | [0032](adr/0032-cart-studio-credited-fork.md) | NES/SNES Cart Studio is a credited fork, published once the ScreenScraper developer ID allows the art harvest |
| 2026-10-13 | [0033](adr/0033-keep-upstream-lid-timeout.md) | Keep upstream's lid doze and power-off after 3 minutes |
| 2026-10-13 | [0034](adr/0034-durability-shader-lines.md) | Named upstream test site (f): the two shader lines in durability.rs's SlotState literal |
| 2026-10-13 | [0035](adr/0035-runner-sensitive-tests-info-on-ci.md) | Runner-sensitive test binaries run as information only on CI, gate locally |
| 2026-10-14 | [0036](adr/0036-line-pixel-sharp-scanlines.md) | NES and SNES get Line (panel-locked scanline) and Pixel (pixellate) after crt-1tap; Scanlines samples Sharp |
| 2026-10-14 | [0037](adr/0037-public-nes-snes-art-set.md) | NES/SNES label art hosted in its own public repo (CC BY-NC-SA 4.0), code repos stay art-free |
| 2026-10-15 | [0038](adr/0038-rebase-to-slot-v1-7-0.md) | Patch set rebased onto slot v1.7.0: 23 patches become 20 (3 dropped, 3 reshaped) |
| 2026-10-15 | [0039](adr/0039-upstream-shelf-memory.md) | Shelf memory comes from upstream #53 (slot.state shelf and shelf_cart); Config/shelf.state is gone (supersedes 0025) |
| 2026-10-15 | [0040](adr/0040-drop-lazy-shelf.md) | lazy-shelf dropped: v1.7.0 Shelf::new is lazy and gb_shell_of reads a cached header |
| 2026-10-15 | [0041](adr/0041-drop-audio-release-pace.md) | audio-release-pace dropped: v1.7.0 Pacer sleeps to absolute deadlines while released |
| 2026-10-15 | [0042](adr/0042-retro-carts-own-renderer.md) | NES and SNES carts keep their procedural look in retro_face.rs and retro_mould.rs; no GBA interior or board behind them |
| 2026-10-15 | [0043](adr/0043-retro-shader-rows-on-v1-7-0-menus.md) | In game, Shader follows the NES or SNES cart; on the NES or SNES shelf, Screen opens that shader page; Color Correction and Palette hidden |
| 2026-10-15 | [0044](adr/0044-test-site-c-gone.md) | Named upstream test site (c) retired: render_shelves.rs lost label_top upstream |
| 2026-10-15 | [0045](adr/0045-layout-hash-tests-in-both-trees.md) | slot-gfx layout.rs runs in both trees and gates on no new failure (two hash tests fail on upstream here) |
| 2026-10-15 | [0046](adr/0046-retro-stretch-crops-height.md) | Stretch: GBA, GB, GBC take upstream's widen-only rect; NES and SNES crop both axes |
| 2026-10-15 | [0047](adr/0047-upstream-first-fixes.md) | A fix that belongs upstream also goes to BrandonKowalski/slot as a PR; our patch is dropped on the rebase after upstream ships it |
| 2026-10-15 | [0048](adr/0048-nes-snes-in-the-screen-platform-list.md) | Screen lists NES and SNES after the Game Boys (hidden on cards without them); named test sites (g) and (h) in slot-ui quick_menu.rs |
| 2026-10-15 | [0049](adr/0049-per-shelf-cart-memory.md) | Each shelf remembers its cart in Config/shelf_carts.txt, saved at rest on top of upstream #53; drop when the upstream PR lands |
| 2026-10-15 | [0050](adr/0050-canvas-per-core-and-platform.md) | Canvas comes from (core, platform): Game Gear 240x160 at 3x like Game Boy, SMS and MD 360x240 at 2x |
| 2026-10-15 | [0051](adr/0051-sega-shaders-outside-slot-state.md) | GG, SMS and MD shaders live in their own Config/ file; SlotState and test site (f) unchanged |
| 2026-10-15 | [0052](adr/0052-md-stretch-follows-frame-width.md) | MD Stretch uses the last frame width (320 or 256); MD defaults to Stretch |
| 2026-10-15 | [0053](adr/0053-genesis-plus-gx-for-sega.md) | Genesis Plus GX is the single core for GG, SMS and MD, one platform each, no picker yet; MD go is provisional on the heavy-title device gate |
| 2026-10-16 | [0054](adr/0054-bitmap-retro-carts.md) | NES, Famicom, SNES and SFC carts are generated 50% grey bitmaps (lighting measured from gba_neutral.png) coloured with upstream's Overlay |
| 2026-10-16 | [0055](adr/0055-sega-tokens-at-named-test-sites.md) | Named test sites (b) and (e) take the Sega platform tokens and `Core::GenesisPlusGx` by the standing rule; (g) and (h) take the three Sega Screen rows |
| 2026-10-16 | [0056](adr/0056-sega-carts-one-box-per-platform.md) | Sega carts are generated neutrals (gg, sms, segacard, megadrive, genesis), one box per platform; card centred in the SMS box, Genesis bottom aligned in the MD box |
| 2026-10-16 | [0057](adr/0057-sms-box-art-tall-well.md) | Master System shows the whole front box (ScreenScraper `box-2D`) for every game, contain fit in a portrait well (cart 140x196, card 114x160); other platforms keep label scans |
| 2026-10-16 | [0058](adr/0058-propose-modular-platform-registry-upstream.md) | Propose upstream a compile-time platform table (PlatformSpec, CoreSpec, CartLook) in eight zero-behaviour PRs, asked first on discussion #64; nothing posted until approved |
| 2026-10-16 | [0059](adr/0059-need-fullpath-load.md) | A core with need_fullpath gets the path with data NULL and slot keeps no ROM copy (gpSP, fceumm, Genesis Plus GX); drop when the upstream PR lands |
| 2026-10-16 | [0062](adr/0062-crop-overscan-picture.md) | NES and SNES gain a Crop picture mode, their new default: slot's source rect drops NES 8 px on every edge (240x224) and SNES 8 lines top and bottom (256x208); Sega and Game Boys unchanged |
| 2026-10-17 | [0063](adr/0063-ps1-in-scope-on-pcsx-rearmed.md) | PS1 is in scope as Phase 8: `Platform::Ps1` and `Core::PcsxRearmed` appended, pcsx_rearmed pinned `c8816799` with archive sha256, `HAVE_PHYSICAL_CDROM=0 BUILTIN_GPU=neon -mcpu=cortex-a53`, CHD on, one core and no picker, user BIOS with HLE fallback, tests force HLE; forks credited |
| 2026-10-17 | [0064](adr/0064-answer-pcsx-declared-option-defaults.md) | pcsx_rearmed only gets its declared option defaults answered (explicit values win), threaded rendering and drc thread set to `auto` explicitly; every other core unchanged; answering defaults for every core is an upstream-first question |
| 2026-10-17 | [0065](adr/0065-ps1-canvas-and-screen-section.md) | PS1 canvas 640x480 (horizontal resample, row doubling), its own budget (convert at most 2 ms, convert plus upload under about 3 ms), 4:3 thumbnails, its own Screen section with the retro shader list and a Picture row (Actual default, Stretch, no Crop) |
| 2026-10-17 | [0066](adr/0066-ps1-rewind-and-run-ahead-off.md) | No rewind and no run-ahead on PS1 (4.4 MB states); manual states, eject autosave and lid-close save stay; no FF gesture in v1 |
| 2026-10-17 | [0067](adr/0067-ps1-disk-control-and-disc-in-states.md) | Disk control answers 13, 57 and 58 from HostExtra; swaps roll back when refused; the disc is kept in `Saves/PS1/<stem>.disc`; multi-disc states end in a `SLOTPSX1` plus u32 index trailer |
| 2026-10-17 | [0068](adr/0068-ps1-input-digital-then-analog.md) | PS1 v1 is the digital pad with L1/R1 (`owns_shoulders`) and L2/R2 (`owns_triggers`) to the game, picture toggle on SELECT+X (other systems keep rewind and FF); v2 reads the analog sticks (ABS 0x02 to 0x05) as DualShock |
| 2026-10-17 | [0069](adr/0069-ps1-jewel-case-shelf.md) | PS1 games are jewel cases faced with the front cover (`box-2D`), US, EU and JP styles (JP spine strip), double case for multi-disc, case opens and the `support-2D` disc slides in; 3D disc style deferred |
| 2026-10-18 | [0070](adr/0070-backport-upstream-settings-scroll.md) | Settings > Screen scrolls six rows that follow the cursor, a backport of upstream e1bfb2b and 2c82294 with SCREEN added to `scrolls()`; every other page fits; on the 1.8.0 rebase keep only the SCREEN token |
| 2026-10-18 | [0071](adr/0071-pace-off-panel-cores-at-their-own-fps.md) | A core more than 2 fps from 60 (PAL, about 50) is paced at its own fps, locked to the panel by a frames-owed carry (a repeat about 1 tick in 6), sound from its own rate; NTSC and Game Boys unchanged; PAL Speed row Native (default) or Panel in the NES, SNES, SMS, MD and PS1 Screen sections |
| 2026-10-18 | [0072](adr/0072-write-sav-when-the-core-gives-no-state.md) | `flush_resume`, `flush_eject` and `autosave` write the trusted save RAM when the core gives no state, and log it; drop when the upstream PR lands |
| 2026-10-18 | [0073](adr/0073-keep-faces-and-selection-across-a-restock.md) | A face built for another cart is dropped in `place`; a restock keeps faces and the selected cart (Recents still opens on its newest); stem lookups try the selected index first; drop when the upstream PR lands |
| 2026-10-18 | [0074](adr/0074-switcher-up-down.md) | Up and Down move through the save state switcher; the delete question is upstream-only, never carried (upstream `delete.rs` presses Y once), the ring of five is not taken; drop when the upstream PR lands |
| 2026-10-18 | [0075](adr/0075-carry-upstream-backlight-floor.md) | Backport upstream 3b6349c (backlight floor 8/255 of max, at least 1, issue #100) with its four test lines at named site (i); drop on the 1.8.0 rebase |
