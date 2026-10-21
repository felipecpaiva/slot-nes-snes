# 0102. Bring PICO-8 carts into scope on pinned FAKE-08, a shelf of their own, no states

- Status: Accepted. Amends [0002](0002-cores.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-21
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0072](0072-write-sav-when-the-core-gives-no-state.md) (a core with no state), [ADR 0094](0094-ngp-flash-staged-checked-published.md) (a core that writes its own saves), [ADR 0097](0097-virtual-boy-on-beetle-vb.md), [ADR 0100](0100-shelf-order-option.md), [issue 203](../../.github/issues/203-pico8-tracking.md), patches `0127-pico8-core-tests` to `0130-pico8-tests`, [docs/research/next-systems-2026-10-20.md](../research/next-systems-2026-10-20.md) ("PICO-8: 39 carts ... The fake-08 core exists; licence unverified")

## Context

The maintainer asked for PICO-8 as a full platform. He owns 39 carts (`Roms/PICO` on B3Tb, the same 39
files byte for byte as `ES-DE/Roms/pico8`, checked by CRC32). Every one is a PNG cart (the 160x205
`.p8.png` export) saved under a `.p8` name; none is a text `.p8`. `docs/rom-library/best-copy/pico8-adds.tsv`
in the workspace lists them, one per cart, named by the cart's own title.

PICO-8 is Lexaloffle's fantasy console: a 128x128 screen in 16 colours (plus 16 secret ones), Lua carts,
a d-pad, two buttons (O and X) and a pause button, 4-channel synth sound, 256 bytes of persistent
"cartdata" per cart. PICO-8 itself is proprietary and is never shipped or fetched.

## Core choice

| Core | Licence | Libretro | State at 2026-10-21 | Verdict |
|---|---|---|---|---|
| **FAKE-08** (jtothebell/fake-08) | MIT (LICENSE.MD), with z8lua (Lua 5.2 MIT, eris MIT, the PICO-8 parts WTFPL 2), lodepng (zlib-like), miniz (MIT), simpleini (MIT), and one CC BY-SA 3.0 snippet (the oval in `source/graphics.cpp`, attributed in LICENSE.MD) | `platform/libretro`, the libretro buildbot's `fake08` | master 814991a, 2026-06-13, active since 2020 | **chosen** |
| retro8 (Jakz/retro8) | GPL-3.0 | yes | 2026-09-12 after a 2022 gap; its `status.md` lists `fillp` missing, `cartdata` "just noop", `btnp` "not working as intended" | rejected: no cartdata, gaps that real carts hit |
| zepto8 (samhocevar/zepto8) | WTFPL 2 | a `libretro.cpp` | not on the libretro buildbot | rejected: no libretro build of record to pin against; FAKE-08 already carries its z8lua |

FAKE-08 is free software with no non-commercial clause and no donation clause, so nothing in it touches
the release terms (LICENSING.md). The CC BY-SA 3.0 snippet is a separate work inside a separately loaded
plugin; the zip stays an aggregate (the snes9x stance in LICENSING.md), and the source ships beside the core.

### Pin and build

- **Pin.** jtothebell/fake-08 `814991a2571ad3970e386cef48f3b148aa1c27b9` (master on 2026-06-13, "Fix vibrato
  effect"), archive sha256 `c3ac9b0b...852c`; its submodule jtothebell/z8lua `e6928578d46b61fd5ea30cfcf547e855a30a0553`,
  archive sha256 `e9fadd5b...b3a4` (the GitHub archive leaves submodules out). `SLOT_PIN` keys `fake08_*`.
- **Build.** `cores/fake08/build.sh`, `make -C platform/libretro platform=unix` and `-mcpu=cortex-a53` on the
  device, `platform=osx` on the host. `cores/lib.sh` gains two optional variables: `owner` (the GitHub owner,
  `libretro` by default; FAKE-08 is not under libretro) and `source_patch` (a patch applied with `patch -p1`
  to the unpacked source before both builds; its path and sha256 go into the stamp and `fake08-src.meta`).
  FAKE-08 is C++: the device build links the C++ runtime statically with `--as-needed`, and
  `cores/fake08/glibc-2.17.h` binds `powf`, `exp2f` (GLIBC_2.27) and `pow` (GLIBC_2.29) to their
  GLIBC_2.17 versions. `task core:device:fake08` checks NEEDED is `libc.so.6` and `libm.so.6` only.

### What `cores/fake08/slot.patch` changes, and why

Each change has a core test that is red on the unpatched core (`pico8_core.rs`, run against a build of the
pinned source without the patch on 2026-10-21: all 11 failed).

1. **stderr.** Four file writers (`saveCartData`, `saveSettingsIni`, `getFileContents`, `writeBufferToFile`)
   used `freopen(path, mode, stderr)` and then `fclose`, which closes fd 2 for the whole slot process; the
   next file slot opened then became fd 2 and took every later log line. They use `fopen`.
2. **Cartdata reaches the card while the game runs.** FAKE-08 wrote cartdata only when the cart closed or
   switched. `Vm::FlushCartData` writes it when it changed, at most once a second (every 60th frame), and
   `saveCartData` writes a temp file, `fsync`s it and renames it over the old one.
3. **Pixel format.** FAKE-08 asks for RGB565 only inside `retro_get_system_av_info`, which slot's frontend
   calls with no environment handler bound, so the request was refused and the picture read as XRGB8888.
   `retro_load_game` asks too. (A frontend fix is the general one; see Consequences.)
4. **Every press reaches a 30 fps cart.** A cart with `_update` reads the pad on every other frame, and the
   press edge from the frame between was dropped, so about half of all short presses came back only as
   `btnp`'s 15-frame repeat. The press is kept until the cart reads the pad.
5. **No way out to FAKE-08's cart browser.** The pause menu loses "exit to menu" and "exit to settings";
   "reset cart" resets a cart loaded from memory from its own bytes (by name it loaded the browser); a Lua
   runtime error stops on "runtime error" and the message, as PICO-8 does, instead of loading the browser.
   From the browser a player could start another cart under the current game's stem and saves.
6. **No states.** See below.

## Decision

- PICO-8 is in scope as Phase 19. One shelf `Games/PICO8`. The platform is `Platform::Pico8`, appended to
  `SHELVES`; the core is `Core::Fake08`, appended to `EVERY`. Upstream's `ALL` stays untouched and every
  policy method answers PICO-8 explicitly. One core, no picker, no BIOS.
- **Shelf.** `.p8` (a text cart, or a PNG cart under that name, which FAKE-08 tells apart by content) and
  `<name>.p8.png`. A bare `.png` is refused by `pico8::admits` with a log line, so a picture on the card is
  never offered to the core. A text cart's title is its first `--` comment line (dashes, tildes, `=`
  decoration, a version word and "by <author>" dropped, each word capitalised but the small ones, a colon
  read as " - "); a PNG cart's title is its file name without `.p8`, `_` read as a space, so the adds TSV
  names each file by its title.

### Screen

- **Canvas and Picture.** The 128x128 picture sits centred on a 240x160 canvas, which maps to 720x480 at
  exactly 3x. **Actual** (the default) is therefore an integer 3x, 384x384, with 48 px above and below and
  168 px at each side; **Stretch** crops to the picture and fills the panel (`stretch_crops_height`), which
  stretches it 1.875x by 3.75x. Stored as `pico8` in `Config/picture.txt`. FAKE-08's own 2x scale and crop
  options are fixed at `1x` and 0 (`FAKE08` in `core_options_policy.rs`).
- **Section.** PICO-8 gets its own Screen section, last, shown only when the card has PICO-8 carts:
  **Shader** (Off and the retro list, `Config/pico8_shader.txt`) and **Picture**. FAKE-08 runs at 60 fps
  and the panel near it, so there is no speed row. Select+X flips the picture as on the Lynx.

### Input

PICO-8 has the NES's controls, so it takes the NES answers: the d-pad, **O on B** (the bottom face button)
and **X on A** (FAKE-08's own libretro map: `RETRO_DEVICE_ID_JOYPAD_B` is O, `_A` is X), **Start** is the
pause button (FAKE-08's pause menu: Continue, the cart's own `menuitem` entries, Reset Cart). Slot owns L
and R; X is turbo X and Y turbo O through slot's turbo map. Select reaches nothing in FAKE-08. Only the
first player's pad is read.

### Saves, and no states

- **Cartdata** is the PICO-8 save. FAKE-08 keeps it in `<save dir>/cdata/<cartdata id>.p8d.txt`; slot
  gives the core `Saves/PICO8` as its save dir (`ngp_flash::core_save_dir`), so it is
  `Saves/PICO8/cdata/`. It is keyed by the id the cart passes to `cartdata()`, not by the file name, as
  in PICO-8. FAKE-08 gives no save RAM, so there is no `.sav`.
- **No states, no resume, no rewind.** At the pin `eris.init_persist_all` is commented out, so the Lua half
  of every state is empty (`persist_all` fails on the first C function in `_G`, and the error was
  swallowed): a load restored the RAM under a program that ran on unchanged. With the call made, the Lua
  state persists (76 KB to 400 KB, 0.3 to 3.8 ms a state on the M-series host, 1,132,612 bytes in all), but
  over three passes of the 39 carts (117 runs) 30 restores failed in eris ("invalid reference",
  "unknown type") and 9 runs crashed (SIGSEGV, SIGTRAP), some after a restore eris reported as good, and
  also after the VM was rebuilt following a failed one. That is not safe to offer, so the patch makes `retro_serialize_size` return 0. slot already
  handles a core with no state (ADR 0072): an eject, a doze or an autosave writes no state, the crash guard
  (ADR 0084) needs none, and the in-game States page is hidden for PICO-8 (`retro_quick::hidden_in_game`).
  `rewinds()` is false. Re-check on a FAKE-08 pin bump; the sum stays in the patched source.

### Cart and labels

- **Cart.** One PICO-8 cart, `RetroShell::Pico8`, drawn by us (`pico8_cart.svg`, `pico8_cart_detail.svg`) to
  the geometry every one of the 39 exports shares: 160x205, rounded top corners and bottom left (r 3), a
  10 px cut at the bottom right, the 128x128 label at (16, 24), the darker title strip at (15, 163), 130x32.
  Seated 240x308, drawn 312x400, grey `64 64 64` (the export's body; the low two bits of every pixel carry
  cart data). Lexaloffle's frame bitmap is not used. docs/cart-art/PICO8.md has every value.
- **Labels.** The label is the cart's own picture. `tools/fetch-labels.py` system `PICO8` needs no network:
  it crops (16, 24, 128x128) from a PNG cart, or draws a text cart's `__label__` section in the 32-colour
  palette, to `Labels/PICO8/<stem>.png`. All 39 of his carts gave a label.
- **Shelf order.** Released **2015-04-18**: zep's "Hello World" post on the Lexaloffle BBS
  (<https://www.lexaloffle.com/bbs/?tid=1808>, 2015-04-18 20:51, "PICO-8! This is quick test of the cart format
  and html5 web player. Voxatron users: check your account page"), the day the alpha (0.1.0) opened to
  Voxatron owners. Wikipedia gives only "April 2015". PICO-8 is the newest system either way.

## Compatibility

The 39 carts on the host core, 1,800 frames each with O pressed every 2 s, X a second later, and right held
from 15 s (`p8_compat`, a throwaway runner, not committed). "Plays" means no Lua error and a moving picture;
it is not a play-through.

| Title | File | Result | ms a frame |
|---|---|---|---|
| Alien Breed Demake | `PicoBreed.p8` | plays | 0.22 |
| Breakout Hero (Beta) | `Breakout_Hero.p8` | plays | 0.15 |
| Cave Runners! | `Cave_Runners.p8` | plays | 0.67 |
| Celeste | `Celeste.p8` | plays | 0.07 |
| Cherry Bomb | `Cherry_Bomb.p8` | plays | 0.07 |
| Chrysopoeia | `chrysopoeia.p8` | runtime error | |
| Circuits | `HI_Robot_programming_puzzle_game.p8` | runtime error | |
| CRATER | `CRATER.p8` | plays | 0.06 |
| DanceJab | `DanceJab.p8` | plays | 0.20 |
| DeFacto | `DeFacto.p8` | plays | 0.09 |
| Demon Castle | `Demon_Castle.p8` | runtime error | |
| Desert Drift | `Desert_Drift.p8` | plays | 0.12 |
| Katamari Christmassy | `Katamari_Christmassy.p8` | plays | 0.14 |
| Kelin's Delivery - Rain | `Kelin's_Delivery_Rain.p8` | plays | 0.05 |
| Ma Puzzle | `mapuzzle.p8` | plays | 0.24 |
| Mellow | `Mellow.p8` | plays | 0.25 |
| NETTY | `NETTY.p8` | plays | 0.12 |
| Omega Enforcer X | `Omega_Enforcer_X.p8` | plays | 0.14 |
| Perisher | `PERISHER_a_CELESTE_mod.p8` | plays | 0.09 |
| Pico de Pon | `Pico_de_Pon.p8` | plays | 0.06 |
| Pico Racer | `Pico_Racer.p8` | plays | 0.10 |
| Pico-Sprint | `Pico-Sprint.p8` | plays | 0.06 |
| Platformer Starter Kit | `Platformer_Starter_Kit.p8` | runtime error | |
| POLAR PANIC | `POLAR_PANIC.p8` | plays | 0.17 |
| Rolly | `Rolly.p8` | plays | 0.19 |
| SLACKER | `SLACKER.p8` | plays | 0.09 |
| StarBase | `StarBase.p8` | plays | 0.08 |
| Steps | `Steps.p8` | plays | 0.12 |
| Tetraminis Deffect | `Tetraminis_Deffect.p8` | plays | 0.15 |
| The Lair | `The_Lair.p8` | plays | 0.15 |
| Thopter Escape | `Thopter_Escape.p8` | plays | 0.07 |
| Tomb of G'nir | `Tomb_of_GNir.p8` | runtime error | |
| Tube Runner | `Tube_Runner.p8` | plays | 0.17 |
| UFO Swamp Odyssey | `UFO_Swamp_Odyssey.p8` | plays | 0.40 |
| Under Construction | `Under_Construction.p8` | runtime error | |
| Valdi - Beginnings | `Valdi_Shadows.p8` | plays | 0.10 |
| Warehouse Panic | `Warehouse_panic.p8` | runtime error | |
| Witch Loves Bullets | `Witch_Loves_Bullets.p8` | plays | 0.08 |
| X-Zero | `X-Zero.p8` | plays | 0.27 |

32 play, 7 stop on a Lua error FAKE-08 does not get past (for example Demon Castle: "attempt to index field
'pal' (a function value)", Under Construction: "bad argument #2 to 'setmetatable'"). They are FAKE-08
gaps, not slot's; they are reported upstream-first when the device gate confirms them.

## Performance

Host only, a direction and not a device number: the median of three runs of 600 frames after the run above,
Apple M-series. The slowest cart is Cave Runners at 0.67 ms a frame; most are under 0.25 ms. The budget at
60 fps is 16.7 ms. The device gate (issue 208) measures it with `bench:device` (`CORE=fake08`) and real play.

## Consequences

- Four patches, 0127 to 0130. No GBA, GB or GBC path changes; a GBA game after a PICO-8 game gets the GBA
  only input and picture (`pico8_then_gba.rs`).
- Upstream test sites (b), (e), (g) and (h) take one more token each, in order: `| Platform::Pico8`,
  `| Core::Fake08`, `"PICO-8"` and `QuickRow::ScreenPico8`, by the standing rule.
- slot's frontend answers no environment call during `retro_get_system_av_info` (upstream
  `slot-retro/src/libretro.rs`, `load`). That is a generic frontend gap and a candidate upstream PR (ADR 0047);
  the core-side request in the patch can go once upstream binds the host there.
- On a pin bump: rerun `pico8_core.rs` against the new source, re-read the four `freopen` writers, the pad
  path in `libretrohost.cpp`, and whether `init_persist_all` is called; states can come back only after a
  three-pass restore check of the owned carts with no failure and no crash.
