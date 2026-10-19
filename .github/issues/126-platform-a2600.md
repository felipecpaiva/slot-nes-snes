---
title: "Add Platform::A2600 with its own shelf, scan and explicit policy"
phase: 14
area: platform
type: feature
size: M
depends_on: [124-a2600-core-build]
---

## Why
The 2600 shelf. Platform and core are appended (`SHELVES`, `EVERY`), never added to upstream's `ALL`, and every policy method answers A2600 explicitly (ADR 0063 pattern).

## Scope
- [ ] `Platform::A2600` and `Core::Stella2014` (`as_str` `stella2014`), shelf `Games/A2600`, extensions `.a26` and `.bin` (the scan is per folder, so MD's `.bin` is unaffected).
- [ ] Policy: rewind on, fast-forward on, link off, no discs, no BIOS; `save_ram_trusted` false (the core has none).
- [ ] Core opened with `open_named` like every core; core joins `dist:device`, `zip-check.sh`; licence files move to `licenses/`; `A2600` joins the `games` list.
- [ ] README row, docs/PLAN.md step.

## Tests
| ID | File | Asserts |
|---|---|---|
| (new) | `a2600_scan.rs` | `.a26` and `.bin` in `Games/A2600` are found, a `.bin` in `Games/MD` stays Mega Drive |
| (new) | `a2600_seat.rs` | a generated cart seats and publishes frames |

## Edge cases
| Case | Expected handling |
|---|---|
| A `.zip` in the folder | Not listed (zip non-goal); README points at the #147 unzip path |
| A 2600 `.bin` in `Games/MD` | Mega Drive refuses it as today; no cross-shelf guessing |

## Acceptance
- [ ] `task check` green; GBA harness 0 diffs.

## Device check (RG34XXSP)
Part of issue 132.

## References
- ADR 0095; docs/research/atari-plan.md
