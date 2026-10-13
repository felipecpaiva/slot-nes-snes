# 0012. Change durability.rs's unknown platform example from nes to pce

- Status: Accepted, amended by [0013](0013-five-named-test-sites.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0002](../../patches/0002-platform-nes.patch), `scripts/check-upstream-tests.sh`

## Context

Upstream's `durability.rs` used `cart_platform=nes` as an example of an unknown platform. NES is
now real and must resume from `cart_platform=nes`.

## Decision

That one value becomes `cart_platform=pce`. `check-upstream-tests.sh` allows only that value.

## Consequences

- `pce` is a system this project will never add.
- The standing rule in CONTRIBUTING.md now says any further value swap like this one stops and asks
  the maintainer.
- Folded into [0013](0013-five-named-test-sites.md).
