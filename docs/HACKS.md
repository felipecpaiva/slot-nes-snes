# ROM hack updates (`tools/hacks.py`)

About 25 ROMs on the maintainer's card are hacks that still get new versions. `tools/hacks.py` tells
you which have one, and updates them without losing the battery save or loading an old version's save
state into the new ROM. The rules are in [ADR 0082](adr/0082-rom-hack-updates-keep-saves-move-states.md).
The ~440 GoodTools `[h1]`, `[b1]`, `[T+...]` entries are old and never updated, and are not in the registry.

```sh
python3 tools/hacks.py --library /Volumes/MuOs/ROMS                         # check (default), read only
python3 tools/hacks.py --device --library ~/ROMS                             # only the hacks on the card
python3 tools/hacks.py --device --library ~/ROMS --update pokemon-unbound --dry-run
python3 tools/hacks.py --device --library ~/ROMS --update pokemon-unbound    # prints the plan, asks y/N
python3 tools/hacks.py --device --library ~/ROMS --all --dry-run             # every hack with an update
python3 tools/hacks.py --device --library ~/ROMS --rollback pokemon-unbound
python3 tools/hacks.py --device --library ~/ROMS --add castlevania-2-revamped --dry-run   # a hack not on the card yet
python3 tools/hacks.py --device --init                                       # write your settings file
python3 tools/hacks.py --library /Volumes/MuOs/ROMS --fix-library-zips --dry-run  # unzip updated hacks
```

`--card <root>` works on a mounted card instead of adb. `--yes` skips the question, `--as-version`
names the version of a patch you dropped in by hand. `task hacks:check` and `task hacks:update` run the
same thing with `-- <flags>`.

## The flow

1. **Check** (default, read only). Per hack: the installed version (the state file, else the version
   in the file name, else `unknown`) against the latest:
   - `github:` the GitHub releases API (`/releases/latest`, cached an hour: unauthenticated calls get
     60 an hour). `UPDATE AVAILABLE` when the tag differs from the installed version.
   - `page:` the page is fetched. With a `version_regex` its first group is the latest version;
     otherwise the page's SHA-256 is compared with the first one seen (kept in the cache dir):
     `page baseline recorded`, `page unchanged since ...` or `page changed since ...: look`, with the link.
   - `manual`: just the link.
   With `--library`, a hack whose installed version is unknown (no version in the file name) is
   identified by CRC32: the newest GitHub releases with a matching asset (up to 10, cached) are built
   against the library's base and compared with the installed ROM's CRC (the library copy's, else the
   card's). A match is recorded in `hacks-state.json` as the installed version; no match while the
   latest builds reads `UPDATE AVAILABLE (installed version unknown)`, which `--all` takes. A patch
   waiting in the incoming folder is built the same way: `UPDATE AVAILABLE (from incoming <version>)`,
   or what is installed when the CRCs agree. Nothing is written to the card, the library or the
   settings; only the cache dir and, for an identified version, the state file.
2. **Get the patch.** A `github:` source downloads the one release asset that matches `asset` (cached
   under the cache dir by version). Any other source reads the newest file in
   `~/ROMHacks/incoming/<id>/`: a `.bps`, `.ips` or `.ups`, a ROM, or a `.zip` holding exactly one of
   them (read in memory; a 7z or rar you extract yourself), with an optional `version.txt` naming its
   version (else `--as-version`, else the version in the file name). Nothing downloaded is ever run.
3. **Find the base ROM** in `--library` by the whole file's CRC32 (`base_crc32`, or when it is unknown
   the source CRC a BPS or UPS carries in its footer): zip headers first, then loose files. Missing:
   refused.
4. **Patch in pure Python.** BPS and UPS check the base's CRC, the result's CRC and the patch's own
   CRC. IPS has no checksums, so the entry's `target_crc32` is checked when known, else a warning. A
   pre-patched ROM is checked against `target_crc32` when known. Any mismatch: refused. xdelta
   (VCDIFF, as Delta Patcher and xdelta3 write it: default code table, no secondary compression) is
   applied too, with xdelta's Adler-32 per window checked; it names no base, so `base_crc32` must be set.
5. **Plan and confirm.** Every refusal (not on the card, seated, no base, CRC, already installed)
   happens before the first write. `--dry-run` prints the plan and stops; a real run prints it and asks.
6. **Card.** Into `Backups/hacks/<SYS>/<stem>/<stamp>_<old version>/`, at the same card paths:
   `backup.json` (what is where), the battery saves copied (`Saves/<SYS>/<stem>.sav`, `.srm`, PS1
   `.disc`), every `States/<SYS>/<core>/<stem>/` folder moved (all cores: GBA can have both `mgba` and
   `gpsp`), the old ROM moved. Then the new ROM is written under the same name.
7. **Library** (the muOS card mounted on the Mac): only the ROM changes. The old file, loose or
   zipped, is moved to `~/ROMHacks/backups/<SYS>/<stem>/<label>/` (outside `ROMS/`, so muOS never lists
   a backup as a game) and the new ROM goes in loose, since slot reads no zip and the library is what
   gets pushed to the slot card: a loose copy keeps its name, a zip comes back as its member's name
   (`Pokemon - Modern Emerald (v2.3.3).zip` holding `Modern Emerald (v2.3.3).gba` becomes the latter),
   and the state file records the new name. If that loose name already exists, the update refuses: a
   zip and a loose copy of one hack never sit side by side. muOS keys RetroArch's saves by the file
   name, so a note lists any `.srm`/`.state*` left under the zip's name. RetroArch's own
   `<stem>.state*` and `.srm` files there are left alone: that card belongs to muOS. A one-line note
   says its old states may not work with the new version.
8. **Record** the new version, CRC32, date and backup paths in
   `~/.config/slot-nes-snes/hacks-state.json`.

If a card step fails partway (a full card, a lost adb link) the tool says which ops ran and stops; the
backup's `backup.json` is written first, so `--rollback <id>` puts the old files back. The state file is
written as soon as the card is done, so a library failure afterwards is only a warning. A card written
from a Mac may spell names in NFD (`Pokémon`); names are compared in NFC and the card's own spelling is used.

`--fix-library-zips` (try `--dry-run` first; needs only `--library`) converts hacks updated before the
tool unzipped: every hack the state file says this tool updated (it has a `backup`) whose library copy
is still a zip holding the installed CRC32 is unzipped the same way, the zip moved to a `<stamp>_unzip`
backup (kind `unzip`, which `--rollback` skips, so a rollback still restores the update's old file). A
zip holding another CRC is refused. The card is not touched.

`--rollback <id>` moves the current ROM, saves and states into a new `<stamp>_rollback` backup and
copies the newest update backup back, on the card and in the library. Nothing is ever deleted.

## Adding a hack that is not on the card yet

`--add <id>` (try `--dry-run` first; needs `--card`/`--device` and `--library`) installs a registry hack
the card does not have: the patch from `~/ROMHacks/incoming/<id>/` (or the GitHub release) is applied to
the clean base found in the library by CRC32, exactly as an update builds it, and the result is written
as a NEW loose file named `card` (in the library, `library` if set, else the same name) on the card and
in the library. The base game is only read. It refuses, before any write, when the state file already
has the hack, when the card or library already holds that name, another version of it (the same name
once version numbers are dropped) or the patched CRC32 (library: every file and zip header; card: every
file of the same size), or when the result is a clean base game. The state file then records it like
an update, so `--check` and `--update` handle it from then on.

## One file per hack, never a duplicate

- Each hack updates exactly one card file (`card`, compared in NFC since a Mac-written card can spell
  names in NFD) and at most one library file (`library` if set, else the copy, loose or zipped, whose
  ROM has the card's stem). None on the card: "not on the card". Two candidates: refused with the list
  ("ambiguous: set `card`/`library` in your settings file"). Never a guess.
- The update replaces that file in place, under the same name (a library zip is swapped for its loose
  member, see step 7). It adds no file to `Games/<SYS>/` or the library and never leaves the old and
  new versions side by side; the old one goes only to the backup.
- A clean base game (any registry `base_crc32`, e.g. Emerald, FireRed 1.0, Mother 3 (Japan)) is never
  a target: if the card or library file resolves to one, the update refuses.
- `--check` warns about files that look like another version of a registry hack (the same name once
  version numbers are dropped, e.g. `Sonic 3 Delta v0.1.bin` next to `v0.1a.bin`). It only warns.
- The card and library file names are recorded at install. If they later differ (a rename, a new
  `card`/`library` setting), the update refuses until you rerun with `--accept-rename`.

## Save and state rules, and why

- **Same file name.** slot keys the save, the states, the label, `cart_shell.txt`, `video_mode.txt`,
  `selected_core.txt`, favourites, recents, `shelf_carts.txt` and the `shelf_cart=` line by the ROM's
  stem. Keeping the name keeps all of them; nothing in `Config/` is edited.
- **The battery save stays.** It is the game's own format; most hacks keep it across versions and
  say so. When the registry says `saves_carry_over: "no"` the `.sav` still stays (and is backed up) with
  a loud warning: the new version may refuse it or start a new game, and you decide.
- **Every save state moves out.** A state is a snapshot of the whole machine made against one ROM;
  loaded into another version it can crash or corrupt the game. `resume.state` loads by itself when
  the game is seated, so it goes too. They are in the backup and come back with `--rollback`.
- **A seated game is refused.** `Config/slot.state` holds `cart=<stem>` and `cart_platform=<system>`
  while a game is in the slot; eject it first, so slot does not resume it with an old state.

## Settings: the registry

`tools/hacks.json` is the researched seed, shipped in the repo. Your own
`~/.config/slot-nes-snes/hacks.json` (next to `screenscraper.env`) is read on top of it: an entry with
a seed id overrides just the fields it gives, a new id adds a hack (it needs `system`, `card` and
`source`), an unknown field or an override for an id that is not in the seed is ignored with a warning.
Both are JSON with whole-line `//` comments (the repo's Python is 3.9, which has no `tomllib`). What
is installed lives in `hacks-state.json`, never in your settings, so the file stays hand-written and
diffable. `--init` writes a commented example (the seed hacks found on the card as commented override
lines, and the card's other hack-looking files, by a version number or `hack` in the name, as new
entries with a blank source); it never overwrites an existing file.

| Field | Meaning |
|---|---|
| id (the key) | stable id, e.g. `pokemon-unbound`; used by `--update`, `--rollback`, the incoming folder, the state file |
| `name` | display name |
| `system` | `GBA`, `GB`, `GBC`, `NES`, `SNES`, `GG`, `SMS`, `MD` or `PS1` (the card's `Games/<SYS>/`) |
| `card` | the ROM's file name on the card, extension included |
| `library` | the file name in the library's system folder (loose or `.zip`), when the card stem alone would match several |
| `source` | `github:<owner>/<repo>` (release assets), `page:<url>` (a forum or site page), `manual` or `manual:<url>`, or `""` (not known yet) |
| `asset` | glob for the release asset (`github:` only), e.g. `*.bps`; it must match exactly one asset |
| `version_regex` | `page:` only: a regex whose first group is the latest version on the page |
| `format` | `bps`, `ips`, `ups`, `xdelta`, `rom` (a pre-patched ROM) or `unknown`; informational, the patch's magic decides |
| `base_name`, `base_crc32` | No-Intro name and CRC32 of the clean ROM the patch applies to |
| `target_crc32` | CRC32 of the patched ROM, when the author publishes it (the only check an IPS gets) |
| `saves_carry_over` | `yes`, `no` or `unknown`, from the release notes |
| `status` | `maintained`, `finished`, `dormant`, `dead` or `no primary source` (informational) |
| `save_note`, `latest_known`, `home`, `cite`, `notes` | the research: what the notes say, the version seen, the home page, the source URLs |

A full user file:

```json
// ~/.config/slot-nes-snes/hacks.json
{
  // override two fields of a seed entry
  "pokemon-unbound": {"source": "page:https://www.pokecommunity.com/threads/pok%C3%A9mon-unbound-completed.382178/",
                      "version_regex": "Unbound v?([0-9][0-9.]+)"},
  // add a hack the seed does not know
  "sonic-fan-remix": {
    "name": "Sonic Fan Remix",
    "system": "MD",
    "card": "Sonic Fan Remix v3.1.bin",
    "source": "github:someone/sonic-fan-remix",
    "asset": "*.bps",
    "format": "bps",
    "base_name": "Sonic The Hedgehog (USA, Europe)",
    "base_crc32": "F9394E97",
    "saves_carry_over": "unknown",
    "cite": ["https://github.com/someone/sonic-fan-remix/releases"]
  }
}
```

## The seed

Researched 2026-10-18; every entry cites its sources in `tools/hacks.json`. Unknown stays unknown.

| id | system | status | latest seen | source | format | base | saves carry over |
|---|---|---|---|---|---|---|---|
| `pokemon-unbound` | GBA | finished | 2.1.1.1 (2022-11-08) | `page` | bps | DD88761C | unknown |
| `pokemon-radical-red` | GBA | maintained | 4.1 (2024-03-22) | `page` | ups | DD88761C | yes |
| `pokemon-inclement-emerald` | GBA | dormant | 1.13 (2021-11-28) | `github` | xdelta | 1F1C08FB | yes |
| `pokemon-modern-emerald` | GBA | maintained | Release3.6 (2026-10-05) | `github` | bps | 1F1C08FB | yes |
| `pokemon-lazarus` | GBA | maintained | 2.0 (about 2026-02) | `manual` | bps | 1F1C08FB | yes |
| `pokemon-emerald-imperium` | GBA | maintained | 1.3.1 (2025-09-04) | `page` | bps | 1F1C08FB | unknown |
| `pokemon-hyper-emerald` | GBA | no primary source | 5.7 Lost Artifacts (secondary sites) | `manual` | rom | unknown | unknown |
| `pokemon-hyper-emerald-lost-artifacts` | GBA | no primary source | 5.7 (secondary sites) | `manual` | rom | unknown | unknown |
| `pokemon-parallel-emerald` | GBA | dormant | 1.2 (2024-03-13) | `page` | ups | 1F1C08FB | unknown |
| `mother-3` | GBA | finished | 1.3 (2021-04-20) | `page` | ups | 42AC9CB9 | yes |
| `castlevania-aos-definitive` | GBA | dead | 1.0 (2024-10-07) | `page` | unknown | unknown | unknown |
| `pokemon-elite-redux` | GBA | maintained | 2.65 Beta 2 (2026-03-08); stable 2.5 Hotfix 2 (2025-04-03) | `page` | unknown | 1F1C08FB | unknown |
| `pokemon-emerald-horizons` | GBA | maintained | 1.16 (first post edited 2025-10-09) | `page` | unknown | 1F1C08FB | unknown |
| `pokemon-pisces` | GBA | maintained | 1.5.4 (2025-12-14) | `page` | bps | unknown | unknown |
| `pokemon-emerald-genesis` | GBA | dead | Beta 2.1 (2020) | `page` | unknown | unknown | unknown |
| `pokemon-emerald-z` | GBA | finished | 1.2.0 (2024-03-10) | `page` | unknown | unknown | yes |
| `pokemon-evolved` | GBA | dead | 1.0 (2025-03-26) | `page` | ips | DAFFECEC | unknown |
| `pokemon-prism` | GBC | maintained | 0.95.0254 Hotfix 5 (2023-08-24) | `page` | unknown | unknown | unknown |
| `sonic-3d-blast-directors-cut` | MD | finished | final (2017-12-24) | `page` | xdelta | 44A2CA44 | unknown |
| `sonic-2-delta-ultimate` | MD | maintained | 1.12 (2025-06-01) | `page` | rom | unknown | unknown |
| `sonic-3-delta` | MD | dead | 0.1a (2002-11-29) | `page` | rom | unknown | unknown |
| `s2k-long` | MD | dead | 1.8.1 / 1.10 (2004-10-22) | `page` | unknown | unknown | unknown |
| `s2smtp` | MD | dead | 0.5 (2008) | `page` | rom | unknown | unknown |

Left out: `Sonic 2 remix`, `Sonic 2 mecha world`, `Sonic 2 GHZ v0.2`, `Knuckles in Sonic 2 GHZ v0.1`,
`sonic 2 salus` and `Sonic 2 haz` (not identified anywhere searched; add them in your settings if you
find their home; searched 2026-10-18 on Sonic Retro, SHC and the web with no result, so treat them as
dead), and the GoodTools-tagged hacks. Pokemon Unbound and Radical Red need FireRed 1.0 (DD88761C,
'1636 Squirrels'): Radical Red's thread names that dump and its patch is a UPS, which checks the source
CRC, and Unbound's thread names none, and its patch (a BPS, per community guides) checks its own source CRC too. FireRed Rev 1
(84EE4776) is refused by both, so their updates wait until a 1.0 dump is in the library.

### Not on the card yet: Metroid and Castlevania (`--add <id>`)

Researched 2026-10-18 (Metroid Construction, romhacking.net, the authors' GitHub and pages). The
downloaded patches wait in `~/ROMHacks/incoming/<id>/`; romhacking.net blocks scripts, so the rows
marked manual need the patch fetched by hand. PS1 disc hacks (SotN, Chronicles) are left out: the
tool cannot patch a disc image.

| id | system | kind | latest seen | format | base | patch |
|---|---|---|---|---|---|---|
| `metroid-mother` | NES | QoL / definitive | 1.0 (2014-04-22) | ips | A2C89CB9 | incoming |
| `metroid-rogue-dawn` | NES | New game (a prequel, play as Dawn Aran) | 1.21 (2017-03-20) | ips | A2C89CB9 | incoming |
| `junkoid` | NES | New game | 1.1 (2022-02-22) | ips | A2C89CB9 | incoming |
| `metroid-fusion-special-edition` | GBA | QoL / definitive | 4.2 (2021-08-29) | ips | 6C75479C | incoming |
| `metroid-oil-spill` | GBA | New game (nonlinear Fusion hack) | 1.5 (2020-03-16) | ips | 6C75479C | incoming |
| `project-zm` | GBA | QoL / definitive (vanilla+) | 0.8.3 (2022-07-10, still WIP) | ips | 5C61A844 | incoming |
| `metroid-scrolls-6` | GBA | New game | 1.1 (2021-02-10) | ips | 5C61A844 | incoming |
| `metroid-dive` | GBA | New game | 1.2 (2026-08-02) | bps | 5C61A844 | incoming |
| `metroid-ii-ejrtq-colorization` | GBC | QoL / definitive | 1.3 (2019-03-01) | ips | DEE05370 | base missing |
| `castlevania-1-improved-controls` | NES | QoL | 3.1 (2021-02-27) | ips | 39C879BB | incoming |
| `castlevania-1-chorus-of-mysteries` | NES | New game | 1.1 (2007) | ips | 12A6CB14 | base missing |
| `castlevania-2-retranslation` | NES | QoL / definitive | 2.12.1.1 (2022-06-02) | ups | A9C2C503 | incoming |
| `castlevania-2-improved-controls` | NES | QoL | 2.0 (2026-07-15) | ips | A9C2C503 | incoming |
| `castlevania-3-redux` | NES | QoL / rebalance | 2.6 (2026-08-21) | ips | 7CC9C669 | manual |
| `castlevania-3-improved-controls` | NES | QoL | 2.1 (2025-06-20) | ips | 7CC9C669 | incoming |
| `castlevania-3-color-bugfixes` | NES | Small fix | 1.0 (2005) | ips | 7CC9C669 | incoming |
| `super-castlevania-4-uncensored` | SNES | Definitive | 2.1 (2021-12-06) | ips | B64FFB12 | manual |
| `castlevania-dracula-x-r-button-subweapon` | SNES | QoL | 1.0.0 (2026-05-15) | bps | 7C4887E1 | incoming |
| `castlevania-bloodlines-revised` | MD | QoL / definitive | 1.0 (updated 2024-06-30) | ips | FB1EA6DF | manual |
| `castlevania-bloodlines-enhanced-colors` | MD | Graphics | 1.0 (2014) | ips | FB1EA6DF | incoming |
| `castlevania-circle-of-the-moon-definitive-edition` | GBA | QoL / definitive | 1.1 (GitHub, 2024-11); romhacking.net 9010 says 1.0 (2025-05) | ips | 1CC059A4 | incoming |
| `castlevania-hod-findesiecle` | GBA | Rebalance / definitive | 2.3.75 (2023-02-26) | ips | 88C1B562 | manual |
