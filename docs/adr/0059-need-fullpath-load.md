# 0059. Hand need_fullpath cores the path only, never a ROM buffer

- Status: Accepted
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0009](0009-host-struct-untouched.md), [patch 0030](../../patches/0030-need-fullpath.patch), [PS1 plan](../research/ps1-plan.md), upstream branch `need-fullpath` on felipecpaiva/slot

## Context

slot v1.7.0 `LibretroCore::load` always reads the whole ROM with `fs::read` and passes path,
data and size to `retro_load_game`. A core whose `retro_get_system_info` sets `need_fullpath`
reads the file itself and may ignore the data. Read from the host dylibs with
`retro_get_system_info`:

| Core | need_fullpath | What it loads from |
|---|---|---|
| mGBA | false | data |
| gpSP | true | `info->path` only (`libretro/libretro.c:585`, pin `7b2dd37`) |
| fceumm | true | path; data only through `GAME_INFO_EXT`, which slot does not answer (`libretro.c:1846`, `:3935-3968`) |
| Genesis Plus GX | true | path; data only through `GAME_INFO_EXT` (`libretro/libretro.c:3131`) |
| nestopia, snes9x, snes9x2005_plus | false | data |

So slot holds up to 32 MB of a GBA ROM that gpSP never reads, and a PS1 core (pcsx_rearmed,
also `need_fullpath`) would be handed a whole disc image. The libretro spec allows `data` to be
NULL when `need_fullpath` is set.

## Decision

`load` asks `retro_get_system_info` first. When `need_fullpath` is true it checks the file exists
(`fs::metadata`, so a missing cart is still `CoreError::Io`), keeps no buffer, and passes the
original path, not a canonicalised one, with `data` NULL and `size` 0. Otherwise it reads the
file as before. `block_extract` is not read: slot never extracts archives. Two accessors,
`needs_full_path` and `rom_bytes_held`, let tests see the decision. `Host` is untouched (ADR 0009).

The load follows AaronC1990/tray (path untouched) and the `SystemInfo` field order follows
bently0602/slot, both GPL-3.0.

## Consequences

- gpSP, fceumm and Genesis Plus GX no longer get a ROM copy. Every frame stays the same: the
  harness compare shows 0 differing frames on mGBA and gpSP, and a 300-frame video, audio and
  state-size hash per core (mGBA, gpSP, fceumm, nestopia, snes9x, snes9x2005_plus, Genesis Plus
  GX on GG, SMS and MD) is identical before and after.
- `crates/slot/tests/fullpath_load.rs` asserts the path-only load on gpSP, fceumm and Genesis
  Plus GX, the full buffer on mGBA, and the Io error for a missing cart.
- PS1 (pcsx_rearmed) can load `.cue`, `.chd` and `.m3u` by path with no further load change.
- **Drop patch 0030 when the upstream PR lands** (ADR 0047). The upstream branch carries the same
  code and accessor names, so nothing above it changes when it is dropped.
