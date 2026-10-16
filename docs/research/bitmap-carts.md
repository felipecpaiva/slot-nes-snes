# Bitmap carts for NES / Famicom / SNES / SFC (slot v1.7.0 style)

Research, 2026-10-15. Tree: ` (branch rebase-v1.7.0, upstream tag `slot-v1.7.0`).
Paths below are relative to that tree. Prototype images: `

## 1. How v1.7.0's bitmap carts work

### Asset files
All in repo-root `assets/`, plain RGBA PNG, **1x only** (no @2x). They are `include_bytes!`'d into the binary
(`crates/slot-ui/src/bitmaps.rs:35-54`, `:228-233`). `load()` (`bitmaps.rs:56-69`) centre-crops or
nearest-neighbour rescales any size mismatch to the declared size, then "bleeds" opaque RGB into
transparent pixels so linear filtering does not pull white in at the edges (`bitmaps.rs:71-95`).

| File | Size | Role |
|---|---|---|
| `gba_neutral.png` | 360x212 | GBA shell, 50% grey, hand painted (bevel, grain, embossed "GAME BOY ADVANCE", label well) |
| `gb_neutral.png` / `gbc_neutral.png` | 312x337 | DMG notched / GBC rounded pak shells, same idea |
| `gba_clear.png`, `gbc_clear.png` | same | **byte-identical copies** of the neutral files (`cmp` confirms). `GB_CLEAR_PNG` points at `gb_neutral.png` (`bitmaps.rs:226-233`) |
| `gba_cart.png`, `gb_cart.png`, `gbc_cart.png` | same | flat white silhouettes (paint/shape template; used for `shade_of` and the silhouette mask, `silhouette.rs:13`) |
| `gba_interior.png`, `gb_interior.png`, `gbc_interior.png` | same | back plastic, seen through clear shells |
| `board.png` 360x212, `gb_board.png` 312x337 | | PCB drawn between back and front of clear carts |
| `slot_front/back_{light,dark}.png`, `link_port_{light,dark}.png` | 720x58 | the slot chrome, **the only themed assets** |
| `background_default(_blur).png`, `bezel_gb(c).png` | 720x480 | wallpaper and per-platform bezels (#77) |
| `socket.png`, `chip.png`, `sticker.png`, `link_*` | various | other chrome |

Measured on `gba_neutral.png`: no saturation at all (R=G=B everywhere). Flat body luma 128.3, std 3.5
(grain, in 2px blocks). Label well 116 (GBA) / 119 flat (GB, GBC). Outer side wall about 105, ramping to
128 over about 8px, with a 130-134 highlight ridge just inside the edge. The well has a dark lip
(about 99-104) on top/left and a light lip (about 133-163) on the bottom. The embossed console name is
54 with a lighter row above it.

### How a face is composed (GB/GBC/GBA)
`cart_face` -> `cart_face_with` (`cart.rs:199-300`):
1. `shell_face` (`cart.rs:555-613`): take `shell_asset(mould, clear)`. Outside the label rect, every
   channel goes through Photoshop **Overlay** with the game's colour (`overlay`, `cart.rs:545-553`).
   50% grey gives the colour unchanged, darker grey darkens it and lighter grey lightens it, so Markus's
   painted highlights, shadows and emboss follow any colour. The label rect keeps the asset's grey and is
   forced opaque.
2. Clear shells use the same pixels at 80% alpha (`CLEAR_ALPHA = 204`, `cart.rs:535-536`). The shelf
   draws interior, then board, then the face (`shelf.rs:478-515`). Glitter adds a hashed 1% white fleck
   (`cart.rs:592-621`).
3. Label: box art (`art::cover`) or a generated flat-colour label with title text (`generated_label`,
   `cart.rs:631-659`). It is pasted **flat** into the rect (`paste_label`, `cart.rs:670-686`), with no
   label-specific shadow or highlight layer. The "inset" look comes from the well lip painted in the PNG.
4. `clip_to_silhouette` with the mask (`cart.rs:302-306`).
Label rects are hard coded to the painted wells: GBA `label_panel` (`cart.rs:23-39`), GB `gb_label_panel`
(`cart.rs:41-53`), GBC exact pixels 45,110 223x199 (`cart.rs:55-61`). Tests assert these against the
art (`tests/cart.rs`, `tests/shell.rs`).

`neutral_shell()` (`cart.rs:408-462`) is a code-generated neutral (grey + `shade_of` + rim + sheen + stamped
console name). It is **not used at runtime**: only `examples/raster_templates.rs` (`:3`, `:118`) calls it, to make
templates for the artist, and `tests/shell.rs:432,457` cover it.

### Theme (light vs dark)
Cart faces are **theme-invariant**. No face is rebuilt on a theme toggle. `frontend.rs:277-283` uploads
both slot sets, and `apply_look` (`frontend.rs:315-330`) only swaps slot front/back, the port, the bolt
icon and the footer ink by `app.light()` (`app.rs:1654`). So "in both themes" means one cart asset that
reads well on both chromes, not two cart assets.

### Favorites star
A Nerd-font glyph texture built once (`icon.rs:157 star_face`, `frontend.rs:248-250`). It is drawn by the shelf at
the top-right corner of the label rect, inset by `STAR_INSET` (`shelf.rs:544-553`). The label rect
comes from `label_rect`/`retro_label_rect`, so it is not baked into any bitmap. NES/SNES already work (`tests/nes_clear.rs:40`).

### Lid / insert animation
Not bitmap specific. The same face texture is moved: `slide_of`/`lift_of`/`lid_from` (`board.rs:143-237`),
with `INSERT_S`/`SEATED_AT` timing (`app.rs:33-38`) and the core lid face (`app.rs:3175`, `:3354`). For
clear GBA carts the board and interior travel under the face (`board_in`, `board.rs:213-215`). Shadows
are the mask in black (`cart_shadow` / `retro_cart_shadow`, `cart.rs:178-197`).

### cart_shell.txt now
`shell_for` (`shell.rs:81-96`): a `cart_shell.txt` choice (colour + Solid/Clear/Glitter + outline) wins.
Otherwise the GBA code table, the GB header table, or `retro_shell::plastic_for` for NES/SNES. For GB/GBA
the colour is applied by Overlay onto the painted neutral, and clear/glitter as above. For NES/SNES the
same `Shell` feeds our code path instead (`retro_face.rs:103-127`, flat fill + `through()` tint for
clear). `is_clear()` is false for every retro cart (`cart.rs:208-210`), so NES/SNES never get the
board/interior stack, and `tests/nes_clear.rs:24-38` asserts their faces stay mostly opaque.

### Our NES/SNES path today (for contrast)
`retro_face` (`retro_face.rs:71-90`): flat shell colour, then shadow/highlight masks rasterised from
`*_cart_detail.svg` plus embossed `lettering_*.png` (`retro_mould.rs:47-110`, `retro_cart.rs:215-226`),
then a 2-3px hard bevel around the label (`recess_label`, `retro_face.rs:205-254`), then the label. No grain, no
outer bevel, no Overlay. That is why the faces look flat next to Markus's carts.

## 2. How the assets were made, and licence

- The repo has **no layered sources** (.psd, .kra, .xcf, .afdesign, .fig). Only the final PNGs. The SVGs in
  `crates/slot-ui/assets/` are the old vector outlines, still used for masks and templates.
- Workflow, from the code: Brandon's `examples/raster_templates.rs` rasterises the SVG outlines into
  size templates (`templates/`, not loaded) -> art is made to those sizes -> PNGs land in `assets/`.
- `tools/fit_bitmaps.py` (added in #74, 452 lines, PIL + svgpathtools) "Fit[s] generated stand-in art to
  the pixel sizes Slot draws". It reads `*_src.jpg` plates from Markus's local Windows path
  (`C:\Users\marku\.cursor\projects\...`, not in the repo), keys out a "hot pink" generated backdrop
  (`key_magenta`), and masks the result with the SVG outline. It writes `gba_cart.png`, interiors,
  `board.png`, socket, chip, plugs, port, slot and sticker. It **never writes `*_neutral.png`**. The shells
  are described as "hand drawn" in `bitmaps.rs:226`, and the #74 commit is "Draw the shelf and host link
  plug from handmade art."
- PR #74 (MarkusMaribu, "Skeuomorphic UI redesign, themes, wallpapers, and launch fixes") has no art
  notes. Brandon landed it as single commit bd2fb8a, with Markus as author. Credit is in README.md:69 and
  CHANGELOG.md:5,10. Markus's GitHub profile is empty (no site or contact).
- Licence: the only explicit art licence is `licenses/bezel-CC-BY-SA-4.0.txt` (the 640x480 SP bezel by
  mugwomp93). Everything else, Markus's PNGs included, ships under the repo's **GPL-3.0** by default, with
  no separate grant. A derivative that reuses his grain or profile in our GPL fork is fine on that
  basis. Still worth asking Markus to confirm the licence and whether he has layered sources.

## 3. Options

The runtime contract is small, and that is the key finding. A cart is (1) a **50%-grey neutral PNG** with the
lighting painted in, (2) **Overlay** with the shell colour everywhere except (3) a fixed **label
rect** that stays grey and opaque, then (4) the silhouette mask. Any source that produces a neutral PNG of
the right size plugs straight in. Our masks, label rects, detail SVGs, lettering and `cart_shell.txt`
colours all stay the same. Retro sizes today: NES/Famicom 312x328, SNES/SFC 360x225 (`retro_cart.rs:104-165`).

### a. Generate the neutrals from our shapes using Markus's measured lighting
Prototype: ` (about 170 lines of PIL/numpy, the same toolset as
upstream's `tools/fit_bitmaps.py`). It measures `gba_neutral.png` directly:
- body 128.3, grain std 3.5 in 2px blocks
- outer bevel by distance from edge: 115, 108, 105x5, 110, 121, 130, 131, then 128
- well 116, with a dark lip of 98-114 on the left, 84-92 on top and a light lip of 150-162 on the bottom
- grooves at about 70 with a lit lower edge at about 145, like his emboss

It applies these to our SNES/SFC mask and `*_cart_detail.svg`, which come out of slot-ui unchanged
through a scratch exporter. The output is `snes_neutral.png`/`sfc_neutral.png`, and the runtime Overlay
is re-implemented in Python to preview them.
- Effort: **S-M**. About 1 day for all four shells, including NES/Famicom lettering emboss and lip tuning.
- Fidelity: medium. It reads as the same family (grain, soft outer bevel, recessed well, matching
  grey response under Overlay), and it is clearly better than today's flat fill. It lacks Markus's painterly
  extras: the curved shoulder scoop and the hand-placed highlights on corners.
- Licence: our code plus parameters measured from GPL-3.0 art, so GPL-3.0. No new terms.
- Upstream: generated NES/SNES art has no upstream path. The owner declined more systems (workspace
  CLAUDE.md projects table). It stays in our own files per ADR 0042.

### b. Hand-made art (Markus or community)
- Who: Markus (@MarkusMaribu). He volunteered #74/#77 unprompted, but his GitHub profile has no contact,
  so the only channel is a comment or discussion on BrandonKowalski/slot. That is an external post, so it is
  the maintainer's call. A community artist is possible, but there is no known candidate.
- Effort for us: **S** of work, plus an unknown wait. We would hand over size templates (our masks at
  312x328 and 360x225, with the label rects marked), which is exactly how `raster_templates.rs` fed #74.
- Fidelity: highest, a true match.
- Licence: must be stated explicitly (ask for GPL-3.0 or CC-BY-SA-4.0, and for layered sources).
- Upstream: same as (a). The shells are NES/SNES-specific and upstream does not want those systems.

### c. Hybrid (recommended)
Ship (a) now. Then offer the generated neutrals to Markus as paint-over bases, since the art contract
stays the same. If he paints them, his PNGs replace ours with no code change.

### Upstream potential of a generic hook
A data-driven "platform supplies its own cart bitmaps" table would carry platform -> (w, h, label rect,
mask, neutral png, clear png, interior). It would replace the `Mould` enum (`bitmaps.rs:7-12`, `:237-253`)
and the five `retro_shell_of` early returns in `cart.rs` (200, 221, 279, 288, plus `is_clear` 209).
Evidence on how Brandon responds:
- He declined more systems on slot#30 (docs/projects.md:62).
- He welcomed the fork ("Go nuts", "Fork away", discussion 64).
- He took our generic perf fix #75, but re-implemented it himself and landed it as 3339c6f with us as
  co-author, closing the PR on 2026-10-14.

So a small, generic, platform-neutral refactor is worth proposing as a discussion. Expect him to rewrite it.
But upstream has no second consumer, so it may read as speculative. Do not block on it. ADR 0042 already
records "Bitmap NES and SNES moulds would need art from the maintainer (open question)". This work closes
that question, and needs a new ADR that amends 0042.

## 4. Prototype (option a, SNES, light theme)
- ` left to right: current code-drawn SNES | option (a)
  SNES (`SNES_GREY` through Overlay) | v1.7.0 GBA (Markus's `gba_neutral` + Overlay) | option (a) in purple.
  It is all at native scale (both widths 360) over the light slot front. `compare_dark.png` shows the same on the dark chrome.
- `zoom_light.png` is a 2x crop of the prototype next to the GBA cart.
- `snes_neutral.png`, `sfc_neutral.png` are the generated assets (360x225 RGBA, same contract as `gba_neutral.png`).
- `cur_*.png` are the current faces from slot-ui. `mask_*`/`detail_*` are the exporter output
  (`export/`, built against the tree with `CARGO_TARGET_DIR` in scratch, so the tree is untouched).
- Caveats: the backdrop is my blend of `background_default.png`, not a device capture. The label text is PIL,
  not slot's `fit_box`. The SNES has no front lettering (`lettering_snes.png` is empty), so emboss was not
  exercised. NES/Famicom were not prototyped.

## 5. Recommendation and steps
Go hybrid. Generate the four neutrals now, wire them through Overlay, and offer them to Markus as paint-over bases.

1. **M**: `tools/gen_retro_neutrals.py` in our fork (precedent: `tools/fit_bitmaps.py`). Port the
   prototype, add NES/Famicom (portrait well, lettering emboss), and write `{nes,famicom,snes,sfc}_neutral.png`
   into `crates/slot-ui/assets/` (our files, ADR 0042). Commit the PNGs. Slot loads PNGs, not the script.
2. **S**: `retro_face.rs::shell_face`, one path for every finish. Compute today's per-pixel colour
   (`retro_face.rs:103-127`: flat for Solid, `through()` with the rim lerp and fleck for Translucent/Glitter),
   then feed it as the colour into `overlay(neutral_px, colour)`. Keep the label rect grey and **alpha at 255**.
   Retro carts get no board or interior behind them (`is_clear` is false, `cart.rs:208-210`), so the
   upstream "80% alpha" trick would show the wallpaper through them and break `tests/nes_clear.rs:24-38`.
   Drop `mould_detail` and `recess_label`, since the art carries them. Copy the 8-line `overlay` into our file
   instead of widening `cart.rs`. That keeps upstream hunks minimal, and upstream tests are frozen by
   `scripts/check-upstream-tests.sh` (CONTRIBUTING.md:16).
3. **S**: Tests. A neutral overlaid with 50% grey equals the asset. The label rect sits inside the painted
   well. `nes_clear.rs` opacity still holds. The star position is unchanged.
4. **S**: Device check on both themes (cart faces are theme-invariant, so one asset per shell) and on the
   lid/insert animation (same texture, no change expected).
5. **S**: The maintainer's decision: ask Markus on the slot repo to confirm the art licence, and offer the
   neutrals plus templates for an optional repaint.
6. **M, optional**: open an upstream discussion proposing a generic per-platform mould table (expect Brandon to rewrite it, as with #75). Only worth it if Brandon wants
   other community platforms.
