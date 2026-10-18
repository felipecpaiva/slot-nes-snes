---
title: "Set the NGP core options and answer NeoPop's declared defaults"
phase: 9
area: cores
type: feature
size: S
depends_on: [72-platform-ngp]
---

## Why
Step 5. NeoPop declares one option. Answering it explicitly keeps the core's behaviour pinned (ADR 0064).

## Scope
- [ ] `ngp_language=english` set by slot's policy options.
- [ ] Decide whether ADR 0064's declared-defaults answer extends to NeoPop (it would, by the same rule, since the only key is `ngp_language`). Record the answer in the patch commit.
- [ ] The declared-key check (`core_option_keys.rs`) covers `mednafen_ngp`.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `core_option_keys.rs` | every key slot sets for mednafen_ngp is declared by the core |
| (new) | `ngp_options.rs` `neopop_runs_in_english` | `option("ngp_language") == Some("english")` after open |

## Edge cases
| Case | Expected handling |
|---|---|
| A future pin adds keys | The declared-key test still passes; new keys keep core defaults until answered |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
None.

## References
- ADR 0064, 0090
