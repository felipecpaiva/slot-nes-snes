---
title: "Add Platform::Ps1 with its own shelf, disc scan and explicit policy"
phase: 8
area: platform
type: feature
size: M
depends_on: [57-ps1-core-build]
---

## Why
Step 5. The PS1 shelf, the way NES, SNES and the Sega systems were added (ADR 0063).

## Scope
- [ ] `Platform::Ps1` in `SHELVES` (not `ALL`), `Core::PcsxRearmed` in `EVERY`, folders `Games/PS1`, `Labels/PS1`, `Saves/PS1`, `States/PS1`.
- [ ] Every policy method answers explicitly: `owns_shoulders`, `turbo_mode`, `shader_choices`, `picker_cores` (one core, no picker, as ADR 0053), `canvas`, and the new `owns_triggers`, `rewind`, `disc_control`.
- [ ] Scan in our own `ps1_*` module: `.chd`, `.cue`, `.pbp`, `.m3u` listed; `.bin` never a game; files a `.cue` or `.m3u` names are hidden; `(Disc N)` and `(Disc N of M)` grouped into one game with a generated `.m3u`; `._` files skipped. Trim `.m3u` lines the same way in scan and load. Log and skip an unreadable `.m3u`.
- [ ] Title from the stem without the `(Disc N)` tag. Placeholder flat case until issue 64.
- [ ] Named test sites (b) and (e) take `Platform::Ps1` and `Core::PcsxRearmed` by the standing rule (ADR 0055).
- [ ] Credit: tray (AaronC1990) and omega-zero (oauramos) for the grouping rules, bently0602 for the trimming.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot-store/tests/ps1_scan.rs` | cue hides its bins; m3u hides its discs; Disc N grouping; `.bin` alone is not a game; spaces in m3u lines |
| (new) | `slot/tests/ps1_*.rs` | a card with `cart_platform=ps1` boots to the shelf on upstream (downgrade) |

## Edge cases
| Case | Expected handling |
|---|---|
| m3u names a missing disc | Game listed, load fails with a toast, nothing panics |
| Over 8 discs | Refused at load (pcsx `disks[8]`), logged |

## Acceptance
- [ ] Tests green, `task check` green, touch-point map regenerated.

## Device check (RG34XXSP)
The maintainer's PS1 folder scans with no duplicate entries.

## References
- ADR 0053, 0055, 0063; docs/research/ps1-plan.md section 3
