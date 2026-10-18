# Per-game cheats for slot-nes-snes: feasibility research

Date: 2026-10-18. Read-only research; no repo was edited. Question from the maintainer: "how difficult will it be to bake in cheats per game with the cheat database".

## Short answer

**Medium. About 3 to 4 weeks of part-time work for the full feature (roughly 15 to 22 dev days), or about 1.5 weeks for a useful first cut.** The database is free to use (CC BY-SA 4.0) and every core we ship except mednafen_ngp already applies cheats. Most of the work is frontend: a list screen, saving the on/off choices, a Mac tool that copies the right file, and per-core code handling.

The real blockers are not technical difficulty:

1. **Policy.** PLAN.md lists cheats as a non-goal (PLAN.md:58, "people who want RetroArch breadth: netplay, cheats, ..."), and slot-forks.md:205 skips the three cheat forks for that reason. Changing it needs an ADR plus a PLAN.md changelog row.
2. **Upstream declined, so this is fork-only.** Upstream issue [#8 "Cheats"](https://github.com/BrandonKowalski/slot/issues/8) was closed by the owner: "It simply isn't a feature I want to provide support for nor troubleshoot." The site FAQ says the same (upstream `site/index.html:611`). Upstream-first (ADR 0047) does not apply. Every line is our rebase cost.
3. **Core quirks that crash or misbehave unless the frontend works around them.** snes9x and nestopia `strcpy` the code into a 256-byte stack buffer, and the database has 14 SNES and 11 NES codes longer than that. snes9x2005_plus does not split multi-part codes. mGBA ignores `enabled`. gpsp holds at most 20 cheats. Details in Q2.
4. **Pinned upstream tests.** The in-game pages `QuickRow::PLAY`, `SETTINGS` and `GAME` are pinned row for row by upstream tests (`crates/slot-ui/tests/quick_menu.rs:127`, `:307-333`). An in-game "Cheats" row means one new named test site (ADR 0013 asks for approval), or else a different entry point.
5. **Matching coverage is partial.** On the maintainer's library (`/Volumes/MuOs/ROMS`), exact CRC matching finds cheats for 17% (GBA) to 72% (Game Gear) of ROMs. ROM hacks get essentially nothing (1 of 501).

## Q1. The database

### libretro-database `cht/`

- Source: <https://github.com/libretro/libretro-database/tree/master/cht>. Sparse clone on 2026-10-18 (`git sparse-checkout set cht`).
- **Licence: CC BY-SA 4.0** (repo `LICENSE`, "Attribution-ShareAlike 4.0 International"). Bundling the files requires attribution and keeping the same licence on those files. The README says the codes are "collected from any available source on the web", so provenance is mixed. That is one more reason not to redistribute them in our zip (see Q4).
- Format (RetroArch): `cheats = N`, then `cheatN_desc`, `cheatN_code`, `cheatN_enable` per entry. A multi-part code joins its parts with `+`, e.g. `"7E00A841+7E00AA41"` (SNES PAR) or `"83004AAC+E0FF+83004AAE+05F5"` (GBA Code Breaker pairs).
- File naming: one file per game, named after the **No-Intro name** (Redump-style names for PS1). The code device is often a suffix, e.g. `3 Ninjas Kick Back (USA) (Action Replay).cht` next to `3 Ninjas Kick Back (USA).cht`, so one game can have 2 or 3 files.
- Junk to filter out: entries with an empty code (blank separators; Pokemon Crystal alone has 7,539 of them), `??` or `XX` wildcard templates that need a user-entered value, `(Rumbles)` files (RetroArch rumble-on-memory-change), and RetroArch `cheatN_handler = 1` entries (RetroArch's own RAM engine: `address`/`value` fields, empty `code`).

### Coverage per system (our systems)

Counted on the 2026-10-18 checkout with a Python scan. "Games" means file names with the device suffix dropped. "Usable" means a non-empty code with no wildcard.

| System | cht folder | Files | Games | Entries | Usable codes | Empty | Wildcard | Bytes | Main code formats seen |
|---|---|---|---|---|---|---|---|---|---|
| GBA | Nintendo - Game Boy Advance | 513 | 512 | 7,015 | 6,898 | 2 | 115 | 717 KB | Code Breaker `XXXXXXXX+YYYY` (485 files suffixed "(Code Breaker)"), some GameShark/AR `8+8` |
| GB | Nintendo - Game Boy | 1,496 | 1,039 | 17,516 | 16,678 | 667 | 171 | 1.59 MB | GameShark `01VVAAAA` (8 hex), Game Genie `XXX-XXX(-XXX)`, Xploder |
| GBC | Nintendo - Game Boy Color | 960 | 729 | 26,865 | 9,072 | 17,590 | 203 | 2.15 MB | as GB; 594 `$XXXXXXXX` (Xploder-style) |
| NES | Nintendo - Nintendo Entertainment System | 2,262 | 1,913 | 44,504 | 42,471 | 817 | 1,216 | 4.30 MB | Game Genie 6/8 letters (27.7k), raw `AAAA:VV` (15.9k), PAR |
| SNES | Nintendo - Super Nintendo Entertainment System | 2,773 | 2,094 | 77,975 | 67,267 | 9,878 | 830 | 7.68 MB | PAR `AAAAAAVV` 8 hex (40k), Game Genie `XXXX-XXXX` (26.7k) |
| Game Gear | Sega - Game Gear | 818 | 566 | 7,284 | 7,168 | 10 | 106 | 678 KB | Game Genie `XXX-XXX(-XXX)`, Action Replay `00AA-AAVV` |
| Master System | Sega - Master System - Mark III | 724 | 645 | 4,747 | 4,495 | 68 | 184 | 453 KB | Action Replay `00AA-AAVV`, Game Genie |
| Mega Drive | Sega - Mega Drive - Genesis | 2,094 | 1,684 | 38,551 | 36,314 | 993 | 1,244 | 3.92 MB | Game Genie `XXXX-XXXX` (24.3k), PAR raw `AAAAAA:VVVV` (12.3k), 550 `AAAAAA:VV` |
| PS1 | Sony - PlayStation | 1,961 | 1,929 | 22,143 | 18,470 | 0 | 3,673 | 2.32 MB | GameShark `AAAAAAAA+VVVV` (pairs, up to 316 parts), Xploder, Game Buster |
| NGP | SNK - Neo Geo Pocket | 5 | 5 | 19 | 0 | 0 | 19 | 1.6 KB | `AAAA:??` templates only |
| NGPC | SNK - Neo Geo Pocket Color | 29 | 29 | 129 | 91 | 0 | 38 | 11 KB | raw `AAAA:VV` RAM writes |

Total for our 11 folders: about 13,600 files and 23.8 MB of text. RetroArch `handler` entries in our folders (RAM-engine only, unsupported in v1): SNES 716, MD 177, NES 123, SMS 44, PS1 12, mostly inside `(Rumbles)` files.

Longest single entries: PS1 2,211 characters (95 entries over 255), GBA 699 (13 over 255), SNES 602 (14), GBC 575 (2), MD 479 (18), NES 458 (11), SMS 299 (1), GG 143 (0). Up to 316 `+`-joined parts per entry (PS1).

### Matching games to files

We already map ROM to No-Intro name by CRC in `tools/fetch-labels.py` (the `Dat` class around line 198, `Rom.crcs()` at lines 512 to 524, which strips an iNES header, a 512-byte SNES copier header and de-interleaves SMD). The cht file name is the No-Intro name, so the chain is **CRC -> No-Intro name -> `<name>.cht` (plus suffixed variants)**.

One wrinkle: the cht names lag current No-Intro naming. Master System is the clearest case: the dat now says `Ace of Aces (Europe, Brazil) (En)`, the cht file says `Ace of Aces (Europe, Brazil)`. Dropping language tags such as `(En)` or `(En,Ja)` before comparing is safe, since they do not change the ROM. It raises SMS from 24% to 64%.

Measured on the maintainer's library card `/Volumes/MuOs/ROMS` (zip CRCs read from the zip directory, `fetch-labels.py`'s `Rom.crcs()` for headers, language tags normalised):

| System | ROMs | CRC-exact match (recommended default) | File-name-exact match | Title-only match (tags dropped; upper bound, unsafe) |
|---|---|---|---|---|
| GBA | 1,203 | 214 (17%) | 50 | 510 (41%) |
| GBC | 1,301 | 741 (56%) | 273 | 815 (62%) |
| NES | 1,960 | 1,036 (52%) | 535 | 1,080 (54%) |
| SNES | 1,661 | 594 (35%) | 609 | 902 (54%) |
| Game Gear | 586 | 426 (72%) | 214 | 455 (77%) |
| Master System | 418 | 269 (64%) | 277 | 306 (73%) |
| Mega Drive | 2,146 | 966 (45%) | 849 | 1,499 (69%) |
| PS1 | 259 discs | n/a (no CRC key, see below) | 26 (10%) | 186 (72%) |
| NGP/NGPC | 41 | n/a | 16 | 21 |

ROM hacks: of 501 ROMs tagged as hacks (`[h`, "hack"), 1 matched (an MD one). The SNES list includes 231 hacks.

PS1 has no CRC key in the cht set. fetch-labels already reads the disc serial (`iso_serial`, `pbp_serial`), but no cht file carries a serial, and the cht names are a mix of Redump names (`(USA)`) and older names (`(USA, Europe)`). A serial -> Redump name step (libretro-database `metadat/redump/Sony - PlayStation.dat` has serials) then a title-key match with region agreement is the realistic path. Expect only about 10% exact hits, and treat the rest as by-name matches.

### Alternatives

- **GameHacking.org** (<https://gamehacking.org/>, checked in the browser; WebFetch gets 403). It is the largest curated set (the home page says it is "the official source of cheats for the MiSTer community"), converts between code formats and exports RetroArch files per game. **No open licence is stated.** Bulk use is arranged by asking them on their Discord ("Join our Discord to inquire how ... your project can benefit"). Use it per game through the user's own downloads, or after written permission. Do not scrape it.
- RetroArch's newer `cht` updates come from the same libretro repo, so there is no separate source.

## Q2. Applying cheats in the cores

The API is `retro_cheat_reset(void)` and `retro_cheat_set(unsigned index, bool enabled, const char *code)`. slot does not bind either symbol today: `crates/slot-retro/src/ffi.rs:149-202` (patched v1.7.0 tree in `build/slot`) resolves `retro_init` through `retro_get_memory_size` only. All our cores export both symbols (mednafen_ngp as stubs), so binding them is small, but they should be **optional** symbols, as Slop does (`slop crates/slot-retro/src/ffi.rs:172-211`). That keeps a core without them as "no cheats" rather than "fails to load".

The one safe calling pattern for every core is RetroArch's: **`retro_cheat_reset()`, then `retro_cheat_set(i, true, code)` for each enabled cheat with contiguous i from 0, after the game is loaded, on the emu thread.** Disabling a cheat means reset and re-add the others. Never call either function when no cheat is enabled. That last rule is the GBA byte-identical invariant.

### Per-core support table (pinned commits)

Sources: vendor tarballs in `slot-nes-snes/vendor/*-src.tar.gz` at the `SLOT_PIN` commits. mGBA and gpSP at upstream slot's `MGBA_COMMIT e31759b` and `GPSP_COMMIT 7b2dd37` (`build/slot/taskfile.yml:6-7`). pcsx_rearmed at `c881679`. mednafen_ngp is not pinned yet, so this is beetle-ngp-libretro HEAD `a50d5ac`.

| System(s) | Core (default first, ADR 0002) | retro_cheat_set | Formats accepted | Splits `+` itself | Honours `enabled` / `index` | Limits and hazards | Citation |
|---|---|---|---|---|---|---|---|
| NES | **fceumm** | yes | raw `AAAA:VV`, `AAAA?CC:VV`, Game Genie 6/8, PAR | yes (`+,;._ ` separators) | no / no (every call adds) | copies into 1024 bytes with `strlcpy`, so longer codes are silently truncated; zero-page writes use RAM-cheat mode | `src/drivers/libretro/libretro.c:3469-3538` |
| NES | nestopia | yes | raw `AAAA:VV`, `AAAA?CC:VV`, Game Genie, Pro Action Rocky | yes | no / no | **`strcpy` into `char[256]`: stack overflow on the 11 NES entries over 255 chars** | `libretro/libretro.cpp:2446-2489` |
| SNES | **snes9x** | yes | Game Genie `XXXX-XXXX`, PAR 8 hex, `AAAAAA:VV` converted to PAR, `addr = val (? cmp)` | yes (`+,.; `) | yes / no | **`strcpy` into `char[256]`: overflow on 14 SNES entries**; applied per frame in `S9xUpdateCheatsInMemory` (`gfx.cpp:249`) | `libretro/libretro.cpp:1234-1270`, parsers `cheats2.cpp:349-430` |
| SNES | snes9x2005_plus | yes | Game Genie, PAR, GoldFinger | **no**: one code per call, so all 14,593 multi-part SNES entries fail unless the frontend splits them | yes / **yes, must be contiguous** (`index > num_cheats` is ignored) | `Cheat.c[MAX_CHEATS]` with `MAX_CHEATS 800` and **no upper bound check**: index 800 writes past the array | `libretro.c:982-1012`, `source/cheats.h:7` |
| GG, SMS, MD | **genesis_plus_gx** | yes | MD: Game Genie `XXXX-XXXX`, PAR/patch `AAAAAA:VVVV`. SMS/GG: Game Genie `XXX-XXX(-XXX)`, Action Replay `00AA-AAVV`, Fusion RAM `AAAA:VV` | yes (`+` only) | yes / no (dedupes on address+data) | `strncpy(...,255)` truncates silently; `MAX_CHEATS 150` total; clears and re-applies ROM patches on every call; `AAAAAA:VV` (550 MD entries) decodes the 2 digits as the high byte of a 16-bit value, so verify before trusting it | `libretro/libretro.c:171`, `:2293-2470`, `:3357-3411` |
| GBA | **mgba** (upstream default) | yes | GBA: autodetect (GameShark, Action Replay incl. encrypted, Code Breaker, PAR v3); GB/GBC: GameShark, Game Genie, VBA | yes (spaces or `+`, regrouped into `8 8` or `8 4` lines) | **no / no** (`UNUSED(index); UNUSED(enabled)`) | none found; frontend must reset and re-add | `src/platform/libretro/libretro.c:2174-2236` |
| GB, GBC | mgba | (as above, GB branch) | GameShark 8 hex, Game Genie `XXX-XXX(-XXX)` | yes | no / no | `$XXXXXXXX` entries (271 GB, 594 GBC) are unverified against the GB parser | same, GB branch |
| GBA | gpsp | yes | **Code Breaker only**, unencrypted | yes (non-hex chars become spaces, read as `8 4` pairs) | yes (`cheat_disable(index)`) / yes | `MAX_CHEATS 20`, `MAX_CHEAT_CODES 64` per cheat, 1023-char limit; GameShark/AR give "Cheat type is not supported!" | `libretro/libretro.c:864-900`, `cheats.c:229-290`, `cheats.h:23-24` |
| PS1 | **pcsx_rearmed** | yes | GameShark/PCSX raw (`80` const16, `30` const8, `D0`/`E0` conditionals, `50` slide, `C2` memcpy, inc/dec) | yes (any non-hex char) | yes / **yes**: `index < NumCheats` edits, otherwise adds, so indices must be contiguous | `strdup`, no length limit; applied every `EmuUpdate` (`libpcsxcore/psxcommon.c:51`) | `frontend/libretro.c:1365-1410`, `libpcsxcore/cheat.h:106-126` |
| NGP (planned) | mednafen_ngp | **stub** (empty bodies) | none | n/a | n/a | needs a frontend RAM poke; core exposes `RETRO_MEMORY_SYSTEM_RAM` = 16 KiB `CPUExRAM` | `libretro.c:778-793` |

Note: RetroGame66's CHANGES.md says "gpSP exports neither" cheat symbol. That is not true at our gpsp pin (`libretro/libretro.c:864-869`).

### What slot must do per core (the "code dispatcher")

- **NES, SNES and Sega cores:** split the entry on `+` in the frontend and send each part as its own `retro_cheat_set` with the next contiguous index. That fixes snes9x2005_plus (no split), removes the 256-byte overflow in snes9x and nestopia (each part is at most 11 chars), and costs nothing on fceumm and genesis_plus_gx. Cap the total below each core's limit (snes9x2005_plus 800, genesis_plus_gx 150) and refuse the rest with a toast.
- **GBA, GB, GBC (mgba/gpsp) and PS1:** send the whole entry. Splitting would break the `8+4` and `8+8` pairs. Guard length: refuse entries of 1024 chars or more on gpsp, and cap at 20 enabled cheats on gpsp. Code Breaker files work on both GBA cores. GameShark/AR GBA files work on mgba only, so show "needs mGBA" instead of failing silently.
- **Refuse templates:** codes with `?` or `X` placeholders, empty codes and `handler` entries are not listed in v1.

### A frontend RAM-poke engine: needed?

Only for mednafen_ngp (the 91 usable NGPC codes are raw `AAAA:VV`) and RetroArch `handler` entries. It means writing `retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM)[addr] = val` after every `retro_run`, plus compare variants. That is size M: about 150 lines and tests, but it needs per-system address maps (NGPC cht addresses are offsets into the 16 KiB work RAM at 0x4000). **Defer.** No other core needs it.

### Interaction with other features

- **Save states and rewind:** none of these cores serialize their cheat list. RAM cheats (snes9x, pcsx, mgba, gpsp, genesis RAM patches) re-assert on the next frame after `retro_unserialize`. ROM-patch cheats (Game Genie on NES/MD/SNES) live in ROM, which states do not hold. So states and rewind need no extra calls. Re-applying the list after a state load is cheap and a safe belt-and-braces step. A state saved while cheats were on keeps the cheated RAM values after cheats are turned off; that is expected and should be documented.
- **Run-ahead:** removed upstream, so nothing to do. Achievements: none in slot.
- **Link cable (GBA/GB, our tree has link mode):** Slop refuses cheats during a cable session because both devices run both machines from the host's state ("a cheat on one is a machine the other is not simulating", `slop crates/slot/src/session.rs:715-725`; commit 93912ff). Do the same.
- **Battery saves (the real risk):** a game that saves while a cheat writes RAM stores the cheated values, and a wrong-revision code can corrupt a save. Slop copies `Saves/<SYS>/<stem>.sav` to `<stem>.sav.before-cheats` the first time cheats run on a cart, and never again (`slop crates/slot-store/src/cheats.rs`, `backup_save_once`). Adopt that. Our ADR 0072 (write `.sav` when the core gives no state) and ADR 0082 (hack updates keep saves) are unaffected.
- **PS1 memory cards:** same risk via pcsx's memory card writes. The same one-time backup of the card file applies.

## Q3. UX on the device

### How the forks did it

| Fork | Files | Entry point | List | Persistence | Notes |
|---|---|---|---|---|---|
| ygordreyer/slot "Slop" (branch Slop, `1aa7811`) | `Cheats/<platform>/<stem>.cht`, RetroArch format, user-supplied | **SELECT+X** in game (`crates/slot-input/src/gesture.rs:41-43, 425`) | 7 rows at 52 px pitch over the paused game, scrolling window, ON/OFF at the right, long names shrink to 20 px then ellipsis (`crates/slot-ui/src/cheat_menu.rs:15-30`) | writes `cheatN_enable` lines back into the same file, everything else untouched, atomic (`crates/slot-store/src/cheats.rs`, `set_enables`) | applies on load, reset+re-add on change, one-time save backup, refused in link sessions, closes on doze; toasts "Cheats on/off", "No cheats" |
| markbruno/slot-plus (`524ba7d`) | same design; Slop absorbed it (commit 522fd12 "Add shaders and cheats.") | | | | |
| RetroGame66/slot (66-mods, `5b146a3`) | `System/Cheats/<stem>.txt`, one code per line, `#` comments | **SELECT+A** opens a table; SELECT+A again flips a master switch | per-code table | every code defaults to OFF at load | README.md:115, 276, 325; CHANGES.md section 6 |

Neither chord ports to our tree. SELECT+X is the picture mode on SNES and PS1 (ADR 0007, 0068), and SELECT+B/A cycle shaders (ADR 0008/0023).

### Recommended layout

- **Entry point:** an in-game row "Cheats" on `QuickRow::PLAY` (Resume, States, **Cheats**, Settings, Exit), **hidden unless the seated cart has a cheat file**. This uses the same hidden-row mechanism as `retro_quick::hidden_on_shelf`. Cost: `QuickRow::PLAY` is pinned exactly by upstream test `the_in_game_pages_hold_their_rows_in_order` (`crates/slot-ui/tests/quick_menu.rs:307-333`), and `QuickRow::ALL` is listed at an existing named site (ADR 0048). Adding the row needs a new named test site, approved in the ADR. The alternative that avoids test hunks is a chord. After the rebase onto upstream main (`e1bfb2b`, remappable Shortcuts page), "Open cheats" could be an unbound shortcut that the user assigns. That keeps factory defaults unchanged.
- **List screen:** reuse Slop's proven geometry. 720x480 gives 7 rows at 52 px between a count line at y 16 and the legend at y 427. Show "N of M on" in the count line. D-pad up/down moves, **L/R page by 7** (files reach 8k to 10k entries, e.g. Pokemon Crystal 7,539 blank plus real ones, and a 10,185-entry SNES file), A toggles, B closes and applies, X clears all. Hide junk entries (empty, wildcard, unsupported format for the current core) and say how many were hidden. Keep the description text from the file; no translation.
- **Which device file:** when a game has several files (plain, `(Game Genie)`, `(Action Replay)`), the Mac tool merges them into one `Cheats/<SYS>/<stem>.cht` with a device tag in each description ("[GG]", "[AR]"). That gives one list per game.
- **Persistence:** Slop's approach is best: the `cheatN_enable` lines in the cart's own `.cht`, rewritten atomically. The file still opens in RetroArch, and there is no second file to drift. The path follows our layout: `Cheats/<SYS>/<stem>.cht` at the card root, or under `Config/cheats/` if the maintainer prefers everything under `Config/`. `Config/` survives updates either way (PLAN.md success criterion 5). Note that ADR 0082 keeps a hack's stem across updates, so `hacks.py --update` must move the hack's `.cht` into the backup with its states.
- **On/off at load:** whatever the file says (the user's last choice is the default). The database ships every entry `false`, so nothing is on until the user turns it on. No factory default changes.
- **Warning:** a toast "Cheats on" when a cart starts with cheats enabled, and a small marker in the in-game menu while any cheat is active. No persistent HUD over the game picture.
- **Per-system rule:** cheats are per game, not per system, so they need no Screen section. Respect the rule anyway: if a global on/off is ever added, it goes in each system's own section, defaulting to On. Without it nothing happens anyway, since no file means no row.

## Q4. Shipping

- **Bundling the database in the release zip: not recommended.** It would add about 13,600 files and 23.8 MB of text. On FAT32 with 32 KiB clusters that is roughly 13,600 x 32 KiB, about 425 MB on the card. It would also put CC BY-SA material of mixed provenance in our zip (attribution plus a `licenses/` entry required), and nearly every file would be useless for a given card.
- **Recommended: a Mac tool**, `tools/fetch-cheats.py` or a `--cheats` mode of `fetch-labels.py`. It would reuse the `Dat` loader, `Rom.crcs()`, the `--card` and `--device --library` scans and the cache directory. For each ROM on the card: CRC, then No-Intro name with language tags normalised, then every matching cht variant, merged into one `Cheats/<SYS>/<card stem>.cht`. It never overwrites a file that has enable lines unless `--force`, and pulls the libretro-database `cht/` once into the cache (sparse git or the raw GitHub URLs fetch-labels already uses). This is the user fetching data for their own card, the same model as labels.
- **By-name fallback is opt-in** (`--by-name`, `--aliases`), mirroring fetch-labels. A cheat for another region or revision can crash the game or corrupt the save, so title-only matches are never automatic. The 41 to 77% title-key figures are an upper bound, not coverage.
- **PS1:** serial (already read by fetch-labels), then the Redump name, then the cht file by exact name, else title key plus region under `--by-name`.
- **ROM hacks:** a hack's CRC is in no No-Intro dat, and its RAM layout usually differs from the parent (big hacks such as Pokemon Unbound rewrite the engine), so parent cheats are unsafe by default. `tools/hacks.json` already knows each hack's `base_name` and `base_crc32` (e.g. `tools/hacks.json:10-11`), so an explicit per-hack opt-in such as `"cheats": "parent"` could copy the parent's file with a warning line at the top. Default: no cheats for hacks. Users can still drop their own `.cht` for a hack.

## Q5. Effort, work breakdown and risk

Sizes: S = up to 1 day, M = 2 to 3 days, L = 4 to 5 days.

| # | Issue | Size | Upstream-generic? | Notes |
|---|---|---|---|---|
| C1 | ADR: cheats in scope (amends PLAN.md non-goal, PLAN changelog row 7); new named test site for `QuickRow::PLAY` | S | no (declined upstream #8) | see ADR outline below |
| C2 | `slot-retro`: optional `retro_cheat_reset`/`retro_cheat_set` symbols, `RetroCore::set_cheats` default `false`, mock core records calls | S | generic in shape, fork-only by policy | follow Slop `ffi.rs:172-211`, `core.rs:116-121`, `libretro.rs:786-803` |
| C3 | `slot-store`: `.cht` parser (BOM, CRLF, quotes, missing count), junk filter, atomic `cheatN_enable` write-back, one-time save backup | S to M | same | Slop's `cheats.rs` is a good base (297 lines with tests) |
| C4 | Code dispatcher per core: split policy, contiguous indices, length guards (255, 1023), caps (gpsp 20, genesis 150, snes9x2005 800), format check per core ("needs mGBA") | M | no | where the crash risks are fixed; table-driven tests |
| C5 | Session lifecycle: apply after load on the emu thread, re-apply after state load, reset on eject, never call when none enabled, refuse during link, toast | M | no | GBA invariant lives here |
| C6 | UI: list screen (7 rows, paging, count, hidden-entry note), PLAY row hidden without a file, in-menu marker | L | no | patch touches `quick_menu.rs` again (7 patches already) |
| C7 | Mac tool: CRC to cht match with language normalisation, variant merge, `--by-name`/`--aliases`, PS1 serial path, `--device` push, report TSV | M | no | reuse fetch-labels helpers; test with fixture dats |
| C8 | `hacks.py`: move the hack's `.cht` into the update backup; optional `"cheats": "parent"` | S | no | ADR 0082 follow-up |
| C9 | Real-core tests: host dylibs in `vendor/` (fceumm, snes9x, snes9x2005_plus, genesis_plus_gx, gpsp, mgba) | M | no | see test strategy |
| C10 | Device gate: one game per system, toggle on/off, state save/load, eject, `.sav` backup present | S | no | DEVICE-GATE.md row |
| C11 | (later) RAM-poke engine for mednafen_ngp and `handler` entries | M | no | defer until NGP ships |

Total C1 to C10: about 15 to 22 dev days.

### Test strategy

- **Unit (no core):** parser fixtures copied verbatim from real files (CRLF, BOM, 8k-entry Pokemon file, empty and wildcard entries, `(Rumbles)` files), per the workspace rule to test with realistic input, not sanitised input. Dispatcher table tests against a recording fake core: split vs whole per core, contiguous indices, caps and the 256-char guard.
- **Real core, synthetic ROM:** load a tiny homebrew or synthetic ROM in the host dylib (the pattern of `crates/slot/tests/nes_fceumm.rs`), set a raw RAM cheat (NES `0010:42`, SNES PAR `7E001042`, MD `FF0010:0042`, GBA Code Breaker `32000010+0042`), run N frames, and assert the byte via `retro_get_memory_data(RETRO_MEMORY_SYSTEM_RAM)`. Also: reset clears it; a disabled entry is not sent; a 600-char SNES code split into parts does not crash snes9x. That last one is the overflow regression test.
- **GBA invariant:** the existing frame-hash harness runs with a cart that has no `.cht` and with one whose entries are all off. Both must match unpatched v1.7.0 byte for byte, and a trace counter must show zero `retro_cheat_*` calls.
- **Device:** C10.

### Main risks

1. **Crashes from long codes** in snes9x and nestopia (stack overflow on the emu thread). Mitigated by C4's split and guard. Without it, a single database entry can take the device down.
2. **Save corruption** from wrong-revision or badly written codes. Mitigated by CRC-exact default matching, the one-time `.before-cheats` backup and the warning toast.
3. **Silent no-ops** (format not supported by the selected core, gpsp's 20 cap, genesis's 150 cap) that make users think cheats are broken. Mitigated by per-core format checks and toasts.
4. **Rebase cost:** fork-only patches in `quick_menu.rs`, `session.rs` and `ffi.rs`, all of which upstream touches often.
5. **Coverage expectations:** 17% to 72% CRC coverage, close to none for hacks. Say so in the README.
6. **Licence:** fine for the Mac-tool route. Bundling needs CC BY-SA attribution, and GameHacking.org content needs permission.

## Recommended approach

1. Write the ADR (C1) and get the maintainer's call on the entry point: a PLAY row with a new named test site, or a user-assigned shortcut after the upstream-main rebase.
2. Build the engine and data path first (C2 to C5 plus C7 with CRC-exact matching only). Reuse Slop's file format and write-back so the files stay RetroArch-compatible.
3. Add the list UI (C6), then hacks and the device gate (C8 to C10). Defer NGP and RAM-engine entries (C11).

**Smallest useful first step (about 1.5 weeks):** C2 + C3 + C4 + C5, a minimal C6 (the list on the PLAY row, no paging polish), and a C7 that only does CRC-exact copying for NES, SNES and the Sega systems. Those have the best coverage (NES 52%, GG 72%, SMS 64%, MD 45%) and the friendliest cores (fceumm, snes9x, genesis_plus_gx all split `+` themselves; the dispatcher still splits for safety). GBA/GB/GBC and PS1 follow once the GBA invariant test is in place.

## ADR draft outline

**00NN. Per-game cheats from the libretro cheat database, off unless the user turns them on**

- Status: Proposed. Amends PLAN.md "Who it's NOT for" (cheats removed from the RetroArch-breadth non-goal) and adds a named test site to ADR 0013.
- Context: maintainer request; PLAN.md:58 non-goal; upstream declined (#8, FAQ), so ADR 0047 upstream-first does not apply; libretro-database `cht/` is CC BY-SA 4.0 with the coverage table above; all shipped cores except mednafen_ngp implement `retro_cheat_set`, with the quirks listed in Q2; forks Slop, markbruno and RetroGame66 prove the UX on the same panel.
- Decision:
  - cheats come from `Cheats/<SYS>/<stem>.cht` (RetroArch format), written only by the Mac tool (CRC-exact by default, by-name opt-in) or by the user; nothing is bundled in the zip;
  - the in-game PLAY page gets a "Cheats" row, hidden when the cart has no file (new named test site for `QuickRow::PLAY`), or the alternative entry point the maintainer picks;
  - enable state lives in the file's `cheatN_enable` lines; the user's last choice is the default; the database default is off;
  - the frontend dispatches per core (split policy, contiguous indices, length and count guards) and never calls `retro_cheat_*` when nothing is enabled;
  - first enable backs up the battery save once; cheats are refused in link sessions;
  - mednafen_ngp and RetroArch `handler` entries are out of scope until a RAM-poke engine is justified.
- Consequences:
  - Positive: per-game cheats on the device with no typing; files stay RetroArch-compatible.
  - Negative: fork-only rebase cost in `quick_menu.rs`, `session.rs`, `ffi.rs` and `libretro.rs`; partial coverage, near zero for hacks; a new upstream test edit site.
  - Invariant: GBA/GB/GBC frame hashes are identical to unpatched v1.7.0 when no cheat is enabled, checked by the harness and a zero-call trace counter.
  - On each rebase: re-check the PLAY pin test, the remappable Shortcuts page (possible chord entry), and each core's `retro_cheat_set` when core pins move (buffer sizes and split behaviour).

## Sources

- libretro-database: <https://github.com/libretro/libretro-database> (`cht/`, `LICENSE`, `README.md`, `metadat/no-intro/*.dat`), cloned 2026-10-18.
- Core sources at pins: `slot-nes-snes/vendor/{fceumm,nestopia,snes9x,snes9x2005_plus,genesis_plus_gx,gpsp}-src.tar.gz`; <https://github.com/libretro/mgba/tree/e31759b24e7a4e3899285ff720d7b573ac328ae7>; <https://github.com/libretro/pcsx_rearmed/tree/c8816799b50388e61cfe237fe2cdbb7d8175f20a>; <https://github.com/libretro/beetle-ngp-libretro> at `a50d5ac`.
- Forks: <https://github.com/ygordreyer/slot> (Slop, `1aa7811`), <https://github.com/markbruno/slot-plus> (`524ba7d`), <https://github.com/RetroGame66/slot> (66-mods, `5b146a3`).
- Upstream: <https://github.com/BrandonKowalski/slot/issues/8>; upstream main `1b20432` `site/index.html:611`; no cheat code in upstream crates.
- slot-nes-snes: `docs/PLAN.md:56-58`, `docs/research/slot-forks.md:57,70,78,205`, `docs/adr/0002`, `0007`, `0008`, `0013`, `0047`, `0048`, `0068`, `0082`, `tools/fetch-labels.py`, `tools/hacks.json`, `build/slot/crates/slot-retro/src/ffi.rs`, `build/slot/crates/slot-ui/tests/quick_menu.rs`.
- GameHacking.org home page (browser, 2026-10-18): no licence statement.
- Library measurements: `/Volumes/MuOs/ROMS` (read only), scripts in the session scratchpad.
