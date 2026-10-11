---
title: "Phase 4: real NES and SNES cart art with variants"
phase: 4
area: ui-art
type: tracking
size: L
depends_on: [18-phase-3-parity]
---

## Why
Cart art must match slot's nostalgia depth for GB/GBC/GBA, including real cartridge variants (docs/PLAN.md Context, Phased rollout Phase 4). Decision: real NES, Famicom, SNES and Super Famicom cart art with variants in v1 (docs/DECISIONS.md). Blocking for the v1 release.

## Scope
Child issues, in merge order:
- [ ] 25-cart-variant-research
- [ ] 26-cart-art
- [ ] 27-cart-shell-grammar-region

## Tests
| ID | File | Asserts |
|---|---|---|
| (children) | see child issues | T34 to T40 are owned by the child issues above |

## Edge cases
| Case | Expected handling |
|---|---|
| (children) | Each edge case is owned by the child issue that touches that layer |

## Acceptance
Phase 4 ships when:
- [ ] T34 to T40 green.
- [ ] Upstream slot-ui tests untouched and green.
- [ ] Harness 0 diffs; H3 equals H1.
- [ ] `evals/eval-cart-likeness.sh` and `evals/eval-colour-sources.sh` pass.
- [ ] Host smoke: `task run:4x3` with a mixed shelf.

## Device check (RG35XXSP)
1. A mixed shelf of NES, Famicom, SNES and SFC carts.
2. Insert and seat animations land in the correct boxes.
3. Gold Zelda shows gold.
4. Shadows sit under the carts.

## Review notes
- No colour ships without a cited reference (see 25-cart-variant-research).
- Famicom Disk System is deferred (33-deferred-fds).

## References
- docs/PLAN.md: Context (cart art decision), Phased rollout (Phase 4), Evaluation criteria
