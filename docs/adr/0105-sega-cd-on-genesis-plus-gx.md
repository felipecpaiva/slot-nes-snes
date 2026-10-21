# 0105. Bring Sega CD / Mega-CD into scope on the Genesis Plus GX already shipped, with a BIOS check and the core's backup RAM made durable

- Status: Accepted. Amends [0053](0053-genesis-plus-gx-for-sega.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-21 (groundwork 2026-10-19, numbered 0094 on the `segacd-groundwork` branch; main's 0094 is the NGP flash ADR)
- Deciders: maintainer (Felipe Paiva)
- Related: [Sega CD plan](../research/segacd-plan.md), [ADR 0053](0053-genesis-plus-gx-for-sega.md), [ADR 0059](0059-need-fullpath-load.md), [ADR 0067](0067-ps1-disk-control-and-disc-in-states.md), [ADR 0069](0069-ps1-jewel-case-shelf.md), [ADR 0072](0072-write-sav-when-the-core-gives-no-state.md), [ADR 0094](0094-ngp-flash-staged-checked-published.md), [ADR 0098](0098-expansion-card.md), [ADR 0100](0100-shelf-order-option.md), [issue 222](../../.github/issues/222-segacd-tracking.md), patches 0139 to 0146

## Context

Sega CD ranks first on the next-systems review (docs/research/next-systems-2026-10-20.md): 59 owned titles on
61 discs, all `.chd`, and the three BIOS files on hand. Genesis Plus GX already ships for Game Gear, Master
System and Mega Drive (ADR 0053), and our pinned build (`393f70c`) has CHD support compiled in. So there is no
new core, no new licence and no new build.

Reading the core at the pin and testing it on slot's open path (patch 0139) found these facts:

- The core picks one BIOS file from the disc's region byte at 0x20b (`get_region`: 0x64 Europe, 0xa1 Japan,
  anything else USA) and checks nothing in it beyond opening it. A missing file fails the load. A junk file
  loads and shows a black screen.
- The core gives slot no `SAVE_RAM` for a CD and does not list the backup RAM in its memory maps. It writes the
  8 KB backup RAM itself, only in `retro_unload_game`, truncating the file in place, as `scd_U.brm` (or E, J)
  shared by every game of a region, or `<stem>.brm` with `genesis_plus_gx_system_bram = per game`.
- **The state does not carry the backup RAM** (`scd_context_save`). Unlike NGP, a resume state is no backstop:
  a power cut loses every save since the last clean eject, resume or not.
- `genesis_plus_gx_cart_size = disabled` does not disable the RAM cart at the pin: `check_variables` stores
  it as `cart_size = 0xff`, and `cd_cart_init` mounts a cart whenever `cart_size` is not zero, with a size mask
  of `1 << (0xff + 13)`. Leaving the option unanswered keeps `cart_size` at 0, no cart (pinned by test).
- The core offers only the legacy disk control interface (no `set_initial_image`), holds 4 discs, and joins
  every `.m3u` line to the playlist's own directory, so an absolute line does not load.
- A synthetic disc cannot boot a program: the BIOS runs a disc only when it carries Sega's security block at
  0x200, which is Sega's code. With a dummy boot ROM every contract slot needs is still testable on CI.

## Decision

- Sega CD is in scope as Phase 22: one shelf `Games/SEGACD` for `.chd`, `.cue`, `.iso` and `.m3u` (a `.bin` is
  a track, never a game), `Platform::SegaCd` appended to `SHELVES` after the PC Engine CD. Upstream `ALL` stays
  untouched and every policy method is answered explicitly (ADR 0063). The core is `Core::GenesisPlusGx` at the
  existing pin, with no picker. Released 12 December 1991 (Mega-CD, Japan) for the shelf order (ADR 0100).
- Picture, timing and pad are the Mega Drive's: the 360x240 canvas, Stretch following the live frame width
  (ADR 0052), 59.92 fps and 49.70 fps for European discs (ADR 0071), the 6-button pad with X and Y to the game
  and L2, R2 kept by slot. Its own Screen section has the Mega Drive rows: Shader (Off and the retro list,
  `Config/segacd_shader.txt`), Picture (Stretch, Actual, 4:3) and PAL Speed. No Region row: a forced region
  would boot a disc under a BIOS slot did not check.
- BIOS: user-supplied `bios_CD_U.bin`, `bios_CD_E.bin` and `bios_CD_J.bin` in `BIOS/`, never shipped and never
  in CI. Before launch slot checks the file of the disc's region: 131072 bytes and a crc32 it knows. US
  `9f6f6276` (md5 `854b9150...`, the Genesis Plus GX doc and the maintainer's file) and `c6d10268` (md5
  `2efd74e3...`, the libretro-database `dat/System.dat` row); Europe `529ac15a` and Japan `9d2da8f2` (both
  System.dat). Missing refuses with a toast naming the file; an unknown 128 KB file launches with one toast a
  session. The region comes from the file name tags, then the byte at 0x20b of a `.cue` or `.iso`, then USA,
  because reading a `.chd` needs a hunk decode.
- Core options, for a Sega CD disc only (the Mega Drive, Master System and Game Gear get none):
  `genesis_plus_gx_system_bram = per game` and `genesis_plus_gx_cd_precache = disabled`, so a reload reads only
  the CHD header. `genesis_plus_gx_cart_size` stays unanswered (the 0xff finding above), which mounts no cart.
- Backup RAM follows the NGP flash design (ADR 0094), generalised in `slot::ngp_flash` by platform, with no
  state backstop:
  1. the core's save dir is `Saves/SEGACD/.core`;
  2. before load the published `Saves/SEGACD/<stem>.brm` is staged there if it is exactly 8192 bytes and ends
     with the format footer the core checks; any other file is moved aside to `<stem>.brm-refused`;
  3. after unload slot publishes the core's file with a temp, fsync and rename, never a torn one;
  4. **flush by reload** (serialize, load the disc again, publish, unserialize) at `flush_resume` (lid close,
     POWER, battery critical), the 60 s autosave and eject. The stem is the content's, so a set's file is named
     after its playlist, and the state's disc trailer keeps a set on its disc through the reload.
- The flush by reload at lid close stays only if the device measurement passes: under 100 ms warm on a real
  CHD (host: well under a frame for a synthetic disc, 2 ms for Final Fight CD). Otherwise it runs only at
  eject, autosave and quick-menu open, and the lid-close loss window is written here as an amendment. A core
  patch that exposes `scd.bram` as `SAVE_RAM` is the last resort, upstream first (ADR 0047), because ADR 0002
  builds cores unpatched.
- Discs follow ADR 0067: SELECT+L2 swaps, rollback, `Saves/SEGACD/<stem>.disc`, and the PS1 state trailer (the
  magic names the format, not the system, and a state never leaves its own `States/SEGACD`). Generated
  playlists live in `Config/playlists/SEGACD` with paths relative to the playlist; PS1 keeps its absolute ones.
  With no `set_initial_image`, a remembered disc is swapped in right after the load.
- The shelf draws the PS1 jewel case (ADR 0069) unchanged, the Japanese style with its spine card, a set as the
  double case, the style from the same region rule as the BIOS check. North American Sega CD games shipped in
  larger cases about the size of a VHS keep case (Wikipedia, Optical disc packaging, read 2026-10-21); v1 draws
  the jewel case for every region with the cover fitted whole in the square well, and the US large case is a
  deferred style, like the PS1 disc stack of issue 68. Covers and disc scans
  come by name from ScreenScraper system 20 (`tools/fetch-labels.py --only SEGACD --by-name --logo-fallback`),
  because a `.chd` has no CRC any dat indexes; the logo fallback reads libretro-thumbnails
  "Sega - Mega-CD - Sega CD".
- The maintainer's discs live on the Expansion Card (ADR 0098): `Games/SEGACD` on `/mnt/expansion` and the line
  `SEGACD` in `Config/expansion.txt`. Saves, states, labels and the BIOS stay on the main card.

## Consequences

- Eight patches (0139 to 0146). They touch neither GBA, GB nor GBC, and give the Mega Drive no new option, so the
  GBA harness compare stays at 0 diffs and the Mega Drive tests are unchanged.
- No build, dist or zip change for the core, which already ships. `zip-check.sh` gains the `SEGACD` games
  folder.
- `slot::ngp_flash` now serves two platforms; NGP keeps its paths, files and checks. The disc helpers in
  `slot_store::ps1` and `slot::ps1_load` take the platform.
- This is the first core whose state does not back up its saves. A Sega CD save written in the window between
  the last flush and a power cut is lost; the flush points above keep that window to at most 60 s of play.
- CI tests the core with a dummy BIOS only. The real BIOS and real discs are covered by the maintainer's local
  runs (`SLOT_SEGACD_BIOS`, `SLOT_SEGACD_DISC`) and the device gate (docs/DEVICE-GATE.md, issue 232).
- On a rebase or a core pin bump, `segacd_core.rs` is the contract to rerun: BIOS file names, the region byte,
  the `.brm` names and timing, the state without the backup RAM, the m3u joining and the RAM cart option.
