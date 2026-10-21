---
title: "SuperGrafx device gate on the RG34XXSP"
phase: 20
area: device
type: chore
size: S
depends_on: [211-platform-sgx, 212-sgx-carts]
---

## Why
No host number is a device number; two VDCs cost twice Beetle PCE Fast on the host.

## Scope
- [ ] Apply sgx-adds.tsv: the five ADD rows into Games/SGX, the two Darius MOVE rows from Games/TG16 with their labels and saves.
- [ ] bench:device with CORE=mednafen_supergrafx on Daimakaimura and 1941.
- [ ] Real play, 10 minutes each, every title; record the rows in docs/DEVICE-GATE.md (SuperGrafx section).

## Tests
| ID | File | Asserts |
|---|---|---|
| (device) |  | `slot.log` under `SLOT_TRACE`: no missed frames past the first window, `starved` 0, `dropped` 0 |

## Edge cases
| Case | Expected handling |
|---|---|
| A card misses frames | the row recorded with the bench number; `sgx_ocmultiplier` stays 1 |

## Acceptance
- [ ] Every title passes or has a recorded row.

## Device check (RG34XXSP)
This issue is the device check.

## References
- ADR 0103; docs/cart-art/SGX.md
