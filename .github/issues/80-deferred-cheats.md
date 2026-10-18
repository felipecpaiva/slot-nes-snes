---
title: "DEFERRED: Per-game cheats from the libretro cheat database"
phase: 6
area: platform
type: chore
size: L
depends_on: [32-phase-6-deferred]
---

## Why
**Deferred.** The maintainer asked for an evaluation of built-in per-game cheats (2026-10-18). The research is in [docs/research/cheats.md](../../docs/research/cheats.md). Cheats are a PLAN.md non-goal (line 58) and upstream declined them (slot issue #8), so going ahead needs an ADR that amends the non-goal, and every line stays our rebase cost.

## Summary of the research
- Effort: about 15 to 22 dev days for the full feature; a first cut of about 1.5 weeks (NES, SNES, Sega; exact CRC matching; an in-game Cheats list hidden unless the game has a cheat file; off by default).
- Database: libretro-database `cht/`, CC BY-SA 4.0, matched through the No-Intro names the label fetcher already resolves. Coverage on the library: GBC 56%, NES 52%, GG 72%, SMS 64%, MD 45%, SNES 35%, GBA 17%; ROM hacks almost none; PS1 needs serial matching.
- Cores: all shipped cores implement `retro_cheat_set` except mednafen_ngp. A small per-core layer is needed: snes9x and nestopia overflow a 256-byte buffer on long codes, snes9x2005_plus does not split multi-part codes, mGBA ignores the enable flag, gpsp takes Code Breaker only (max 20), genesis_plus_gx max 150.
- Delivery: a Mac tool copies only matched cheat files (no bundling in the zip).
- UX: needs either a new named upstream test site for an in-game row or a user-assigned shortcut on upstream's remapping.

## Scope
Not started. Work items C1 to C11 are listed in the research doc.
