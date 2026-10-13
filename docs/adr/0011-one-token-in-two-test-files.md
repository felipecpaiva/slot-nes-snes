# 0011. Add one token each to two upstream test files

- Status: Accepted, amended by [0013](0013-five-named-test-sites.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [patch 0002](../../patches/0002-platform-nes.patch), [patch 0005](../../patches/0005-platform-snes.patch), `scripts/check-upstream-tests.sh`

## Context

The helpers `label_band` in `chrome.rs` and `label_top` in `render_shelves.rs` match exhaustively
over `Platform`. A new variant cannot compile against them unchanged.

## Decision

`chrome.rs` gains `| Platform::Nes` and `render_shelves.rs` gains `| CartPlatform::Nes` on the
Game Boy arm; `Snes` follows later. `check-upstream-tests.sh` allows exactly these tokens.

## Consequences

- The first break of the literal "unmodified" bar, kept to one checked token per file.
- The guard compares each file byte for byte with the tokens removed.
- Folded into the five-site rule of [0013](0013-five-named-test-sites.md).
