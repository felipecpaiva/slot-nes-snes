# 0067. Swap PS1 discs through both disk-control interfaces, remember the disc, and record it in states

- Status: Accepted
- Date: 2026-10-17
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0009](0009-host-struct-untouched.md), [ADR 0063](0063-ps1-in-scope-on-pcsx-rearmed.md), [PS1 plan](../research/ps1-plan.md), [issue 61](../../.github/issues/61-ps1-disk-control.md)

## Context

Multi-disc games need the libretro disk-control interface. pcsx registers the EXT interface (58)
only if the frontend answers GET_DISK_CONTROL_INTERFACE_VERSION (57), and otherwise the legacy
one (13). With EXT, `set_initial_image` makes a game start on the disc it was left on. The forks
differ:

- tray and omega-zero answer 13, 57 and 58 and remember the disc in `Saves/PS1/<stem>.disc`, but
  they do not roll back a refused swap;
- bently answers 13 only, rolls back a refused index and appends the disc index to every state;
- omega-zero's states do not record the disc, so loading a disc 1 state while disc 2 is in plays
  the wrong disc.

## Decision

- Answer 13, 57 (version 1) and 58. The interface lives in `HostExtra` (ADR 0009), never `Host`.
- A swap is: open the tray, set the index, close the tray. If the core refuses, or the index is out
  of range (pcsx holds 8), go back to the previous index and close. A toast says the swap failed.
- The disc in play is written to `Saves/PS1/<stem>.disc` (the index, one line) on every swap,
  and passed to `set_initial_image` before `load_game`. A missing, unreadable or out-of-range file
  means disc 1, logged.
- **State format.** A state of a game with more than one disc gets a trailer after the core's
  bytes: the 8 ASCII bytes `SLOTPSX1` (the `1` is the format version) and the disc index as a
  little-endian u32. On load, slot strips the trailer and swaps to that disc before
  `retro_unserialize`. A state with no trailer loads on the current disc. A trailer with an
  unknown version is refused with a toast. Single-disc states stay exactly the core's bytes.

## Consequences

- A multi-disc state is unreadable by other pcsx frontends unless they strip the last 12 bytes.
  That is the cost of the state carrying its own disc, and it is written down here.
- The swap row needs a menu home. The in-game Screen page is pinned (ADR 0061), so issue 61 picks
  one and asks the maintainer if it needs a new named test site.
- One more `Saves/PS1` file per multi-disc game.
