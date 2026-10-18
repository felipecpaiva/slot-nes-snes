# 0070. Scroll the Screen page with a backport of upstream's settings-page scrolling

- Status: Accepted. Shrunk on the rebase onto upstream main 1b20432 to `&QuickRow::SCREEN` in upstream's `scrolls()` ([ADR 0083](0083-rebase-to-slot-main-1b20432.md))
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), [ADR 0048](0048-nes-snes-in-the-screen-platform-list.md), [ADR 0055](0055-sega-tokens-at-named-test-sites.md), [ADR 0065](0065-ps1-canvas-and-screen-section.md), patch `patches/0042-screen-scroll.patch`, upstream [e1bfb2b](https://github.com/BrandonKowalski/slot/commit/e1bfb2b) and [2c82294](https://github.com/BrandonKowalski/slot/commit/2c82294)

## Context

Settings > Screen lists nine systems on a card that has games for all of them: GBA, GBC and GB
from upstream, then NES, SNES, Game Gear, Master System, Mega Drive and PlayStation (ADR 0048,
0055, 0065). At `QUICK_PITCH` 52 px that is 468 px of rows against the legend at y 427, so
`quick_row_top` puts the first row at y -20.5 and the last runs over the legend. The page does
not scroll in v1.7.0. The maintainer saw the overlap on the RG34XXSP.

Upstream main after v1.7.0 (unreleased 1.8.0) scrolls long settings pages. e1bfb2b adds
`QUICK_VISIBLE = 6`, a `scrolls()` whitelist, `quick_window` (six rows centred on the cursor,
clamped to the ends), `quick_row_top_at`, and a draw loop that draws only the window. 2c82294
renames the whitelisted carousel page to GENERAL. The whitelist is CONTROLS, SHORTCUTS and
GENERAL; SCREEN has three rows upstream, so it is not in it.

marghost/slot_modded had its own scrolling settings page (3751a4a) and removed it in a merge
(7931365) because its menus were reshaped until every page fitted. That code is on v1.6.0 menus
and is not a base for us.

Every other page fits (over 8 rows overflows): GAME 7 rows (364 px), GENERAL 6, MAIN 4, SCREEN_GB
4, SCREEN_GBA and SCREEN_GBC 3, every retro system section 2 (Shader, Picture). In game: PLAY 4,
SETTINGS 2, PLAY_SCREEN 4 as the bottom panel.

## Decision

Patch `0042-screen-scroll` backports upstream's mechanism as it is, into `quick_menu.rs` and the
`lib.rs` re-export, and nothing else from those commits (no bindings, no description line, no
legend change). Our PLAY_SCREEN top (`LEGEND_Y - PANEL_GAP`) stays as in v1.7.0. The whitelist is
`[GENERAL, SCREEN]`: CONTROLS and SHORTCUTS do not exist in v1.7.0, GENERAL is kept so the line
matches upstream (at 6 rows it never scrolls), and SCREEN is our one added token. Row height,
legend and the centred column are unchanged; the page shows six rows that follow the cursor.

We keep the whitelist and do not make every page longer than `QUICK_VISIBLE` scroll: GAME has 7
rows, and upstream 1.8.0 does not scroll it, so a count rule would change how an upstream page
looks.

## Consequences

- A card with seven or eight systems also scrolls now (six rows shown) where all rows used to fit.
  This is what upstream does with GENERAL at seven rows. Our own test
  `the_full_screen_list_of_eight_systems_fits_between_the_top_and_the_legend` (patch 0027) now
  expects six bands.
- There is no up or down mark for hidden rows, as upstream.
- Tests: `crates/slot-ui/tests/screen_scroll.rs` (every drawn row of the nine-system list sits in
  0..427 for every cursor position; the selected row is always drawn) and
  `crates/slot/tests/render_screen_scroll.rs` (macOS render: no row cut at the top or into the
  legend; after moving to PlayStation its lit row is inside the area). Both go red when SCREEN is
  taken out of `scrolls()`.
- **On the 1.8.0 rebase:** drop this patch's mechanism, keep only `&QuickRow::SCREEN` added to
  upstream's `scrolls()` list (one token), unless upstream takes the proposal below, then drop it
  all. Re-run both tests.

## Upstream proposal (prepared, not sent)

Title: Scroll any settings page that is taller than the menu area

> `scrolls()` in `quick_menu.rs` lists the pages that scroll (CONTROLS, SHORTCUTS, GENERAL). A
> fork or a future release that adds rows to another page has to remember to add it there, or the
> rows run off the top and over the legend. Our NES/SNES/Sega/PS1 patch set hit this on the Screen
> page (9 rows, 468 px against the legend at 427).
>
> Proposal: scroll a page when its rows do not fit, `count as f32 * QUICK_PITCH > LEGEND_Y`
> (more than 8 rows at 52 px against 427), instead of a list. A count rule
> (`count > QUICK_VISIBLE`) would start scrolling GAME at 7 rows, which fits today, so the test
> is the height. The one visible change: GENERAL (7 rows, 364 px) would show all its rows
> instead of a 6-row window. If you prefer GENERAL to keep scrolling, keep the list and add the
> height test as a second condition, so a page that outgrows the area scrolls without anyone
> having to list it. Happy to send a PR with a test that every page's drawn rows stay above the
> legend.
