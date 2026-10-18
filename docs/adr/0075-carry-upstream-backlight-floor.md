# 0075. Carry upstream 3b6349c, a backlight floor of 8/255, until the 1.8.0 rebase

- Status: Accepted. Backport, drop on the 1.8.0 rebase (0047)
- Date: 2026-10-18
- Deciders: maintainer (Felipe Paiva)
- Related: [ADR 0021](0021-reference-device-rg34xxsp.md), [ADR 0047](0047-upstream-first-fixes.md), [ADR 0013](0013-five-named-test-sites.md), patch `patches/0047-backlight-floor.patch`, upstream [3b6349c](https://github.com/BrandonKowalski/slot/commit/3b6349c) (issue #100), [fork review](../research/fork-review-2026-10-18.md)

## Context

v1.7.0 has `BACKLIGHT_FLOOR = 1.0` in `crates/slot-power/src/device.rs`: step 1 writes a raw 1 to
the backlight, which leaves the RG34XX panel black (upstream issue #100). Upstream fixed it after
v1.7.0 in 3b6349c: the floor is 8/255 of the kernel's maximum, at least 1. The same commit changes
four lines of its own `crates/slot-power/tests/device.rs`, and the v1.7.0 versions of three of its
tests fail against the new floor.

## Decision

Patch `backlight-floor` backports 3b6349c whole, the source and its test change. The maintainer
approved named test site (i) on 2026-10-18: in `crates/slot-power/tests/device.rs`, exactly the four
lines 3b6349c changes, checked byte for byte by `scripts/check-upstream-tests.sh`.

## Consequences

- Step 1 writes 8 of 255 (the steps are 0, 8, 14, 30, 52, 81, 117, 157, 204, 255).
- Upstream's own tests cover it; no test of ours is added.
- **On the 1.8.0 rebase, drop the patch and site (i)**: upstream ships both.
