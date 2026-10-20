---
title: "Set the FBNeo options: Auto frameskip, no held-Start service menu"
phase: 17
area: cores
type: feature
size: S
depends_on: [185-platform-arcade]
---

## Why
FBNeo's frameskip key is not `<prefix>_frameskip`, and its default diagnostic input opens the service menu on a held Start.

## Scope
- [x] `core_options_policy::FBNEO`: frameskip Auto, diagnostic input None, Neo Geo mode DIPSWITCH, memory card off, patched romsets allowed.

## Tests
| ID | File | Asserts |
|---|---|---|
| O1 | `arcade_options.rs` | each explicit option is answered and is a value the pinned core declares |

## Edge cases
| Case | Expected handling |
|---|---|
| A Neo Geo key on a CPS set | declared only for Neo Geo sets; harmless when unanswered |

## Acceptance
- [x] O1 passes.

## Device check (RG34XXSP)
Issue 193.

## References
- ADR 0099
