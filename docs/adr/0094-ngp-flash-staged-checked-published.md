# 0094. Keep NGP cart flash safe: a staging save dir, a check before load, an atomic publish and a flush by reload

- Status: Accepted
- Date: 2026-10-19
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0090](0090-ngp-on-beetle-neopop.md), [ADR 0072](0077-write-sav-when-the-core-gives-no-state.md), [ADR 0082](0087-rom-hack-updates-keep-saves-move-states.md), [issue 75](../../.github/issues/75-ngp-flash-saves.md), [NGP plan](../research/ngp-plan.md) section 3, `patches/0079-ngp-flash.patch`

## Context

Beetle NeoPop exposes no `SAVE_RAM`. The game's progress lives in cart flash, which the core
writes itself to `<save dir>/<stem>.flash` only in `retro_unload_game`, through a stdio stream
opened for write, so the file is truncated first. At load it trusts the lengths in that file:
`flash_read` allocates `total_file_length` bytes and fills what the file holds, and
`do_flash_read` walks `block_count` block headers with no bounds check (`mednafen/ngp/flash.c` at
`a50d5ac`). A file torn after its 8-byte header loads heap garbage into the cart. slot's `.sav`
path, ADR 0072's no-state path and `save_ram_trusted` never see the flash, and slot handed every
core `Saves/`, so NeoPop wrote beside the platform folders.

The plan listed five options (section 3). Answering `GET_VFS_INTERFACE` with an atomic writer was
rejected because every core that uses libretro-common `filestream` would go through it.

## Decision

Options 1, 2 and 3 of the plan, with the resume state (option 5) as the backstop it already is.

- **Save dir.** A new policy answer, `Platform::flashes_on_unload`, is true for NGP only.
  `ngp_flash::core_save_dir` gives that core `Saves/NGP/.core` (a staging dir) and every other core
  `Saves/` as before, so no other system changes.
- **Check before load.** In the opening thread, before the core loads, the staged copy is deleted
  and `Saves/NGP/<stem>.flash` is copied in only if it matches NeoPop's layout: id `0x0053`, at most
  256 blocks, `total_file_length` equal to the file size, and every block header and its data
  inside the file. A file that fails is renamed `<stem>.flash-refused`, logged, and the game starts
  with blank flash. A torn staged file left by a crash is never loaded, because staging is cleared
  first. An old `Saves/<stem>.flash` is moved into `Saves/NGP/` once.
- **Atomic publish.** A staged file that passes the same check and differs from the published one
  is written with `slot_store::atomic_write` (temp file, fsync, rename, directory fsync). A torn or
  missing staged file never replaces or deletes the published one.
- **Flush by reload.** Lid close, POWER, battery critical, the power menu, the 60 s autosave and
  eject already ask the core for its save RAM through the emu thread. For NGP that request first
  serializes, loads the cart again (the core unloads, writing its flash, then reads it back),
  unserializes, and publishes; the game carries on. The emu thread also publishes after the core
  is dropped, which covers quitting slot. If the reload fails the core is stopped, since NeoPop
  cannot run unloaded, and the resume state, which carries the flash, is the copy.

## Consequences

- The flash reaches the card at every flush point slot already has, and a power cut at any moment
  leaves either the old or the new file whole at `Saves/NGP/<stem>.flash`.
- The reload took 0.12 ms on the M5 Max host (fastest of five, a 64 KB generated cart). It runs on
  the emu thread, so the game pauses for that long at each flush; measure it on the RG34XXSP under
  `SLOT_TRACE` (issue 79). A publish costs an fsync, but only when the flash changed.
- Upstream touch points: one token in `open_named` (the save dir), three lines in
  `Session::spawn_core` and `finish_opening`, and in `emu.rs` one `Shared` field, one setter, one call
  in the `Sav` command and one after the core drops. Every one is a no-op for other cores.
- `tools/hacks.py` backs up `Saves/<SYS>/<stem>.flash` with the `.sav` files (ADR 0082).
- On each rebase: rerun `ngp_core.rs` (the core's flash contract) and `ngp_flash.rs`, and re-read
  `flash.c` if the NeoPop pin moves, since the check mirrors its reader.
