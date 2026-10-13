# More NES/SNES shaders for slot-nes-snes: research (2026-10-13)

Read-only research. Code paths are relative to `work/slot` unless noted.

## 1. Inventory: what exists today

### The shader model
- `Shader` enum, `crates/slot-store/src/slot_state.rs:46-52`: `Off, Lcd3x, Grid, Dot, Simpletex`.
- Per-platform lists, `slot_state.rs:55-57`:
  - `GBA = [Off, Lcd3x, Grid, Dot]`
  - `GB = [Off, Grid, Simpletex]`
  - `RETRO = [Off, Grid, Dot]` (added by patch 0014, used by NES and SNES)
- NES and SNES default to `Off` (`slot_state.rs:116-117`). Settings are stored as `shader_nes` / `shader_snes`, and parsing only accepts members of `RETRO` (`slot_state.rs:218-220`).
- Platform mapping: `crates/slot-store/src/platform_policy.rs:53-55` (`Nes | Snes => &Shader::RETRO`).
- **Patch 0014 added no GLSL.** It reused upstream's existing Grid and Dot modes for NES/SNES. Its hunks are only store/state/app/tests (`patches/0014-shaders.patch` diffstat). Patch 0018 only adds quick menu rows that cycle `Shader::RETRO` (`slot-ui/src/quick_menu.rs`, our own `quick_retro.rs`, `retro_quick.rs`).

### How the GLSL is written
- Everything is in **one uber fragment shader**, `GAME_FRAG`, at `crates/slot-gfx/src/shaders.rs:48-114`. It branches on a float uniform `u_mode` using thresholds:
  - `> 3.5` Simpletex (`:79`)
  - `> 2.5` Dot (`:92`)
  - `> 1.5` Grid (`:102`)
  - `> 0.5` LCD3x (`:106`)
  - New modes must be inserted above the top threshold, so the branch order matters.
- `u_mode` comes from `ScreenEffect::mode()`, which returns `self as u8 as f32` (`crates/slot-gfx/src/lcd3x.rs:13-25`). That enum is `None, Lcd3x, Grid, Dot, Simpletex`.
- **GLSL version:** on the device it is GLSL ES 1.00. The EGL context is ES2 (`fbdev.rs:187,218`, `EGL_CONTEXT_CLIENT_VERSION 2`), and the ES preamble adds no `#version` (`shaders.rs:8-9`). The desktop build uses `#version 330 core` with `texture2D` macros (`shaders.rs:3-6`). Precision is `highp` when available (`shaders.rs:49-53`). So ports must use ES 1.00 syntax only: no `texture()`, no `textureSize`, constant loop bounds.
- **It is single-pass** and there is no multi-pass chain. The game quad is drawn with this program into an FBO (`slot-gfx/src/fbo.rs:263-273`), then blitted with `BLIT_FRAG` (`shaders.rs:148-156`). A multi-pass shader would need a new FBO chain.
- **Uniforms available to the effect** (`pipeline.rs:47-66,186-207`):
  - `u_game`: the source texture.
  - `u_src`: the canvas size in texels, which is the source size. It is updated in `set_canvas`, `pipeline.rs:138`.
  - `u_uv`: the source sub-rect.
  - `u_rect`: the on-screen rect in 720x480 logical px.
  - `u_fbo`: FBO scale relative to 720x480 (1.0 on the RG34XXSP).
  - `u_pic`: the picture rect.
  - `u_bright`.
  - `u_paper` / `u_paper_size`: Simpletex texture.
  - `gl_FragCoord` is also used (`shaders.rs:90`).
  - Output size in px is derivable as `u_rect.zw * u_fbo`, which Grid already does (`shaders.rs:103`).
  - **There is no FrameCount uniform**, so interlace/flicker effects are out unless you add one.
- **The source texture is `GL_NEAREST`** (`pipeline.rs:38`, `:133`). This is the biggest porting fact. The cheap libretro CRT shaders are written for `filter_linear0 = true`: zfast-crt, crt-pi, crt-1tap, fakelottes, crt-lottes-fast and sharp-bilinear all set it in their `.glslp` (sources in section 2). A port has two choices:
  - (a) Switch the texture to LINEAR for those modes. That is a `TexParameteri` in `draw_source` (`pipeline.rs:186-208`), one more hunk in a file 0004 already patches.
  - (b) Emulate bilinear in-shader with 2 or 4 NEAREST fetches. That costs no gfx-plumbing hunk, but each shader goes from 1 fetch to 2 or 4.
  - Shaders that work as-is on NEAREST (crt-easymode, crt-hyllian, crt-geom, xbr-lv2) are the heavier ones.
- Grid has a special source crop. `whole_scale_source` (`pipeline.rs:176,211-226`) snaps the source to a whole scale when the trim is under 10%.

### How GBA/GB shaders are done upstream
They use the same uber shader, as one-pass math on a single NEAREST fetch:
- LCD3x: sine RGB triad and scanline (`shaders.rs:106-110`). Mirrored on the CPU for tests in `lcd3x.rs:7-35`.
- Grid: zfast_lcd-style band edges (`:102-105`).
- Dot: Themaister dot, a 3x3 `exp()` loop (`:92-101`).
- Simpletex: zfast_lcd plus a paper texture (`:79-91`).

Attribution is in `licenses/shaders.txt`:
- LCD3x: public domain.
- Dot: public domain.
- zfast_lcd: GPL-2+.
- simpletex: GPL-2+.

slot is GPL-3+.

### Every touch point for one new NES/SNES shader (current design)
The enums are matched exhaustively, so each new variant hits all of these:

| File (upstream?) | Hunks | What |
|---|---|---|
| `slot-store/src/slot_state.rs` (upstream, 0014 already touches it) | 3 | enum variant (`:46`), `name()` (`:60`), `parse` list (`:70`); `RETRO` const grows (`:57`, the existing 0014 line) |
| `slot-gfx/src/lcd3x.rs` (upstream, **untouched today**) | 1 | `ScreenEffect` variant (append, so the `as u8` discriminant stays stable) |
| `slot-gfx/src/shaders.rs` (upstream, **untouched today**) | 1 | new `u_mode > N.5` branch, placed at the top of the chain |
| `slot/src/frontend.rs` (upstream, already patched) | 1 | `Shader -> ScreenEffect` map (`:344-350`) |
| `slot/src/app.rs` (upstream, 22 hunks already) | 2 | toast match (`:1423-1429`), `shader_value` (`:3399-3406`) |
| `slot-ui/src/toast.rs` (upstream) | 3 | variant (`:19-23`), `FIXED: [Toast; 15]` (`:39-46`), `text()` (`:84-88`) |
| `slot-ui/src/quick_menu.rs` (upstream, 0018 already touches it) | 3 | `QuickValue` variant (`:154`), `ALL: [_; 10]` (`:168`), `text()` (`:186`) |
| `slot-gfx/src/pipeline.rs` (upstream, 0004) | 0-1 | only if the shader needs LINEAR sampling (option a above) |
| `licenses/shaders.txt` (upstream file) | 1 | attribution |
| tests: `slot-store/tests/nes_shader_state.rs`, `slot/tests/nes_snes_shader.rs`, `slot/tests/quick_retro_shader.rs` (ours) | - | expected cycle orders, for example `[Grid, Dot, Off]` at `nes_snes_shader.rs:39` and `quick_retro_shader.rs:85`. These are our files and cost no upstream hunk. |

**Estimate:**
- The first new shader costs about 13-15 new upstream hunks across 8-9 files. Two of those files (`shaders.rs`, `lcd3x.rs`) would be touched by the patch set for the first time.
- Each later shader mostly extends the same hunks: about +1 line in each of the ~13 places, plus a GLSL block.
- `docs/UPSTREAM-TOUCHPOINTS.md` regenerates via `task diffsurface`. **Zero upstream hunks per shader is not possible with the current enums.**

**Pay-once option (described, not designed).** Use one payload variant per enum, on the model of the existing `Toast::Palette(GbPalette)` (`toast.rs:57`, `Toast::all()` chains `GbPalette::all()`):
- e.g. `Shader::Retro(RetroFx)`, `ScreenEffect::Retro(RetroFx)`, `Toast::Retro(RetroFx)`, `QuickValue::Retro(RetroFx)`.
- `RetroFx`, its labels and its GLSL live in our own files, for example a new `slot-gfx/src/retro_fx.rs` with its own GL program that `GamePass` selects in `draw_source`.
- After the one-time setup, each added shader touches only our files.
- Catches:
  - `ScreenEffect::mode()` and `QuickValue::index()` are `self as u8/usize` casts, which do not work on data-carrying enums. Both need offset arithmetic, as `Toast::index` already does.
  - `Shader::RETRO` is a fixed-size `const` array.
  - The setup itself is a bigger one-time diff than adding 2-3 plain variants.
- Worth it only if more than about 3 shaders are planned.

## 2. Screen geometry: why non-integer scale matters

- NES canvas is 256x240. Overscan crop is forced to 0 for fceumm and nestopia (`slot/src/core_options_policy.rs:11-30`, patches 0003/0010). SNES is 256x224, or 512x224 hires, or 448/478 lines interlaced.
- Panel and logical output: 720x480 (`slot-gfx/src/surface.rs:4-5`).
- NES/SNES default to **Stretch** (`docs/adr/0022-nes-snes-default-stretch.md`, `slot/src/platform_video.rs:10`). Actual is integer 2x: 512x480 and 512x448 (`docs/adr/0021-reference-device-rg34xxsp.md`).

| Case | Vertical scale | Horizontal scale |
|---|---|---|
| NES, Stretch or Actual | 480/240 = **exactly 2x** | Stretch 720/256 = 2.8125x; Actual 2x |
| SNES, Actual | 448/224 = **exactly 2x** | 2x |
| SNES, Stretch (default) | 480/224 = **2.142857x** (non-integer) | 2.8125x |
| SNES interlace, 448/478 lines | ~1.07x / ~1.004x | - |

What this means for each kind of effect:
- **Source-locked scanlines at SNES Stretch beat.** 224 lines spread over 480 rows gives 32 lines of 3 rows and 192 lines of 2 rows, so you see a visible periodic band roughly every 7th line.
  - Grid's whole-scale snap does not help here. `whole_scale` (`pipeline.rs:218-225`): ceil(480/224)=3, trim=672-480=192, which is at least 0.1x224, so no snap.
  - Fixes:
    - (1) Use a smooth (sine/gaussian) scanline profile. Its sub-pixel variation hides the beat better than a hard 1-on/1-off pattern.
    - (2) Multisample the scanline weight. crt-pi's `MULTISAMPLE` exists for this.
    - (3) Recommend Actual (integer 2x) for scanline shaders.
    - (4) Skip scanlines when the source has 400 or more lines (interlace/hires).
- **Even at an exact 2x, a scanline is only 2 output rows.** That is a bright row and a dark row, which looks harsh and loses about 25-50% brightness. crt-pi's author says scanline banding evens out only with "4x or more" screen px per scanline ([libretro forum, crt-pi thread](https://forums.libretro.com/t/raspberry-pi-friendly-crt-shader/3937)). So expect mild, bright-boosted scanlines here, not a convincing CRT.
- **Masks keyed to `gl_FragCoord`** (crt-pi `MASK_TYPE`, zfast's `whichmask`) are tied to output pixels, so the 2.8125x horizontal stretch does not cause moire. Masks keyed to source texels would.
- **The horizontal stretch at 2.8125x is non-integer under NEAREST.** Columns alternate 2 and 3 px wide, which shimmers on scroll. Sharp-bilinear and shimmerless smoothing exist exactly for this, and Stretch is the default. That makes the strongest case for adding a "sharp" smoothing mode.

## 3. Candidates

Cost anchor: the already-shipped **Dot** mode (`shaders.rs:92-101`, 1 fetch plus a 3x3 loop of 9 `exp()`) runs on the device. "Cheap" means at or below Dot; "medium" is above Dot but single-pass; "heavy" is multi-pass or many fetches plus transcendental functions. No reliable Mali-G31 MP2 clock or GFLOP figure for the H700 was found, so none is quoted. Pixel load is 720x480 at about 60 Hz, about 20.7 Mpx/s. That is about 1/6 of the 1080p60 crt-pi was built for on Pi VideoCore. **Shader cost on top of the core is unmeasured** (`docs/PERFORMANCE.md:255`).

| Shader | Look | Passes | Needs | Fetches (filter) | License (from file header) | Cost vs Dot | Portable to slot ES 1.00 one-pass? |
|---|---|---|---|---|---|---|---|
| **Simple scanlines**: scanlines-sine-abs / NextUI `res-independent-scanlines` (RiskyJumps) | dark lines between source lines | 1 | source size, output size | 1 (any) | **Public domain** | cheaper | Yes, trivial |
| `scanlines/scanline.glsl` | sine scanline plus faint grid | 1 | source, output | 1 | **No header** (unknown) | cheaper | Yes, but prefer the PD sine-abs |
| **sharp-bilinear** (Themaister) / sharp-bilinear-simple / sharp-shimmerless (zadpos) | crisp pixels without shimmer at non-integer scale | 1 | source, output | 1 (**LINEAR**), or 4 NEAREST manual | **Public domain** (sharp-bilinear; sharp-bilinear-scanlines by rsn8887 PD; shimmerless PD per NextUI copy) | cheaper | Yes; needs LINEAR or a 4-tap manual bilinear |
| **zfast-crt** (Greg Hogan) | light scanlines that fade with luma, mono aperture mask, slight X blur | 1 | source, output | 1 (**LINEAR**) | **GPL-2.0+** (same author and license as the shipped zfast_lcd) | cheaper (no transcendental calls) | Yes. Written for weak GPUs |
| **crt-pi** (davej) | gamma-correct scanlines with bloom, 2- or 3-px RGB mask on `gl_FragCoord` | 1 | source, output (for MULTISAMPLE) | 1 (**LINEAR**) | **GPL-2.0+** | about Dot (2 pow, 3x scanline weight with MULTISAMPLE) | Yes. MULTISAMPLE helps the SNES 2.14x beat |
| **crt-1tap** (fishku, GLSL port by DariusG) | soft scanline beam, 1 fetch | 1 | source, output | 1 (**LINEAR**) | **CC0** (public domain) | cheaper | Yes |
| **fakelottes** (hunterk) | Lottes-style scanlines and mask, optional curvature | 1 | source, output | 1 (LINEAR), 2 pow, sin | **No license in header** (needs confirmation) | about Dot | Yes (drop CURVATURE) |
| **crt-lottes-fast** (Timothy Lottes, adapted by hunterk) | Lottes CRTS: scanlines, mask, warp | 1 | source, output | about 13 fetch sites (LINEAR), sRGB pow | **Public domain** | medium (many taps) | Yes, but it is 700 lines; a bigger port |
| **crt-easymode** (EasyMode) | sharp CRT with mask and halation-free scanlines | 1 | source, output, FrameCount (optional) | 4 bilinear or 8 lanczos (NEAREST), several pow and cos | "**License: GPL**", no version stated. That means any GPL version may be chosen (GPL-3 section 14), so it is fine for slot | medium (about 2-4x Dot fetches plus pow) | Yes |
| crt-aperture (EasyMode) | aperture-grille mask and scanlines | 1 | source, output | 2-3 mat3 taps (NEAREST), pow | "License: GPL" (as above) | medium | Yes |
| crt-hyllian | sharp Trinitron/BVM look | 1 | source, output | 8 (NEAREST) plus gamma | **MIT** | medium | Yes |
| crt-geom (cgwg, Themaister, DOLLS) | curved CRT, Lanczos, scanline gaussian | 1 | source, output, FrameCount for interlace | 8 (NEAREST), exp/pow per tap, oversample loop | **GPL-2.0+** | heavy for this GPU (many transcendental calls per pixel) | Possible but not worth it at 2x |
| zfast_crt_geo / _svideo (Hogan + Dogway) | zfast plus curvature/glow/svideo | 1 | source, output | 3 | GPL-2.0+ | cheap to medium | Yes. RetroGameCorps pick |
| NTSC: ntsc-adaptive / blargg / ntsc-mini / tiny_ntsc | composite artifacts, dither blending | 2-4 (`ntsc-adaptive.glslp` 2, `ntsc-simple` 4, `ntsc-mini` 3) | intermediate FBOs, FrameCount | many | mixed | heavy on structure (needs an FBO chain slot lacks) | **No** without a multi-pass pipeline |
| xBR-lv2 (Hyllian) | edge-smoothing upscale | 1 | source | **21** (NEAREST) plus heavy ALU | MIT | heavy (about 2x Dot fetches plus branching) | Possible, but it is a smoothing filter, not a retro look |
| ScaleFX / scalefx-hybrid | best edge smoothing | **5** passes (`scalefx.glslp`) | FBO chain | many | - | heavy | **No** |
| crt-royale | full phosphor/mask simulation | about 12 passes | FBO chain, LUTs | many | GPL-2+ | far too heavy | **No** |

Shader sources: [libretro/glsl-shaders](https://github.com/libretro/glsl-shaders).
- `crt/shaders/zfast_crt.glsl`, `crt-pi.glsl`, `crt-easymode.glsl`, `fakelottes.glsl`, `crt-lottes-fast.glsl`, `crt-geom.glsl`, `crt-aperture.glsl`, `crt-Ntap/crt-1tap.glsl`, `hyllian/crt-hyllian.glsl`
- `interpolation/shaders/sharp-bilinear*.glsl`
- `xbr/shaders/xbr-lv2.glsl`
- presets `crt/*.glslp`, `scalefx/*.glslp`, `ntsc/*.glslp`

License caveats:
- The GitHub API reports `license: null` for the glsl-shaders repo, so the per-file header is the only license. Files without a header (fakelottes, `scanline.glsl`) should be treated as unknown until confirmed.
- [NextUI's shader copies](https://github.com/LoveRetro/NextUI/tree/main/skeleton/BASE/Shaders/glsl) also carry PD headers for res-independent-scanlines and sharp-shimmerless.

## 4. Popularity: what handheld CFWs and guides actually use for NES/SNES

Only sources fetched directly are marked confirmed.

| Source | NES/SNES-relevant default or recommendation | Status |
|---|---|---|
| Knulli (H700 CFW, Batocera-based) shader sets ([knulli.org shaders](https://knulli.org/configure/customization/shaders/)) | "Scanlines" set uses **crt-pi for low-GPU devices** (crt-easymode elsewhere); "Zfast" set uses **zfast-crt**; "Curvature" uses **crt-lottes-fast**; "Retro" uses **sharp-bilinear-simple** | confirmed |
| Batocera ([wiki: shader sets](https://wiki.batocera.org/emulationstation:shaders_set)) | **sharp-bilinear-simple is the default shader since v32**; sets: scanlines, curvature, zfast, retro, enhanced, flatten-glow | confirmed |
| NextUI (minarch, ships h700 builds) ([repo tree](https://github.com/LoveRetro/NextUI/tree/main/skeleton/BASE/Shaders)) | bundled presets: `scanlines.cfg` (res-independent-scanlines), `old-tv.cfg` (barrel-distortion plus scanlines), `pixelperfect-sharp` / `pixelperfect-smooth`; glsl folder also has sharp-bilinear, sharp-shimmerless (plus grid/subpixel), lcd1x/lcd3x, retro-v2, scale3x, aa-shader | confirmed |
| MinUI (minarch) ([minarch.c](https://github.com/shauninman/MinUI/blob/main/workspace/all/minarch/minarch.c)) | built-in Screen Effect: **None / Line / Grid**; Sharpness: **Sharp / Crisp / Soft** (Crisp is the sharp-bilinear idea) | confirmed |
| RetroGameCorps "Shaders and Overlays on Retro Handhelds" ([guide](https://retrogamecorps.com/2024/09/01/guide-shaders-and-overlays-on-retro-handhelds/)) | home consoles on low-power handhelds: **sharp-shimmerless** for clean pixels; **zfast_crt_geo_svideo** ("dramatic CRT shader that is lightweight"); **crt-1tap** (light); crt-geom only for integer-scaled setups | confirmed |
| RetroPie / Pi community ([crt-pi thread](https://forums.libretro.com/t/raspberry-pi-friendly-crt-shader/3937)) | crt-pi was the de facto Pi CRT shader, built for 1080p60 on VideoCore; zfast was made faster still | confirmed (thread) |
| muOS, OnionOS, ROCKNIX | no NES/SNES default found in docs (ROCKNIX docs list only handheld LCD shaders: dot, lcd-3x, lcd-grid-v2, zfast-lcd...) | **not confirmed** |
| r/SBCGaming / Reddit | not fetched | **not confirmed** |

Overall: in this space the most used light CRT shaders are **crt-pi** and **zfast-crt**; the most used "no-CRT" default is **sharp-bilinear(-simple)/shimmerless**; plain **scanlines** is the built-in in MinUI and NextUI; and crt-1tap / zfast_crt_geo are rising guide picks.

## 5. Recommendation (ordered; weighted by popularity and Mali-G31 cost)

1. **Sharp (sharp-bilinear / shimmerless).** It is the Batocera/Knulli default and in MinUI and NextUI. It directly fixes the 2.8125x horizontal shimmer of the default Stretch mode, it is public domain, and it costs 1 LINEAR fetch (or 4 NEAREST). It is the most useful one for NES/SNES on this panel.
2. **Scanlines (sine-abs / res-independent, public domain).** MinUI's "Line" and NextUI's `scanlines.cfg`. It is about the cheapest effect possible. Use a smooth sine profile with a brightness boost. Ship it knowing it beats at SNES Stretch 2.14x and looks clean in Actual and on NES.
3. **CRT (crt-pi, GPL-2+).** It is Knulli's own low-GPU choice for its Scanlines set and the best-known light CRT shader. It is single-pass with 1 fetch and a `gl_FragCoord` mask, and MULTISAMPLE softens the SNES Stretch beat. Pick crt-pi **or** zfast-crt, not both, because they overlap. zfast-crt is cheaper (no pow) and GPL-2+ like the zfast_lcd slot already ships. crt-pi edges it on popularity in H700 CFWs and on non-integer handling.
4. **crt-1tap (CC0)**, optional. It is a light, soft CRT beam that RetroGameCorps recommends, with 1 fetch and the cleanest license. It is a good second CRT flavour if the menu gets a 4th new entry.
5. *(Optional, later)* **crt-easymode or crt-hyllian** as a "sharp CRT" if device perf has headroom. Both are medium cost and single-pass.

**Skip and why:**
- crt-geom: transcendental-heavy, and curvature at 2x looks poor.
- xBR-lv2: 21 taps, and it smooths rather than giving a retro look.
- ScaleFX / scalefx-hybrid: 5 passes.
- NTSC (ntsc-adaptive, blargg, ntsc-mini, tiny_ntsc): 2-4 passes, and slot has no FBO chain or FrameCount.
- crt-royale: about 12 passes.
- fakelottes: no license header until confirmed.
- `scanlines/scanline.glsl`: no header; use the public-domain sine-abs instead.
- zfast_crt_geo / _svideo: curvature and glow add cost for a small, 2x picture.

**Gates before shipping each new mode:**
- Run `task perf:play` with the frame-trace patch per new mode, comparing present-interval p99 and missed latches against `Off` on the heaviest SNES title. `PERFORMANCE.md:255` lists shader cost as not measured yet.
- Add a CPU mirror or pixel test like `lcd3x_mask` (`lcd3x.rs:27-35`) and update the cycle-order tests.
- Add the `licenses/shaders.txt` entry.
- Decide LINEAR versus manual bilinear once for all 1-tap shaders: one `pipeline.rs` hunk versus 4x fetches.
