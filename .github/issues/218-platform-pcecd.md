---
title: "Add Platform::Pcecd with its options, Screen section, saves and the TurboGrafx-16 pad"
phase: 21
area: platform
type: feature
size: M
depends_on: [217-pcecd-core-build]
---

## Why
The PC Engine CD needs its own shelf, `Games/PCECD`, every policy answered explicitly, and the shelf quality bar: Screen section, saves, states, rewind, the pad.

## Scope
- [x] `Platform::Pcecd` appended to `SHELVES`; `.cue`, `.chd`, `.ccd`, titled by stem; Saves, States and Labels folders made at boot; release date 4 December 1988 in `RELEASED`.
- [x] `Core::MednafenPceFast` runs the TurboGrafx-16 and the PC Engine CD; the list answers `pce_fast_cdbios` "System Card 3" and `pce_fast_cdimagecache` disabled.
- [x] Screen section: Shader (retro list, `Config/pcecd_shader.txt`) and Picture (Crop default, Stretch, Actual, 4:3, `pcecd`).
- [x] Input: the TurboGrafx-16 pad, X and Y as turbo.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `slot-store/tests/pcecd_platform.rs` | shelf, extensions, track files skipped, TG16 shelf unchanged, core, policies equal to TG16, rewind on, resume, shader file |
| P2 | `slot/tests/pcecd_platform.rs` | CD options answered with declared values, a disc boots through slot's open path, Screen rows, shader and picture walks, folders, release row |
| P3 | `slot/tests/pcecd_platform.rs` | backup RAM `.sav` round trip through Saves/PCECD, the 2 KB sav on eject, the pad |

## Edge cases
| Case | Expected handling |
|---|---|
| A `.chd` on the TG16 shelf | skipped there |
| `.bin`, `.img`, `.sub`, `.m3u` on the CD shelf | never shown |

## Acceptance
- [x] P1 to P3 pass.

## Device check (RG34XXSP)
Issue 221.

## References
- ADR 0104
