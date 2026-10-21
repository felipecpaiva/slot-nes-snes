---
title: "Test the SuperGrafx with a generated HuCard on Beetle SuperGrafx"
phase: 20
area: tests
type: test
size: S
depends_on: [210-sgx-core-build]
---

## Why
Every core fact the platform builds on needs a test that fails when it breaks, without a commercial ROM.

## Scope
- [x] `sgx_common/mod.rs`: the TurboGrafx-16 HuCard as `.sgx` or `.pce`, and the work RAM size read from the core.
- [x] Core half (patch 0131): `sgx_core.rs`. Platform half (patches 0132 and 0133): `sgx_platform.rs` in slot-store and slot, `sgx_card.rs`.

## Tests
| ID | File | Asserts |
|---|---|---|
| T1 | `sgx_core.rs` | C1 and C2 of issue 210 |
| T2 | `sgx_platform.rs`, `sgx_card.rs` | P1 to P3 of issue 211, A1 of issue 212 |

## Edge cases
| Case | Expected handling |
|---|---|
| The dylib is missing | skip locally, fail under SLOT_REQUIRE_CORES=1 |

## Acceptance
- [x] T1 and T2 pass; each was broken once and went red (PR body).

## Device check (RG34XXSP)
Issue 214.

## References
- ADR 0103; docs/cart-art/SGX.md
