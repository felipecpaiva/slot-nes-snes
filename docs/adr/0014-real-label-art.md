# 0014. Show real cartridge label art on carts, never a screenshot

- Status: Accepted. Amended by [0057](0057-sms-box-art-tall-well.md) and [0069](0069-ps1-jewel-case-shelf.md); Logo Only fallback implemented (amendment below)
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

## Amendment, 2026-10-18: the Logo Only fallback is implemented (patch 0048-logo-label)

The fallback is a tool output, not slot code: `tools/fetch-labels.py --by-name --logo-fallback` writes a
Logo Only PNG to `Labels/<SYSTEM>/<stem>.png` for a ROM every other pass left without a label, and the
shelf shows it like any label. slot's runtime is unchanged.

- Renderer: `crates/slot-ui/examples/logo_label.rs` (patch `0048-logo-label`, built by
  `task labels:logo-tool` to `build/slot/target/release/examples/logo_label`, `SLOT_LOGO_LABEL` overrides
  the path). It is Cart Studio's Logo Only style as ported by cloudwithax/unslot
  ([0b0f3a3](https://github.com/cloudwithax/unslot/commit/0b0f3a307da447d8d048425ab8e70a9fc4aeab43),
  `slot-ui/src/scraped.rs`), at `label_size` for the system and stem. unslot's box-art cover and box-art
  hue are left out (box art stays limited to ADRs 0057 and 0069); the ground's hue is the one slot gives
  the game's generated text label (`label_colour`).
- Logo: libretro-thumbnails `Named_Logos` (none exist for GBC, GG and PS1) matched by `title_key` under
  the by-name rules (one title, or for a cut name the one title starting with it), else the ScreenScraper
  `wheel` of the game the name pass or an `ss:` alias found. A hack takes a parent's logo only through
  `--aliases`. See [BY-NAME.md](../cart-art/BY-NAME.md).
