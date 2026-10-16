# PS1 on slot-nes-snes: evaluation (2026-10-15)

Read-only research. "Our tree" means ` (slot v1.7.0 plus patches 0001-0020).
"pcsx" means libretro/pcsx_rearmed at HEAD `c881679` (2026-10-02), cloned shallow.
Nothing below was measured on the device. Neither fork publishes H700 numbers either.

## TL;DR

- **Verdict: go-with-limits, after a device spike, and after Game Gear, Master System and Mega Drive.**
- The emulation side is easy. pcsx_rearmed is the H700 standard: ARM64 dynarec (ari64), NEON GPU, HLE BIOS fallback, licence GPL-2.0-or-later.
- The work is in four slot seams that NES and SNES never needed:
  - load games by path (`need_fullpath`);
  - libretro disk control for multi-disc games;
  - a larger, variable source frame;
  - handing L2 and R2 to the game.
- **Analog is not needed for v1.** pcsx defaults to the standard digital pad. Neither fork reads the sticks.
- Expected size: about 9 to 11 patches. That is about half the NES plus SNES effort, smaller than N64, and larger than GG, SMS or MD.

## 1. What the forks did (reference only)

### gmaster1998/slot.ps1

- Repo: https://github.com/gmaster1998/slot.ps1, HEAD `b662665`, 16 "Add files via upload" commits on 10-12 to 10-14.
- Base: upstream `94a35a0`, which is after the GPL-3 switch. LICENSE is GPL-3.0.
- Closed upstream as PR #76: https://github.com/BrandonKowalski/slot/pull/76
- What it adds:
  - **Core:** PCSX ReARMed, built by CI from **unpinned HEAD** (`git clone --depth 1`). It writes a `.commit` file, but the COPYING copy is `|| true`, so it can silently go missing. There is no source tarball.
    - It also builds Snes9x and a PPSSPP stub the same way.
    - `Platform::{Ps1,Snes,Psp}` and `Core::{Pcsx,Snes9x,Ppsspp}` are added straight into upstream's enums: `Platform::ALL` becomes 6, and upstream tests are edited.
  - **Discs:**
    - Extensions `cue chd m3u pbp iso`.
    - `is_disc_image()` passes the path instead of the bytes. It keys on file extension and does not read `need_fullpath`.
    - Multi-disc games go in subfolders with an `.m3u`. **There is no disk-control interface, so a game cannot swap discs.**
  - **BIOS:** user-supplied in `BIOS/` (for example `scph5501.bin`), with an HLE fallback. Nothing is shipped.
  - **Memory card:** relies on SAVE_RAM by default. It sets no memcard option explicitly.
  - **Video:**
    - A global `HIRES` mutex frame at native size, up to 1024x1024 BGRA.
    - A new `VideoPass` GL program with five filters (Crisp, Sharp, Smooth, Scanlines, CRT).
    - A 240x160 box-filtered copy that is kept for thumbnails, refreshed every 6th frame.
    - SELECT+Y toggles fill or 4:3 (`ps1_fill`).
  - **Input:**
    - `ButtonMask::L2/R2` (bits 12 and 13).
    - `Gestures::set_triggers_to_game` takes L2 and R2 away from rewind and fast-forward.
    - **No analog.** `input_state` still answers only JOYPAD.
  - **Turned off for PS1:** rewind, FF, shaders and link. No run-ahead.
  - **Shelf:** a procedural disc (`disc_face`, 312x312): silver hub, cover art printed on the disc. No case.
- Performance: no numbers.

### bently0602/slot

- Repo: https://github.com/bently0602/slot, HEAD `db39c5d`. Base is upstream `511f0e0`. LICENSE is GPL-3.0.
- PS1 arrived in "add features" `ac6d819` and was refined in `d355744` and `db39c5d`.
- Of the two forks, it is the better reference for every system-agnostic seam:
  - **Core build:** `cores/pcsx/build.sh` follows slot's own mgba/gpsp pattern:
    - pinned commit `c8816799` (today's pcsx HEAD), with `.meta` stamp;
    - recipe `make -f Makefile.libretro platform=unix DYNAREC=ari64 HAVE_CHD=1`;
    - a source tarball that includes the libpicofe submodule;
    - `licenses/pcsx_rearmed.txt`, plus the GPL-2.0 text.
  - **Loading:** reads `system.need_fullpath`, which is the right seam. Extensions `chd cue pbp iso exe m3u`.
  - **Disk control:** handles `SET_DISK_CONTROL_INTERFACE` and adds `discs()` and `change_disc()`.
  - **Core options:**
    - `pcsx_rearmed_bios=auto` (the HLE fallback);
    - `memcard1=libretro`, a 128 KB SAVE_RAM;
    - `memcard2=none`;
    - `frameskip_type=disabled`;
    - multitap.
  - **Video:** a fixed **640x480** canvas (`set_video_canvas(640,480)`, `Platform::Psx => (640,480)`).
  - **Input:** up to 4 pads and external controllers. **No analog** (no ABS_X/ABS_RX or ANALOG anywhere).
  - **Tests (worth copying):** `crates/slot-retro/tests/pcsx.rs` builds a homebrew PS-X EXE and a synthetic ISO9660 two-disc set entirely in code. It then asserts:
    - a 640x480 frame;
    - a 128 KB memory card that persists;
    - disc 1/2 swap, and resume on the second disc;
    - run-ahead instance isolation.
    - All of it runs with HLE BIOS, so **no copyrighted BIOS is needed in CI**.
  - **Shelf:** a jewel case (tray, lid, disc textures in `slot-ui/src/psx.rs`) with an open-and-insert animation.

### Licence check

- Both forks are GPL-3.0 and our patch set is GPL-3.0-or-later, so code is compatible.
- Credit: the author in the commit trailer, plus LICENSING.md, the same way the ezGBA borrowings are handled.
- pcsx_rearmed:
  - COPYING is the GPL-2 text;
  - source headers say "version 2 ... or (at your option) any later version";
  - bundled deps (lightrec, lightning, libchdr, libpicofe) keep their own licences and go into the source tarball.
- **pcsx combines with GPL-3 directly.** It does not even need the snes9x "separate program across the C ABI" stance, which makes it cleaner than our SNES cores.

## 2. Gaps against our standards

| Standard | gmaster1998 | bently0602 | What PS1 needs from us |
|---|---|---|---|
| Exhaustive platform policy (Step 0 matches, `Platform::SHELVES`, `Core::EVERY`; upstream `ALL` untouched) | Edits `ALL` and upstream tests | Edits enums in place | `Platform::Ps1` and `Core::PcsxRearmed` appended. Every policy method answers explicitly: `owns_shoulders`, `turbo_mode`, `shader_choices`, `picker_cores`, `canvas`, plus new `owns_triggers`, `rewind`, `disc_control` |
| Own shelf (`Games/PS1`, `Labels/PS1`, `Saves/PS1`, `States/PS1`) | Yes | Yes (PSX) | Yes. Use `PS1`, the folder name every H700 firmware uses |
| Core from a pinned commit, plus licence record (ADR 0002, SUPPLY-CHAIN.md) | No (unpinned) | Yes | `cores/pcsx/build.sh` with a sha in `SLOT_PIN`, `platform=unix DYNAREC=ari64 HAVE_CHD=1`. **Fits ADR 0002's build rule with no exception**, unlike N64 |
| Per-platform core pair (ADR 0002, picker is a strict pair) | Not in picker | Not in picker | One core only. **Gate the picker for one-core platforms**, the same seam N64 needs. Name a second core (swanstation, beetle-psx) only if the spike shows it runs at speed. Their licences were not checked here |
| Canvas (ADR 0004 fixed, issue 36 Option B deferred) | Variable, via a global mutex and its own GL pass | Fixed 640x480 | See section 3 |
| Cart art with variants (ADR 0006, 0014, 0042) | Disc only | Jewel case | See section 4 |
| Named test sites (ADR 0013, 0044), upstream tests unmodified | Edits upstream tests | Edits upstream tests | New tests in our own files only. Port bently's homebrew EXE and synthetic ISO approach |
| Touch-point map (ADR 0024) | n/a | n/a | New rows for `libretro.rs` (fullpath, disk control), `gesture.rs` (L2/R2), `root.rs` (BIOS dir check), `input/mask.rs` |
| Device gate titles | none | none | See section 6 |
| Frontend cost ≤ GBA budget (Success #3) | n/a | n/a | **Fails as written at a 640x480 canvas.** PS1 needs its own budget line, the same as N64 |

## 3. Core, BIOS, video, audio, states

### Core: pcsx_rearmed

- It is the default PS1 core on muOS, Knulli and ROCKNIX for the H700.
- Device recipe: aarch64 selects `DYNAREC=ari64` and `BUILTIN_GPU=neon` (Makefile.libretro:140-151).
- Host recipe (bently): macOS `platform=osx DYNAREC=0`, i.e. the interpreter. That is fine for tests.

### BIOS

- Option `pcsx_rearmed_bios`, default `auto`: it uses a real BIOS from the system dir if one is present, otherwise HLE.
- Names it looks for (libretro.c:3865): `scph5500/5501/5502`, `scph1001`, `scph7001`, `scph101`, `psxonpsp660`.
- slot already points `GET_SYSTEM_DIRECTORY` at `BIOS/`.
- Rule: user-supplied, never shipped, never in CI. Tests force `HLE`.
- `root.rs`'s BIOS check is GBA-only (`gba_bios.bin`, 16 KB). It needs no change, but do not reuse it for PS1.

### Memory cards

- Force `pcsx_rearmed_memcard1=libretro`. That exposes the card as 128 KB SAVE_RAM (libretro.c:2230-2245), so slot's existing save path writes `Saves/PS1/<stem>.srm` unchanged.
- Set `memcard2=none`.
- An `.m3u` stem gives multi-disc games one shared card.

### Disc formats

- List `.chd` (the recommended format; `HAVE_CHD=1`), `.cue`, `.pbp` and `.m3u` on the shelf.
- Hide `.bin`. Also hide any disc an `.m3u` names, so the scan must read `.m3u` files.
- pcsx sets `need_fullpath = true` (libretro.c:1228). Our tree reads the whole file (`libretro.rs:588 fs::read`), so that must be fixed.

### Multi-disc

- pcsx registers `SET_DISK_CONTROL_EXT_INTERFACE`, then the legacy `SET_DISK_CONTROL_INTERFACE` (libretro.c:3989-3991). We answer at least the legacy one.
- Swapping needs a "Disc n/m" row on the PS1 in-game menu (ADR 0043 per-platform menus).

### Video

- pcsx outputs RGB565 at varying widths (256, 320, 368, 384, 512, 640) and heights (240, or 480 interlaced). The size changes mid-game, for example between menus and gameplay.
- Force the NEON enhancement off. Otherwise frames double to 1024x512.
- Two canvas options:
  - **A. Fixed 360x240 with the SNES 2:1 blend: rejected.**
    - 368 and 384 wide do not fit 360 and are not 2x.
    - PS1 pixels are not square: every width must be stretched to a 4:3 picture.
  - **B. Fixed 640x480 for pcsx (lean, same as bently).**
    - The 4:3 picture at full height on a 720x480 panel is exactly 640x480, so the canvas maps 1:1 to panel pixels.
    - Resample each frame horizontally to 640: 320 becomes an exact 2x and 640 an exact 1x; 256, 368 and 512 are non-integer.
    - Double the rows of 240-line frames.
    - This stays inside ADR 0004's "fixed canvas per core" model (`Core::canvas()` returns (640,480)). ADR 0016 and 0019 already re-allocate the texture when the canvas changes. **Issue 36 Option B is not needed.**
    - Costs:
      - about 1.2 MB a frame to convert and upload, against about 150 KB for GBA and about 345 KB for NES and SNES;
      - thumbnails and polaroids are 4:3, not 3:2, which breaks ADR 0004's consequence, so a new ADR is needed;
      - our retro shaders assume low-res input, so v1 offers PS1 Sharp and Stretch/4:3 only.
  - A fallback if B's cost fails the spike: a fixed 320x240 canvas with the same resample (exact for 320, blends 640 and 480i). It is cheaper and lower detail.

### Audio, pacing, states

- **Audio:** 44100 Hz. slot resamples from the core rate. PAL discs run at 50 Hz, the same pacing caveat as issue 34.
- **States:** `retro_serialize_size()` = 0x440000, about 4.4 MB.
  - Manual states and lid-close save work. Check the lid-close write time for 4.4 MB on SD.
  - **Rewind off.** The ring is 20 MB (`rewind.rs:3`), which holds about 4 uncompressed states, and a 4.4 MB serialize every frame is too costly on the A53.
  - **Run-ahead off.** v1.7.0 gates it to mGBA already (`session.rs:401`).
  - FF: offered, but not promised in the parity table.

## 4. Shelf look (PS1 is discs, not carts)

- Proposal: **a jewel case on the shelf, with the disc inside shown on insert.** That follows bently's open-and-insert idea, drawn in our own procedural renderer the way ADR 0042 does it. The cover art is the label.
- ADR 0014 bans screenshots, not covers. PS1 has no cart label, so the front cover is the equivalent. That needs a one-line amendment.
- Region variants, the equivalent of NES/Famicom and SNES/SFC:
  - **NTSC-U:** standard black-tray jewel case. Variants: the 1995 launch long box and Greatest Hits (green-banded spine).
  - **PAL:** jewel case with the PAL spine and back layout. Variant: Platinum (silver band).
  - **NTSC-J:** jewel case with the spine card (obi). Variant: "PlayStation the Best".
  - **Multi-disc:** a double (fat) jewel case, read from `.m3u` disc counts.
  - **Disc face:** PS1 discs have a black data side, and the label print varies. Draw it on insert only.
- Region auto-pick for `auto`:
  - the serial in `SYSTEM.CNF`: SLUS/SCUS is NTSC-U, SLES/SCES is PAL, SLPS/SCPS/SLPM is NTSC-J;
  - or, cheaper, the filename tags `(USA)`, `(Europe)` or `(Japan)`, as we do for carts.
- Colour tables need cited sources (`eval-colour-sources.sh`); renders are judged blind against reference photos.
- Effort: this is the biggest UI item (L), and it can ship after a flat-case placeholder, as Phase 1 to 3 did for NES and SNES.

## 5. Input

- **v1, digital:**
  - pcsx treats `RETRO_DEVICE_JOYPAD` as `PSE_PAD_TYPE_STANDARD` (libretro.c:1176-1190), and slot already sets port 0 to JOYPAD. Most of the library plays.
  - `ButtonMask` bits 12 to 15 equal the libretro ids L2, R2, L3, R3, so they fit the u16 exactly.
  - L2 and R2 are upstream's rewind and FF gestures. With rewind off for PS1, a policy `owns_triggers` hands them to the game; gm's `set_triggers_to_game` in `gesture.rs` is the reference.
  - Face buttons: the PS layout (Cross, Circle, Square, Triangle) maps to B, A, Y, X positions. `TurboMode::PassThrough` keeps X and Y.
- **v2, DualShock analog:** needed for analog-only games (Ape Escape) and for analog steering or camera control.
  - Read `ABS_X`, `ABS_Y`, `ABS_RX` and `ABS_RY` in `input/evdev.rs` and `device.rs`. Today only HAT0 is read.
  - Add deadzone and calibration.
  - Add a separate axes atomic next to the `AtomicU16`, so GBA input timing stays unchanged.
  - Answer `RETRO_DEVICE_ANALOG` in `input_state`.
  - Call `set_controller_port_device(0, RETRO_DEVICE_PSE_DUALSHOCK)`, which is `SUBCLASS(ANALOG,1)`, behind a per-game or per-shelf toggle.
  - L3 and R3.
  - Unknown, and shared with the N64 spike: whether BaseOS exposes the sticks as evdev axes, and whether they snap to cardinals.
- Rumble: slot already has `GET_RUMBLE_INTERFACE`. Whether the device has a motor is unknown.

## 6. Patch list (S/M/L, upstream touch)

| # | Patch | Size | Upstream touch | Upstream candidate? |
|---|---|---|---|---|
| 0 | Spike (below) | S | none | - |
| 1 | `0021-core-pcsx`: build.sh, SLOT_PIN, SUPPLY-CHAIN, licence and source tarball | M | none (build) | no |
| 2 | `0022-platform-ps1`: enum append, SHELVES, folders, scan (`.m3u` hides named discs, `.bin` hidden), every policy method, picker gate for one-core platforms | M | `slot-store` platform/core/scan, `core_picker.rs` | the picker gate maybe |
| 3 | `0023-fullpath-load`: honour `need_fullpath` | S | `libretro.rs` load | **yes**: a correctness fix for any core |
| 4 | `0024-ps1-canvas`: `Core::canvas()=(640,480)`, horizontal resample, row doubling, 4:3 thumbnails | M | `canvas.rs` (ours), `video_mode`/fit at the 1x scale | the variable-frame part of Option B; low odds |
| 5 | `0025-disk-control`: env 13 and 58, `discs()`, `change_disc()`, a menu row | M | `libretro.rs` env, `ffi.rs`, PS1 menu | generic, but GBA never uses it: low odds |
| 6 | `0026-ps1-input`: L2/R2 to the game, PS face mapping | S | `gesture.rs`, `input/mask.rs` | no |
| 7 | `0027-ps1-options-states`: BIOS auto, memcard, enhancement off, rewind off, FF not promised | S | `core_options_policy.rs`, rewind gate | no |
| 8 | `0028-ps1-cases`: jewel case art and region variants (placeholder first) | L | `slot-ui` cart.rs hunks, own `retro_*` files | no |
| 9 | `0029-ps1-tests`: homebrew EXE, synthetic ISO two-disc, card persist, harness leg "PS1, eject, GBA" equal to GBA-only | M | own test files (ADR 0020) | no |
| 10 | `0030-analog` (v2) | M-L | `evdev.rs`, `device.rs`, `emu.rs`, `libretro.rs` | generic; low odds, since upstream has no stick system |

- Total: about 10 patches for v1 (items 1 to 9), plus analog later.
- Write-ups needed:
  - **New ADRs:** PS1 in scope (amends the PLAN non-goal "more systems"); 640x480 PS1 canvas and its own frontend budget (amends 0004); one-core picker gate; PS1 case art (amends 0006 and 0014); no rewind for PS1.
- Upstream reality:
  - The owner said no more systems (slot#30), and PR #76 was closed.
  - No written "upstream-first" ADR was found in `docs/adr`.
  - Only `need_fullpath` (item 3) is a strong upstream PR candidate. Disk control, analog and variable canvas are generic, but GBA never exercises them.

## 7. Smallest device spike (1 day, nothing in the patch set)

1. Build pcsx at `c881679` in the bullseye aarch64 container with bently's recipe.
2. Use a throwaway branch of `work/slot`:
   - `Platform::Ps1` (hacky);
   - the fullpath load;
   - a 640x480 canvas;
   - BIOS `auto`.
3. On the RG34XXSP, run two digital titles the owner has dumped, 10 minutes each under `SLOT_TRACE`:
   - one 2D (for example Symphony of the Night);
   - one 3D (for example Crash Bandicoot or Gran Turismo).
   - Log every frame size `video_refresh` sees, so the resolution changes are measured, not assumed.
4. Record:
   - ms/frame for `retro_run`;
   - the frontend convert and upload ms at 640x480 and at 320x240;
   - audio underruns;
   - lid-close save time for 4.4 MB.
5. Same session: dump evdev while moving both sticks. This answers the N64 spike's question too.
6. **Go if:** both titles are full speed with zero underruns and the frontend cost is under about 3 ms a frame. Otherwise drop to the 320x240 canvas, or park.

## 8. Recommendation and order

- **Go-with-limits.** v1 scope:
  - pcsx_rearmed only, with the picker gated;
  - digital pad;
  - `.chd`, `.cue`, `.pbp` and `.m3u` with disc swap;
  - per-game 128 KB card;
  - manual states and autosave;
  - no rewind, no run-ahead, FF not promised;
  - Sharp and 4:3/Stretch only;
  - jewel case placeholder, then region variants;
  - gated titles chosen after the spike (2D plus 3D, NTSC-U, PAL and NTSC-J);
  - analog deferred to v2.
- **Order: after Game Gear, Master System and Mega Drive.** Those are carts with a joypad, their frames fit the existing 360x240 canvas model, their states are small, rewind works, and they reuse the cart renderer. They need none of the four new seams.
- Run the PS1 spike together with the N64 stick dump, so both share one device session.
