# 0101. Bring the PC Engine SuperGrafx into scope on pinned Beetle SuperGrafx, a shelf of its own beside an unchanged TurboGrafx-16

- Status: Accepted. Amends [0002](0002-cores.md), the docs/PLAN.md "Who it's NOT for" line on more systems, and [0091](0091-tg16-on-beetle-pce-fast.md) ("SuperGrafx out of scope")
- Date: 2026-10-21
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0091](0091-tg16-on-beetle-pce-fast.md) (the TurboGrafx-16 precedent this follows), [ADR 0087](0087-four-three-picture.md), [ADR 0100](0100-shelf-order-option.md), [issue 194](../../.github/issues/194-sgx-tracking.md), patches `0120-sgx-core-tests` to `0123-sgx-pad`, [docs/cart-art/SGX.md](../cart-art/SGX.md)

## Context

The maintainer asked for the PC Engine SuperGrafx as its own platform. NEC released it in Japan on
8 December 1989 ([Wikipedia](https://en.wikipedia.org/wiki/PC_Engine_SuperGrafx), infobox, read
2026-10-21). It is a PC Engine with a second HuC6270 VDC, the HuC6202 VPC that mixes the two, and 32 KB
of work RAM instead of 8 KB. Five HuCards need it (1941: Counter Attack, Aldynes, Battle Ace,
Daimakaimura, Madou King Granzort) and two PC Engine HuCards use it when present (Darius Plus, the one
commercial card with the PC-SG mark, and Darius Alpha). The maintainer owns all seven: the five in
`ES-DE/Roms/supergrafx` on B3Tb, and the two Darius cards, which are on the device's TG16 shelf today.

ADR 0091 left SuperGrafx out ("Beetle SuperGrafx: SuperGrafx only matters for 5 HuCards"). Beetle PCE
Fast has no SuperGrafx code, so the TG16 shelf cannot run them.

The libretro SuperGrafx cores are **Beetle SuperGrafx** (libretro/beetle-supergrafx-libretro,
`mednafen_supergrafx`: Mednafen's pce_fast with the SuperGrafx hardware added, the same source tree as
Beetle PCE Fast) and **Beetle PCE** (`mednafen_pce`, the accurate module, heavier). Beetle SuperGrafx is
the one RetroArch and ES-DE use for the system (`supergrafx/systeminfo.txt` on B3Tb lists it first).

## Decision

- The SuperGrafx is in scope as Phase 18, after the arcade boards. One shelf `Games/SGX`. The platform is
  `Platform::Sgx`, appended to `SHELVES` after `Cps2`; the core is `Core::MednafenSupergrafx`, appended to
  `EVERY` after `Fbneo`. Upstream's `ALL` stays untouched and every policy method answers the SuperGrafx
  explicitly. One core, no picker. The TurboGrafx-16 shelf and Beetle PCE Fast do not change.
- **Core pin.** libretro/beetle-supergrafx-libretro `9c11dcd213a79d57d2c86313971631af801f2cdc` (its
  HEAD on 2026-10-21), archive sha256
  `7fbe720bd6173bac54e76b1f772b11179a3c5aae0f2d6e14f040df71311e2976`, checked by `build.sh fetch`.
- **Build.** The Beetle PCE Fast recipe (ADR 0091): `make platform=unix`, `-mcpu=cortex-a53` on the
  device, `platform=osx` on the host, `make_args="HAVE_CDROM=0 HAVE_CHD=0"`. This makefile defaults to
  `HAVE_CHD = 1`, so `HAVE_CHD=0` is what keeps the rchd reader and its codecs out; the CD image readers
  (`.cue`, `.ccd`) and Tremor are still compiled and unreachable from a HuCard shelf. The core is C++, so
  the device build links `-static-libstdc++ -static-libgcc -Wl,--as-needed`. `psg.cpp` calls `powf`,
  which glibc 2.27 re-versioned; `cores/mednafen_supergrafx/glibc-2.17.h` binds `powf@GLIBC_2.17` as
  for Beetle PCE Fast. The device `.so` needs only `GLIBC_2.17` symbols (`task
  core:device:mednafen_supergrafx` checks it); its sha256 at this pin is `1ccf030a...c846d`.
- **Licence.** Mednafen is GPL. The root `COPYING` is GPL-2.0, and no file says version 2 only: 47 of
  the 119 Mednafen and root sources say "any later version" (45 GPL-2.0-or-later, Blip_Buffer
  LGPL-2.1-or-later, `msvc_compat.h` GPL-3.0-or-later), the 31 Tremor files are Xiph BSD, and 42 have no
  licence text in their first 60 lines (`libretro.cpp` among them: its GPL-2.0-or-later block starts at
  line 636). The combined core is GPL-3.0-or-later like slot. It ships with
  `licenses/mednafen_supergrafx-GPL-2.0.txt` (`COPYING` verbatim), `-tremor-BSD.txt`
  (`mednafen/tremor/COPYING` verbatim) and `-headerless-files.txt`, and its source tarball. LICENSING.md
  has the counts and the commands.
- **Shelf.** `.sgx` and `.pce`, titled by the file stem. No-Intro names the five SuperGrafx cards `.sgx`
  (`NEC - PC Engine SuperGrafx`), and the two Darius cards `.pce` with `(SG Enhanced)` in the PC Engine
  dat. A `.sgx` file on the TG16 shelf is skipped, as before; a `.pce` card is a TurboGrafx-16 card on the
  TG16 shelf and a SuperGrafx card on the SGX shelf, so the folder decides.

### SuperGrafx mode: `sgx_forcesgx` is answered `enabled`

The core runs a card as a SuperGrafx only for a `.sgx` extension or a CRC in its own table
(`mednafen/pce_fast/pce.cpp`, `sgx_table`), or when `sgx_forcesgx` is on. The table has Darius Plus
(`BEBFE042`) and the five SuperGrafx cards, but **not Darius Alpha** (`B0BA689F`), so Darius Alpha would
run as a plain PC Engine. Answering `sgx_forcesgx=enabled` makes the shelf a SuperGrafx console: every card
on it gets the second VDC and 32 KB, which is what the real console does with a PC Engine HuCard. The core
declares the option `disabled` by default but its own setting starts `true` (`mednafen/settings.cpp`), so
the answer is stated, not left to either default. `forcesgx` is applied after the CRC checks, so it also
overrides the core's one exception, Space Harrier (two CRCs in `pce.cpp`, not SuperGrafx compatible);
that card belongs on the TG16 shelf. `sgx_core.rs` pins it: a `.pce` card
outside the table reports 8 KB of work RAM (`retro_get_memory_size(RETRO_MEMORY_SYSTEM_RAM)`) with the
option disabled and 32 KB with it enabled, and a `.sgx` file 32 KB.

### Options

The TurboGrafx-16 list (ADR 0091, issue 84) under the `sgx_` prefix, each key and value read from
`libretro_core_options.h` at the pin and checked against the core's declared values by `sgx_platform.rs`:
`sgx_initial_scanline=3` and `sgx_last_scanline=242` (unanswered, the core draws 243 lines, which the
240-line canvas halves; `sgx_core.rs` tests both), `sgx_hoverscan=352`, `sgx_palette=RGB`,
`sgx_default_joypad_type_p1=2 Buttons`, `sgx_disable_softreset=disabled`, `sgx_turbo_toggle=disabled`
(the key is `_toggle` here, `_toggling` in Beetle PCE Fast), `sgx_nospritelimit=disabled`,
`sgx_ocmultiplier=1`, and `sgx_forcesgx=enabled`. The CD keys stay unanswered. The core declares **no
frameskip option**, so slot's `<prefix>_frameskip=auto` has nothing to answer and logs that once at load;
fast-forward runs every frame (see Performance).

### Video and the Screen section

The video path is the TurboGrafx-16 one: the 360x240 canvas, a 256x240 picture at x 52, wider dot clocks
followed by Stretch (`follows_frame_width`), no new canvas code. `sgx_core.rs` checks the red test card
fills the canvas height at 59.82 fps and 44.1 kHz.

The Screen page gains a **SuperGrafx** section, last in the classic order (after CPS2) and by date in the
Release year order (after Lynx). Its rows are the TurboGrafx-16 rows, Shader and Picture:

- Shader walks the retro list, kept in `Config/sgx_shader.txt` (`sgx=`), and the in-game Shader row steps it.
- Picture starts at **Crop** (8 lines off the top and bottom, the TurboGrafx-16 and SNES amount) and walks
  Stretch, Actual and **4:3**, kept in `Config/picture.txt` as `sgx`. 4:3 is offered because the
  SuperGrafx is a television console, the ADR 0087 rule for NES, SNES, Master System and Mega Drive. The
  TurboGrafx-16 Picture row (Crop, Stretch, Actual) was left as it is; offering it 4:3 too is a one-token
  change in `offers_four_three` and a separate decision.

### Input

The TurboGrafx-16 pad: B is II, A is I, START is Run, SELECT reaches the game after slot's chord hold, so
Select and Run together are the console's soft reset (kept on). X and Y are the turbo switches through
`Platform::turbo_on_xy()` (now TurboGrafx-16 and SuperGrafx), and slot's Turbo Buttons row pulses I and II
or sends nothing; the core's own turbo stays off. L1 and R1 stay slot's picture keys.

**The 6-button pad is a Pad row, 2 Buttons by default.** The core emulates the Avenue Pad 6
(`sgx_default_joypad_type_p1`, read when the core starts) and maps III, IV, V and VI to RetroPad Y, X, L
and R (`libretro.cpp`, `update_input`); its turbo works only in 2-button mode. Its help text warns that
6-button mode "can have weird behaviors in non compatible games", and none of the seven SuperGrafx titles
uses it (it is for PC Engine fighting games such as Street Fighter II' Champion Edition), so 2 Buttons
stays the default. The Pad row (patch 0123, `Config/sgx.txt`, `pad = 2` or `6`) answers the option at the
next start. With 6 buttons, latched when the card seats like the Virtual Boy Right Pad: X and Y reach the
core raw (slot's turbo is passed by, `set_pass_through`), L1 and R1 go to the game (slot gives up the
shoulders), and the picture toggle moves to SELECT+X, as on the SNES. A GBA game after a six-button
SuperGrafx game gets the GBA-only input and picture (`sgx_then_gba.rs`).

### Saves and states

Every card gets the core's 2 KB backup RAM with the `HUBM` header as save RAM, as on the TurboGrafx-16,
so slot writes a 2 KB `.sav` to `Saves/SGX` for every card (issue 86's rule). States round-trip; rewind,
fast-forward, doze, the crash guard and resume are the generic paths, and `cart_platform=sgx` resumes a
SuperGrafx game.

### Cart

A `.sgx` card wears the **Super HuCard**: the white HuCard at the same size, turned over, with the gold
contacts and cut marks above the label and the ridges below. Super HuCard labels are printed the other
way up from standard HuCards ([Wikipedia](https://en.wikipedia.org/wiki/PC_Engine_SuperGrafx): "The
labels on SuperGrafx HuCards were upside-down relative to standard HuCards"). The SuperGrafx branding is
on the label scan itself. The two `(SG Enhanced)` `.pce` cards keep the standard HuCard, which is what
they are. Values and sources are in docs/cart-art/SGX.md.

### Labels

`tools/fetch-labels.py` system `SGX`: library folder `supergrafx`, dats `NEC - PC Engine SuperGrafx` and
`NEC - PC Engine - TurboGrafx 16` (for the two Darius cards), ScreenScraper system 105 ("PC Engine
SuperGrafx", screenscraper.fr systemeinfos.php, checked 2026-10-21; Skyscraper's `platforms_idmap.csv` has
no SuperGrafx row). An `(SG Enhanced)` card is asked under the PC Engine id 31. libretro-thumbnails has
`NEC - PC Engine SuperGrafx` Named_Logos for all five SuperGrafx cards, for `--logo-fallback`.

### The library

The five SuperGrafx cards are ADD rows, the two Darius cards MOVE rows from `Games/TG16` to `Games/SGX`, in
`docs/rom-library/best-copy/sgx-adds.tsv` (workspace). The device copies of the Darius cards match the
No-Intro md5 (`C87135A6...` and `3274EEE6...`). They move rather than stay on both shelves: the
no-duplicates rule, and only the SGX shelf runs their SuperGrafx code. Their labels in `Labels/TG16` move
with them.

## Performance

Host only, a direction and not a device number: `core_bench` (`--frames 1800 --warmup 600 --repeats 3`,
release, Apple M5 Max) on the maintainer's dumps (read only, never committed), with the platform's options.

| Card | ms a frame | with `--frameskip` |
|---|---|---|
| Daimakaimura (SuperGrafx) | 0.315 | 0.314 |
| 1941: Counter Attack (SuperGrafx) | 0.287 | 0.279 |
| Darius Plus (PC-SG) | 0.206 | 0.207 |
| Darius Plus on Beetle PCE Fast, for scale | 0.137 | |

Two VDCs cost about twice Beetle PCE Fast. `--frameskip` changes nothing because the core has no frameskip
option. PERFORMANCE.md puts the RG34XXSP 15 to 22 times behind this host, so expect 3 to 7 ms a frame on
the Cortex-A53 against a 16.7 ms budget at 59.82 fps: full speed, with fast-forward near 2.5x rather
than the 4x of lighter cores. The device gate (issue 199) measures it with `bench:device`
(`CORE=mednafen_supergrafx`) and real play.

## Consequences

- Four patches, 0120 to 0123. No GBA, GB or GBC path changes; the TurboGrafx-16 shelf is unchanged.
- Upstream test sites (b), (e), (g) and (h) take one more token each, in order, by the standing rule:
  `| Platform::Sgx`, `| Core::MednafenSupergrafx`, `"SuperGrafx"` and `QuickRow::ScreenSgx`.
- The core joins `task core:host`, `task core:device`, `task check`, `dist:device` and `zip-check.sh`.
- On a pin bump, check `sgx_table` (`pce.cpp`) still lacks nothing that matters, that `forcesgx` still
  starts true in `settings.cpp`, whether a frameskip option appeared, the re-versioned libm functions
  ADR 0091 lists, and that `HAVE_CHD` still defaults to 1.
