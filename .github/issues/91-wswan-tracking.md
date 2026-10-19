---
title: "WonderSwan: WonderSwan and WonderSwan Color on Beetle Cygne, built the NES and SNES way"
phase: 11
area: device
type: tracking
size: L
depends_on: [56-ps1-tracking]
---

## Why
The 2026-10-18 fork review lists WonderSwan and WonderSwan Color (item 18; fourth in docs/research/fork-nelynes.md's ranking). Horizontal games are a 3x fit on the 480-line panel, vertical ones a 2x fit drawn upright by the core, no BIOS, saves through the ordinary `.sav` path. One core, Beetle Cygne pinned at `4b01295`, one shelf `Games/WS` (ADR 0092). The plan is docs/research/wswan-plan.md.

## Scope
Child work, in merge order:
- [x] 1. Decision record: ADR 0092 and these issues.
- [x] 2. 92-wswan-core-build (groundwork, on the v1.7.0 base)
- [x] 3. 97-wswan-tests, core half: patch 0064 (groundwork; the platform half grows with each step below)
- [x] 4. 93-platform-wswan, saves included (on the main 1b20432 base, like everything below): patch 0065
- [x] 5. 94-wswan-options: patch 0066
- [x] 6. 95-wswan-canvas-screen: patch 0067 (the per-game canvas seam and the Shader and Picture rows came in 0065, the PS1 split)
- [x] 7. 96-wswan-input: patch 0068
- [x] 8. 98-wswan-carts: patch 0069 and tools/fetch-labels.py
- [ ] 9. 99-wswan-device-gate

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | Each step owns its tests |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Owned by the child issue that touches that layer |

## Acceptance
- [ ] Steps 4 to 8 done on the host; `task check` green with `SLOT_REQUIRE_CORES=1` and the mednafen_wswan dylib.
- [x] Harness: a WonderSwan game, eject, GBA leg equals the GBA-only run (`wswan_then_gba.rs`, a vertical game first); `bench:compare` GBA within 2%.
- [ ] README, docs/PLAN.md and LICENSING.md say WonderSwan shipped, with the nelynes/slotPlus and cloudwithax/unslot credits of ADR 0092.

## Device check (RG34XXSP)
Issue 99.

## Review notes
- Nine issues, not ten: `scripts/setup-github-project.py` globs two-digit stems, so there is no issue 100. Saves are part of 93 because Cygne uses the ordinary `.sav` path (plan section 6).
- slot#30: no more systems upstream. Only generic seams go upstream (ADR 0047).
- Phase 11 is new: `scripts/setup-github-project.py` now lists "Phase 11: WonderSwan", which the board's Phase field gets on the next sync. No `numbers.json` entries until then.
- Written beside the NGP (issues 70 to 79, its own branch) and TG16 (issues 81 to 90) groundwork branches, while another branch ports the patch set to upstream 1.8.0. Steps 4 on wait for that base; issue numbers 91 to 99, ADR 0092, patch 0064 and the phase number may be renumbered at merge.

## Decisions taken while implementing
- The SELECT flip of a vertical game lasts for the session; every boot starts upright. "Remembered per cart" named no mechanism, so nothing is persisted yet (a `Saves/WS/<stem>.view` file like PS1's `.disc` would be the shape if wanted).
- Stretch keeps the 8-line borders above and below a horizontal picture (`stretch_crops_height` false, as issue 93 lists).
- No new outline words in `Config/cart_shell.txt` for the two shells; a colour line still applies.

## References
- ADR 0092; docs/research/wswan-plan.md; docs/research/fork-nelynes.md section 2
