---
title: "Add Platform::A7800 with its own shelf, scan, header handling and explicit policy"
phase: 14
area: platform
type: feature
size: M
depends_on: [155-a7800-core-build]
---

## Why
The 7800 shelf. All 73 of the maintainer's dumps are headerless (No-Intro); ProSystem finds headerless games by md5 in its own database (all 66 games match) and runs an unknown one as NTSC (tested).

## Scope
- [ ] `Platform::A7800` and `Core::Prosystem` (`as_str` `prosystem`), shelf `Games/A7800`, `.a78` headered (128 bytes, `ATARI7800` at offset 1) or not.
- [ ] Title from the header (offset 17, 32 bytes) when present, else the stem. Skip `[BIOS]`, `(Program)`, `Development Card`, `Diagnostic` and `High Score Cartridge` dumps by name.
- [ ] Policy as for A2600; core joins `dist:device`, `zip-check.sh`; licence files move to `licenses/`; `A7800` joins `games`.
- [ ] README row, docs/PLAN.md step.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `a7800_scan.rs` | headered and headerless files listed; BIOS and tool dumps skipped; header title used |
| (new) | `a7800_seat.rs` | a generated cart seats and publishes frames |

## Edge cases
| Case | Expected handling |
|---|---|
| A CC2 hack image (`>>` at offset 1) | The core refuses it; slot shows its load-failure toast |
| A headered file with a wrong size field | The core trusts the header; logged |

## Acceptance
- [ ] `task check` green; GBA harness 0 diffs.

## Device check (RG34XXSP)
Part of issue 170.

## References
- ADR 0095; docs/research/atari-plan.md
