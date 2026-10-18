# Architecture Decision Records

An ADR records one binding decision, its context and its consequences, so nobody has to guess why
the patch set looks the way it does.

## Adding one

1. Copy [template.md](template.md) to `NNNN-kebab-title.md` with the next free number.
2. Fill it in. Keep it short (about 50 lines), plain English, no em or en dashes.
3. Add a row to the index below.
4. If it reverses or replaces an earlier decision, set the old ADR's status to
   `Superseded by [NNNN](...)` and the new one's to `Supersedes [NNNN](...)`. If it only extends
   one, use `Amended by` and `Amends`. Never delete an old ADR.
5. Add a row to the table in [docs/DECISIONS.md](../DECISIONS.md).

## Index

| Number | Title | Status | Date |
|---|---|---|---|
| [0001](0001-patch-set-over-pinned-slot.md) | Ship NES and SNES as a patch set over pinned slot releases | Accepted | 2026-10-11 |
| [0002](0002-cores.md) | Use fceumm and nestopia for NES, snes9x and snes9x2005_plus for SNES | Amended by 0053 and 0063 | 2026-10-11 |
| [0003](0003-reference-device-rg35xxsp.md) | Use the Anbernic RG35XXSP as the reference device | Superseded by [0021](0021-reference-device-rg34xxsp.md) | 2026-10-11 |
| [0004](0004-fixed-2x-canvas.md) | Give NES and SNES cores a fixed 360x240 canvas at 2x | Amended by 0050 and 0065 | 2026-10-11 |
| [0005](0005-gba-sp-bezel-on-rg35xxsp.md) | Keep the GBA SP bezel for NES and SNES on the RG35XXSP | Accepted | 2026-10-11 |
| [0006](0006-real-cart-art-with-variants.md) | Ship real NES, Famicom, SNES and Super Famicom cart art with variants in v1 | Amended by 0042 | 2026-10-11 |
| [0007](0007-snes-select-x-picture-mode.md) | Toggle the SNES picture mode with SELECT+X | Accepted | 2026-10-11 |
| [0008](0008-no-new-quick-menu-rows.md) | Add no quick menu rows; NES and SNES shaders change with SELECT+B/A | Superseded by [0023](0023-quick-menu-shader-rows.md) | 2026-10-11 |
| [0009](0009-host-struct-untouched.md) | Keep the Host struct unchanged and put new libretro state in a side struct | Accepted | 2026-10-11 |
| [0010](0010-macos-primary-ci.md) | Run tests on macOS; Linux arm only builds device artefacts | Accepted | 2026-10-11 |
| [0011](0011-one-token-in-two-test-files.md) | Add one token each to two upstream test files | Accepted | 2026-10-12 |
| [0012](0012-durability-value-pce.md) | Change durability.rs's unknown platform example from nes to pce | Accepted | 2026-10-12 |
| [0013](0013-five-named-test-sites.md) | Allow upstream test edits only at named sites checked by the guard | Amended by 0044, 0048 and 0055 | 2026-10-12 |
| [0014](0014-real-label-art.md) | Show real cartridge label art on carts, never a screenshot | Accepted. Amended by 0057 and 0069; Logo Only fallback implemented 2026-10-18 | 2026-10-12 |
| [0015](0015-hostextra-canvas-only.md) | Start HostExtra with only the canvas field | Accepted | 2026-10-12 |
| [0016](0016-set-game-canvas-every-frame.md) | Call set_game_canvas every frame and return early when unchanged | Accepted | 2026-10-12 |
| [0017](0017-thumb-sized-new-file.md) | Put thumb::png_sized in a new file | Accepted | 2026-10-12 |
| [0018](0018-source-rect-takes-canvas.md) | Pass the canvas to video_mode::source_rect | Amended by 0046 | 2026-10-12 |
| [0019](0019-unsafe-gamepass-set-canvas.md) | Allow unsafe for the GL texture re-allocation in GamePass::set_canvas | Accepted | 2026-10-12 |
| [0020](0020-unsafe-in-own-test-files.md) | Allow unsafe in our own test files that read GL output or core symbols | Accepted | 2026-10-12 |
| [0021](0021-reference-device-rg34xxsp.md) | Use the Anbernic RG34XXSP as the reference and test device | Accepted | 2026-10-12 |
| [0022](0022-nes-snes-default-stretch.md) | Default NES and SNES to the Stretch picture mode | Accepted. Amended by [0061](0061-per-system-picture-row.md) and [0062](0062-crop-overscan-picture.md) | 2026-10-12 |
| [0023](0023-quick-menu-shader-rows.md) | Show a NES and an SNES shader row on the quick menu Screen page | Amended by 0043 | 2026-10-13 |
| [0024](0024-upstream-touch-point-map.md) | Track every upstream touch point instead of an app.rs line limit | Accepted | 2026-10-13 |
| [0025](0025-shelf-memory.md) | Remember the last shelf and each shelf's cart in Config/shelf.state | Superseded by [0039](0039-upstream-shelf-memory.md); per-shelf carts back in 0049 | 2026-10-13 |
| [0026](0026-four-more-retro-shaders.md) | Add Sharp, Scanlines, crt-pi and crt-1tap for NES and SNES | Accepted | 2026-10-13 |
| [0027](0027-retro-shaders-pay-once.md) | Add retro shaders through one payload variant per enum | Accepted | 2026-10-13 |
| [0028](0028-retro-shaders-own-gl-program.md) | Run the retro shaders in their own GL program | Accepted | 2026-10-13 |
| [0029](0029-manual-bilinear-sampling.md) | Sample bilinearly by hand in the shaders that expect linear filtering | Accepted | 2026-10-13 |
| [0030](0030-keep-alsa-open-while-fed.md) | Keep the ALSA device open while a game feeds the ring | Accepted | 2026-10-13 |
| [0031](0031-warm-retro-shaders-at-boot.md) | Build and warm the retro shader program at start-up | Accepted | 2026-10-13 |
| [0032](0032-cart-studio-credited-fork.md) | Bring NES and SNES labels to Cart Studio as a credited fork, published once ScreenScraper art is available | Amended by 0037 | 2026-10-13 |
| [0033](0033-keep-upstream-lid-timeout.md) | Keep upstream's lid behaviour: doze, then power off after 3 minutes | Accepted | 2026-10-13 |
| [0034](0034-durability-shader-lines.md) | Allow the two shader lines in durability.rs's SlotState literal (named test site f) | Accepted | 2026-10-13 |
| [0035](0035-runner-sensitive-tests-info-on-ci.md) | Run runner-sensitive test binaries as information only on CI | Amended by 0045 | 2026-10-13 |
| [0036](0036-line-pixel-sharp-scanlines.md) | Add Line and Pixel and make Scanlines sharp | Accepted | 2026-10-14 |
| [0037](0037-public-nes-snes-art-set.md) | Host the NES and SNES label art in a public art repo of our own | Accepted | 2026-10-14 |
| [0038](0038-rebase-to-slot-v1-7-0.md) | Rebase the patch set onto slot v1.7.0 | Accepted | 2026-10-15 |
| [0039](0039-upstream-shelf-memory.md) | Use upstream's shelf memory and drop Config/shelf.state | Accepted. Supersedes 0025. Amended by 0049 | 2026-10-15 |
| [0040](0040-drop-lazy-shelf.md) | Drop lazy-shelf: upstream looks up shells lazily | Accepted | 2026-10-15 |
| [0041](0041-drop-audio-release-pace.md) | Drop audio-release-pace: upstream paces the released device | Accepted | 2026-10-15 |
| [0042](0042-retro-carts-own-renderer.md) | Draw NES and SNES carts with our own procedural renderer on v1.7.0 | Accepted. Amends 0006. Amended by 0054 | 2026-10-15 |
| [0043](0043-retro-shader-rows-on-v1-7-0-menus.md) | Fit the NES and SNES shader rows into v1.7.0's per-platform menus | Accepted. Amends 0023. Amended by 0048 | 2026-10-15 |
| [0044](0044-test-site-c-gone.md) | Retire named test site (c): upstream deleted label_top | Accepted. Amends 0013 | 2026-10-15 |
| [0045](0045-layout-hash-tests-in-both-trees.md) | Run upstream's layout frame-hash tests in both trees | Accepted. Amends 0035 | 2026-10-15 |
| [0046](0046-retro-stretch-crops-height.md) | Keep the NES and SNES stretch crop on both axes | Accepted. Amends 0018. Amended by 0052 and 0062 | 2026-10-15 |
| [0047](0047-upstream-first-fixes.md) | Upstream-first fixes | Accepted | 2026-10-15 |
| [0048](0048-nes-snes-in-the-screen-platform-list.md) | List NES and SNES on the Screen page after the Game Boys | Accepted. Amends 0043 and 0013. Amended by 0055 | 2026-10-15 |
| [0049](0049-per-shelf-cart-memory.md) | Remember each shelf's cart on top of upstream's shelf memory | Accepted. Amends 0039 | 2026-10-15 |
| [0050](0050-canvas-per-core-and-platform.md) | Choose the canvas per core and platform, so Game Gear runs at 3x like Game Boy | Accepted. Amends 0004. Amended by 0065 | 2026-10-15 |
| [0051](0051-sega-shaders-outside-slot-state.md) | Store the Sega shader settings in their own file, outside slot.state | Accepted. Amended by 0060 | 2026-10-15 |
| [0052](0052-md-stretch-follows-frame-width.md) | Make Mega Drive Stretch follow the live frame width | Accepted. Amends 0046 | 2026-10-15 |
| [0053](0053-genesis-plus-gx-for-sega.md) | Use Genesis Plus GX as the one core for Game Gear, Master System and Mega Drive | Accepted. Amends 0002 | 2026-10-15 |
| [0054](0054-bitmap-retro-carts.md) | Draw NES and SNES carts from generated neutral bitmaps with upstream's Overlay | Accepted. Amends 0042 | 2026-10-16 |
| [0055](0055-sega-tokens-at-named-test-sites.md) | Widen named test sites (b), (e), (g) and (h) for the Sega platforms and Genesis Plus GX | Accepted. Amends 0013 and 0048 | 2026-10-16 |
| [0056](0056-sega-carts-one-box-per-platform.md) | Draw the Sega carts from generated neutrals, one box per platform | Accepted. Extends 0054. Amended by 0057 | 2026-10-16 |
| [0057](0057-sms-box-art-tall-well.md) | Show the whole Master System box front in a tall label well | Accepted. Amends 0014 and 0056 | 2026-10-16 |
| [0058](0058-propose-modular-platform-registry-upstream.md) | Propose a modular platform registry upstream, asked first on discussion #64 | Proposed | 2026-10-16 |
| [0059](0059-need-fullpath-load.md) | Hand need_fullpath cores the path only, never a ROM buffer | Accepted. Drop when upstream lands (0047) | 2026-10-16 |
| [0060](0060-game-gear-lcd3x.md) | Offer upstream's LCD3x for Game Gear, right after Off | Accepted. Amends 0051 | 2026-10-16 |
| [0061](0061-per-system-picture-row.md) | Give each retro system's Screen section a Picture row for its default picture mode | Accepted. Amends 0022. Amended by 0062 and 0065 | 2026-10-16 |
| [0062](0062-crop-overscan-picture.md) | Add a Crop picture mode that hides the NES and SNES overscan edges, default for both | Accepted. Amends 0046 and 0061 | 2026-10-16 |
| [0063](0063-ps1-in-scope-on-pcsx-rearmed.md) | Bring PlayStation into scope, built the NES and SNES way, on pinned pcsx_rearmed | Accepted. Amends 0002 | 2026-10-17 |
| [0064](0064-answer-pcsx-declared-option-defaults.md) | Answer pcsx_rearmed's declared option defaults, and leave every other core's answers alone | Accepted | 2026-10-17 |
| [0065](0065-ps1-canvas-and-screen-section.md) | Give PS1 a fixed 640x480 canvas, its own frontend budget and its own Screen section | Accepted. Amends 0004, 0050 and 0061 | 2026-10-17 |
| [0066](0066-ps1-rewind-and-run-ahead-off.md) | Turn rewind and run-ahead off for PS1 | Accepted | 2026-10-17 |
| [0067](0067-ps1-disk-control-and-disc-in-states.md) | Swap PS1 discs through both disk-control interfaces, remember the disc, and record it in states | Accepted | 2026-10-17 |
| [0068](0068-ps1-input-digital-then-analog.md) | Ship PS1 with the digital pad and L2/R2 to the game, and analog DualShock in v2 | Accepted | 2026-10-17 |
| [0069](0069-ps1-jewel-case-shelf.md) | Show PS1 games as jewel cases with front cover art, and the disc on insert | Accepted. Amends 0014 | 2026-10-17 |
| [0070](0070-backport-upstream-settings-scroll.md) | Scroll the Screen page with a backport of upstream's settings-page scrolling | Accepted. Backport, drop on the 1.8.0 rebase (0047) | 2026-10-18 |
| [0071](0071-pace-off-panel-cores-at-their-own-fps.md) | Pace a core more than 2 fps from 60 at its own fps, locked to the panel, with a per-system PAL Speed row (Native default) | Accepted. Amends 0061, 0065 | 2026-10-18 |
| [0072](0072-write-sav-when-the-core-gives-no-state.md) | Write the battery save on a flush, an eject or an autosave even when the core gives no state | Accepted. Drop when upstream lands (0047) | 2026-10-18 |
| [0073](0073-keep-faces-and-selection-across-a-restock.md) | Drop stale cart faces, keep faces and selection across a restock, prefer the selected cart | Accepted. Drop when upstream lands (0047) | 2026-10-18 |
| [0074](0074-switcher-up-down.md) | Move through the save state switcher with Up and Down too | Accepted. Drop when upstream lands (0047) | 2026-10-18 |
| [0075](0075-carry-upstream-backlight-floor.md) | Carry upstream 3b6349c, a backlight floor of 8/255, until the 1.8.0 rebase | Accepted. Backport, drop on the 1.8.0 rebase (0047) | 2026-10-18 |
| [0076](0076-master-system-region-row.md) | Give the Master System Screen section a Region row mapped to Genesis Plus GX's region option | Accepted. Amends 0061 | 2026-10-18 |
| [0077](0077-battery-low-banners.md) | Show a Battery Low banner at 15% and at 10% | Accepted. Drop when upstream lands (0047) | 2026-10-18 |
| [0078](0078-rest-while-dozing.md) | Stop drawing while dozing | Accepted. Amends 0033. Drop when upstream lands (0047) | 2026-10-18 |
| [0079](0079-favourite-removal-confirm-upstream-only.md) | Confirm favourite removal with a second Y: upstream only | Accepted (not carried) | 2026-10-18 |
| [0080](0080-volume-hud-on-a-silent-start.md) | Show the volume HUD when a game starts muted or at zero | Accepted. Drop when upstream lands (0047) | 2026-10-18 |
| [0081](0081-start-closes-the-core-picker.md) | START closes the core picker it opened: upstream only | Accepted (not carried) | 2026-10-18 |
| [0082](0082-rom-hack-updates-keep-saves-move-states.md) | A ROM hack update keeps the name and the battery save, and moves every save state away | Accepted | 2026-10-18 |
