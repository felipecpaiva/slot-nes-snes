---
title: "Draw the yellow Disk Card and fetch disk labels"
phase: 18
area: ui-art
type: feature
size: M
depends_on: [195-platform-fds]
---

## Why
Every shelf has its own object at the same fidelity. A disk is a Disk Card, not a cartridge.

## Scope
- [x] `RetroShell::Fds`: the yellow card, stepped top and centre tab, U panel with head window and hub, write-protect holes, label well, NINTENDO moulding; no shutter (most yellow disks had none).
- [x] `tools/fetch-labels.py` system FDS: No-Intro dat, headerless CRC first, ScreenScraper 106.

## Tests
| ID | File | Asserts |
|---|---|---|
| C1 | `slot-ui/tests/fds_cart.rs` | shell, colour, proportions, label well, rendering |
| C2 | `tools/tests/test_fetch_labels.py` | system row, header-stripped CRC, id 106 |

## Edge cases
| Case | Expected handling |
|---|---|
| a chosen shell colour | wins over the yellow |

## Acceptance
- [x] C1 and C2 pass; every other neutral regenerates byte for byte.

## Device check (RG34XXSP)
Issue 202, step 2.

## References
- ADR 0101; docs/cart-art/FDS.md
