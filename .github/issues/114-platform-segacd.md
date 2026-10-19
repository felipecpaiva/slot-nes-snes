---
title: "Add Platform::SegaCd with its own shelf, disc scan and explicit policy"
phase: 13
area: platform
type: feature
size: M
depends_on: [113-segacd-tracking]
---

## Why
Step 3. Sega CD gets its own shelf and folders like every system (ADR 0094). The core is Genesis Plus GX, already in `Core::EVERY`, so there is no core work: this is the `Platform` half only.

## Scope
- [ ] `Platform::SegaCd` appended to `SHELVES`; upstream `ALL` untouched; every policy method answered explicitly (the ADR 0063 rule). `core()` is `Core::GenesisPlusGx`, no picker.
- [ ] Folders `Games/SEGACD`, `Saves/SEGACD`, `States/SEGACD`, `Labels/SEGACD`; shelf title "Sega CD".
- [ ] Scan `.chd`, `.cue`, `.m3u` and `.iso`. A `.bin` (a track), `.wav` and Mac resource files are never games. A playlist hides the discs it names (the PS1 code).
- [ ] Discs named `(Disc N)` with no playlist get a generated `.m3u` holding paths **relative to the playlist** (GPGX joins every line to the playlist's directory, pinned by `segacd_core.rs`), lowercase `.m3u` (the core reads only that), 4 discs at most.
- [ ] Policy answers as Mega Drive where the picture and pad are concerned (`owns_shoulders` false, canvas as issue 117).
- [ ] Joins `zip-check.sh`'s `games` list; README row moves from planned to shipped at the end of the phase, not here.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `slot-store/tests/segacd_platform.rs` | the extensions; `.bin` and `._x.chd` are not games; an m3u hides its discs; generated playlist lines are relative and the file is lowercase `.m3u` |
| (new) | `segacd_emu.rs` | a shelf launch of a synthetic disc (dummy BIOS) reaches the core through `Platform::SegaCd` |

## Edge cases
| Case | Expected handling |
|---|---|
| `X.cue` and `X.chd` side by side | Both listed (the PS1 rule; the user keeps one) |
| A `.cue` whose `.bin` is missing | Listed; the load fails with a toast, not a crash |
| A 5-disc set | Playlist of the first 4, logged (core limit) |
| A Mega Drive `.bin` dropped into `Games/SEGACD` | Not listed |

## Acceptance
- [ ] `task check` green; GBA harness compare 0 diffs.

## Device check (RG34XXSP)
The shelf lists the maintainer's 62 `.chd` files with the right titles.

## References
- ADR 0059, 0063, 0094; patch 0034 (PS1 scan and playlists); docs/research/segacd-plan.md sections 1 and 6
