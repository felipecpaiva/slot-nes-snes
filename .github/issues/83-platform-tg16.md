---
title: "Add Platform::Tg16 with its own shelf, scan and explicit policy"
phase: 10
area: platform
type: feature
size: M
depends_on: [82-tg16-core-build]
---

## Why
Step 4. The shelf and the core enum, the PS1 and NGP way: appended to our lists, upstream's `ALL` and tests untouched (ADR 0009, 0013, 0015, 0091).

## Scope
- [ ] `Platform::Tg16` appended to `SHELVES`; `Core::MednafenPceFast` (`as_str` `mednafen_pce_fast`) appended to `EVERY`; every policy method answered explicitly (no wildcard arm).
- [ ] Shelf `Games/TG16`, scan `.pce` only (no `.sgx`, no `.cue`/`.ccd`/`.chd`/`.toc`/`.m3u`), title from the file stem. `Saves/TG16`, `States/TG16`, `Labels/TG16` created on first boot like the other platforms.
- [ ] Core open: BIOS dir as for every core (none needed); `need_fullpath` load (ADR 0059).
- [ ] Join `scripts/dist-device.sh` and `scripts/zip-check.sh`: cores list, `req` and `ok` lists, licence files (move `cores/mednafen_pce_fast/*.txt` to `licenses/`), the strings pair `mednafen_pce_fast:Beetle.PCE.Fast`, `TG16` in `games`, the source tarball sha256 pair.
- [ ] Named test sites gain the TG16 tokens (ADR 0055); CONTRIBUTING.md in the same patch.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `tg16_platform.rs` | `.pce` lands on the TG16 shelf, `.sgx` and `.cue` do not; dirs created; every policy method answered |
| (new) | `zip-check.sh` | the release holds the core, its `.meta`, source and both licence files |

## Edge cases
| Case | Expected handling |
|---|---|
| A headered `.pce` (512-byte copier header) | Scanned like any other; the core strips the header |
| A `.cue` in `Games/TG16` | Not scanned (CD out of scope) |

## Acceptance
- [ ] `task check` green; GBA harness compare 0 diffs.

## Device check (RG34XXSP)
The shelf shows on the device (issue 90).

## References
- ADR 0009, 0013, 0015, 0055, 0059, 0063, 0091; docs/research/tg16-plan.md section 6
