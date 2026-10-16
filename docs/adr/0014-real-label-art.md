# 0014. Show real cartridge label art on carts, never a screenshot

- Status: Accepted. Amended by [0057](0057-sms-box-art-tall-well.md) and [0069](0069-ps1-jewel-case-shelf.md)
- Date: 2026-10-12
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 40](../../.github/issues/40-cart-studio-nes-snes.md), [issue 41](../../.github/issues/41-label-fetcher-cli.md), [PLAN.md](../PLAN.md) Phase 4, slot discussion #64

## Context

The shelf should mirror the physical carts. slot's Cart Studio (GPL-3.0-or-later) produces real
labels for GB, GBC and GBA only. Label art is Nintendo's.

## Decision

Carts show the real cartridge label art, never a screenshot. NES and SNES get a Cart Studio
equivalent. The owner was asked on slot #64 whether it lands as a PR to slot-cart-studio or a
credited fork. A user-side fetch script (issue 41) is the fallback.

## Consequences

- No Nintendo art is ever committed to any of our repos. Labels are fetched at user time.
- With no label texture the fallback is Logo Only (a logo on a generated ground), never a
  screenshot or box art.
- Issue 40 starts only after the owner's answer and records it.
