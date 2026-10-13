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
| [0002](0002-cores.md) | Use fceumm and nestopia for NES, snes9x and snes9x2005_plus for SNES | Accepted | 2026-10-11 |
| [0003](0003-reference-device-rg35xxsp.md) | Use the Anbernic RG35XXSP as the reference device | Superseded by [0021](0021-reference-device-rg34xxsp.md) | 2026-10-11 |
| [0004](0004-fixed-2x-canvas.md) | Give NES and SNES cores a fixed 360x240 canvas at 2x | Accepted | 2026-10-11 |
| [0005](0005-gba-sp-bezel-on-rg35xxsp.md) | Keep the GBA SP bezel for NES and SNES on the RG35XXSP | Accepted | 2026-10-11 |
| [0006](0006-real-cart-art-with-variants.md) | Ship real NES, Famicom, SNES and Super Famicom cart art with variants in v1 | Accepted | 2026-10-11 |
| [0007](0007-snes-select-x-picture-mode.md) | Toggle the SNES picture mode with SELECT+X | Accepted | 2026-10-11 |
| [0008](0008-no-new-quick-menu-rows.md) | Add no quick menu rows; NES and SNES shaders change with SELECT+B/A | Superseded by [0023](0023-quick-menu-shader-rows.md) | 2026-10-11 |
| [0009](0009-host-struct-untouched.md) | Keep the Host struct unchanged and put new libretro state in a side struct | Accepted | 2026-10-11 |
| [0010](0010-macos-primary-ci.md) | Run tests on macOS; Linux arm only builds device artefacts | Accepted | 2026-10-11 |
| [0011](0011-one-token-in-two-test-files.md) | Add one token each to two upstream test files | Accepted | 2026-10-12 |
| [0012](0012-durability-value-pce.md) | Change durability.rs's unknown platform example from nes to pce | Accepted | 2026-10-12 |
| [0013](0013-five-named-test-sites.md) | Allow upstream test edits only at named sites checked by the guard | Accepted | 2026-10-12 |
| [0014](0014-real-label-art.md) | Show real cartridge label art on carts, never a screenshot | Accepted | 2026-10-12 |
| [0015](0015-hostextra-canvas-only.md) | Start HostExtra with only the canvas field | Accepted | 2026-10-12 |
| [0016](0016-set-game-canvas-every-frame.md) | Call set_game_canvas every frame and return early when unchanged | Accepted | 2026-10-12 |
| [0017](0017-thumb-sized-new-file.md) | Put thumb::png_sized in a new file | Accepted | 2026-10-12 |
| [0018](0018-source-rect-takes-canvas.md) | Pass the canvas to video_mode::source_rect | Accepted | 2026-10-12 |
| [0019](0019-unsafe-gamepass-set-canvas.md) | Allow unsafe for the GL texture re-allocation in GamePass::set_canvas | Accepted | 2026-10-12 |
| [0020](0020-unsafe-in-own-test-files.md) | Allow unsafe in our own test files that read GL output or core symbols | Accepted | 2026-10-12 |
| [0021](0021-reference-device-rg34xxsp.md) | Use the Anbernic RG34XXSP as the reference and test device | Accepted | 2026-10-12 |
| [0022](0022-nes-snes-default-stretch.md) | Default NES and SNES to the Stretch picture mode | Accepted | 2026-10-12 |
| [0023](0023-quick-menu-shader-rows.md) | Show a NES and an SNES shader row on the quick menu Screen page | Accepted | 2026-10-13 |
| [0024](0024-upstream-touch-point-map.md) | Track every upstream touch point instead of an app.rs line limit | Accepted | 2026-10-13 |
| [0025](0025-shelf-memory.md) | Remember the last shelf and each shelf's cart in Config/shelf.state | Accepted | 2026-10-13 |
| [0026](0026-four-more-retro-shaders.md) | Add Sharp, Scanlines, crt-pi and crt-1tap for NES and SNES | Accepted | 2026-10-13 |
| [0027](0027-retro-shaders-pay-once.md) | Add retro shaders through one payload variant per enum | Accepted | 2026-10-13 |
| [0028](0028-retro-shaders-own-gl-program.md) | Run the retro shaders in their own GL program | Accepted | 2026-10-13 |
| [0029](0029-manual-bilinear-sampling.md) | Sample bilinearly by hand in the shaders that expect linear filtering | Accepted | 2026-10-13 |
| [0030](0030-keep-alsa-open-while-fed.md) | Keep the ALSA device open while a game feeds the ring | Accepted | 2026-10-13 |
| [0031](0031-warm-retro-shaders-at-boot.md) | Build and warm the retro shader program at start-up | Accepted | 2026-10-13 |
| [0032](0032-cart-studio-credited-fork.md) | Bring NES and SNES labels to Cart Studio as a credited fork, published once ScreenScraper art is available | Accepted | 2026-10-13 |
| [0033](0033-keep-upstream-lid-timeout.md) | Keep upstream's lid behaviour: doze, then power off after 3 minutes | Accepted | 2026-10-13 |
| [0034](0034-durability-shader-lines.md) | Allow the two shader lines in durability.rs's SlotState literal (named test site f) | Accepted | 2026-10-13 |
| [0035](0035-runner-sensitive-tests-info-on-ci.md) | Run runner-sensitive test binaries as information only on CI | Accepted | 2026-10-13 |
