---
title: "Swap PS1 discs, remember the disc per game and record it in states"
phase: 8
area: platform
type: feature
size: M
depends_on: [60-ps1-canvas-screen]
---

## Why
Step 8. Multi-disc games cannot be finished without a swap (ADR 0067).

## Scope
- [x] Answer `SET_DISK_CONTROL_INTERFACE` (13), `GET_DISK_CONTROL_INTERFACE_VERSION` (57, answers 1) and `SET_DISK_CONTROL_EXT_INTERFACE` (58). Interface in `HostExtra`, `// SAFETY:` on every core call.
- [x] Swap: tray open, set index, tray close; roll back to the old index when refused or out of range (bently0602), toast on failure.
- [x] `Saves/PS1/<stem>.disc` written on swap; `set_initial_image` before `load_game` (tray, omega-zero).
- [x] State trailer for multi-disc games: `SLOTPSX1` plus u32 LE index, stripped and applied before `retro_unserialize`; no trailer loads on the current disc; unknown version refused.
- [x] A swap row: pick a menu home that does not widen `QuickRow::PLAY_SCREEN`; if none fits, ask the maintainer for a named test site. Built as the SELECT+L2 chord, no test site needed (ADR 0067 amendment); a menu row stays open for the maintainer.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot/tests/ps1_discs.rs` | swap 0 to 1; out-of-range swap refused and index kept; resume on disc 2 from the `.disc` file; a disc 1 state loaded on disc 2 swaps back to disc 1; single-disc state has no trailer |

## Edge cases
| Case | Expected handling |
|---|---|
| `.disc` file corrupt | Disc 1, logged |
| State from before this patch | Loads on the current disc |

## Acceptance
- [x] Tests green with generated two-disc ISOs and HLE BIOS.

## Device check (RG34XXSP)
A real multi-disc game swapped to disc 2, saved, quit and resumed on disc 2.

## References
- ADR 0009, 0067
