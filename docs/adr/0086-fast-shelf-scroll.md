# 0086. Hold to scroll a long shelf 3 carts at a time, drawing placeholders instead of waiting for faces

- Status: Proposed. Needs the device measurement below
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: patches/0054-fast-shelf-scroll.patch, [fork-marghost.md](../research/fork-marghost.md)
  section 1 and 7.2, [fork-review-2026-10-18.md](../research/fork-review-2026-10-18.md) item 14

## Context

Upstream repeats a held Left or Right after 400 ms, then every 110, 85, 65 and 50 ms, one cart each:
about 20 carts a second at best. A full NES or SNES set is 700 carts or more. marghost/slot_modded
(efe32cd, from stevolarn/slot) moves 3 carts per repeat after 30 repeats (about 2 s) on a shelf of
60 or more carts. Two things then go wrong, and the fork fixed only the first:

- The scroll spring lags the selection by about 2v/omega carts (omega 16): about 7.5 carts at 60
  carts a second, more than the 3 slots drawn each side, so the board goes blank. marghost 0fce212
  re-centres the drawing on the scroll position.
- `CartFaces::sync` blocks the frame until every face marked `on_screen` is built. At 60 carts a
  second on the PS1 shelf (jewel cases with cover decode) or the SNES shelf (bitmap carts), slow
  builds would turn into frame hitches.

## Decision

- After 30 repeats on a shelf of 60 or more carts, each repeat moves 3 carts (marghost's numbers).
  Shorter shelves and the first 30 repeats behave exactly as upstream. A new press starts over.
- While fast, the scroll is kept within 1 cart of the selection after each spring step (a leash), so
  the 7 drawn slots always cover the screen. Upstream's drawing code is unchanged; the leash lets go
  on release and the spring settles as before.
- While fast, no face is marked `on_screen`, so `CartFaces::sync` never blocks. Faces are still
  requested in the same order and placed as they arrive; a cart without one draws as its
  label-coloured rectangle, which upstream already does for a face not built yet.
- Once a fast hold is let go and the row has settled (within 0.05 carts of the selection), the
  device loop logs one line:
  `slot: fast scroll: 412 frames, p50 16.72 p99 17.10 max 18.20 ms, period 16.72 ms, 380 with a placeholder, 0 empty`.
  Frame time is swap to swap, from the first fast frame to the last settle frame, so the release and
  the frame that waits for the visible faces again are in it. "With a placeholder" counts frames
  where a visible cart had no face; "empty" counts frames where the row drew nothing. It needs no
  trace flag.
- The logic lives in new files (`slot-ui/src/shelf/fast.rs`, a child of `shelf.rs` so it reads the
  hold state, `slot/src/app/fast_scroll.rs`, `slot/src/fast_scroll_trace.rs`). Upstream hunks: one
  `mod` line and two one-line changes in `shelf.rs`, one token in `face_wants`, three lines in
  `device_app.rs`.

## Consequences

- Long holds reach 60 carts a second; the Up/Down letter jump stays for coarse moves.
- While fast, most faces on the PS1 and SNES shelves show as placeholders. That is the intent: speed
  over art while moving.
- On release, `CartFaces::sync` blocks again for the visible faces not built yet (upstream
  behaviour at rest). On the PS1 shelf that may be one longer frame right after letting go. The log
  line includes it, so the max and p99 show it. If it fails the gate, the next step is to stay
  non-blocking until the row settles (one more condition in `face_wants`); that is the maintainer's
  call from the numbers, not done here.
- Generic, so it is an upstream candidate (ADR 0047), credited to marghost and stevolarn.
- Ported onto upstream main 1b20432 (ADR 0083) with no conflict: `Shelf::tick`, `Shelf::update` and
  `App::face_wants` are unchanged there. Upstream's remapping does not reach this path: Left and Right
  on the shelf are still the fixed D-pad (`GbaDown(Btn::Left/Right)` into `Shelf::hold_left/right`,
  released by `GbaUp`), and the left stick steering the D-pad (bfb8bb2) arrives the same way, so it
  scrolls fast too. The remappable shelf keys (`CarouselAction`: Previous Shelf, Next Shelf,
  Favorite) are matched first; a user who binds one of them to plain Left or Right gets that action
  instead of a hold, as upstream does, and so no fast scroll on that key.

## Device measurement (maintainer)

1. `task deploy:device`. Use a card with at least 200 carts on the SNES shelf and on the PS1 shelf
   (60 is the minimum for fast scroll). Run the GBA shelf too as a cheap-face control if it is long
   enough.
2. On each shelf: hold Right for 10 s, release, wait 2 s. Repeat 5 times. Do the same with Left once.
3. `adb shell grep 'slot: fast scroll:' /mnt/sdcard/Logs/slot.log` (or `task log:device | grep 'fast scroll'`).
   One line per hold.
4. Pass per shelf: on every line, p99 at most 1.1x the period (18.4 ms at 16.72), and `0 empty`.
   Record max and the placeholder count as numbers (placeholders are expected on PS1). A max well
   above the period with a good p99 is the release frame waiting for faces: note it per shelf.
5. Visual check: film one hold and release per shelf with a phone and look for a frame with no
   carts (there should be none) and a visible hitch on landing.
6. Baseline, if wanted: the same holds on the current build (no fast scroll) with
   `System/trace-latency.on` give `slot: frametime:` windows to compare against.
