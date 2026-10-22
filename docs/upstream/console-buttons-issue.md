# Draft issue for BrandonKowalski/slot (not posted)

Status: draft for the maintainer. Nothing here has been posted (he cannot open pull requests on the
upstream repo at the moment). Generic part of ADR 0108.

---

**Title:** Controls: let a core's own buttons be rows on the In-Game page, named by the core

**Body:**

Slot 1.8.0 puts every control in one table and the In-Game page lists the twelve `GameButton`s (D-pad,
A, B, Select, Start, L, R, Turbo A, Turbo B), with Game Boy Advance names, and the same set is saved for
every console in `Config/controls.txt`. That fits GBA, GB and GBC, where those are all the buttons the
core reads.

A core with more buttons than that has nowhere to show them. Two things would make the table carry any
core without a frontend change per core:

1. **Rows per RetroPad bit, not per GBA button.** `GameButton` gains the bits a core can read that the
   twelve do not cover (L2 and R2 at least; X and Y are already Turbo A and Turbo B's bits). Which rows a
   page shows comes from the core: the ids it declares with `RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS`
   (port 0, joypad), and a row whose bit the core does not declare is hidden. The page names each row with
   the core's own description ("Cross", "C", "Attack"). GBA, GB and GBC stay exactly as today, because
   mGBA and gpSP declare the same twelve.
2. **Saving per core or per system.** The shared `controls.txt` stays the base; a change made on the
   In-Game page while a game plays is kept in a second file for that system and overrides the base row by
   row, so a main-menu change still reaches every system that has not changed that row.

Two small pieces are needed in `slot-retro` for this and are useful on their own:

- answering environment call 11 (`SET_INPUT_DESCRIPTORS`) and keeping port 0's joypad entries, and
- recording which joypad ids the core polls in `input_state`, which a test can compare with what the
  page offers (we use it to prove every button a core reads can be reached from some row).

Tests that keep it honest (we run these on a fork, glad to share them): every visible row's button,
pressed through the real `Pad` mask, reaches the id the core polls; no two rows start on the same
device button; a fresh card shows no clash warning on any system's page.

The one upstream test this touches is `the_thumb_reaches_the_bottom_only_on_the_last_row` in
`slot-ui/tests/quick_menu.rs`, which walks `QuickRow::CONTROLS`; with more rows on the page it would walk
the page itself.
