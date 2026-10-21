---
title: "Test PICO-8 with generated text and PNG carts, and GBA after PICO-8"
phase: 19
area: tests
type: test
size: S
depends_on: [204-pico8-core-build]
---

## Why
The core contract and the GBA-unchanged rule each need their own tests.

## Scope
- [x] `pico8_common`: generated carts (our own Lua), a stored-deflate PNG writer for `.p8.png`.
- [x] Core half (patch 0127): `pico8_core.rs`.
- [x] Platform half (patch 0130): `pico8_then_gba.rs`; `resume_platform.rs` covers PICO-8.

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | `pico8_then_gba.rs` | a GBA game after a PICO-8 game gets the GBA only input and picture, rewind back on |

## Edge cases
| Case | Expected handling |
|---|---|
| FAKE-08 dylib missing | skip locally, fail under SLOT_REQUIRE_CORES=1 |

## Acceptance
- [x] T1 passes.

## Device check (RG34XXSP)
Issue 208.

## References
- ADR 0102
