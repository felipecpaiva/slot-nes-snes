# 0017. Put thumb::png_sized in a new file

- Status: Accepted
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 09](../../.github/issues/09-canvas.md), [patch 0004](../../patches/0004-canvas.patch)

## Context

Save-state thumbnails must encode the 360x240 canvas (`emu.rs:884`). CONTRIBUTING.md section 3
says new code goes in new files.

## Decision

`thumb::png_sized` lives in the new file `thumb_sized.rs`. `thumb.rs` gets one `pub use` line so
the path `thumb::png_sized` still holds.

## Consequences

- Upstream's `png` is unchanged; the upstream hunk is one line.
- T11 checks a 360x240 thumbnail round-trips.
