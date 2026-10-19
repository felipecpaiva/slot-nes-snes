# 0085. A PS1 disc hack patches track 1 of a bin/cue extracted with chdman, and goes back as a new .chd

- Status: Accepted
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: `tools/hacks.py`, `tools/hacks.json`, [docs/HACKS.md](../HACKS.md), [ADR 0082](0082-rom-hack-updates-keep-saves-move-states.md)

## Context

The PS1 games on the card and in the library are `.chd`. The good PS1 hacks (Symphony of the Night's
Quality hack, the Castlevania Chronicles knockback fix) ship as PPF or xdelta patches made against a
redump bin/cue, usually against the data track only. A `.chd` cannot be patched in place: it is
compressed in hunks, and its own SHA-1s cover the data. The tool's patchers worked on one file in
memory, had no PPF, and its duplicate checks CRC'd whole files, which for discs (hundreds of MB, about
260 in the library) means reading a hundred GB, or pulling every same-size disc over adb.

## Decision

A PS1 entry names its base disc by file name (`base_name`, the library's `<base_name>.chd`) and its
base by the redump CRC32 of track 1 (`base_crc32`). The tool extracts the base with MAME's `chdman
extractcd --splitbin` into a temp dir (one bin per track plus the cue), refuses unless track 1 has that
CRC, applies the patch to track 1 (PPF in place through an mmap; a write past the track's end is
refused), packs the cue with `chdman createcd`, then extracts the new disc again and refuses unless
track 1 is the patched CRC, every other track is byte-identical, and `chdman info` shows the same track
layout (types, frames, pregaps). The result is written as a new `.chd` under the hack's own name, so the
base disc is only read, and every rule of ADR 0082 applies unchanged (PS1 states in
`States/PS1/<core>/<stem>/` move on an update, `Saves/PS1/<stem>.sav` and `.disc` are copied). The
state file records the `.chd` file's CRC32: chdman's output is deterministic for one version, and it is
what the card holds. PPF 1.0, 2.0 and 3.0 are applied in pure Python, with PPF2's and PPF3's block
check and PPF3's undo data compared against the image before the first write.

Duplicates are found by size first, then CRC: a card file of the same size is read from its library
copy of the same name and size when there is one (a Mac read), and pulled from the card only when
there is none. A new game whose name already has saves or states on the card is refused.

## Consequences

- PS1 hacks install like cartridge hacks: one new file, never a duplicate, the original untouched. One
  disc build takes 20 to 30 seconds on the M5 Max and needs about three times the disc's size free in
  the temp dir.
- Each disc update keeps the old disc as its backup. On a full card, set `backups` to a folder off the
  card (ADR 0082, amendment of 2026-10-19).
- `chdman` must be installed (`brew install rom-tools`; mise has no package for it). Without it a PS1
  build is refused and its tests are skipped.
- `createcd` is pinned to the library's codecs (cdlz, cdzl, cdfl). If a chdman upgrade still changes
  the output bytes, an `--update` with the same patch no longer reads "already installed": it backs up
  the disc and moves its states aside for an identical game (nothing lost, `--rollback` brings them back).
- `--check` does not identify an installed PS1 hack by CRC (that would build a disc per check); the
  state file's version is shown.
- A patch for a track other than 1, a patched base in another container (.cue, .pbp), or a pre-patched
  `.chd` with a `target_crc32` is not handled: `target_crc32` on a PS1 entry is the patched track 1.
- A same-name, same-size library copy is taken as the card file's content. If the two ever differ
  under one name, a duplicate on the card can be missed (nothing is overwritten: the new file has its
  own name).
