---
title: "Make Stretch the default picture mode for NES and SNES carts"
phase: 2
area: video
type: feature
size: S
depends_on: [09-canvas, 12-platform-snes]
---

## Why
On the RG34XXSP (720x480) NES and SNES show at an exact 2x with black bars at the sides, because slot's default picture mode is Actual. The maintainer tested GBA, NES and SNES on the device on 2026-10-12 and asked for NES and SNES to fill the screen by default. GBA already fills a 720x480 panel; GBA and GB must stay exactly as upstream (rule 1), so only the new platforms change.

## Scope
`patches/NNNN-default-stretch.patch` (numbered after the patches merged before it):
- [ ] `Platform::default_video_mode()` in `platform_policy.rs`: `Gba | Gb | Gbc => VideoMode::Actual` (upstream's default), `Nes | Snes => VideoMode::Stretch`.
- [ ] Where slot reads a cart's picture mode (`slot: crates/slot/src/video_mode.rs:32` `video_mode_for` and its callers), a cart with no line in `Config/video_mode.txt` takes its platform's default. A saved line always wins, so a user who switches a game back to Actual keeps that choice.
- [ ] Keep the change in new code: a platform-aware wrapper in a new file, and a one-token swap at the call site(s). `Config/video_mode.txt` format unchanged.

## Tests
| ID | File | Asserts |
|---|---|---|
| T50 | `slot/tests/nes_video_mode.rs` | A NES cart and a SNES cart with no saved mode read as Stretch; a saved `actual` line wins; GBA, GB, GBC with no line read as Actual |
| T51 | harness | GBA, GB, GBC 0 diffs (H1, H1G, H2, B1); H3's GBA part still equals H1 |

## Edge cases
| Case | Expected handling |
|---|---|
| NES and SNES stretched to 720x480 look about 40% wider than the original 8:7 picture | Accepted by the maintainer; the per-game picture toggle (L1/R1 on NES, SELECT+X on SNES from issue 15) switches back to Actual and the choice is saved |
| 4:3 devices (RG35XXSP, 640x427 window above the bezel) | Stretch fills the window above the bezel, like GB's Stretch does there |
| A user upgrading from upstream slot with no `video_mode.txt` lines for NES/SNES | NES and SNES start in Stretch; GBA and GB unchanged |

## Acceptance
- [ ] T50 green; harness 0 diffs; upstream tests unmodified.
- [ ] On the RG34XXSP a NES and a SNES game fill the screen on first launch, and switching one back to Actual survives a reboot.

## Device check (RG34XXSP)
Insert a NES cart and a SNES cart that were never played: both fill the screen. Toggle one to Actual, eject, reboot, insert again: it stays Actual.

## Review notes
- The default lives in policy, not in `video_mode.txt`: nothing is written to the card until the user toggles.
- The upstream `VideoMode::default()` stays Actual, so upstream tests and GBA/GB behaviour are untouched.

## References
- Maintainer's device test, 2026-10-12 (GBA, NES, SNES boot and play on the RG34XXSP)
- `slot: crates/slot/src/video_mode.rs`, `slot: crates/slot/src/app.rs` (picture mode toggle on L1/R1)
