# 0082. A ROM hack update keeps the name and the battery save, and moves every save state away

- Status: Accepted
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: `tools/hacks.py`, `tools/hacks.json`, [docs/HACKS.md](../HACKS.md); slot code read at patch
  `0052-silent-start-hud`: `crates/slot-store/src/ring.rs`, `crates/slot/src/persist.rs`,
  `crates/slot/src/ps1_load.rs`, `crates/slot-store/src/slot_state.rs`, `crates/slot-store/src/shelf_carts.rs`

## Context

About 25 ROMs on the card are hacks that still get new versions (Pokemon Unbound, Radical Red, Mother 3's
translation, the Sonic hacks). Updating one by hand risks three things:

- slot keys almost everything by the ROM's file stem: `Saves/<SYS>/<stem>.sav` (or `.srm`),
  `States/<SYS>/<core>/<stem>/` (the ring of `<stamp>.state` + `<stamp>.png`, `resume.state`,
  `resume-refused-*.state`), `Labels/<SYS>/<stem>.png`, `Config/cart_shell.txt`, `video_mode.txt`,
  `selected_core.txt`, `recents.txt`, `favorites.txt`, `shelf_carts.txt` and the `shelf_cart=` line.
  A new file name orphans all of it.
- A save state is a snapshot of the whole machine, RAM and all, made against one ROM. Loaded into
  another version it can crash or quietly corrupt the game, and the resume state loads by itself when
  the game is seated. A battery save is the game's own format, and hacks usually say whether it carries.
- `Config/slot.state` keeps the seated game as `cart=<stem>` and `cart_platform=<system>`. Swapping
  the ROM under a seated cart means slot resumes it with a state from the old ROM.

## Decision

The tool installs the new ROM under the same file name, leaves the `.sav`/`.srm` in place (and copies
it into the backup), and moves every state folder of that game, for every core, including the resume
state, into `Backups/hacks/<SYS>/<stem>/<stamp>_<old version>/`, along with the old ROM. It refuses
while the game is seated, and refuses on any CRC mismatch, before it writes anything. When the
registry says saves do not carry over, the `.sav` still stays (the user decides) with a loud warning.
Nothing is deleted: rollback moves the current files into a new backup and copies the old ones back.
The library copy (the muOS card mounted on the Mac) gets only its ROM replaced, with the old ROM backed
up outside `ROMS/`. Its RetroArch `.state*` and `.srm` files are muOS's and are left alone, with a note
that old states there may not load: only the slot card's states are moved aside.

## Consequences

- Labels, cart shells, favourites, recents and shelf memory stay attached with no edit to any Config file.
- A player loses quick access to old states after an update; they are in the backup and come back
  with `--rollback`.
- No slot change is needed. If slot ever keys a file by ROM content or adds a stem-keyed file, the
  list in `card_items` (tools/hacks.py) has to follow; check on each upstream rebase that the state
  and save paths above are unchanged.
