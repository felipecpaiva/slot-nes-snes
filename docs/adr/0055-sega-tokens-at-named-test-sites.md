# 0055. Widen named test sites (b), (e), (g) and (h) for the Sega platforms and Genesis Plus GX

- Status: Accepted. Amends [0013](0013-five-named-test-sites.md) and [0048](0048-nes-snes-in-the-screen-platform-list.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 50](../../.github/issues/50-sega-tracking.md), [ADR 0053](0053-genesis-plus-gx-for-sega.md), [patch 0024](../../patches/0024-platform-gg.patch), [patch 0027](../../patches/0027-sega-shaders.patch), `scripts/check-upstream-tests.sh`, CONTRIBUTING.md section 1

## Context

`Platform::Gg`, `Platform::Sms` and `Platform::Md` and `Core::GenesisPlusGx` are new enum
variants. Two upstream test files hold exhaustive matches over those enums, so they stop
compiling without one new token each: `label_band` in `crates/slot-ui/tests/chrome.rs` (site b)
and the colour-correction match in `crates/slot/tests/gpsp.rs` (site e). No other change to
those tests makes them compile, and neither test runs a Sega cart.

The maintainer asked for the Sega shaders on the Screen page like NES and SNES (ADR 0048,
ADR 0051). `QuickRow::SCREEN` then lists eight systems, and `the_rows_run_in_the_order_the_user_chose`
in `crates/slot-ui/tests/quick_menu.rs` pins both the label literal (site g) and the list of rows
that open pages (site h). Any Screen row for a Sega system changes those two lines, so this is
unavoidable once the rows exist; it is not the standing rule (a value change), so it is named here.

## Decision

- Site (b): the Game Boy arm, which already carries `| Platform::Nes | Platform::Snes`, gains
  `| Platform::Gg`, `| Platform::Sms` and `| Platform::Md`, in that order, on the same line.
- Site (e): the `Core::Mgba` arm gains `| Core::GenesisPlusGx` after `| Core::Snes9x2005Plus`.
- Both are the standing rule of CONTRIBUTING section 1 (a new variant token appended to an
  existing arm of an exhaustive match). `check-upstream-tests.sh` checks each one byte for byte
  after the tokens are removed.
- Site (g): the Screen labels line gains `, "Game Gear", "Master System", "Mega Drive"` after
  `"SNES"`. Site (h): the opens line gains `, QuickRow::ScreenGg, QuickRow::ScreenSms,
  QuickRow::ScreenMd` after `QuickRow::ScreenSnes`. Both on their one line, checked the same way.
- On a card with no cart of a Sega system its Screen row is hidden
  (`retro_quick::hidden_on_shelf`, per system), so a GBA, GB and GBC card keeps upstream's
  menu and frames.

## Consequences

- The two upstream tests compile and run unchanged in what they assert.
- A reflowed arm or a token in another arm still fails the guard.
- On each rebase, recheck the four lines as for the NES and SNES tokens.
