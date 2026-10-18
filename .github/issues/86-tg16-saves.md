---
title: "Keep TG16 backup RAM in .sav like every core; TurboCD out of scope"
phase: 10
area: platform
type: feature
size: S
depends_on: [83-platform-tg16]
---

## Why
Step 7. Most HuCards keep no save, but PCE Fast exposes its 2 KB backup RAM (BRAM), formatted with the `HUBM` header, as save RAM for every game (pinned by `tg16_core.rs`). Populous exposes its own 32 KB cart RAM instead. So the generic `.sav` path covers TG16 with no new code, and every game gets a 2 KB `.sav`.

## Scope
- [ ] Saves go to `Saves/TG16/<stem>.sav` through the standard path (load at insert, atomic write at flush, eject and autosave; ADR 0012, 0034, 0072).
- [ ] Decide: accept a header-only 2 KB `.sav` per game (recommended, generic, what RetroArch does) or skip writing a `.sav` that is only the formatted header (a TG16-only rule). Record it in an ADR if the second.
- [ ] Confirm `save_ram_trusted` accepts the header-only buffer (it is not blank, so ADR 0072's guard does not fire).
- [ ] **TurboCD is out of scope** (ADR 0091): no system card BIOS, no CD BRAM model, no disc images.

## Tests
| ID | File | Asserts |
|---|---|---|
| (done) | `tg16_core.rs` | BRAM is `Some`, 2048 bytes, `HUBM` header, and `load_save_ram` round-trips |
| (new) | `tg16_saves.rs` | a marked BRAM survives eject and reinsert through `Saves/TG16`; a lid-close flush writes it |

## Edge cases
| Case | Expected handling |
|---|---|
| A 2 KB `.sav` from RetroArch (`.srm` renamed) | Loads, same layout |
| Populous | 32 KB `.sav`, same path |
| A truncated `.sav` | The standard short-file handling |

## Acceptance
- [ ] `task check` green.

## Device check (RG34XXSP)
A BRAM or Populous save survives a lid close and a battery pull (issue 90).

## References
- ADR 0012, 0034, 0072, 0091; docs/research/tg16-plan.md section 3
