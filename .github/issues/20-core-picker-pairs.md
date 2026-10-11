---
title: "Patch 0008: Make the core picker pair-relative and add Core::Nestopia and Core::Snes9x2005Plus"
phase: 3
area: cores
type: feature
size: M
depends_on: [15-snes-input, 19-alt-cores-build]
---

## Why
A third `Core` makes `SOCKET_U[i]` (`[f32; 2]`) index out of bounds, and the picker assumes Mgba is on the left. The picker must walk the seated platform's `(left, right)` pair, with faces from `Core::EVERY` (docs/PLAN.md Approach "Core picker is pair-relative", Build step 18).

## Scope
`patches/0008-core-picker-pairs.patch`:
- [ ] Append `Core::Nestopia` ("Nestopia") and `Core::Snes9x2005Plus` ("Snes9x 2005+") in `slot: crates/slot-store/src/core.rs`, with `parse`, `runs`, `canvas`, `option_prefix`, `colour_option` None.
- [ ] `Platform::picker_cores()`: GBA (Mgba, Gpsp), NES (Fceumm, Nestopia), SNES (Snes9x, Snes9x2005Plus), GB/GBC None.
- [ ] `slot: crates/slot/src/core_picker.rs`: pair field; new `CorePicker::open_pair(seat, pair, now)`; `open(seat, now)` delegates with (Mgba, Gpsp). Pair-relative `:115`, `:116` (Left/Right), `:151` (`rightward = hop.from == pair.0`), `:163` (`across = pos(seat)`).
- [ ] `slot: crates/slot/src/frontend.rs:602,606`: socket and chip faces built from `Core::EVERY` (6 each), indexed by `core.index()`.
- [ ] `slot: crates/slot/src/app.rs:2243-2244`: draw loop walks the pair, `SOCKET_U[pos]` with pos 0/1, `sockets[core.index()]`; chip faces by `core.index()` (`:2272`).

## Tests
| ID | File | Asserts |
|---|---|---|
| T23 | `slot/tests/nes_core_picker.rs` | NES picker, Right then A: `<stem> = nestopia` written; no panic; positions 0/1; rendered sockets carry FCEUmm and Nestopia ink (compared to `socket_face(Core::Fceumm/Nestopia)`) |
| T24 | upstream `slot/tests/core_picker.rs`, `slot/tests/render_shelf.rs` (unchanged) | GBA picker: pass untouched |
| T31 | `slot/tests/alt_cores.rs` | `SLOT_REQUIRE_CORES=1`. nestopia and snes9x2005_plus boot generated ROMs: uniform per-core recorded RGB, not mock |

Upstream `slot: crates/slot/tests/core_picker.rs` and `slot: crates/slot/tests/render_shelf.rs:49-62` stay unmodified (the 2-entry face vectors from `Core::ALL` still index correctly for the GBA pair, indices 0 and 1).

## Edge cases
| Case | Expected handling |
|---|---|
| Third Core reaches `SOCKET_U[2]` (`slot: crates/slot/src/app.rs:2244`) and panics, or a chip draws off board (`slot: crates/slot/src/core_picker.rs:163`) | Draw loop walks the platform pair with positions 0/1; `across` and `rightward` are pair-relative; T23 renders a NES picker frame |

## Acceptance
- [ ] T23, T24, T31 green; T31 under `SLOT_REQUIRE_CORES=1`.
- [ ] GBA harness compare 0 diffs (H1, H2): the GBA picker renders identically.
- [ ] `SOCKET_U` stays `[f32; 2]` (`slot: crates/slot-ui/src/board.rs:164`).
- [ ] `Core::ALL.len() == 2` still.

## Device check (RG35XXSP)
None separate. Socket names and swaps are in the phase device check in 18-phase-3-parity.

## Review notes
- Gotcha 3 (SOCKET_U panic, wrong socket names, chip drift): `socket_face` inks the core name (`slot: crates/slot-ui/src/board.rs:282-293`), so a NES picker must show FCEUmm/Nestopia sockets. Faces are indexed by `core.index()` over `EVERY`; positions are pair-relative.
- `app.rs` pair loop counts toward the 30-line `app.rs` diff-surface target.
- `CorePicker::open` signature unchanged.

## References
- docs/PLAN.md: Approach (Core picker is pair-relative), Phase 3 deliverables (0008), Build step 18, Signature impact table (`CorePicker::open`), Consumer-grep evidence
- `slot: crates/slot-ui/src/board.rs:164,282-293`; `slot: crates/slot/src/core_picker.rs:115,116,151,163`; `slot: crates/slot/src/frontend.rs:602,606`; `slot: crates/slot/src/app.rs:2243-2244,2272`
