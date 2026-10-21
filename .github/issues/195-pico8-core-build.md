---
title: "Build FAKE-08 from a pinned commit for host and device with our source patch, and record its licence"
phase: 18
area: cores
type: feature
size: M
depends_on: [194-pico8-tracking]
---

## Why
FAKE-08 is the only libretro core that runs PICO-8 carts and is free software (MIT). At the pin it closes slot's stderr, writes cartdata only at cart close, asks for RGB565 where slot does not answer, drops half of the short presses of a 30 fps cart, can leave the game for its own cart browser, and its states are not reliable.

## Scope
- [x] `cores/lib.sh` gains `owner` (FAKE-08 is not under libretro) and `source_patch` (applied before both builds, in the stamp).
- [x] `cores/fake08/build.sh`, `cores/fake08/slot.patch`, `cores/fake08/glibc-2.17.h`; `SLOT_PIN` `fake08_*` and `fake08_z8lua_*`.
- [x] `task core:fake08:src`, `:host` and `core:device:fake08` (NEEDED libc and libm at GLIBC_2.17 or older).
- [x] LICENSING.md section, `licenses/fake08-LICENSE.md`, `fake08-z8lua-notices.txt`, `fake08-lodepng-LICENSE.txt`, `fake08-miniz-LICENSE.txt`; dist-device.sh, zip-check.sh, run-tests.sh and bench-device.sh list the core.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `pico8_core.rs` | text, `.p8.png` and PNG-named-`.p8` carts boot at 60 fps and 22050 Hz and draw 128x128 centred on the 240x160 canvas |
| C2 | `pico8_core.rs` | O is libretro B; cartdata reaches `cdata/` within a second through a temp file; the next game reads it |
| C3 | `pico8_core.rs` | stderr is the same file before and after a cartdata write |
| C4 | `pico8_core.rs` | every one-frame press reaches a 30 fps cart |
| C5 | `pico8_core.rs` | the pause menu ends on Reset Cart, which restarts the same cart; a runtime error stays on the error |
| C6 | `pico8_core.rs` | the core offers no state |

## Edge cases
| Case | Expected handling |
|---|---|
| A pin bump re-versions a libm symbol | `task core:device:fake08` fails |
| A pin bump moves a patched line | the patch fails to apply and the build stops |
| A cart calls `load()` for another cart | FAKE-08 resolves it in the cart's own folder |

## Acceptance
- [x] C1 to C6 pass with SLOT_REQUIRE_CORES=1; each was red against the unpatched core; the device core needs only libc and libm.

## Device check (RG34XXSP)
Issue 199.

## References
- ADR 0101
