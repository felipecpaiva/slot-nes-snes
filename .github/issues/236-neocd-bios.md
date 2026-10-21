---
title: "Choose the Neo Geo CD model and check its BIOS before a disc starts"
phase: 23
area: platform
type: feature
size: S
depends_on: [235-platform-neocd]
---

## Why
NeoCD boots its incomplete built-in BIOS without a word when none is found, and it names a BIOS by file and model.

## Scope
- [x] BIOS row in the Neo Geo CD section: CDZ (default), Front Loader, Top Loader in `Config/neocd.txt`, hidden in game, sent as `neocd_bios` before the load.
- [x] Check `BIOS/neocd/<file>`: 524288 bytes and the System.dat crc32; missing refuses with a toast, unknown launches with a toast once a session; a resumed disc is checked too.

## Tests
| ID | File | Asserts |
|---|---|---|
| B1 | `slot/tests/neocd_bios.rs` | files, crcs and option values; NeoCD declares exactly those values |
| B2 | `slot/tests/neocd_bios.rs` | missing, short, long and unknown files; the other models do not stand in; resume is checked |
| B3 | `slot/tests/neocd_bios.rs` | the row walks both ways into `neocd.txt`, the check follows it, the model is sent before the load, the row is hidden in game |
| B4 | `slot/tests/neocd_bios.rs` | the toasts upload after the Sega CD ones |

## Edge cases
| Case | Expected handling |
|---|---|
| A resume state from another model | loads: the state carries the BIOS ROM |

## Acceptance
- [x] B1 to B4 pass (the known-dump tests skip without `SLOT_NEOCD_BIOS`).

## Device check (RG34XXSP)
Issue 238.

## References
- ADR 0106; ADR 0104 (the check shape)
