---
title: "Add Platform::Neocd with its options, Screen section, saves and the Neo Geo pad"
phase: 23
area: platform
type: feature
size: M
depends_on: [234-neocd-core-build]
---

## Why
Every system gets its own shelf, Screen section and saves.

## Scope
- [x] `Platform::Neocd` after `SegaCd`, `Core::Neocd` after `MednafenSupergrafx`; `Games/NEOCD` for `.cue` and `.chd`; every policy answered explicitly, the Neo Geo shelf's input.
- [x] NeoCD options: CDZ, USA, speed hack and load skip on, shared backup RAM file off, 1:1, no overclock.
- [x] Backup RAM in `Saves/NEOCD/<stem>.sav`, blank for a first insert; rewind off (about 8 MB states).
- [x] Screen section: Shader (`Config/neocd_shader.txt`) and Picture (Stretch, Actual, 4:3); `RELEASED` 1994-09-09.
- [x] Upstream test sites (b), (e), (g), (h) gain the Neo Geo CD tokens.

## Tests
| ID | File | Asserts |
|---|---|---|
| P1 | `slot-store/tests/neocd_platform.rs` | shelf, scan, core, policy like the Neo Geo, resume, shader file |
| P2 | `slot/tests/neocd_platform.rs` | options declared, Screen rows, picture walk, folders, backup RAM survives eject, a first insert gets blank backup RAM, pad, in-game shader, release date |

## Edge cases
| Case | Expected handling |
|---|---|
| Another game's `neocd.srm` in `BIOS/neocd/` | never reaches the game (P2) |

## Acceptance
- [x] P1 and P2 pass.

## Device check (RG34XXSP)
Issue 238.

## References
- ADR 0107; ADR 0099
