# 0084. Keep a cart whose last start never finished on the shelf

- Status: Accepted. Amended by [0109](0109-rebase-to-slot-v1-9-0.md): upstream's loading mark (v1.9.0) replaced the detection, only the banner and the selected cart are ours
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0047](0047-upstream-first-fixes.md), issue 67 (#130), patch `patches/0052-crash-guard.patch`, oauramos/omega-zero be6eb11 (the idea), upstream PR text in [docs/contributions/upstream-crash-guard-pr.md](../contributions/upstream-crash-guard-pr.md)

## Context

Upstream v1.7.0 puts the last cart back in the slot on every boot (`App::start`, then
`Session::boot_with` opens its core at once). A game that crashes slot while it starts (core load,
resume state load, first frames) crashes it again on the next boot, and the next: a boot loop. A
single-cart card is the worst case, since it never shows the shelf. PS1 makes a bad start more
likely. Upstream main 1b20432 (24 commits past v1.7.0, our base since ADR 0083) logs a crash's signal (`crash.rs`, already in
v1.7.0) and moves a refused resume state aside (f8703a0, in v1.7.0), but has no guard against a
crashing start, so there is nothing to backport.

## Decision

- `Session::spawn_core` writes `Config/starting.txt` with one line, `<platform dir>/<stem>` (for
  example `GBA/Emerald`), synchronously, before it opens the core. The core loads on its own
  thread, so a deferred write could lose the race with the crash.
- The mark is removed once the game has published 300 frames (about 5 seconds), or as soon as a
  resume state is written for the seated cart (`flush_resume` on eject, power tap or doze, and the
  autosave), since either proves the game ran.
- At boot, `App::start` reads the mark. If it names the cart it would put back (stem and platform
  both match), that cart is selected on the shelf instead, the banner "Last start failed" shows,
  and `slot: start guard: <line> did not finish its last start, kept on the shelf` is logged. This
  covers the single-cart branch too (upstream already allows a single cart on the shelf, see
  `a_single_cart_that_will_not_load_falls_back_to_the_shelf`).
- Nothing is deleted: the resume state stays where it is, and the mark and `state.cart` stay as
  they are, so a power cycle before the player acts lands on the shelf again instead of looping.
  The player can tap A to try the resume again or hold A to start clean (upstream's clean start).
  The next start writes a new mark.
- A core that reports `Failed` leaves the mark down too. That boot already falls back to the
  shelf; the next boot then also shows the shelf with the banner, which is true ("Last start
  failed"), rather than retrying a core that just failed.
- No fsync: the target is a process crash, after which the kernel still writes the file. A kernel
  hang with a power cut may lose the mark and cost one more crash.
- Code: `crates/slot/src/app/start_guard.rs` (mark, settle, check) and
  `crates/slot-ui/src/start_toast.rs` (the banner's place). Upstream files get one-line hooks:
  `app.rs` (mod line, one field, the check in `start`, a call in `flush_resume` and `autosave`),
  `session.rs` (mark in `spawn_core`, settle in `update`), `toast.rs` (variant, index, text). The
  banner sits after the battery banners and before the disc banners in `Toast::every()`, so
  `disc_index` gains 1; `Toast::all()` stays upstream's list.

## Consequences

- `crates/slot/tests/crash_guard.rs`: a mark left by a start that never ran frames keeps the cart
  selected on the shelf with the banner; the resume state is untouched; a second boot still shows
  the shelf; a start that publishes 300 frames resumes on the next boot with no banner; a flush
  before 300 frames also clears the mark; the mark holds back only the cart it names; the banner
  has its own place in `Toast::every()`.
- Edge case: a power loss in the first 5 seconds of a start, before any flush, costs one resume
  (the next boot shows the shelf with the banner, then all is normal).
- On the 1.8.0 base, `spawn_core` opens the core on a `slot-open` thread (upstream a1c3314); the
  mark line still goes right after the `opening {stem}` launch line, before that thread starts.
- **Drop the patch when the upstream PR lands.**
