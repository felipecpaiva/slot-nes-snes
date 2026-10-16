# 0045. Run upstream's layout frame-hash tests in both trees

- Status: Accepted. Amends [0035](0035-runner-sensitive-tests-info-on-ci.md)
- Date: 2026-10-15
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0038](0038-rebase-to-slot-v1-7-0.md), `scripts/run-tests.sh`

## Context

slot v1.7.0 adds `crates/slot-gfx/tests/layout.rs`. Two of its tests
(`a_framed_frame_on_a_4_by_3_panel_is_todays_frame` and
`a_framed_frame_after_a_native_one_is_todays_frame_again`) compare a frame hash pinned on
upstream's machine. They fail on the unpatched v1.7.0 tree on the M5 Max too (hash 0xb8a0bd32...
against 0xe3b9652d...), with `cargo test` and with `--test-threads=1`.

## Decision

`run-tests.sh` leaves `slot-gfx:layout` out of the gating run and runs it in
`build/slot-upstream` and `build/slot`; it fails only if the patched tree fails a test the
upstream tree passes. Upstream tests stay unmodified.

## Consequences

- A GPU where both pass makes the check a plain gate again; one where upstream fails cannot hide
  a patched failure of the other eight tests.
- Costs one extra build of the layout binary in the upstream tree.
