---
title: "Check lynxboot.img before a Lynx launch and toast instead of a silent black screen"
phase: 12
area: platform
type: feature
size: S
depends_on: [103-platform-lynx]
---

## Why
Step 5. With no `lynxboot.img`, or one under 512 bytes, Beetle Lynx loads the cart without an error and never draws (pinned by `lynx_core.rs`). The player sees a dark screen and no reason. slot must catch it before launch (ADR 0093).

## Scope
- [x] Before seating a Lynx cart, check `BIOS/lynxboot.img`: present, exactly 512 bytes, crc32 `0x0d973c9d` (the `[BIOS] Atari Lynx` entry in the core's own cart list; md5 `fcd403db69f54290b51035d82f835e7b`).
- [x] Missing, unreadable or the wrong size: do not launch; toast "Lynx needs BIOS/lynxboot.img" and leave the cart on the shelf. No resume attempt, no crash-guard mark (issue 67).
- [x] Right size, wrong checksum: launch and toast once per session ("lynxboot.img is not the known dump").
- [x] The check is one function shared by the shelf launch and the resume path, so a resumed Lynx game is checked too.
- [x] README: where the file goes, that slot never ships or fetches it, and that a 0-byte placeholder of the right name is treated as missing.
- If the maintainer picks Handy: missing or wrong BIOS launches on the HLE boot with a one-time toast instead of refusing.

## Tests
| ID | File | Asserts |
|---|---|---|
| (exists) | `lynx_core.rs` `with_no_bios_a_lnx_cart_loads_without_error_and_never_draws` | the failure the check prevents |
| (exists) | `lynx_core.rs` `a_bios_file_shorter_than_512_bytes_is_ignored_the_same_silent_way` | short file case |
| (new) | `lynx_bios.rs` | missing, 0-byte, 256-byte, wrong-crc and right files; the launch is refused or allowed and the toast text; runs with no real BIOS (synthetic files only) |

## Edge cases
| Case | Expected handling |
|---|---|
| `lynxboot.img` is a 0-byte placeholder | Missing |
| A 513+ byte file | Wrong size, refused (the core reads the first 512 only, but the known dump is exactly 512) |
| `LYNXBOOT.IMG` on a case-insensitive card | Found, the filesystem decides |

## Acceptance
- [x] `task check` green; the toast shows on the host render test.

## Status
Landed as patch 0072-lynx-bios (2026-10-19): the check sits in `App::insert`, which both the shelf launch and the boot resume go through; the toasts are their own list after the disc toasts.

## Device check (RG34XXSP)
Rename the BIOS away: launching shows the toast, no dark screen. Put it back: the game boots.

## References
- ADR 0093; `mednafen/lynx/rom.cpp` and `cart.cpp` at `fcdefcf`
