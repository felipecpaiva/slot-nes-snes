# 0100. Offer a Shelf order option: Classic by default, or the systems by first release date

- Status: Accepted. Settings row added and the Screen list made to follow the order on 2026-10-20 (site (k), patch 0118)
- Date: 2026-10-20
- Deciders: maintainer (Felipe Paiva)
- Related: patches `patches/0117-shelf-order.patch` and `patches/0118-shelf-order-row.patch`, [ADR 0025](0025-shelf-memory.md), [ADR 0049](0049-per-shelf-cart-memory.md), [ADR 0085](0085-cpu-governor-user-option.md), [ADR 0048](0048-nes-snes-in-the-screen-platform-list.md)

## Context

The system shelves come in the order the systems were added to this project (`Platform::SHELVES`:
GBA, GB, GBC, NES, SNES, then each new system at the end). With 20 systems that order means
nothing to a player. The maintainer asked for the shelves after Recents in the order each platform
was first released, oldest first. The project rule is to keep options and never retune a factory
default for one device, so the old order stays the default and the new one is an option.

## Decision

`Config/shelf_order.txt` holds one key, `order`:

- `classic` (or no file, or any other word, which is logged and read as Classic): today's order,
  `Platform::SHELVES` unchanged.
- `release-year`: the system shelves sorted by their first release anywhere, ties broken by month
  and then day.

Recents stays first and Favorites second in both orders. The dates are one table, `RELEASED` in
`crates/slot/src/shelf_order.rs`, one `(Platform, year, month, day)` row per platform (day 0 where
no day is recorded). A new system adds one row; `every_shelf_platform_has_exactly_one_release_date`
in `crates/slot/tests/shelf_order.rs` fails for a shelf platform without one. A platform missing at
run time (the test not run) is shelved last with a `slot: shelf order:` log line.

The order is applied once in `App::boot`, right after the shelves are built, by sorting
`App::shelves` (`App::arrange_shelves` in the new `crates/slot/src/app/shelf_order.rs`). Every user
of the shelf order reads that vector, so all of them follow the option with no further change: R1
and L1 (`next_shelf`), the neighbour shelves peeking on the main screen and their faces, the shelf
name, and the first shelf with carts on a boot with nothing remembered. The remembered shelf and
cart (ADR 0025, ADR 0049) are stored by shelf key (`vb`, `snes`), not by position, so they come back
in either order.

### The Settings row (added 2026-10-20)

First shipped as the file alone, because a row in General changes the label list in upstream
`slot-ui/tests/quick_menu.rs` `the_rows_run_in_the_order_the_user_chose`, which needs a named
test site. The maintainer approved site (k) on 2026-10-20 (CONTRIBUTING section 1).

Settings > General > Shelf Order (Classic, Release Year) sits between Game Titles and CPU. Left or
Right flips it and saves `Config/shelf_order.txt` the way `CpuMode::save` writes `cpu.txt`, with a
card-write log entry. The place was checked against every upstream test that walks General:
`show_titles_sits_under_recents_on_the_general_page` pins Game Titles right after Recents,
`the_arrows_stand_only_around_the_selected_rows_value` (`slot/tests/quick_menu.rs`) presses Down
once from Lid Power Off and expects Date & Time, the slot-ui wrap tests pin Recents at position 3,
and the rest find their row with `position`. Between Game Titles and CPU moves none of them.

The new order applies at once, with no restart: `App::flip_shelf_order` sorts `App::shelves` again
and selects the same shelf it was on. That is safe because every shelf moves with its carts,
selection and faces; a cart face still being built for an old position is dropped by
`shelf_restock::face_fits` (ADR 0073) and asked for again; and the remembered shelf is keyed by
name. The rest-write cache (`rested`) is cleared so the next rest writes the seat again.

### The Screen platform list follows the shelf order (amended 2026-10-20)

First shipped fixed. The maintainer then asked for Settings > Screen to list the systems in the
same order as the shelves. It reads the same list: `ShelfOrder::screen_rows` maps
`ShelfOrder::platforms()` through `screen_row` (an exhaustive match, one Screen row per platform),
and `App::arrange_shelves` hands it to slot-ui with `slot_ui::set_screen_page` every time it sorts
the shelves, at boot and on a row flip. `QuickRow::page`, `centred`, `child` and the scroll check
read `slot_ui::screen_page()` instead of `QuickRow::SCREEN`.

`QuickRow::SCREEN` itself keeps the classic order, so site (g) and every upstream test that reads
it stay as they are, and no new site is needed for this part (the maintainer had approved one if
it were). The page is held per thread (`thread_local`, default `QuickRow::SCREEN`): the menu is
built, walked and drawn on the thread that owns `App`, and tests that run in parallel threads each
keep their own. `set_screen_page` refuses (and logs) a list that is not the Screen rows reordered.
Systems without carts are still hidden from the page, in either order.

### The dates

First release anywhere, from each platform's English Wikipedia article (read 2026-10-20).

| Platform | First release | Where | Source |
|---|---|---|---|
| Atari 2600 | September 1977 (day not known; August to October) | North America | [Atari 2600](https://en.wikipedia.org/wiki/Atari_2600) |
| NES (Famicom) | 15 July 1983 | Japan | [Nintendo Entertainment System](https://en.wikipedia.org/wiki/Nintendo_Entertainment_System) |
| Master System (Mark III) | 20 October 1985 | Japan | [Master System](https://en.wikipedia.org/wiki/Master_System) |
| Atari 7800 | May 1986 (no 1984 test market reached shops) | North America | [Atari 7800](https://en.wikipedia.org/wiki/Atari_7800) |
| TurboGrafx-16 (PC Engine) | 30 October 1987 | Japan | [TurboGrafx-16](https://en.wikipedia.org/wiki/TurboGrafx-16) |
| CPS1 | 13 May 1988 (Forgotten Worlds) | Japan | [CP System](https://en.wikipedia.org/wiki/CP_System) |
| Mega Drive | 29 October 1988 | Japan | [Sega Genesis](https://en.wikipedia.org/wiki/Sega_Genesis) |
| PC Engine CD-ROM² | 4 December 1988 (added with ADR 0104, read 2026-10-21) | Japan | [TurboGrafx-16](https://en.wikipedia.org/wiki/TurboGrafx-16), section "CD-ROM² / TurboGrafx-CD" |
| Game Boy | 21 April 1989 | Japan | [Game Boy](https://en.wikipedia.org/wiki/Game_Boy) |
| Lynx | 1 September 1989 | North America | [Atari Lynx](https://en.wikipedia.org/wiki/Atari_Lynx) |
| PC Engine SuperGrafx | 8 December 1989 (added with ADR 0103, read 2026-10-21) | Japan | [PC Engine SuperGrafx](https://en.wikipedia.org/wiki/PC_Engine_SuperGrafx) |
| Neo Geo MVS | 16 April 1990 | Japan | [Neo Geo (system)](https://en.wikipedia.org/wiki/Neo_Geo_(system)) |
| Game Gear | 6 October 1990 | Japan | [Game Gear](https://en.wikipedia.org/wiki/Game_Gear) |
| SNES (Super Famicom) | 21 November 1990 | Japan | [Super Nintendo Entertainment System](https://en.wikipedia.org/wiki/Super_Nintendo_Entertainment_System) |
| Sega CD (Mega-CD) | 12 December 1991 (added with ADR 0105, read 2026-10-21) | Japan | [Sega CD](https://en.wikipedia.org/wiki/Sega_CD) |
| CPS2 | 10 September 1993 (Super Street Fighter II) | Japan | [CP System II](https://en.wikipedia.org/wiki/CP_System_II) |
| Neo Geo CD | 9 September 1994 (added with ADR 0107, read 2026-10-21) | Japan | [Neo Geo CD](https://en.wikipedia.org/wiki/Neo_Geo_CD) |
| Sega 32X | 21 November 1994 | North America | [32X](https://en.wikipedia.org/wiki/32X) |
| PlayStation | 3 December 1994 | Japan | [PlayStation (console)](https://en.wikipedia.org/wiki/PlayStation_(console)) |
| Virtual Boy | 21 July 1995 | Japan | [Virtual Boy](https://en.wikipedia.org/wiki/Virtual_Boy) |
| Game Boy Color | 21 October 1998 | Japan | [Game Boy Color](https://en.wikipedia.org/wiki/Game_Boy_Color) |
| Neo Geo Pocket | 28 October 1998 | Japan | [Neo Geo Pocket](https://en.wikipedia.org/wiki/Neo_Geo_Pocket) |
| WonderSwan | 4 March 1999 | Japan | [WonderSwan](https://en.wikipedia.org/wiki/WonderSwan) |
| Game Boy Advance | 21 March 2001 | Japan | [Game Boy Advance](https://en.wikipedia.org/wiki/Game_Boy_Advance) |

Game Boy Color and Neo Geo Pocket share October 1998, so the day decides (21 before 28). Every
other pair differs by month or year, so the two rows without a day (2600, 7800) never need one.
The order matches the one the maintainer gave.

## Consequences

- Classic is byte for byte the old order, so no upstream test and no existing test of ours moves.
- A player sets the option in Settings > General > Shelf Order, or by writing the file.
- `crates/slot/tests/shelf_order_row.rs`: the row's place, Classic on a fresh card, Right saving
  `order = release-year` and a reboot keeping it, the order applying at once with the same shelf
  selected, and flipping back to Classic; the Screen page in the classic order by default and in
  Release year at once and after a reboot, and the Release year Screen rows equal to the shelf
  order's platforms.
- `crates/slot/tests/shelf_order.rs`: both orders through R1 from Recents and back, L1 backwards,
  a remembered Virtual Boy shelf coming back in Release year with Game Boy Color after it, an
  unknown word read as Classic, and one release row per shelf platform.
- Upstream touch points: one `mod shelf_order;` line and one call in `App::boot` in `app.rs`, one
  `pub mod` line in `lib.rs`; the row adds the `shelf_order` field, its quick value, one flip branch
  and two `| QuickRow::ShelfOrder` tokens in `app.rs`, and the row and its two values in
  `slot-ui/src/quick_menu.rs`. Check on each rebase that `App::boot` still builds the shelves in
  `App::new` before reading the card.
