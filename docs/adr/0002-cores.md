# 0002. Use fceumm and nestopia for NES, snes9x and snes9x2005_plus for SNES

- Status: Accepted
- Date: 2026-10-11
- Deciders: maintainer (Felipe Paiva)
- Related: [issue 04](../../.github/issues/04-fceumm-core-build.md), [issue 13](../../.github/issues/13-snes9x-core-build.md), [issue 19](../../.github/issues/19-alt-cores-build.md), [issue 20](../../.github/issues/20-core-picker-pairs.md), [patch 0003](../../patches/0003-core-fceumm.patch), [patch 0009](../../patches/0009-core-picker-pairs.patch), [RESEARCH.md](../RESEARCH.md), [LICENSING.md](../../LICENSING.md)

## Context

slot's core picker offers two cores per platform. The target is Anbernic H700 handhelds.
RESEARCH.md: every NES core is full speed on the A53, and fceumm has the widest mapper coverage.
snes9x is the SNES default on ROCKNIX, Knulli, muOS and NextUI; snes9x2005_plus has the same
licence and is faster.

## Decision

NES: fceumm (default) and nestopia (alternative). SNES: snes9x (default) and snes9x2005_plus
(alternative). These are the defaults on muOS, Knulli, ROCKNIX and NextUI for H700-class devices.

## Consequences

- Users get the cores they already know from other H700 firmwares.
- The snes9x family is licensed for non-commercial use only and is not GPL-compatible.
  LICENSING.md records the stance (a separate program loaded across the libretro C ABI) and the
  release ships its licence and source. Commercial redistribution is out of scope.
- Each core is built from a pinned commit with a sha256 in `SLOT_PIN`
  ([SUPPLY-CHAIN.md](../SUPPLY-CHAIN.md)), with `make platform=unix`, never `platform=arm64`.
- A GPL-clean SNES option (Beetle Supafaust) exists but is unverified on the H700.
