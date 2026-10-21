---
title: "Add Platform::SegaCd with its own shelf, disc scan and explicit policy"
phase: 21
area: platform
type: feature
size: M
depends_on: [216-segacd-tracking]
---

## Why
Step 3. Sega CD gets its own shelf and folders like every system (ADR 0104). The core is Genesis Plus GX, already in `Core::EVERY`, so there is no core work: this is the `Platform` half only.

## Scope
- [x] `Platform::SegaCd` appended to `SHELVES`; upstream `ALL` untouched; every policy method answered explicitly (the ADR 0063 rule). `core()` is `Core::GenesisPlusGx`, no picker.
- [x] Folders `Games/SEGACD`, `Saves/SEGACD`, `States/SEGACD`, `Labels/SEGACD`; shelf title "Sega CD".
- [x] Scan `.chd`, `.cue`, `.m3u` and `.iso`. A `.bin` (a track), `.wav` and Mac resource files are never games. A playlist hides the discs it names (the PS1 code).
- [x] Discs named `(Disc N)` with no playlist get a generated `.m3u` holding paths **relative to the playlist** (GPGX joins every line to the playlist's directory, pinned by `segacd_core.rs`), lowercase `.m3u` (the core reads only that), 4 discs at most.
- [x] Policy answers as Mega Drive where the picture and pad are concerned (`owns_shoulders` false, canvas as issue 220).
- [x] Joins `zip-check.sh`'s `games` list; README row added with the phase.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done, 0136) | `slot-store/tests/segacd_platform.rs` | the extensions; `.bin` and `._x.chd` are not games; an m3u hides its discs; generated playlist lines are relative and the file is lowercase `.m3u` |
| (done, 0140) | `segacd_saves.rs` session tests | a shelf launch of a synthetic disc (dummy BIOS) plays through `Platform::SegaCd` |

## Edge cases
| Case | Expected handling |
|---|---|
| `X.cue` and `X.chd` side by side | Both listed (the PS1 rule; the user keeps one) |
| A `.cue` whose `.bin` is missing | Listed; the load fails with a toast, not a crash |
| A 5-disc set | The core reads the first 4 (no such set in the library) |
| A Mega Drive `.bin` dropped into `Games/SEGACD` | Not listed |

## Acceptance
- [x] `task check` green; GBA harness compare 0 diffs.

## Device check (RG34XXSP)
The shelf lists the maintainer's 62 `.chd` files with the right titles.

## References
- ADR 0059, 0063, 0104; patch 0034 (PS1 scan and playlists); docs/research/segacd-plan.md sections 1 and 6
