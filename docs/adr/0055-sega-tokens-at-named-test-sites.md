# 0055. Widen named test sites (b) and (e) for the Sega platforms and Genesis Plus GX

- Status: Accepted. Amends [0013](0013-five-named-test-sites.md)
- Date: 2026-10-16
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 50](../../.github/issues/50-sega-tracking.md), [ADR 0053](0053-genesis-plus-gx-for-sega.md), [patch 0024](../../patches/0024-platform-gg.patch), `scripts/check-upstream-tests.sh`, CONTRIBUTING.md section 1

## Context

`Platform::Gg`, `Platform::Sms` and `Platform::Md` and `Core::GenesisPlusGx` are new enum
variants. Two upstream test files hold exhaustive matches over those enums, so they stop
compiling without one new token each: `label_band` in `crates/slot-ui/tests/chrome.rs` (site b)
and the colour-correction match in `crates/slot/tests/gpsp.rs` (site e). No other change to
those tests makes them compile, and neither test runs a Sega cart.

## Decision

- Site (b): the Game Boy arm, which already carries `| Platform::Nes | Platform::Snes`, gains
  `| Platform::Gg`, `| Platform::Sms` and `| Platform::Md`, in that order, on the same line.
- Site (e): the `Core::Mgba` arm gains `| Core::GenesisPlusGx` after `| Core::Snes9x2005Plus`.
- Both are the standing rule of CONTRIBUTING section 1 (a new variant token appended to an
  existing arm of an exhaustive match). `check-upstream-tests.sh` checks each one byte for byte
  after the tokens are removed.

## Consequences

- The two upstream tests compile and run unchanged in what they assert.
- A reflowed arm or a token in another arm still fails the guard.
- On each rebase, recheck the two lines as for the NES and SNES tokens.
