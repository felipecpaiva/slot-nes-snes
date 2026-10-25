> Superseded on 2026-10-25 (ADR 0109): upstream v1.9.0 shipped its own guard (`loading_mark.rs`). This text stays as
> history. What is still ours is the banner and the selected cart, see docs/upstream/start-failed-banner-issue.md.

# PR title

Leave a game on the shelf when its last start crashed

# PR body

## Problem

slot puts the last game back in the slot on every boot. If that game crashes slot while it starts
(core load, resume state load, the first frames), the next boot crashes the same way, and so does
every boot after it. On a card with one game the shelf is never reached, so there is no way out on
the device.

## Change

- `Session::spawn_core` writes `Config/starting.txt` (`<platform dir>/<stem>`) before the
  `slot-open` thread starts, synchronously, so the mark is on the card before the core can crash.
- The mark is removed once the game has published 300 frames, or when a resume state is written
  for the seated cart (`flush_resume`, `autosave`), since either proves the game ran.
- `App::start` reads it at boot. When it names the cart it would put back (stem and platform), the
  cart is selected on the shelf instead, a "Last start failed" banner shows, and a `slot: start
  guard:` line is logged. The single-cart branch is covered too.
- Nothing is deleted. The resume state stays, so a tap of A tries it again and a held A starts
  clean. The mark stays until a start gets through, so a power cycle does not bring the loop back.

## Tests

New `crates/slot/tests/crash_guard.rs`, no real core needed:
- a start that never ran frames leaves the cart selected on the shelf with the banner;
- its resume state is untouched;
- a second boot still shows the shelf;
- a start that publishes 300 frames resumes on the next boot, with no banner;
- a flush before 300 frames also clears the mark;
- the mark holds back only the cart it names;
- the banner has its own place in the uploaded toast list.

## Edge cases

A power loss in the first seconds of a start, before any flush, costs one resume: the next boot
shows the shelf with the banner, then everything is normal.

## Credit

The idea is from oauramos/omega-zero be6eb11, which keeps such a game on the shelf with a notice.
