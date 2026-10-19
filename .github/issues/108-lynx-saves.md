---
title: "Lynx saves: states only on Beetle Lynx, and say so"
phase: 12
area: platform
type: chore
size: S
depends_on: [103-platform-lynx]
---

## Why
Step 10. Beetle Lynx exposes only `SYSTEM_RAM` and has no EEPROM emulation at `fcdefcf` (pinned by `beetle_lynx_gives_the_frontend_no_save_ram`). The few carts that save to an EEPROM (mostly late and homebrew releases) lose progress except through states (ADR 0093).

## Scope
- [x] `save_ram_trusted` false for Lynx; no `.sav` is written (the core has none to give).
- [x] The resume state and the 60 s autosave are the save path; nothing extra.
- [x] README known gaps: "Lynx: states only, no EEPROM saves".
- If the maintainer picks Handy: EEPROM goes to `<save dir>/<name>.eeprom`, written only at `retro_reset` and `retro_deinit`. That is the NGP issue 75 shape (core-owned file, written late, non-atomic), so it takes the same answer: a per-platform save dir, an atomic publish and a flush by reload.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `lynx_core.rs` `beetle_lynx_gives_the_frontend_no_save_ram` | `save_ram()` is None |
| (new) | `lynx_seat.rs` | no `.sav` appears after a session; a resume state restores the game (BIOS-gated) |

## Edge cases
| Case | Expected handling |
|---|---|
| A player copies an `.eeprom` from another frontend | Ignored, documented |

## Acceptance
- [x] `task check` green; README line.

## Status
Landed as patch 0076-lynx-saves (2026-10-19): no code change was needed, the core exposes no save RAM so no `.sav` is ever written; `lynx_seat.rs` pins it with a real session (BIOS-gated).

## Device check (RG34XXSP)
Close the lid mid-game, reopen: resumes.

## References
- ADR 0012, 0072, 0093
