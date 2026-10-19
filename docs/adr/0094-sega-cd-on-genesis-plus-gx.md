# 0094. Bring Sega CD / Mega-CD into scope on the Genesis Plus GX already shipped, with a BIOS check and the core's backup RAM made durable

- Status: Accepted for the groundwork. Amends [0053](0053-genesis-plus-gx-for-sega.md) and the docs/PLAN.md "Who it's NOT for" line on more systems
- Date: 2026-10-19
- Deciders: maintainer (Felipe Paiva)
- Related: [Sega CD plan](../research/segacd-plan.md), [ADR 0053](0053-genesis-plus-gx-for-sega.md), [ADR 0059](0059-need-fullpath-load.md), [ADR 0067](0067-ps1-disk-control-and-disc-in-states.md), [ADR 0069](0069-ps1-jewel-case-shelf.md), [ADR 0072](0072-write-sav-when-the-core-gives-no-state.md), [issue 113](../../.github/issues/113-segacd-tracking.md), [issue 118](../../.github/issues/118-segacd-backup-ram.md), patch `patches/0057-segacd-core-tests.patch`

## Context

Sega CD ranks first on the next-systems review (2026-10-19): about 62 owned discs, all `.chd`, and the
three BIOS files on hand with the md5s the Genesis Plus GX doc lists. Genesis Plus GX already ships for
Game Gear, Master System and Mega Drive (ADR 0053), and our pinned build (`393f70c`) has CHD support
compiled in. So there is no new core, no new licence and no new build.

Reading the core at the pin and testing it on slot's Mega Drive open path (patch 0057) found four things
that shape the design:

- The core picks one BIOS file from the disc's region byte at 0x20b and checks nothing in it beyond
  opening it. A missing file fails the load. A junk file loads and shows a black screen.
- The core gives slot no `SAVE_RAM` for a CD and does not list the backup RAM in its memory maps. It
  writes the 8 KB backup RAM itself, only in `retro_unload_game`, truncating the file in place, as
  `scd_U.brm` (or E, J) shared by every game of a region, or `<stem>.brm` with
  `genesis_plus_gx_system_bram = per game`.
- **The state does not carry the backup RAM** (`scd_context_save`). This differs from NGP, where a
  resume state alone brings the flash back. Here a power cut loses every save since the last clean eject,
  resume or not.
- A synthetic disc cannot boot a program. The BIOS runs a disc only when it carries Sega's security block
  at 0x200. That block is Sega's code and is not in the BIOS as a plain copy. With a dummy boot ROM,
  though, every contract slot needs can be tested on CI: load, region, timing, canvas and the backup RAM
  file.

## Decision

- Sega CD is in scope as Phase 13: one shelf `Games/SEGACD` for `.chd`, `.cue`, `.m3u` and `.iso`, as
  `Platform::SegaCd`, appended to `SHELVES`. Upstream `ALL` stays untouched and every policy method is
  answered explicitly (ADR 0063). The core is `Core::GenesisPlusGx` at the existing pin, with no picker.
- BIOS: user-supplied `bios_CD_U.bin`, `bios_CD_E.bin` and `bios_CD_J.bin` in `BIOS/`, never shipped and
  never in CI.
  - slot checks the file for the disc's region before launch: present, 131072 bytes, and an md5 it
    knows.
  - A missing file refuses the launch with a toast. An unknown dump launches with a one-time toast.
  - The region comes from the file name tags, then the 0x20b byte where it is cheap to read (`.cue`,
    `.iso`), then US.
- Picture, timing and pad are the Mega Drive's:
  - the 360x240 canvas, ADR 0052's stretch, and its own Screen section with the Mega Drive rows;
  - 59.92 fps, and 49.70 fps for PAL discs, handled by ADR 0071;
  - the 6-button pad.
- Core options are explicit:
  - `genesis_plus_gx_system_bram = per game`;
  - `genesis_plus_gx_cart_size = disabled`. No RAM cart, which is what slot gets today because it
    answers no option it was not given. RetroArch's default is one shared 512 KB cart.
  - `genesis_plus_gx_cd_precache = disabled`, so a reload does not read the whole CHD.
- Backup RAM durability follows NGP issue 75's design with no state backstop:
  1. the core's save dir is `Saves/SEGACD/`;
  2. the core writes into a staging dir;
  3. before load, the `.brm` is checked (exactly 8192 bytes, with the format footer) and copied in;
  4. after unload, it is published with `persist`'s temp, fsync and rename;
  5. **flush by reload** (serialize, reload the disc, publish, unserialize) runs at `flush_resume`,
     eject and autosave.
- The flush by reload at lid close is accepted **only if the device measurement passes**: under 100 ms
  warm on a real CHD. It measured 2 ms on the host for Final Fight CD.
  - Otherwise the reload runs only at eject, autosave and quick-menu open, and the lid-close loss window
    is written down here as an amendment.
  - A core patch that exposes `scd.bram` as `SAVE_RAM` is the last resort, and goes upstream first
    (ADR 0047), because ADR 0002 builds cores unpatched.
- Discs follow ADR 0067: swap, rollback, `Saves/SEGACD/<stem>.disc`, and a state trailer with its own
  magic. The core offers only the legacy disk interface, so the remembered disc is restored by a swap
  after load.
  - Generated playlists hold paths relative to the playlist, because the core joins every line to the
    playlist's directory. PS1's absolute playlists do not load here.
- The shelf is ADR 0069's jewel case, faced with the front cover:
  - US, EU and JP styles, the JP one with its obi;
  - covers from ScreenScraper system 20.

## Consequences

- About 9 patches (issues 114 to 122). They touch neither GBA, GB nor GBC, so the GBA harness compare
  stays at 0 diffs.
- No build, dist or zip change for the core, which already ships. `zip-check.sh` gains the `SEGACD`
  games folder with the platform patch.
- This is the second core whose saves slot never sees, after NGP, and the first whose state does not
  back them up. Until issue 118 lands, a power cut loses Sega CD progress back to the last eject. The
  platform patch must not ship to the release without issue 118.
- CI tests the core with a dummy BIOS only. The real BIOS and real discs are covered by the
  maintainer's local runs (`SLOT_SEGACD_BIOS`, `SLOT_SEGACD_DISC`) and the device gate.
- On a rebase or a core pin bump, `segacd_core.rs` is the contract to rerun: BIOS file names, the
  region byte, the `.brm` names and timing, the state without the backup RAM, and the m3u joining.
