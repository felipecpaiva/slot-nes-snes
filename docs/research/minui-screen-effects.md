# MinUI / NextUI screen effects vs slot-nes-snes retro shaders (2026-10-14)

Read-only research. Sources: shallow clones of `shauninman/MinUI` (HEAD dbf8943, 2025-11-27, the repo is
archived) and `LoveRetro/NextUI` (HEAD a87e3b5, 2026-10-13), plus a blobless clone of MinUI for history.
Paths below are relative to each repo root. slot paths are relative to `work/slot/crates`.

Outcome: [ADR 0036](../adr/0036-line-pixel-sharp-scanlines.md) and patch 0022 built Line, Pixel and
the sharp Scanlines from this research. Where the build differs from section 6: Line darkens only the
top panel row of each repeat (the task's rule, not the half-row table of line-3..6), and it keeps the
dark row on hires (448/478 line) pictures, where no special case was asked for.

## TL;DR

- MinUI does **not** use shaders. It has three independent axes: **Screen Scaling** (Native/Aspect/
  Fullscreen[/Cropped]), **Screen Sharpness** (Sharp/Crisp/Soft) and **Screen Effect** (None/Line/Grid).
- On H700 (`rg35xxplus` platform, which covers RG34XX and RG34XXSP) all three are done with SDL2 GPU
  texture copies: Sharp/Soft = nearest/linear texture filter; **Crisp** = nearest integer prescale into a
  render target, then a linear copy to the panel; **Line/Grid** = a 1280x960 PNG pattern drawn **1:1 on
  panel pixels** over the picture with alpha, pattern period = MinUI's integer "scale".
- **Crisp is mathematically the same thing as our Sharp** (sharp-bilinear-simple) on the 720x480 panel.
  No value in porting it.
- **Line is the same idea as our Scanlines** but with two real differences: a hard 1-px 50% dark row
  (vs our sine profile), and it is **panel-locked** (computed from `gl_FragCoord`, period = whole scale)
  rather than source-locked. Panel-locking gives uniform stripes, with a far weaker beat than our
  Scanlines shows at SNES Stretch (2.14x). Some residual beat remains: 3-row source lines get 1 or 2 dark
  rows. Caveat: MinUI's period comes from `MAX(ceil(720/src_w), ceil(480/src_h))`, so on the 720-wide
  panel in Aspect it is **3** for both NES and SNES (the width term wins). It is misaligned with the
  2x/2.14x picture and only correct in Native. Our proposed period, floor(rows per source line) = 2, is
  a deliberate improvement, not a copy. And in MinUI it is normally combined with Crisp, so it does not shimmer
  horizontally; our Scanlines samples NEAREST and does shimmer at 2.8125x.
- **Grid** (MinUI) is a subtle 1-px panel-pixel LCD grid; slot's own Grid already covers that look and
  RGC recommends Grid for handheld systems, Line for home consoles. Low value for NES/SNES.
- NextUI kept MinUI's Line/Grid/overlay code and added a 3-pass GLSL pipeline with presets. The one NES/
  SNES-relevant preset we lack is **Pixel Perfect Sharp** = `pixellate.glsl` (area-coverage AA, 4 NEAREST
  taps). It is sharper than sharp-bilinear at non-integer scale.
- **Licences:** MinUI has **no licence** (all rights reserved; author only invites forking "to learn").
  NextUI is **PolyForm Noncommercial 1.0.0** since 2026-08-15 (was GPL-3.0). Neither can be copied into
  GPL-3.0-or-later slot. Ideas are free; the GLSL files NextUI bundles carry their own permissive headers
  (pixellate: ISC-style by Fes; sharp-shimmerless and res-independent-scanlines: public domain) and should
  be taken from libretro/glsl-shaders, not from NextUI.
- **Recommendation:** add 2 entries, both touching only our two files (ADR 0027):
  1. **Line** (MinUI-style panel-locked scanline over a Sharp-sampled picture).
  2. **Pixel** (pixellate/shimmerless area-coverage sharpness).
  Skip Crisp, Soft, MinUI Grid and a separate sharpness axis.

## 1. What MinUI offers, and how

### Option names and defaults

| Option | Values | Default | Evidence |
|---|---|---|---|
| Screen Scaling (`minarch_screen_scaling`) | Native, Aspect, Fullscreen, Cropped (Cropped only on some devices) | Aspect | `workspace/all/minarch/minarch.c:615-621, 47, 841-849`; desc at `:813-819` |
| Screen Effect (`minarch_screen_effect`) | None, Line, Grid | None | `minarch.c:622-627, 49, 851-859`; desc "Grid simulates an LCD grid. Line simulates CRT scanlines. Effects usually look best at native scaling." `:854` |
| Screen Sharpness (`minarch_screen_sharpness`) | Sharp, Crisp, Soft | Soft (code), **Crisp** on rg35xxplus/my355/magicmini via `system.cfg` | `minarch.c:628-633, 861-869` ("Sharp uses nearest neighbor sampling. Crisp integer upscales before linear sampling. Soft uses linear sampling."); `skeleton/SYSTEM/rg35xxplus/system.cfg:1` |
| Shortcuts | Cycle Scaling, Cycle Effect | unbound | `minarch.c:936-937, 1718-1726` |

- **Native forces Sharp** regardless of the sharpness setting: `minarch.c:977, 992`
  (commit `6568086` "native scaling disables crisp sharpness", 2024-01-03).
- **Per-console defaults on rg35xxplus** (`skeleton/SYSTEM/rg35xxplus/paks/Emus/*/default*.cfg`):
  - GB, GBC: Native + Sharp.
  - GBA: Native + Sharp on the wide (RG34XX) and cube variants only.
  - FC (NES) and SFC (SNES): **no screen keys**, so system default **Aspect + Crisp + None**. FC locks
    `fceumm_aspect = 8:7 PAR` (`FC.pak/default.cfg`, the `-` prefix hides it).
  - On the CubeXX: FC/SFC get Cropped + Sharp (`default-cube.cfg`).
- **GB DMG grid colour:** a patched gambatte writes the palette's lightest colour to `/tmp/dmg_grid_color`
  (`workspace/all/cores/patches/gambatte/001-export-dmg-grid-color-on-change.patch:12`). minarch reads it
  (`minarch.c:1372-1380`) and tints the Grid PNG with it (`rg35xxplus/platform/platform.c:714-733`).
  This is GB-only and not relevant to NES/SNES.
- History: Line and Grid were added 2024-08-16 (`13b53f1` "all: added (scan)Line and Grid Screen
  Effects"). An older "scanlines" option was removed 2023-06-19 (`5efaad1`).

### Platform mapping

- `rg35xxplus` is the H700 build. It covers RG35XX Plus/H/SP, RG40XX, CubeXX, RG28XX, **RG34XX and
  RG34XXSP**.
  - `is_rg34xx = prefixMatch("RG34xx", getenv("RGXX_MODEL"))` (`rg35xxplus/platform/platform.c:410-412`)
    matches "RG34xxSP".
  - `RGXX_MODEL` comes from `strings /mnt/vendor/bin/dmenu.bin | grep ^RG`
    (`skeleton/SYSTEM/rg35xxplus/paks/MinUI.pak/launch.sh:25`). `RG34xx*` selects `DEVICE=wide`
    (`:33-34`, also `workspace/rg35xxplus/boot/boot.sh:72`).
  - `skeleton/BASE/README.txt:75` lists RG34XXSP under the RG35XX PLUS install family.
  - That gives `FIXED_WIDTH` 720 x 480 (`rg35xxplus/platform/platform.h:111-112`).
  - The README lists RG34xxSP as added in MinUI-20250920-0. All devices are now "Legacy".
- `my355` is the Miyoo Flip. `tg5040` is the Trimui Smart Pro and Brick. Both use the same SDL2 code
  (`my355/platform/platform.c:242-371`, `tg5040/platform/platform.c:167-296`). tg5040 always prescales
  4x for Crisp (`:175-176`).
- The original rg35xx and miyoomini (not H700) use **CPU NEON/C scalers**. There the effect is baked
  per-pixel in the scaler:
  - `rg35xx/platform/platform.c:399-422`; `all/common/scaler.c:2929, 3022`.
  - Line: the dark row = `Weight3_2(c, black)` = 60 % brightness.
  - Grid 2x: 3 of 4 pixels at `Weight3_1` = 75 %.

### How each H700 mode is drawn (`rg35xxplus/platform/platform.c`)

- **Core frame:** minarch does no CPU scaling on this platform. `PLAT_getScaler` returns `scale1x1_c16`
  (`:752-756`). The frame is uploaded as an RGB565 streaming texture, and SDL2's GLES renderer scales it
  in `PLAT_flip` (`:758-850`).
- **Sharp / Soft:**
  - `SDL_HINT_RENDER_SCALE_QUALITY` is set to "0" or "1" when the texture is created (`:579`).
  - That means GL_NEAREST or GL_LINEAR on the single copy to `dst_rect`.
- **Crisp:**
  - `resizeVideo` creates a target texture `w*hard_scale x h*hard_scale` (`:582-588`).
  - `hard_scale` is 2 when the source height is at least 160 (NES/SNES/GBA), 4 for GB-sized sources, and
    1 when the source is panel-sized (`:561-571`).
  - Each frame it copies the source to the target with **nearest** filtering (integer prescale), then
    copies the target to the screen with **linear** filtering (`:787-797`).
  - It is the classic "sharp-bilinear by prescale" done with two SDL copies, i.e. an extra
    render-to-texture pass.
- **Line / Grid:**
  - `updateEffect` (`:645-741`) loads `line-N.png` / `grid-N.png` (1280x960 RGBA) chosen by
    `renderer->scale`.
  - The alpha is set with `SDL_SetTextureAlphaMod`:
    - Line: 128 (50 %).
    - Grid: 64 / 112 / 144 / 160 / 112 / 144 / 136 for N = 2 / 3 / 4 / 5 / 6 / 8 / 11, tuned so average
      darkening stays about 19-25 % (comments in source).
  - It is drawn with src rect `{0,0,dst_w,dst_h}` onto `dst_rect` (`:838-846`), i.e. **1:1 panel
    pixels, origin at the picture's top-left**. The pattern is tied to the panel grid and not to the
    source texels.
- Decoded pattern tiles (black, alpha before AlphaMod; full PNGs in `skeleton/SYSTEM/res/`):
  - line-2: row 0 opaque, row 1 clear.
  - line-3: rows 255 / 128 / 0.
  - line-4: 2 opaque, 2 clear.
  - line-5: 255 / 255 / 128 / 0 / 0.
  - line-6: 3 opaque, 3 clear.
  - grid-N: a 1-px opaque top row and left column per N x N cell (grid-6 uses 2 px).
- **What "scale" is at non-integer modes:**
  - On rg35xxplus `fit = 0` (no `USES_SWSCALER`, `minarch.c:2498-2502`).
  - Aspect/Fullscreen take `scale = MAX(ceil(720/src_w), ceil(480/src_h))` (`minarch.c:2660-2668`).
  - Example, NES in Aspect: scale = max(3, 2) = 3, so a period-3 line pattern lies over a picture that
    is exactly 2x vertically. The pattern is uniform on screen but not aligned with source lines.
  - That is why the menu text says effects look best at Native. In Native (NES 256x240 -> 512x480,
    SNES -> 512x448, scale 2) line-2 is a perfect source-locked 1-on/1-off scanline.
- **Non-integer handling in short:**
  - Aspect plus Crisp gives 2x nearest, then linear by 1.14x (NES 8:7 PAR: 512->585 wide, 480 tall
    exact).
  - SNES 4:3 is 512x448 -> 640x480.
  - The effect overlay never blurs and never beats in intensity because it is panel-pixel exact.

## 2. NextUI (LoveRetro/NextUI, MinUI fork)

- **Frontend options** (`workspace/all/minarch/ma_config.c:905-1010, 1330-1420`):
  - Screen Scaling: Native, Aspect, **Aspect Screen**, Fullscreen, Cropped.
  - Screen Effect: None/Line/Grid, the same PNGs and opacity table in
    `workspace/all/common/generic_video.c:944-1027`, drawn 1:1 at `dst_rect` (`:2288-2294`).
  - **Overlay:** a user PNG.
  - Screen Sharpness was re-keyed to `minarch_scale_filter` with values **NEAREST/LINEAR**. Crisp was
    removed (`:1000-1010`) because the shader pipeline replaces it.
  - "Shaders" menu (`ma_menu.c:952`): up to 3 GLSL passes with per-pass filter, srctype, scaletype and
    upscale (`minarch_shaderN_*`).
- **h700 defaults** (`skeleton/SYSTEM/h700/system.cfg`):
  - Aspect, `minarch_nrofshaders = 0`, scale filter NEAREST.
  - A pre-filled but disabled chain recreates Crisp: stock 2x NEAREST -> stock relative LINEAR -> screen.
  - FC/SFC paks set no screen keys. So **NES/SNES default = Aspect + NEAREST + no effect.**
- **Bundled presets** (`skeleton/BASE/Shaders/*.cfg`):
  - `scanlines` = res-independent-scanlines (PD, RiskyJumps; the same source as our Scanlines).
  - `old-tv` = barrel-distortion + scanlines.
  - **`pixelperfect-sharp` = `pixellate.glsl` at screen size, NEAREST.**
  - `pixelperfect-smooth` = stock 3x NEAREST then LINEAR (= Crisp).
  - `real-gameboy` / `real-gba` = pixellate + lcd3x (GB/GBA only).
- **GLSL folder** also has: sharp-bilinear (PD), sharp-shimmerless (+grid, +subpixel-vrgb; PD, zadpos),
  scanline, lcd1x/lcd3x, retro-v2, scale3x, aa-shader-4.0, bicubic, fast-sharpen, edge1pixel,
  pixel_art_AA, waterpaint.
- **pixellate.glsl** (Fes, ISC-style permissive):
  - Box-filters the source over the output pixel's footprint: 4 NEAREST taps weighted by covered area.
  - Optionally in linear gamma, 4x `pow(2.2)` + 1 `pow(1/2.2)`.
  - Transition width is at most 1 output pixel. Compare sharp-bilinear at 2.8125x: 2x prescale, then a
    bilinear span of about 1.4 px.
  - It is the sharpest shimmer-free filter of the bunch.
- **Licence:**
  - `LICENSE` = PolyForm Noncommercial 1.0.0.
  - `NOTICE`: "previously licensed under GPL 3.0. As of August 15, 2026 ... PolyForm Noncommercial", and
    "The original MinUI repository carries no formal license."

## 3. Why users rate MinUI's picture on low-end devices

There is little direct user commentary. What was found and confirmed:

- RetroGameCorps, "Shaders and Overlays on Retro Handhelds"
  (https://retrogamecorps.com/2024/09/01/guide-shaders-and-overlays-on-retro-handhelds/):
  - MinUI devices "have the option to add a light grid or scanline shader".
  - It recommends Grid for handheld (LCD) systems and Line for home-console (CRT) systems.
  - On 640x480 screens "non-integer scaling can present some issues with pixel balance".
  - GPU-side effects carry no "significant performance tax" because emulation is CPU-bound.
- RetroGameCorps, MinUI Starter Guide (https://retrogamecorps.com/2025/10/24/minui-starter-guide/):
  - The author's preference is "Screen Scaling: Aspect / Screen Effect: Grid / Screen Sharpness: Crisp
    (only applicable on some handhelds)".
  - The guide notes the settings are "already pre-configured by the MinUI developer".
- Reddit r/SBCGaming could not be fetched (proxy refused). **No Reddit quote is confirmed.**

Technical reasons, from the code above:

1. **Crisp by default on H700:** no shimmer at non-integer Aspect, and the image barely softens.
2. **Effects are panel-pixel exact:** a hard 1-px pattern, no moire from sampling, no intensity beat
   bands, never blurred.
3. **Per-console curation:** GB/GBC/GBA default to Native + Sharp, so they look perfect with zero setup.
   Opacity is tuned per scale.
4. **Nearly free:**
   - One extra textured quad for the overlay.
   - One render-to-texture for Crisp.
   - No per-pixel math.
   - On non-GPU devices the effect is baked into the NEON scaler.

## 4. Licence conclusion

- **MinUI:** no licence file (confirmed: no LICENSE in the tree; the NextUI NOTICE says the same). The
  default is all rights reserved, so **do not copy code or the PNGs**. The patterns are trivial, so
  generate them procedurally. The technique (panel-locked overlay with period = whole scale, prescale-
  then-linear) is an idea and is free to reimplement.
- **NextUI:** PolyForm NC is incompatible with GPL-3.0 (it adds a noncommercial restriction). Don't port.
  GPL-era NextUI code is MinUI-derived with unclear upstream rights, so avoid it too.
- **Shaders:** port from libretro/glsl-shaders originals:
  - `interpolation/shaders/pixellate.glsl` (ISC-style, GPL-compatible).
  - `sharp-shimmerless` (PD per its header by zadpos; it is not at `interpolation/shaders/` in libretro/glsl-shaders (404), so confirm the canonical source before porting, or use pixellate).
  - pixellate's ISC-style terms require its **full copyright and permission notice** in the copy, not a
    one-line credit. Put the whole notice in the GLSL comment in `pipeline/retro.rs`, as crt-pi's GPL
    notice already is.
  - `work/slot/licenses/shaders.txt` (upstream file) lists only LCD3x, Dot, zfast_lcd and simpletex.
    Patch 0020 did not add Sharp, Scanlines, crt-pi or crt-1tap there. So adding pixellate there would be
    the first patch hunk to that file, which is optional; its in-source notice is enough for the
    licence. If the maintainer wants shaders.txt complete, that is a one-time upstream-file append
    covering all retro shaders.

## 5. Gap analysis vs slot NES/SNES list (Off, Grid, Dot, Sharp, Scanlines, crt-pi, crt-1tap)

Our geometry (docs/research/retro-shaders.md section 2):
- NES Stretch: 2.8125x horizontal, exactly 2x vertical.
- SNES Stretch: 2.8125x horizontal, 2.142857x vertical.
- Actual: integer 2x.

| MinUI/NextUI | Closest slot | Same? | New value |
|---|---|---|---|
| Crisp | Sharp (`pipeline/retro.rs` `sharp()`, sharp-bilinear-simple) | **Equivalent.** Both are integer prescale floor(out/in) then bilinear. At 720x480 that is prescale (2,2) for NES and SNES in Stretch and Aspect, exactly MinUI's `hard_scale = 2`. Ours is analytic in one pass (4 manual taps); MinUI uses an extra FBO. | none |
| Sharp (nearest) | Off | same | none |
| Soft (plain linear) | none (but `bilinear()` already exists in retro.rs) | - | low. Blurry; one line if wanted |
| Line | Scanlines (sine-abs, source-locked, NEAREST base) | **Different.** At NES 2x: ours gives rows at about 100 % / 35 % (abs(sin) x 1.25 clipped); MinUI gives 100 % / 50 %. At SNES Stretch: ours beats (bands about every 7th line); a panel-locked period-2 gives uniform stripes (MinUI itself uses period 3 in Aspect, period 2 only in Native). Base sampling: ours NEAREST (shimmers at 2.8125x), MinUI Crisp. | **yes.** A near beat-free, shimmer-free, cheap scanline |
| Grid | Grid (upstream, source-locked, antialiased band edges, 75 % darken at edges) | Similar intent. MinUI's is a much lighter 1-px panel grid (about 19 % average at 2x). | low for NES/SNES (an LCD look on CRT-era systems) |
| NextUI pixelperfect-sharp (pixellate) | Sharp | **Different:** a 1-px area-AA edge vs about a 1.4-px bilinear edge at 2.8125x | **yes.** The sharpest shimmer-free option |
| NextUI scanlines (res-independent) | Scanlines | identical source | none |
| NextUI old-tv (barrel + scanlines) | crt-pi / crt-1tap | curvature at 2x looks poor (previous research) | skip |
| Native / Aspect / Fullscreen / Cropped | Actual / aspect / Stretch | Cropped is aimed at the 720x720 CubeXX | skip |

## 6. How to add them in our design

Both new entries are `RetroShader` variants with a branch in `RETRO_FRAG`. They touch only
`slot-store/src/retro_shader.rs` and `slot-gfx/src/pipeline/retro.rs`, so **zero upstream hunks**
(ADR 0027). The licence notice goes in the GLSL comment (see section 4). No second pass, no overlay texture, no PNG asset.

### Line (MinUI-style)

```glsl
// period k = whole output rows per source line, min 2 (MinUI's integer "scale")
float k = max(floor(1.0 / texel_per_px.y), 2.0);
float row = mod(floor(gl_FragCoord.y - pic_top_px), k);   // origin = picture's top edge in FBO px
float half_k = k * 0.5;
float dark = row < floor(half_k) ? 1.0 : (row < half_k ? 0.5 : 0.0);  // matches line-2..6 tiles
c = sharp(uv, 1.0 / texel_per_px) * (1.0 - 0.5 * dark);    // 50% like MinUI AlphaMod 128
```

- Values of k:
  - NES Stretch/Actual: k = 2, aligned with source lines. Same result as MinUI in **Native**.
  - SNES Stretch: k = 2, uniform stripes with a far weaker beat.
  - **Not** what MinUI does in Aspect. There its period is `MAX(ceil(720/src_w), ceil(480/src_h))` = 3
    for NES and SNES (`minarch.c:2660-2668`), a period-3 pattern over a ~2x picture. Deriving k from
    the vertical scale only is our improvement.
  - SNES Actual: k = 2.
  - Interlace/hires (448/478 lines): 1/texel_per_px.y < 2, so k clamps to 2. Consider `dark = 0` when
    `u_src.y >= 400`, as the previous research advised.
- **Alignment:**
  - gl_FragCoord is bottom-up in the FBO. The y origin must come from `u_rect`
    (`u_rect.y`/`u_rect.w` x `u_fbo`).
  - Use the bottom or top edge consistently so that, at NES 2x, the dark row lands on the **first (top)
    row** of each source line, matching MinUI's line-2 tile (row 0 opaque) and the GLSL above. Verify on device with a 1-px test pattern or a screenshot.
  - Assumption: the FBO is in panel pixels, the same assumption crt-pi's `gl_FragCoord` mask already
    relies on. This needs `u_fbo` = 1.0, i.e. FBO = panel, which holds on the RG34XXSP. The final blit must be
    1:1 (any rotation stays pixel-exact).
- **Cost:**
  - 4 NEAREST taps (sharp), or 1 if the base is plain.
  - A handful of ALU ops.
  - Cheaper than crt-pi, which shipped with no measurable cost (ADR 0026, DEVICE-GATE.md).
- **Sampling choice:** Line uses `sharp()` as its base. That gives MinUI's default "Crisp + Line"
  combination without a sharpness axis.

### Pixel (area coverage, pixellate / sharp-shimmerless)

- 4 NEAREST taps weighted by the overlap of the output pixel footprint (`texel_per_px`) with texel
  cells. Fits the existing `tap()`.
- Gamma-correct averaging:
  - The original uses 5 `pow`. Use `c*c` in and `sqrt` out (gamma 2.0) to avoid transcendentals.
  - Or skip gamma: the visual difference is minor at 2-3x.
- Port from `libretro/glsl-shaders interpolation/shaders/pixellate.glsl` (ISC) or sharp-shimmerless
  (PD), with the attribution comment.
- Cost: 4 taps, the same as Sharp.

### Plumbing gotchas inside our two files

- `warm()` in `pipeline/retro.rs` hard-codes `for n in 0..4u8` ("the four branches"). It must become
  `0..RetroShader::ALL.len()` (or 6), or the new modes pay the 31-67 ms first-present hitch that ADR
  0031 fixed.
  - slot-gfx can't see slot-store, so use a const or pass the count.
- The `u_mode` threshold chain is ordered. New branches go at the top (`> 4.5`, `> 3.5`), with the
  variants appended to `RetroShader::ALL` so the stored indices stay stable.
- Labels: "Line" (or "Scanlines (sharp)") and "Pixel". Decide whether "Line" sits alongside or
  **replaces** the existing "Scanlines". Replacing one would change the meaning of a stored
  `shader_nes=scanlines` value. Keep both, or map the old name.
- Tests (ours only):
  - A CPU mirror of the row-to-dark function and of the coverage weights, as `lcd3x_mask` does.
  - Example assertions:
    - k = 2 at NES Stretch; k = 2 at SNES Stretch; k = 3 for a 160-line source at 480.
    - Coverage weights sum to 1.
    - The coverage of a texel-aligned pixel is exactly 1 tap.
  - Update the cycle-order expectations in `slot-store/tests/nes_shader_state.rs`,
    `slot/tests/nes_snes_shader.rs` and `slot/tests/quick_retro_shader.rs`.
  - Device gate: `task perf:play` p99 versus Off.

### Separate sharpness axis (MinUI-style scaling x sharpness x effect)?

Cost in slot:
- New `slot.state` keys (`sharpness_nes`/`sharpness_snes`) and parse/default code in the upstream
  `slot_state.rs`.
- A new quick-menu row. `QuickRow::SCREEN` is pinned at 4 by upstream tests
  (`slot-ui/src/quick_menu.rs:54`; ADR 0008/0023 kept it at 4). A per-shelf page would be needed again.
- New Toast faces, and a frontend -> `GamePass` field (an upstream `pipeline.rs`/`frontend.rs` hunk).
- Grid and Dot live in upstream `GAME_FRAG` (`slot-gfx/src/shaders.rs:73-113`), so sharp-sampled
  Grid/Dot would need upstream shader edits.

That breaks ADR 0027's zero-touch goal for about 8-12 upstream hunks.

Benefit: the only real combinations users want are Sharp+Line and Sharp+CRT. The CRT shaders already
bilinear-sample, and Line can bake `sharp()` in.

**Recommendation: no separate axis.** Bake the sharp base into the effects that need it. Optionally
switch the existing Scanlines to sample `sharp()` instead of NEAREST: one line, and it fixes its
horizontal shimmer.

## 7. Recommendation (in order)

1. **Add "Line"**: MinUI-style panel-locked 50 % 1-on/1-off scanline over a Sharp-sampled picture. It is
   the near beat-free, shimmer-free, cheapest scanline, and it is what MinUI users mean by "Line + Crisp".
2. **Add "Pixel"**: pixellate/shimmerless area-coverage sharpness (NextUI "Pixel Perfect Sharp"). It is
   sharper than our Sharp at 2.8125x, with the same 4-tap cost and an ISC/PD licence.
3. *(Cheap fix)* Make the existing Scanlines sample `sharp()` instead of NEAREST.
4. *(Optional)* Consider making NES/SNES presets mirror MinUI's per-console thinking. For example, Line
   could default to Actual for SNES. Not needed now.

**Skip:**
- Crisp: identical to Sharp here.
- Soft: plain blur.
- MinUI Grid: slot Grid covers it, and it is an LCD look on CRT systems.
- A separate sharpness axis: about 8-12 upstream hunks for combinations we can bake in.
- Cropped scaling: aimed at the CubeXX.
- old-tv / barrel: curvature at 2x.
- Copying any MinUI or NextUI code or PNGs (licence).

## Sources

- https://github.com/shauninman/MinUI (archived 2025-11-27): files and lines above; commits 13b53f1,
  6568086, c002ee8, 5051ace.
- https://github.com/LoveRetro/NextUI (a87e3b5): LICENSE, NOTICE, `ma_config.c`, `generic_video.c`,
  `skeleton/BASE/Shaders`, `skeleton/SYSTEM/h700/system.cfg`.
- https://retrogamecorps.com/2024/09/01/guide-shaders-and-overlays-on-retro-handhelds/
- https://retrogamecorps.com/2025/10/24/minui-starter-guide/
- https://github.com/libretro/glsl-shaders/blob/master/interpolation/shaders/pixellate.glsl (verified 200).
