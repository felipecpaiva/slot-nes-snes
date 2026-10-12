---
title: "Patch 0009: Make the core picker pair-relative and add Core::Nestopia and Core::Snes9x2005Plus"
phase: 3
area: cores
type: feature
size: M
depends_on: [15-snes-input, 19-alt-cores-build]
---

## Why
A third `Core` makes `SOCKET_U[i]` (`[f32; 2]`) index out of bounds, and the picker assumes Mgba is on the left. The picker must walk the seated platform's `(left, right)` pair, with faces from `Core::EVERY` (docs/PLAN.md Approach "Core picker is pair-relative", Build step 18).

## Scope
`patches/0009-core-picker-pairs.patch`:
- [x] Append `Core::Nestopia` ("Nestopia") and `Core::Snes9x2005Plus` ("Snes9x 2005+") in `slot: crates/slot-store/src/core.rs`, with `parse`, `runs`, `canvas`, `option_prefix`, `colour_option` None. Also `Core::EVERY` grows to 6 and `Core::pair()` gives a core's picker pair (`core_policy.rs`).
- [x] `Platform::picker_cores()`: GBA (Mgba, Gpsp), NES (Fceumm, Nestopia), SNES (Snes9x, Snes9x2005Plus), GB/GBC None.
- [x] `slot: crates/slot/src/core_picker.rs`: pair field; new `CorePicker::open_pair(seat, pair, now)`; `open(seat, now)` delegates with `seat.pair()` (for a GBA seat that is (Mgba, Gpsp), so GBA is unchanged). Pair-relative Left/Right, `rightward = hop.from == pair.0`, `across = seat == pair.1`.
- [x] `slot: crates/slot/src/frontend.rs` and new `slot: crates/slot/src/core_faces.rs`: socket and chip faces are built from `Core::EVERY` (6 each); `PairFaces` hands `App` the two sockets of the seated platform's pair in pair order (index 0 = pair.0), and all 6 chips indexed by `core.index()`.
- [x] `slot: crates/slot/src/app.rs`: **no change (0 lines)**. See the design note below.

## app.rs design (0 lines)
The `app.rs` budget (25 changed lines across all patches) is spent: 0001 6, 0002 8, 0004 4, 0005 4, 0007 3. The change in the first draft of this issue (draw loop walking the pair, `sockets[core.index()]`, chip `index()`) is not made. What `app.rs` indexes today:
- the draw loop enumerates `core_socket_faces` with `SOCKET_U[i]`, so it needs exactly 2 sockets in left, right order;
- the chip face is `core_chip_faces.get(core.index())`, and `index()` is the enum discriminant (Nestopia 4, Snes9x2005Plus 5), so the chip vector must be indexed by discriminant (6 entries from `Core::EVERY`; the GBA test still passes its 2-entry `Core::ALL` vectors);
- `chip.across` comes from `core_picker.rs`, which is now pair-relative (0.0 or 1.0).

So `PairFaces::follow` (called each frame from `Frontend`) reads `App::core_picker()` and calls the existing `App::set_core_part_faces` with the two sockets of `seat.pair()` and the 6 chips. `open_core_picker` already calls `CorePicker::open(seat, now)`, which now derives the pair from the seat, so no `app.rs` call site changes either.

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
- [x] T23, T24, T31 green; T31 under `SLOT_REQUIRE_CORES=1`.
- [x] GBA harness compare 0 diffs (H1, H2): the GBA picker renders identically. `task check` 2026-10-13: `compare: 0 diffs (H1, H1G, H2, B1, H3 patched only, held against H1)`. Also `the_picker_redraws_gba_faces_after_a_nes_visit_in_one_process` (GBA, NES, GBA in one process, pixel-equal to upstream faces).
- [x] `SOCKET_U` stays `[f32; 2]` (`slot: crates/slot-ui/src/board.rs:164`).
- [x] `Core::ALL.len() == 2` still. `app.rs` has 0 changed lines in this patch.

## Device check (RG34XXSP)
None separate. Socket names and swaps are in the phase device check in 18-phase-3-parity.

## Review notes
- Gotcha 3 (SOCKET_U panic, wrong socket names, chip drift): `socket_face` inks the core name (`slot: crates/slot-ui/src/board.rs:282-293`), so a NES picker must show FCEUmm/Nestopia sockets. Faces are indexed by `core.index()` over `EVERY`; positions are pair-relative.
- `app.rs` is untouched by this patch (budget already at 25). Faces are swapped per pair outside `app.rs`.
- `CorePicker::open` signature unchanged; it derives the pair from the seat.
- T23 and the render half of the picker need GL (macOS, not the sandbox); T23 is three tests in `nes_core_picker.rs`. T31 is three tests in `alt_cores.rs`, with recorded RGB: nestopia `[32, 49, 181, 0]` (fceumm `[32, 32, 208, 0]`), snes9x2005_plus `[57, 195, 255, 0]` (snes9x `[57, 199, 255, 0]`).
- `gpsp.rs` gains `| Core::Nestopia` and `| Core::Snes9x2005Plus` on the `Core::Mgba` arm (named exception (e)). `snes_platform.rs` (ours) now expects the SNES pair.

## References
- docs/PLAN.md: Approach (Core picker is pair-relative), Phase 3 deliverables (0009), Build step 18, Signature impact table (`CorePicker::open`), Consumer-grep evidence
- `slot: crates/slot-ui/src/board.rs:164,282-293`; `slot: crates/slot/src/core_picker.rs:115,116,151,163`; `slot: crates/slot/src/frontend.rs:602,606`; `slot: crates/slot/src/app.rs:2243-2244,2272`
