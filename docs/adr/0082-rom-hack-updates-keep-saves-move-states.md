# 0082. A ROM hack update keeps the name and the battery save, and moves every save state away

- Status: Accepted
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: `tools/hacks.py`, `tools/hacks.json`, [docs/HACKS.md](../HACKS.md); slot code read at patch
  `0051-silent-start-hud`: `crates/slot-store/src/ring.rs`, `crates/slot/src/persist.rs`,
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
- One hack maps to exactly one card file and at most one library file; ambiguity, a clean base game
  as the target, or a name that changed since install refuses, so an update never makes a duplicate.
- A player loses quick access to old states after an update; they are in the backup and come back
  with `--rollback`.
- No slot change is needed. If slot ever keys a file by ROM content or adds a stem-keyed file, the
  list in `card_items` (tools/hacks.py) has to follow; check on each upstream rebase that the state
  and save paths above are unchanged.

## Amendment (2026-10-19): the backups can live off the card

PS1 discs fill the card, and every update keeps a whole old disc in `Backups/hacks/`. A `backups`
setting (in `~/.config/slot-nes-snes/hacks.json`, overridden for one run by `--backups card|DIR`) names
where the backup goes: `card` (the default, the behaviour above) or a mounted folder on the Mac, such as
a backup drive. Off the card the layout is the same, `<DIR>/<SYS>/<stem>/<stamp>_<old version>/` with
the files at their card paths, and the order changes so the old version is never lost:

- every file (old ROM, saves, state folders) is copied from the card to the folder and checked, size
  and CRC32 of the copy against the bytes read from the card; only when all of them check are the old
  ROM and the state folders removed from the card, and only then is the new ROM written;
- a rollback copies the saved files back the same way, each copy checked on the card;
- the folder must be reachable (it is created if missing, then a probe file is written): an unmounted
  drive or a folder that cannot be written refuses the update before anything is written. It never
  falls back to the card on its own; `--backups card` keeps that run's backup on the card.

`hacks-state.json` records each backup's path (relative to the card, or absolute off it), and rollback
looks for the newest update backup on the card, in the configured folder and where the state file says
the last one is, so a backup made before the setting still rolls back. A rollback reads the saved files
from where the backup is now, not from the paths `backup.json` wrote on the day, so a moved backup works.
`--migrate-backups` moves the card's existing `Backups/hacks/` into the folder with the same check
before each removal, and points the state file at the new place.

This replaces "Nothing is deleted" for the off-card case: the card copy of the old version is deleted,
after its copy off the card has checked. On the card nothing changes.
