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

## Amendment (2026-10-17, issue 61 build)

- **Swap home: SELECT+L2, the next disc, on PlayStation only.** The in-game Screen page and the
  in-game menu lists (`QuickRow::PLAY`, `PLAY_SCREEN`) are pinned by upstream tests, so a menu row
  would need a new named test site. A chord needs none. L2 and R2 belong to the game (ADR 0068),
  SELECT+L1 and SELECT+R1 are load and save, SELECT+R2 is fast-forward, and SELECT+L2 was the
  palette step back, which PS1 has no use for. Every other system keeps SELECT+L2 as before. A menu
  row can replace the chord later if the maintainer adds a test site for it.
- The swap result is a banner: "Disc 2" after a swap, "Disc swap failed" after a rollback, and
  "State needs a newer slot" for a trailer of an unknown version.
- `Saves/PS1/<stem>.disc` holds the 0-based index on one line. A state load that swaps the disc
  writes it too.
- The pinned pcsx records its own disc in its state (`CdromFrontendId` in `retro_serialize`) and
  swaps back on `retro_unserialize`, so a state with no trailer already returns to its disc on this
  core. The trailer stays as decided: it keeps the disc in the state whatever the core does, and
  slot swaps only when the trailer's disc is not the one in play, so the tray never moves for a
  state of the current disc.
- The three calls are answered for every core, because pcsx asks in `retro_init`, before slot knows
  the platform. Genesis Plus GX registers the legacy interface for Sega CD; it is stored and never
  used. Every disc call (count, index, swap, the initial disc, the trailer on save and on load)
  first checks a `HostExtra` flag that `open_named` sets only where `Platform::swaps_discs` is
  true, today PlayStation alone.

