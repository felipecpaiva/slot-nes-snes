---
title: "Check the region's Sega CD BIOS before a launch and toast instead of a black screen"
phase: 13
area: platform
type: feature
size: S
depends_on: [114-platform-segacd]
---

## Why
Step 4. Genesis Plus GX opens one BIOS file per disc, picked by the region byte at 0x20b (0x64 Europe, 0xa1 Japan, anything else US). A missing file fails the load; a junk file of the right name loads and shows a black screen, because the core checks nothing but that the file opens (both pinned by `segacd_core.rs`). slot must say which file is missing and must hash what is there (ADR 0094).

## Scope
- [ ] The region of a disc: the file name tags `(USA)`, `(Europe)`, `(Japan)` first; else the byte at 0x20b of the data track for a `.cue` (first track file, raw or cooked) or `.iso`; else US (a `.chd` with no tag; reading it needs a hunk decode). For an `.m3u`, its first disc.
- [ ] Before seating, check `BIOS/bios_CD_U.bin`, `bios_CD_E.bin` or `bios_CD_J.bin` for that region: present and 131072 bytes, else refuse and toast "Sega CD needs BIOS/bios_CD_U.bin" (the region's name). No resume attempt, no crash-guard mark (issue 67).
- [ ] Right size, unknown md5: launch, toast once per session ("bios_CD_U.bin is not a known dump"). Known: U `854b9150240a198070150e4566ae1290`, E `e66fa1dc5820d254611fdcdba0662372`, J `278a9397d192149e84e820ac621a8edd` (GPGX libretro doc; the maintainer's files match). Decide whether the PicoDrive-doc US revision `2efd74e3...` is also known (boot it in GPGX first).
- [ ] If the guessed region was wrong (no tag, a `.chd`) the core's load failure still lands on the same toast, naming all three files.
- [ ] One function shared by the shelf launch and the resume path.
- [ ] README: where the files go, that slot never ships or fetches them.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `segacd_core.rs` `a_sega_cd_disc_with_no_bios_is_refused` | the failure the check names |
| (exists) | `segacd_core.rs` `the_region_byte_at_0x20b_picks_the_bios_file_the_core_opens` | the core's pick the check mirrors |
| (new) | `segacd_bios.rs` | region from tags, from a raw and a cooked 0x20b, default US; missing, 0-byte, short and unknown-md5 files; refusal and toast text; synthetic files only |

## Edge cases
| Case | Expected handling |
|---|---|
| A 0-byte placeholder (muOS ships some) | Missing |
| `(USA, Europe)` tag | The 0x20b byte decides, else US |
| `BIOS_CD_U.BIN` on a case-insensitive card | Found, the filesystem decides |

## Acceptance
- [ ] `task check` green; the toast shows on the host render test.

## Device check (RG34XXSP)
Rename `bios_CD_U.bin` away: a US game shows the toast, no black screen. Put it back: it boots.

## References
- ADR 0094; `core/loadrom.c` `get_region` (line 1065) and `load_bios` (line 394) at `393f70c`; Lynx issue 104 (same shape)
